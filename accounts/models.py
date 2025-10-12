from django.db import models
from django.contrib.auth.models import AbstractUser
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