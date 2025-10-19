from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.hashers import make_password

from accounts.models import User

class UserListSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for the User model.
    
    Purpose:
        - Expose non-sensitive user details for display in APIs.
        - Hide password and other sensitive fields.

    Fields:
        user_id (UUIDField, read-only): Unique identifier for the user.
        username (CharField): Optional username.
        email (EmailField): User's email (used for login).
        first_name (CharField): User's first name.
        last_name (CharField): User's last name.
        is_active (BooleanField, read-only): Whether the user account is active.
        is_staff (BooleanField, read-only): Whether the user has staff/admin rights.
        date_joined (DateTimeField, read-only): Timestamp when the user registered.
    """
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined']
        read_only_fields = ['user_id', 'is_active', 'is_staff', 'date_joined']

class UserDetailSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for detailed User information.

    Purpose:
        - Expose all user details for detailed display in APIs.

    Fields:
        Same as UserListSerializer, but with all fields included.
    """
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined', 'role', 'phone_number', 'address', 'date_of_birth']
        read_only_fields = ['user_id', 'is_active', 'is_staff', 'date_joined']

class UserCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Write serializer for creating or updating User.

    Special behavior:
        - Password is write-only and is automatically hashed before saving.

    Fields:
        email (EmailField): Required, unique identifier for login.
        username (CharField): Optional username.
        password (CharField, write-only): User's password (hashed before saving).
        role (CharField): User role (customer/admin).
        phone_number (CharField): Optional contact number.
        address (TextField): Optional address.
        date_of_birth (DateField): Optional date of birth.
    """
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "first_name", "last_name", "role", "phone_number", "address", "date_of_birth"]
        required_fields = ["email", "password"]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)