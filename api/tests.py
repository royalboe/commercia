from django.test import TestCase
from django.contrib.auth import get_user_model

# Create your tests here.

class UserModelTest(TestCase):
    """Test case for the custom user model."""
    def test_create_user(self):
        """Test creating a new user with an email is successful."""

        customer_email = 'test@example.com'
        customer_username = 'testuser'

        User = get_user_model()
        user_customer = User.objects.create_user(
            username=customer_username,
            email=customer_email,
            password='customerpass123',
            role='customer'
            )
        self.assertEqual(user_customer.email, customer_email)
        self.assertEqual(user_customer.username, customer_username)
        self.assertTrue(user_customer.is_active)
        self.assertFalse(user_customer.is_staff)
        self.assertFalse(user_customer.is_superuser)

        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNotNone(user_customer.username)
        except AttributeError:
            pass

        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email="")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="foo")

    def test_create_superuser(self):
        admin_email = 'admin@example.com'
        admin_username = 'adminuser'
        User = get_user_model()
        admin_user = User.objects.create_superuser(email=admin_email, username=admin_username, password="adminpass123")
        self.assertEqual(admin_user.email, admin_email)
        self.assertEqual(admin_user.username, admin_username)
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNotNone(admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email=admin_email, password="foo", is_superuser=False)
        
