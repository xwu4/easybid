from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404

from django.views.decorators.csrf import csrf_exempt
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapps.settings")
django.setup()

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from easybid.forms import LoginForm, RegisterForm, AuctionItemPicForm, ProfilePicForm, AuctionItemEditForm
from easybid.models import Profile, AuctionItem, Bid
from datetime import datetime
from django.utils.timezone import get_current_timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from django.utils import timezone
from django.db.utils import OperationalError
import time # for adding sleep calls to demonstrate concurrency issues
from background_task import background
from django.conf import settings
from django.core.mail import send_mail

# Create your views here.
def home(request):
    context = {}
    context["auction_items"] = AuctionItem.objects.all().order_by("product_name")
    id_list = []
    try:
        for each in context["auction_items"]:
            id_list.append(str(each.id))
    except OperationalError:
        pass

    context["id_list"] = ",".join(id_list)
    return render(request, 'easybid/homepage.html', context)

def auction_view(request, type):
    context = {}
    cur_time = datetime.now()
    if type == "Upcoming":
        context["auction_items"] = AuctionItem.objects.filter(start_time__gt = cur_time).order_by("product_name")
        context["page_name"] = "Upcoming Auctions"
    elif type == "Expired":
        context["auction_items"] = AuctionItem.objects.filter(end_time__lt = cur_time).order_by("product_name")
        context["page_name"] = "Expired Auctions"
    else:
        context["auction_items"] = AuctionItem.objects.filter(start_time__lt = cur_time).filter(end_time__gt = cur_time).order_by("end_time")
        context["page_name"] = "Current Auctions"
    id_list = []

    try:
        for each in context["auction_items"]:
                id_list.append(str(each.id))
    except OperationalError:
        pass

    context["id_list"] = ",".join(id_list)
    return render(request, 'easybid/homepage.html', context)


def login_action(request):
    context = {}

    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'easybid/login.html', context)

    form = LoginForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'easybid/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)

    return redirect(reverse('home'))


def logout_action(request):
    logout(request)
    return redirect('home')


def register_action(request):
    context = {}
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'easybid/register.html', context)

    form = RegisterForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'easybid/register.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])

    new_user.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    subject = 'Welcome to Easybid!'
    message = f'Hi {new_user.first_name}, thank you for registering in Easybid.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [new_user.email, ]
    send_mail( subject, message, email_from, recipient_list )
    
    # Create Profile
    new_profile = Profile(owner=new_user, update_time=timezone.now())
    new_profile.save()

    login(request, new_user)

    return redirect(reverse('home'))


@login_required
def new_auction_page(request):
    context = {}
    context['form'] = AuctionItemPicForm()
    return render(request, 'easybid/new_auction.html', context)


def get_user_info(request, context):
    context["user"] = request.user
    return context


@login_required
@ensure_csrf_cookie
def create_auction(request):
    if request.method == 'GET':
        context = {}
        context['form'] = AuctionItemPicForm()
        return render(request, 'easybid/new_auction.html', context)

    else:
        context = {}
        context = get_user_info(request, context)
        context["product_name"] = request.POST["product_name"]
        context["product_description"] = request.POST["product_description"]
        context["product_value"] = request.POST["product_value"]
        context["starting_price"] = request.POST["starting_price"]
        context["min_bid_increment"] = request.POST["min_bid_increment"]
        context["start_time"] = request.POST["start_time"]
        context["end_time"] = request.POST["end_time"]
        print((context["start_time"]))
        new_auction = AuctionItem(seller=request.user, product_name=context["product_name"],
                                  product_description=context["product_description"],
                                  product_value=context["product_value"],
                                  starting_price=context["starting_price"],
                                  min_bid_increment=context["min_bid_increment"])
        local = get_current_timezone()
        start_time_naive = datetime.strptime(context["start_time"], "%m/%d/%Y %I:%M %p")
        new_auction.start_time = local.localize(start_time_naive)
        end_time_naive = datetime.strptime(context["end_time"] , "%m/%d/%Y %I:%M %p")
        new_auction.end_time = local.localize(end_time_naive)
        now = datetime.now()
        now = local.localize(now)
        now_withoutsecond = now.replace(second=0, microsecond=0)
        auction_item_form = AuctionItemPicForm(request.POST, request.FILES, instance=new_auction)
        if new_auction.end_time <= new_auction.start_time:
            context['form'] = auction_item_form
            context['error'] = "End time must be later than start time!"
            return render(request, 'easybid/new_auction.html', context)
        
        if new_auction.start_time < now_withoutsecond:
            context['form'] = auction_item_form
            context['error'] = "Please choose future start time!"
            return render(request, 'easybid/new_auction.html', context)

        if not auction_item_form.is_valid():
            context['form'] = auction_item_form
            return render(request, 'easybid/new_auction.html', context)

        else:
            if new_auction.start_time == now_withoutsecond:
                new_auction.start_time = now
            if auction_item_form.cleaned_data['product_image'] != None:
                new_auction.content_type = auction_item_form.cleaned_data['product_image'].content_type
            new_auction.update_time = now
            new_auction.save()
            
            context = {}
            context["item"] = new_auction
            context["message"] = "Your auction has been created successfully!"
            return render(request, 'easybid/auction_success.html', context)


