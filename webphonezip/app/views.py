from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from django.db.models.signals import post_save
from django.forms.models import model_to_dict
from django.dispatch import receiver
from .models import User, Product, Order, OrderItem, Slider, Profile, Cart, CartItem
from random import sample
import unidecode
import smtplib
import random
import datetime
import json
import os
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files import File
from django.core.paginator import Paginator, EmptyPage

def sort(request):
    price_order = request.GET.get('priceOrder', 'asc')

    if price_order == 'desc':
        products = Product.objects.order_by('-price')
    else:
        products = Product.objects.order_by('price')

    products_list = list(products.values())

    return JsonResponse(products_list, safe=False)

# Create your views here.
# Load Home page
def home(request):
    if request.user.is_authenticated:
        customer = request.user
        cart, created = Cart.objects.get_or_create(customer=customer)
    else:
        cart = {'getCartItemsAmount': 0}
    sliders = Slider.objects.all()
    context = {'cart': cart, 'sliders': sliders}
    return render(request, 'app/home.html', context)

# Load notifications page
def notifications(request):
    if request.user.is_authenticated:
        user = request.user
        cart, created = Cart.objects.get_or_create(customer=user)
    else:
        user = None
        cart = {'getCartItemsAmount': 0}
    context = {'cart': cart}
    return render(request, 'app/notifications.html', context)


def gurantee(request):
    if request.user.is_authenticated:
        user = request.user
        cart, created = Cart.objects.get_or_create(customer=user)
    else:
        user = None
        cart = {'getCartItemsAmount': 0}
    context = {'cart': cart}
    return render(request, 'app/gurantee.html', context)

def aboutus(request):
    if request.user.is_authenticated:
        user = request.user
        cart, created = Cart.objects.get_or_create(customer=user)
    else:
        user = None
        cart = {'getCartItemsAmount': 0}
    context = {'cart': cart}
    return render(request, 'app/aboutus.html', context)



# Load info product page
def product(request, slugName):
    if request.user.is_authenticated:
        customer = request.user
        cart, created = Cart.objects.get_or_create(customer=customer)
    else:
        customer = None
        cart = {'getCartItemsAmount': 0}
    
    allProducts = list(Product.objects.values('id', 'slugName', 'imageURL'))
    random.shuffle(allProducts)  # Xáo trộn danh sách
    if len(allProducts) > 30:
        products = allProducts[:30]  # Lấy 30 sản phẩm đầu tiên sau khi xáo trộn
    else:
        products = allProducts
    product = get_object_or_404(Product, slugName=slugName)
    context = {'cart': cart, 'products': products, 'product': product}
    return render(request, 'app/product.html', context)

# Load cart page
def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        cart, created = Cart.objects.get_or_create(customer=customer)
        cartItems = cart.cartitem_set.all()
    else:
        customer = None
        cartItems = []
        cart = {'getCartItemsAmount': 0}
    context = {'cartItems': cartItems, 'cart': cart}
    return render(request, 'app/cart.html', context)

# Load payment page
def payment(request):
    if request.user.is_authenticated:
        customer = request.user
        cart, created = Cart.objects.get_or_create(customer=customer)
        try:
            order = get_object_or_404(Order, customer=customer, complete=False, active=True)
            items = order.orderitem_set.all()
        except Http404:
            order = {'get_cart_items':0, 'get_cart_total':0}
            items = []
    else:
        customer = None
        items = []
        cart = {'getCartItemsAmount': 0}
        order = {'get_cart_items':0, 'get_cart_total':0}
    context = {'cart': cart, 'order': order, 'items': items}
    return render(request, 'app/payment.html', context)

# Load informations of customer orders
def order(request):
    if request.user.is_authenticated:
        customer = request.user
        cart, created = Cart.objects.get_or_create(customer=customer)
        orders = Order.objects.filter(customer=customer)
        ordersWithItems = []

        for order in orders:
            orderItems = order.orderitem_set.all()
            ordersWithItems.append((order, orderItems))
    else:
        customer = None
        cart = {'getCartItemsAmount': 0}
        ordersWithItems = []
    context = {'cart': cart ,'ordersWithItems': ordersWithItems}
    return render(request, 'app/order.html', context)

# Load order infomations details
def orderDetails(request, order_id):
    if request.user.is_authenticated:
        customer = request.user
        cart, created = Cart.objects.get_or_create(customer=customer)
        try:
            order = get_object_or_404(Order, customer=customer, id=order_id)
            items = order.orderitem_set.all()
        except Http404:
            order = {'get_cart_items':0, 'get_cart_total':0}
            items = []
    else:
        customer = None
        cart = {'getCartItemsAmount': 0}
        order = {'get_cart_items':0, 'get_cart_total':0}
        items = []
    context = {'cart': cart ,'order': order, 'items': items}
    return render(request, 'app/orderdetail.html', context)

