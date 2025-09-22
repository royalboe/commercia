from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import uuid

from .managers import CustomUserManager

# Create your models here.


class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.

    Key changes:
    - Uses `email` as the unique identifier for authentication instead of `username`.
    - Keeps `username` optional, but still required for superuser creation.
    - Adds extra fields such as `role`, `phone_number`, and `address`.

    Fields:
        role (CharField): User role, either "customer" or "admin". Defaults to "customer".
        username (CharField): Optional username, unique if provided.
        email (EmailField): Required unique email, used for login.
        phone_number (CharField): Optional phone number for contact.
        address (TextField): Optional address field.
        date_of_birth (DateField): Optional date of birth field.
        updated_at (DateTimeField): Timestamp of the last update.        

    Authentication:
        USERNAME_FIELD is set to 'email'.
        REQUIRED_FIELDS includes 'username' for superuser creation.

    Meta:
        verbose_name: "User"
        verbose_name_plural: "Users"

    String Representations:
        __str__: Returns username if available, otherwise email.
        __repr__: Returns username or email along with join date.
    """

    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username or self.email

    def __repr__(self):
        return f'{self.username or self.email} joined on {self.date_joined}'

class Category(models.Model):
    """
    Category model representing product categories in the e-commerce platform.

    Fields:
        category_id (UUIDField): Primary key for the category.
        name (CharField): Name of the category. Must be unique.
        description (TextField): Detailed description of the category.
        created_at (DateTimeField): Timestamp when the category was created.
        updated_at (DateTimeField): Timestamp when the category was last updated.
        slug (SlugField): URL-friendly identifier, auto-generated from name.
        image_field (ImageField): Optional image for the category.
    Meta:
        verbose_name: "Category"
        verbose_name_plural: "Categories"
    String Representations:
        __str__: Returns the category name.
        __repr__: Returns the category name along with its description.
    """

    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    image_field = models.ImageField(upload_to='category_images/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.name} - {self.description}'

class Product(models.Model):
    """
    Product model representing items available in the e-commerce platform.

    Fields:
        product_id (UUIDField): Primary key for the product.
        name (CharField): Name of the product.
        description (TextField): Detailed description of the product.
        price (DecimalField): Price of the product with two decimal places.
        stock (IntegerField): Available stock quantity.
        created_at (DateTimeField): Timestamp when the product was created.
        updated_at (DateTimeField): Timestamp when the product was last updated.
        categories (ManyToManyField): Categories the product belongs to.
        slug (SlugField): URL-friendly identifier, auto-generated from name.
        image_field (ImageField): Optional image for the product.

    Meta:
        verbose_name: "Product"
        verbose_name_plural: "Products"

    String Representations:
        __str__: Returns the product name.
        __repr__: Returns the product name along with its price.
    """

    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    slug = models.SlugField(unique=True, blank=True, null=True)
    image_field = models.ImageField(upload_to='product_images/', blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, related_name='products', blank=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


    @property
    def is_in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.name} priced at {self.price}'
    

class Order(models.Model):
    """
    Order model representing customer orders in the e-commerce platform.

    Fields:
        order_id (UUIDField): Primary key for the order.
        user (ForeignKey): Reference to the User who placed the order.
        products (ManyToManyField): Products included in the order.
        total_amount (DecimalField): Total amount for the order.
        status (CharField): Current status of the order.
        created_at (DateTimeField): Timestamp when the order was created.
        updated_at (DateTimeField): Timestamp when the order was last updated.

    Meta:
        verbose_name: "Order"
        verbose_name_plural: "Orders"

    String Representations:
        __str__: Returns the order ID and user email.
        __repr__: Returns the order ID along with its status and total amount.
    """

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    )

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, related_name='orders', through='OrderItem')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def calculate_total(self):
        total = sum(
            item.price_at_order * item.quantity for item in self.items.all()
        )
        self.total_price = total
        self.save()
        return total

    def __str__(self):
        return f'Order {self.order_id} by {self.user.email}'

    def __repr__(self):
        return f'Order {self.order_id}: {self.status} - Total: {self.total_amount}'
    

class OrderItem(models.Model):
    """
    Intermediate model representing products in an order with their quantities.

    Fields:
        order (ForeignKey): Reference to the Order.
        product (ForeignKey): Reference to the Product.
        quantity (IntegerField): Quantity of the product in the order.

    Meta:
        verbose_name: "Order Item"
        verbose_name_plural: "Order Items"

    String Representations:
        __str__: Returns the product name and quantity in the order.
        __repr__: Returns the product name along with its quantity and order ID.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)


    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        unique_together = ('order', 'product')

    @property
    def total_price(self):
        if self.price_at_order and self.quantity:
            return self.price_at_order * self.quantity
        else:
            return 0

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    def __repr__(self):
        return f'OrderItem: {self.quantity} x {self.product.name} in Order {self.order.order_id}'
    

class Cart(models.Model):
    """
    Cart model representing a user's shopping cart in the e-commerce platform.

    Fields:
        cart_id (UUIDField): Primary key for the cart.
        user (OneToOneField): Reference to the User who owns the cart.
        products (ManyToManyField): Products added to the cart.
        created_at (DateTimeField): Timestamp when the cart was created.
        updated_at (DateTimeField): Timestamp when the cart was last updated.

    Meta:
        verbose_name: "Cart"
        verbose_name_plural: "Carts"

    String Representations:
        __str__: Returns the cart ID and user email.
        __repr__: Returns the cart ID along with its creation date.
    """

    cart_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='cart', 
        null=True, 
        blank=True, 
        help_text="Authenticated user who owns the cart. Null for guest carts."
        )
    cart_code = models.CharField(
        max_length=11, 
        unique=True, 
        null=True, 
        blank=True, 
        help_text="Unique code for guest carts"
        )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"


    def __str__(self):
        return f'Cart {self.cart_id} for {self.user.email}'

    def __repr__(self):
        return f'Cart {self.cart_id} created on {self.created_at}'
    

class CartItem(models.Model):
    """
    Intermediate model representing products in a cart with their quantities.

    Fields:
        cart (ForeignKey): Reference to the Cart.
        product (ForeignKey): Reference to the Product.
        quantity (IntegerField): Quantity of the product in the cart.
        is_active (BooleanField): Indicates if the item is active in the cart.

    Meta:
        verbose_name: "Cart Item"
        verbose_name_plural: "Cart Items"

    String Representations:
        __str__: Returns the product name and quantity in the cart.
        __repr__: Returns the product name along with its quantity and cart ID.
    """

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ('cart', 'product')

    @property
    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    def __repr__(self):
        return f'CartItem: {self.quantity} x {self.product.name} in Cart {self.cart.cart_id}'