@login_required
@ensure_csrf_cookie
def view_my_profile(request):
    context = {}
    context = get_user_info(request, context)
    profile = get_object_or_404(Profile, owner=request.user)
    context["user"] = request.user
    context["profile_picture"] = profile.profile_picture
    context["form"] = ProfilePicForm()
    context["bio_text"] = profile.bio_text
    context["auction_items"] = AuctionItem.objects.filter(seller=request.user).order_by("product_name")
    bids = Bid.objects.filter(bidder=request.user)
    bid_items = set()
    for each in bids:
        bid_items.add(each.auction_item)
    context["bid_items"] = bid_items
    return render(request, 'easybid/user_profile.html', context)


@login_required
@ensure_csrf_cookie
def profile_picture(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, owner=user)

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not profile.profile_picture:
        raise Http404

    return HttpResponse(profile.profile_picture, content_type=profile.content_type)


@login_required
@ensure_csrf_cookie
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        context = {}
        context = get_user_info(request, context)
        profile = get_object_or_404(Profile, owner=request.user)

        profile.bio_text = request.POST["bio_text"]
        profile.save(update_fields=["bio_text"])
        context["bio_text"] = profile.bio_text

        profile_picture_form = ProfilePicForm(request.POST, request.FILES, instance=profile)
        if not profile_picture_form.is_valid():
            context['form'] = profile_picture_form
            return redirect(reverse('view_my_profile'))

        else:
            profile.content_type = profile_picture_form.cleaned_data['profile_picture'].content_type
            profile.save(update_fields=["profile_picture"])
            profile.save(update_fields=["content_type"])
            context['form'] = ProfilePicForm()

    return redirect(reverse('view_my_profile'))

@ensure_csrf_cookie
def view_item_detail(request, id):
    context = {}
    if request.user.is_authenticated: 
        context = get_user_info(request, context)
        profile = get_object_or_404(Profile, owner=request.user)

    item = get_object_or_404(AuctionItem, id=id)
    
    context['item'] = item
    context["user"] = request.user
    context['room_name'] = id
  
    return render(request, 'easybid/item_detail.html', context)


def bid_price_check(id, price):
    message = None
    item = get_object_or_404(AuctionItem, id=id)
    if item.is_expired == True:
        message = "Expired"
        return False, message
    if item.is_expired == False:
        if item.highest_bid is None:
            if item.starting_price > price:
                message = "The bidding price is too low! Discard this bid."
                return False, message
        elif item.highest_bid.price + item.min_bid_increment > price:
            message = "The bidding price is too low! Discard this bid."
            return False, message
    return True, message