# Search product by name
def search(request, query):
    if request.user.is_authenticated:
        customer = request.user
        cart, created = Cart.objects.get_or_create(customer=customer)
    else:
        cart = {'getCartItemsAmount': 0}
    result = query
    query = '-'.join(unidecode.unidecode(query.strip()).split())
    products = Product.objects.filter(slugName__icontains=query)
    size = products.count()
    context = {'result' : result, 'size' : size, 'cart': cart ,'products' : products}
    return render(request, 'app/search.html', context)

# Search product by category
def filter_category(request):
    category = request.GET.get('category')
    products = Product.objects.filter(category=category)
    product_list = []

    for product in products:
        product_dict = model_to_dict(product, exclude=["image"])
        product_dict['imageURL'] = product.imageURL
        product_list.append(product_dict)

    return JsonResponse(product_list, safe=False)

# API get list product for homepage
allProductsAPI = list(Product.objects.values('id', 'name', 'price', 'cost', 'slugName', 'imageURL'))
paginator = Paginator(allProductsAPI, 18)

def productsApi(request):
    start = int(request.GET.get('start', 1))

    if start == 1:
        random.shuffle(allProductsAPI)

    try:
        pageObj = paginator.page(start)
        listProducts = list(pageObj.object_list)
    except EmptyPage:
        listProducts = []
 
    return JsonResponse(listProducts, safe=False)

