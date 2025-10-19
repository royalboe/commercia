from django_filters import rest_framework as filter
from rest_framework import filters
from .models import Product, Category

class ProductFilter(filter.FilterSet):
    """
    A Django FilterSet for filtering Product instances based on category, price range, and name.
    Fields:
      min_price (NumberFilter): Filters products with price greater than or equal to this value.
      max_price (NumberFilter): Filters products with price less than or equal to this value.
    Meta:
      model (Product): The Product model to filter.
      fields (dict): Specifies the fields and their supported lookup expressions:
        - category: exact, contains
        - min_price: exact
        - max_price: exact
        - name: contains, exact
        - price: exact, gte, lte, gt, lt, range
    """
    min_price = filter.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filter.NumberFilter(field_name="price", lookup_expr='lte')

    class Meta:
        model = Product
        fields = {
            'categories': ['exact', 'contains'],
            'name': ['icontains', 'iexact'],
            'price': ['exact', 'gte', 'lte', 'gt', 'lt', 'range']
        }


class CategoryFilter(filter.FilterSet):
    """
    A Django FilterSet for filtering Category instances based on name.
    Fields:
      name (CharFilter): Filters categories by name.
    Meta:
      model (Category): The Category model to filter.
      fields (dict): Specifies the fields and their supported lookup expressions:
        - name: contains, exact
    """
    class Meta:
        model = Category
        fields = {
            'name': ['contains', 'exact']
        }


class InStockBackend(filters.BaseFilterBackend):
    """
    A Django FilterBackend for filtering products based on stock availability.
    """
    def filter_queryset(self, request, queryset, view):
        """
        Filters the queryset to include only products with stock greater than 0.
        Args:
          request (Request): The request object.
          queryset (QuerySet): The queryset to filter.
          view (View): The view instance.
        Returns:
          QuerySet: The filtered queryset.
        """
        return queryset.filter(stock__gt=0)