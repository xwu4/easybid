from django.urls import path
from easybid import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('home', views.home, name = 'home'),
    path('login', views.login_action, name = 'login'),
    path('register', views.register_action, name = 'register'),
    path('logout', views.logout_action, name='logout'),
    path('new_auction', views.new_auction_page, name='new_auction'),
    path('create_auction', views.create_auction, name='create_auction'),
    path('view_my_profile', views.view_my_profile, name='view_my_profile'),
    path('profile_picture/<str:username>', views.profile_picture, name='profile_picture'),
    path('update_profile', views.update_profile, name='update_profile'),
    path('view_item_detail/<int:id>', views.view_item_detail, name='view_item_detail'),
    path('update_bid_price/<int:id>', views.update_bid_price, name='update_bid_price'),
    path('view_other_profile/<int:id>', views.view_other_profile, name='view_other_profile'),
    path('edit_auction/<int:id>', views.auction_item_edit, name='edit_auction'),
    path('product_image/<int:id>', views.product_image, name='product_image'),
    path('delete_auction/<int:id>', views.auction_item_delete, name='delete_auction'),
    path('auction_view/<str:type>', views.auction_view, name='auction_view'),
    path('notify_winner/<int:id>', views.notify_winner, name='notify_winner'),
    path('paypal/<int:id>', views.paypal, name='paypal')
]