@login_required
@ensure_csrf_cookie
@transaction.atomic
def update_bid_price(request, id):
    if request.method == "POST":
        context = {}
        context = get_user_info(request, context)
        item = get_object_or_404(AuctionItem, id=id)

        if request.user == item.seller:
            return redirect(reverse('view_item_detail', kwargs={'id': id}))

        # Handle invalid bid price
        # if item.is_expired == False:
        #     if item.highest_bid is None:
        #         if item.starting_price > float(request.POST["bid_price"]):
        #             print("The bidding price is too low! Discard this bid.")
        #             return redirect(reverse('view_item_detail', kwargs={'id': id}))
        #     elif item.highest_bid.price + item.min_bid_increment > float(request.POST["bid_price"]):
        #         print(item.highest_bid.price + item.min_bid_increment)
        #         print(request.POST["bid_price"])
        #         print("The bidding price is too low! Discard this bid.")
        #         return redirect(reverse('view_item_detail', kwargs={'id': id}))
        status, message = bid_price_check(id, float(request.POST["bid_price"]))
        if status == False:
            print(message)
            return redirect(reverse('view_item_detail', kwargs={'id': id}))

        new_bid = Bid()
        new_bid.auction_item = item
        new_bid.bidder = request.user
        new_bid.time = timezone.now()
        new_bid.price = request.POST["bid_price"]
        new_bid.save()

        # Send email notification to bidder with lower price when there is higher price
        subject = f'Higher price on item {item.product_name}!'
        message = f'Someone has bid item {item.product_name} with price ${item.highest_bid.price}!'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = []
        for bidder in item.lower_price_bidder_list:
            recipient_list.append(bidder.email)
        send_mail( subject, message, email_from, recipient_list)
    return redirect(reverse('view_item_detail', kwargs={'id': id}))

def view_other_profile(request, id):
    if request.user.is_authenticated and request.user.id == id: 
        return redirect("view_my_profile")
    context = {}
    user = get_object_or_404(User, id = id)
    profile = get_object_or_404(Profile, owner=user)
    context["user"] = request.user
    context["owner"] = user
    context["profile_picture"] = profile.profile_picture
    context["bio_text"] = profile.bio_text
    context["auction_items"] = AuctionItem.objects.filter(seller=user).order_by("product_name")
    return render(request, 'easybid/other_profile.html', context)

def product_image(request, id):
    item = get_object_or_404(AuctionItem, id=id)

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not item.product_image:
        raise Http404

    return HttpResponse(item.product_image, content_type=item.content_type)

