from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError
from datetime import datetime, timedelta, timezone
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

class Profile(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    bio_text = models.CharField(max_length=500)
    profile_picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50,blank=True)
    update_time = models.DateTimeField(default = datetime.now())

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(owner=instance)
    instance.profile.save()

class AuctionItem(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    product_image = models.FileField(blank=True)
    content_type = models.CharField(max_length=50, blank=True)
    product_description = models.CharField(max_length=500)
    product_value = models.DecimalField(validators=[MinValueValidator(0.0)], max_digits=19, decimal_places=2)
    starting_price = models.DecimalField(validators=[MinValueValidator(0.0)], max_digits=19, decimal_places=2)
    min_bid_increment = models.DecimalField(validators=[MinValueValidator(1.0)], max_digits=19, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    bid_count = models.IntegerField(default=0)
    update_time = models.DateTimeField()
    # winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="winner", related_query_name="winner")

    @property
    def is_expired(self):
        if datetime.now(timezone.utc) > self.end_time:
            return True
        return False
    
    @property
    def is_started(self):
        if datetime.now(timezone.utc) > self.start_time:
            return True
        return False

    @property
    def time_remaining(self):
        if not self.is_expired:
            now = datetime.now(timezone.utc)
            time_remaining = self.end_time - now
            return time_remaining
        else:
            return 0
    
    @property
    @transaction.atomic
    def highest_bid(self):
        # TODO: For same price, choose the earlier bid
        highest_bid = Bid.objects.filter(auction_item=self).order_by('-price').first()
        if highest_bid:
            return highest_bid
        return None

    @property
    def lower_price_bidder_list(self):
        bid_list = Bid.objects.filter(auction_item=self).all()
        bidder_list = []
        for bid in bid_list:
            bidder_list.append(bid.bidder)
        highest_bid = Bid.objects.filter(auction_item=self).order_by('-price').first()
        highest_bidder = highest_bid.bidder
        bidder_list.remove(highest_bidder)
        return bidder_list
    
    @property
    def next_price(self):
        highest_bid = Bid.objects.filter(auction_item=self).order_by('-price').first()
        if highest_bid:
            return highest_bid.price+self.min_bid_increment
        else:
            return self.starting_price+self.min_bid_increment
   

class Bid(models.Model):
    auction_item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField()
    price = models.DecimalField(max_digits=19, decimal_places=2)

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.auction_item = AuctionItem.objects.get(pk=self.auction_item.pk)
        self.auction_item.bid_count +=1
        self.auction_item.save(update_fields=["bid_count"])
        super(Bid, self).save(*args, **kwargs)
    
    @transaction.atomic
    def delete(self, *args, **kwargs):
        self.auction_item = AuctionItem.objects.get(pk=self.auction_item.pk)
        self.auction_item.bid_count -=1
        self.auction_item.save(update_fields=["bid_count"])
        super(Bid, self).delete(*args, **kwargs)
    
    def __str__(self):
        return str(self.auction_item.product_name) + ' ' + str(self.price)

    