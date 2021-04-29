from django.contrib import admin

# Register your models here.

from .models import Profile, AuctionItem, Bid
admin.site.register(AuctionItem)
admin.site.register(Profile)
admin.site.register(Bid)