# from django.test import TestCase
# from django.contrib.auth import get_user_model

# # Create your tests here.

# class UserModelTest(TestCase):
#     """Test case for the custom user model."""
#     def test_create_user(self):
#         """Test creating a new user with an email is successful."""

#         customer_email = 'test@example.com'
#         customer_username = 'testuser'

#         User = get_user_model()
#         user_customer = User.objects.create_user(
#             username=customer_username,
#             email=customer_email,
#             password='customerpass123',
#             role='customer'
#             )
#         self.assertEqual(user_customer.email, customer_email)
#         self.assertEqual(user_customer.username, customer_username)
#         self.assertTrue(user_customer.is_active)
#         self.assertFalse(user_customer.is_staff)
#         self.assertFalse(user_customer.is_superuser)
#         self.assertEqual(user_customer.role, 'customer')
#         self.assertTrue(user_customer.check_password("customerpass123"))


#         try:
#             # username is None for the AbstractUser option
#             # username does not exist for the AbstractBaseUser option
#             self.assertIsNotNone(user_customer.username)
#         except AttributeError:
#             pass

#         with self.assertRaises(TypeError):
#             User.objects.create_user()
#         with self.assertRaises(TypeError):
#             User.objects.create_user(email="")
#         with self.assertRaises(ValueError):
#             User.objects.create_user(email="", password="foo")
#         with self.assertRaises(Exception):
#             User.objects.create_user(email=customer_email, password="anotherpasss", username="anotheruser")

#     def test_create_superuser(self):
#         """Test creating a new superuser with email is successful."""
#         admin_email = 'admin@example.com'
#         admin_username = 'adminuser'
#         User = get_user_model()
#         admin_user = User.objects.create_superuser(email=admin_email, username=admin_username, password="adminpass123")
#         self.assertEqual(admin_user.email, admin_email)
#         self.assertEqual(admin_user.username, admin_username)
#         self.assertTrue(admin_user.is_active)
#         self.assertTrue(admin_user.is_staff)
#         self.assertTrue(admin_user.is_superuser)
#         self.assertEqual(admin_user.role, 'admin')
#         self.assertTrue(admin_user.check_password("adminpass123"))
#         try:
#             # username is None for the AbstractUser option
#             # username does not exist for the AbstractBaseUser option
#             self.assertIsNotNone(admin_user.username)
#         except AttributeError:
#             pass
#         with self.assertRaises(ValueError):
#             User.objects.create_superuser(
#                 email=admin_email, password="foo", is_superuser=False)
        

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_create_user():
    """Test creating a new user with an email is successful."""
    customer_email = 'test@example.com'
    customer_username = 'testuser'

    user_customer = User.objects.create_user(
        username=customer_username,
        email=customer_email,
        password='customerpass123',
        role='customer'
    )

    assert user_customer.email == customer_email
    assert user_customer.username == customer_username
    assert user_customer.is_active is True
    assert user_customer.is_staff is False
    assert user_customer.is_superuser is False
    assert user_customer.check_password("customerpass123")

    # Required field checks
    with pytest.raises(TypeError):
        User.objects.create_user()
    with pytest.raises(TypeError):
        User.objects.create_user(email="")
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="foo")


@pytest.mark.django_db
def test_create_superuser():
    """Test creating a new superuser with an email is successful."""
    admin_email = 'admin@example.com'
    admin_username = 'adminuser'

    admin_user = User.objects.create_superuser(
        email=admin_email,
        username=admin_username,
        password="adminpass123"
    )

    assert admin_user.email == admin_email
    assert admin_user.username == admin_username
    assert admin_user.is_active is True
    assert admin_user.is_staff is True
    assert admin_user.is_superuser is True
    assert admin_user.check_password("adminpass123")

    # Invalid superuser case
    with pytest.raises(ValueError):
        User.objects.create_superuser(
            email=admin_email, password="foo", is_superuser=False
        )