# Handle update product to cart
def updateItem(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            action = data['action']
            
            product = Product.objects.get(id=data['productId'])
            cart, created = Cart.objects.get_or_create(customer=request.user)
            cartItem, created = CartItem.objects.get_or_create(cart=cart, product=product)

            if action == 'add':
                cartItem.quantity += data['quantity']
            elif action == 'remove':
                cartItem.quantity -= 1
            elif action == 'delete':
                cartItem.quantity = -1
            cartItem.save()
            if cartItem.quantity <= 0:
                cartItem.delete()

            return JsonResponse({'success': 'Cập nhật thành công'})
        else:
            return JsonResponse({'error': 'Người dùng chưa đăng nhập'})
    else:
        return JsonResponse({'error': 'Gửi yêu cầu thất bại'})

# Create a order for current user
def createOrder(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            listProductsOrder = data['listProductsOrder']

            Order.objects.filter(customer=request.user, active=True).update(active=False)
            order = Order.objects.create(customer=request.user, complete=False, active=True, isPaid=False)

            for item in listProductsOrder:
                try:
                    product = Product.objects.get(id=item['id'])
                    quantity = item['quantity']
                    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
                    orderItem.quantity = quantity
                    orderItem.save()
                except:
                    return JsonResponse({'error': 'Sản phẩm này không còn tồn tại, vui lòng cập nhật giỏ hàng'})
            return JsonResponse({'success': 'Đã tạo đơn hàng'})
        else:
            return JsonResponse({'error': 'Vui lòng đăng nhập để thanh toán'})
    else:
        return JsonResponse({'error': 'Gửi yêu cầu thất bại'})

def confirmPaymentOrder(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)

            try:
                order = get_object_or_404(Order, customer=request.user, complete=False, active=True)

                order.name = data['name']
                order.phoneNumber = data['phone-number']
                order.address = data['address']
                order.active = False
                order.isPaid = True
                order.save()
                return JsonResponse({'success': 'Thành công'})
            except Http404:
                return JsonResponse({'error': 'Không tìm thấy đơn hàng'}, status=404)
        else:
            return JsonResponse({'error': 'Vui lòng đăng nhập để thanh toán'})
    else:
        return JsonResponse({'error': 'Gửi yêu cầu thất bại'})

def paymentOrderAgain(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)

            try:
                order = get_object_or_404(Order, customer=request.user, complete=False, id=data['order-id'])
                order.active = True
                order.save()

                return JsonResponse({'success': 'Gửi yêu cầu thanh toán lại thành công'})
            except Http404:
                return JsonResponse({'error': 'Không tìm thấy đơn hàng'}, status=404)
        else:
            return JsonResponse({'error': 'Vui lòng đăng nhập để thanh toán'})
    else:
        return JsonResponse({'error': 'Gửi yêu cầu thất bại'})

def confirmOrderComplete(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            customer = request.user
            
            try:
                order = get_object_or_404(Order, customer=customer, id=data['order-id'])
                order.complete = True
                order.save()
                return JsonResponse({'success': 'Đơn hàng đã hoàn thành'})
            except Http404:
                return JsonResponse({'error': 'Không tìm thấy đơn hàng'})
        else:
            return JsonResponse({'error': 'Vui lòng đăng nhập để tiếp tục'})
    else:
        return JsonResponse({'error': 'Gửi yêu cầu thất bại'})

def updateCartItem(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            listProductsId = data['listProductsId']

            cart, created = Cart.objects.get_or_create(customer=request.user)
            for productId in listProductsId:
                product = Product.objects.get(id=productId)
                cartItem, created = CartItem.objects.get_or_create(cart=cart, product=product)
                cartItem.delete()
            return JsonResponse({'success': 'Cập nhật thành công'})
        else:
            return JsonResponse({'error': 'Người dùng chưa đăng nhập'})
    else:
        return JsonResponse({'error': 'Gửi yêu cầu thất bại'})

# Load info account page
def profile(request):
    if request.user.is_authenticated:
        user = request.user
        cart, created = Cart.objects.get_or_create(customer=user)
    else:
        user = None
        cart = {'getCartItemsAmount': 0}
    context = {'user': user, 'cart': cart}
    return render(request, 'app/profile.html', context)

# Handle send and receive new user account registration information
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        if User.objects.filter(username=data['username']).exists():
            return JsonResponse({'error': 'Username đã tồn tại, vui lòng sử dụng một tên khác.'})
        
        if User.objects.filter(email=data['email']).exists():
            return JsonResponse({'error': 'Email này đã được đăng ký cho một tài khoản khác, vui lòng sử dụng một email khác.'})
        
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        user.save()

        return JsonResponse({'success': 'Đăng ký thành công'}, status=200)
    else:
        return JsonResponse({'error': 'Gửi yêu cầu thất bại, vui lòng thử lại sau.'}, status=400)

def signIn(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        account = data.get('name-account')
        password = data.get('password')
        User = get_user_model()
        try:
            if '@' in account:
                user = User.objects.get(email=account)
            else:
                user = User.objects.get(username=account)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Tên tài khoản này không tồn tại.'}, status=400)

        if user.check_password(password):
            login(request, user)
            return JsonResponse({'success': 'Đăng nhập thành công.'}, status=200)
        else:
            return JsonResponse({'error': 'Mật khẩu sai.'}, status=400)
    else:
        return JsonResponse({'error': 'Gửi yêu cầu thất bại, vui lòng thử lại sau.'}, status=400)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def signOut(request):
    logout(request)
    return JsonResponse({'success': 'Đăng xuất thành công.'}, status=200)

# API to update info account
def updateAccount(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            user = User.objects.get(id=data['userId'])

            if 'username' in data:
                if User.objects.filter(username=data['username']).exists():
                    return JsonResponse({'error': 'Username đã tồn tại, vui lòng sử dụng một tên khác.'})

                setattr(user, 'username', data['username'])
                user.save()
                return JsonResponse({'success': 'Username đã được cập nhật.'})

            elif 'fullname' in data:
                setattr(user.profile, 'fullname', data['fullname'])
                user.profile.save()
                return JsonResponse({'success': 'Tên của bạn đã được cập nhật.'})

            elif 'phone-number' in data:
                if len(data['phone-number']) == 10 and data['phone-number'].isdigit():
                    setattr(user.profile, 'phoneNumber', data['phone-number'])
                    user.profile.save()
                    return JsonResponse({'success': 'Số điện thoại đã được cập nhật.'})
                else:
                    return JsonResponse({'error': 'Số điện thoại chưa đúng định dạng (chỉ gồm 10 kí tự số).'})

            elif 'email' in data:
                if user.email == data['email']:
                    return JsonResponse({'error': 'Email này trùng với email hiện tại của bạn, vui lòng sử dụng một email khác'})

                if User.objects.filter(email=data['email']).exists():
                    return JsonResponse({'error': 'Email này đã được đăng ký cho một tài khoản khác, vui lòng sử dụng một email khác.'})
            else:
                return JsonResponse({'error': 'Dữ liệu không hợp lệ.'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'Tài khoản không tồn tại.'})
    else:
        return JsonResponse({'error': 'Gửi yêu cầu thất bại, vui lòng thử lại sau.'})

def getIdUser(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            return JsonResponse({'id': request.user.id})
        else:
            return JsonResponse({'error': 'Chưa có tài khoản nào đăng nhập.'})
    else:
        return JsonResponse({'error': 'Gửi yêu cầu thất bại, vui lòng thử lại sau.'})

@api_view(['POST'])
def updateAvatar(request):
    if request.method == 'POST':
        if 'avatar' in request.FILES:
            file = request.FILES['avatar']
            user = request.user

            oldAvatarPath = user.profile.avatar.path if user.profile.avatar else None   # Get old path file user avatar
            
            # Delete old file user avatar when new avatar is update
            if oldAvatarPath and os.path.isfile(oldAvatarPath):
                os.remove(oldAvatarPath)

            user.profile.avatar.save(file.name, File(file), save=True)

            return Response({'success': 'Avatar đã được cập nhật.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Không tìm thấy file.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error': 'Gửi yêu cầu thất bại, vui lòng thử lại sau.'}, status=400)

def changePassword(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = User.objects.get(id=data['userId'])

        if check_password(data['password'], user.password):
            if(data['new-password'] == data['password']):
                return JsonResponse({'error': 'Mật khẩu này trùng với mật khẩu cũ, vui lòng sử dụng mật khẩu khác.'})
            else:
                user.set_password(data['new-password'])
                user.save()
                return JsonResponse({'success': 'Thay đổi mật khẩu thành công.'})
        else:
            return JsonResponse({'error': 'Mật khẩu cũ không đúng, vui lòng nhập lại.'})
    else:
        return JsonResponse({'error': 'Gửi yêu cầu thất bại, vui lòng thử lại sau.'})
