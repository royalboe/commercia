from rest_framework import viewsets
from .models import User
from .user_serializers import (UserListSerializer, UserDetailSerializer,
                               UserCreateUpdateSerializer)

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.

    Provides:
        - list: Retrieve all users.
        - retrieve: Get a specific user by ID.
        - create: Add a new user.
        - update: Modify an existing user.
        - destroy: Remove a user.
    Uses:
        - UserSerializer for read operations.
        - UserCreateUpdateSerializer for write operations.
    """

    queryset = User.objects.all()
    serializer_class = UserListSerializer

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        return super().get_serializer_class()
