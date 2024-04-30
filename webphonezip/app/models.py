from django.db import models
from django.contrib.auth.models import User
import unidecode
import re
import urllib.parse

class Profile(models.Model):
    """User profile model."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(default='user', max_length=50, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatar', null=True, blank=True)
    phoneNumber = models.CharField(default='Chưa có', max_length=10, null=True, blank=True)
    address = models.CharField(default='Chưa có', max_length=300, null=True, blank=True)

    @property
    def avatarURL(self):
        """Get avatar URL."""
        url = '/static/app/images/avatar-icon.png'
        try:
            url = self.avatar.url
        except:
            url = '/static/app/images/avatar-icon.png'
        return url

class Product(models.Model):
    """Product model."""

    name = models.CharField(max_length=100, null=True)
    price = models.IntegerField()
    cost = models.IntegerField()
    image = models.ImageField(upload_to='product', null=True, blank=True)
    imageURL = models.URLField(null=True, blank=True)
    launchYear = models.IntegerField(default='N/A', null=True, blank=True)
    author = models.CharField(default='N/A', max_length=100, null=True, blank=True)
    description = models.CharField(default='Người bán chưa cung cấp thông tin mô tả sản phẩm.', max_length=3000, null=True, blank=True)
    slugName = models.SlugField(unique=True, null=True, blank=True)
    
    CATEGORY_CHOICES = [
        ('category0', 'Chưa phân loại'),
        ('category1', 'iPhone cũ'),
        ('category2', 'Tablet'),
        ('category3', 'Samsung'),
        ('category4', 'Oppo - Xiaomi'),
        ('category5', 'Laptop'),
        ('category6', 'iPhone'),
    ]

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default='category0',
    )
    
    def save(self, *args, **kwargs):
        """Override save method to set imageURL and slugName."""
        super().save(*args, **kwargs)
        try:
            self.imageURL = urllib.parse.unquote(self.image.url)
        except:
            self.imageURL = '/static/app/images/icon-camera.png'

        if self.name:
            self.slugName = unidecode.unidecode(self.name)
            self.slugName = self.slugName.lower()
            self.slugName = re.sub(r'\W+', ' ', self.slugName)
            self.slugName = self.slugName.strip()
            self.slugName = self.slugName.replace(" ", "-")
        else:
            self.slugName = ""
        super().save(*args, **kwargs)

    def __str__(self):
        """String representation of the object."""
        return self.name

class Cart(models.Model):
    """Shopping cart model."""

    customer = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)

    def getCartItemsAmount(self):
        """Get total number of items in the cart."""
        cartItems = self.cartitem_set.all()
        total = sum([item.quantity for item in cartItems])
        return total

class CartItem(models.Model):
    """Item in the shopping cart model."""

    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    dateAdded = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        """Get total price for the item."""
        return self.product.price * self.quantity

class Order(models.Model):
    """Order model."""

    customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=250, null=True)
    phoneNumber = models.CharField(max_length=10, null=True)
    dateOrder = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    active = models.BooleanField(default=False)
    isPaid = models.BooleanField(default=False) 

    def getDateOrder(self):
        """Get formatted order date."""
        weekdays = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
        return weekdays[self.dateOrder.astimezone().weekday()] + ', ' + self.dateOrder.astimezone().strftime("%d/%m/%Y, %H:%M")

    def __str__(self):
        """String representation of the object."""
        return str(self.id)

    @property
    def getOrderItemsAmount(self):
        """Get total number of items in the order."""
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    
    def getOrderTotalPrice(self):
        """Get total price of the order."""
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

class OrderItem(models.Model):
    """Item in the order model."""

    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    dateAdded = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        """Get total price for the item."""
        return self.product.price * self.quantity

class Slider(models.Model):
    """Slider model."""

    image = models.ImageField(upload_to='sliders', null=True, blank=True)
    url = models.CharField(default='/', max_length=200 ,null=True, blank=True)
