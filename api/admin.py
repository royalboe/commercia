from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Category, Product, Order, OrderItem

# class OrderItemInline(admin.TabularInline):
#     """Inline admin for adding/editing OrderItems within an Order."""
#     model = OrderItem
#     extra = 1
#     # autocomplete_fields = ["product"]  # nice dropdown search for products
#     readonly_fields = ["price_at_order", 
#                       #  "display_total_price"
#                        ]

#     # def display_total_price(self, obj):
#     #     """Calculate and display total price for the order item."""
#     #     return obj.total_price
#     # display_total_price.short_description = "Total Price"


# class OrderAdmin(admin.ModelAdmin):
#     """Admin customization for Orders."""
#     # list_display = ("order_id", "user", "status", "total_amount", "created_at")
#     # list_filter = ("status", "created_at")
#     # search_fields = ("order_id", "user__email")
#     # readonly_fields = ("total_amount", "created_at", "updated_at")
#     inlines = [OrderItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = ["product"]
    readonly_fields = ["price_at_order", "display_total_price"]

    def display_total_price(self, obj):
        return obj.total_price
    display_total_price.short_description = "Total Price"


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

    def save_formset(self, request, form, formset, change):
        """
        Hook into saving of inlines. Ensure price_at_order is set before insert.
        """
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, OrderItem) and obj.product and obj.price_at_order is None:
                obj.price_at_order = obj.product.price
            obj.save()
        formset.save_m2m()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.calculate_total()
        form.instance.save()


class ProductAdmin(admin.ModelAdmin):
    """Admin customization for Products."""
    list_display = ("name", "price", "stock", "product_id")
    list_filter = ("categories",)
    search_fields = ("name", "description")
    autocomplete_fields = ["categories"]


class CategoryAdmin(admin.ModelAdmin):
    """Admin customization for Categories."""
    list_display = ("name", "description")
    search_fields = ("name", "description")


# Register models

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