@login_required
@transaction.atomic
def auction_item_edit(request, id):
    try:
        if request.method == "GET":
            item = AuctionItem.objects.get(id=id)
            context = {}
            context = get_user_info(request, context)
            context["product_name"] = item.product_name
            context["product_description"] = item.product_description
            context["product_value"] = item.product_value
            context["starting_price"] = item.starting_price
            context["min_bid_increment"] = item.min_bid_increment
            context["start_time"] = item.start_time.replace(tzinfo=None).strftime("%m/%d/%Y %-I:%M %p")
            context["end_time"] = item.end_time.replace(tzinfo=None).strftime("%m/%d/%Y %-I:%M %p")
            context["item"] = item
            context['form'] = AuctionItemEditForm(instance=item)
            return render(request, 'easybid/edit_auction.html', context)

        context = {}
        context = get_user_info(request, context)
        context["product_name"] = request.POST["product_name"]
        context["product_description"] = request.POST["product_description"]
        context["product_value"] = request.POST["product_value"]
        context["starting_price"] = request.POST["starting_price"]
        context["min_bid_increment"] = request.POST["min_bid_increment"]
        context["start_time"] = request.POST["start_time"]
        context["end_time"] = request.POST["end_time"]

        auction_edited = AuctionItem.objects.select_for_update().get(id=id)
        context["item"] = auction_edited
        db_update_time = auction_edited.update_time
        prev_start_time = auction_edited.start_time
        local = get_current_timezone()
        start_time_naive = datetime.strptime(context["start_time"], "%m/%d/%Y %I:%M %p")
        auction_edited.start_time = local.localize(start_time_naive)
        end_time_naive = datetime.strptime(context["end_time"] , "%m/%d/%Y %I:%M %p")
        auction_edited.end_time = local.localize(end_time_naive)
        now = datetime.now()
        now = local.localize(now)
        now_withoutsecond = now.replace(second=0, microsecond=0)

        if now > prev_start_time:
            return redirect(reverse('view_item_detail', kwargs={'id': id}))

        auction_item_form = AuctionItemEditForm(request.POST, request.FILES, instance=auction_edited)

        if auction_edited.end_time <= auction_edited.start_time:
            context['form'] = auction_item_form
            context['error'] = "End time must be later than start time!"
            return render(request, 'easybid/edit_auction.html', context)
        
        if auction_edited.start_time < now_withoutsecond:
            context['form'] = auction_item_form
            context['error'] = "Please choose future start time!"
            return render(request, 'easybid/edit_auction.html', context)

        if not auction_item_form.is_valid():
            context['form'] = auction_item_form
            if "No image was uploaded" not in auction_item_form.errors.as_json():
                return render(request, 'easybid/edit_auction.html', context)
        
        # if update times do not match, someone else updated DB record while we were editing
        if db_update_time != auction_item_form.cleaned_data['update_time']:
            # Refetch entry from DB (because EditForm had modified it) and try again.
            auction_edited = AuctionItem.objects.get(id=id)
            form = AuctionItemEditForm(instance=auction_edited)
            context = {
                'error': 'This record has been modified.  Re-enter your changes.',
                'item':   auction_edited,
                'form':    form,
            }
            context = get_user_info(request, context)
            context["product_name"] = auction_edited.product_name
            context["product_description"] = auction_edited.product_description
            context["product_value"] = auction_edited.product_value
            context["starting_price"] = auction_edited.starting_price
            context["min_bid_increment"] = auction_edited.min_bid_increment
            context["start_time"] = auction_edited.start_time.replace(tzinfo=None).strftime("%m/%d/%Y %-I:%M %p")
            context["end_time"] = auction_edited.end_time.replace(tzinfo=None).strftime("%m/%d/%Y %-I:%M %p")
            return render(request, 'easybid/edit_auction.html', context)
        
        else:
            if auction_edited.start_time == now_withoutsecond:
                auction_edited.start_time = now
            if auction_item_form.is_valid():
                auction_edited.content_type = auction_item_form.cleaned_data['product_image'].content_type
            auction_edited.product_name = context["product_name"]
            auction_edited.product_description = context["product_description"]
            auction_edited.product_value = context["product_value"]
            auction_edited.starting_price = context["starting_price"]
            auction_edited.min_bid_increment = context["min_bid_increment"]
            auction_edited.update_time = now
            auction_edited.save()
            context = {}
            context["item"] = auction_edited
            context["message"] = "Your auction has been updated successfully!"
            return render(request, 'easybid/auction_success.html', context)


    except AuctionItem.DoesNotExist:
        return home(request)

@login_required
def auction_item_delete(request, id):
    if request.method == 'POST':
        print("this?")
        item = get_object_or_404(AuctionItem, id=id)
        if request.user == item.seller:
            print("here?")
            item.delete()
            message = 'Your auction has been deleted successfully!'
            return render(request, 'easybid/auction_success.html', { 'message': message })
    else:
        return view_item_detail(request, id)

def notify_winner(request, id):
    print("notify winner")
    item = get_object_or_404(AuctionItem, id=id)
    highest_bidder = item.highest_bid.bidder
    subject = f'You win bid of {item.product_name}!'
    message = f'''Hi, {highest_bidder.first_name},
    Congratulations on winning bid of {item.product_name}! with price ${item.highest_bid.price}'''
    email_from = settings.EMAIL_HOST_USER
    recipient_list = []
    recipient_list.append(highest_bidder.email)
    send_mail( subject, message, email_from, recipient_list)
    return redirect(reverse('view_item_detail', kwargs={'id': id}))


def paypal(request, id):
    context = {}
    item = get_object_or_404(AuctionItem, id=id)
    context['item'] = item
    return render(request, "easybid/paypal.html", context)
