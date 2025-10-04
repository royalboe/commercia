from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    """
    Custom user manager for the User model that uses email instead of username.

    Provides helper methods for creating regular users and superusers,
    ensuring that email is always required and normalized.

    Methods:
        create_user(email, password=None, **extra_fields):
            Creates and returns a regular user with the given email and password.
            Raises ValueError if email is not provided.

        create_superuser(email, password=None, **extra_fields):
            Creates and returns a superuser with the given email and password.
            Ensures that `is_staff` and `is_superuser` are always set to True.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a user with the given email and password.

        Args:
            email (str): The user's email address (required).
            password (str, optional): The user's password. Defaults to None.
            **extra_fields: Additional fields to set on the user.

        Returns:
            User: The created user instance.

        Raises:
            ValueError: If email is not provided.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given email and password.

        Ensures that `is_staff` and `is_superuser` are set to True.

        Args:
            email (str): The superuser's email address (required).
            password (str, optional): The superuser's password. Defaults to None.
            **extra_fields: Additional fields to set on the superuser.

        Returns:
            User: The created superuser instance.

        Raises:
            ValueError: If `is_staff` or `is_superuser` are not True.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
