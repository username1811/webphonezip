
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.signIn, name='login'),
    path('logout/', views.signOut, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('cart/', views.cart, name='cart'),
    path('product/<str:slugName>/', views.product, name='product'),
    path('payment/', views.payment, name='payment'),
    path('update-item/', views.updateItem, name='update-item'),
    path('search/<str:query>/', views.search, name='search'),
    path('filter-category/', views.filter_category, name='filter-category'),
    path('api/products/', views.productsApi, name='products-api'),
    path('api/update-account/', views.updateAccount, name='update-account'),
    path('api/user-id/', views.getIdUser, name='user-id'),
    path('api/update-avatar/', views.updateAvatar, name='update-avatar'),
    path('api/change-password/', views.changePassword, name='change-password'),
    path('notifications/', views.notifications, name='notifications'),
    path('order/', views.order, name='order'),
    path('create-order/', views.createOrder, name='create-order'),
    path('confirm-payment-order/', views.confirmPaymentOrder, name='confirm-payment-order'),
    path('update-cart-items/', views.updateCartItem, name='update-cart-items'),
    path('confirm-order-complete/', views.confirmOrderComplete, name='confirm-order-complete'),
    path('order/details/<int:order_id>', views.orderDetails, name='order-details'),
    path('order/payment-again/', views.paymentOrderAgain, name='payment-again'),
    path('api/sort', views.sort, name='sort'),
    path('gurantee.html', views.gurantee, name='gurantee'),
    path('aboutus.html', views.aboutus, name='aboutus')
]