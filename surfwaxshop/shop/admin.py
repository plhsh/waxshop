from django.contrib import admin
from .models import PriceList, CartItems


# admin.site.register(Pricelist)


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ["product_name", "slug", "on_sale", "price"]
    list_editable = ["on_sale", "price"]


@admin.register(CartItems)
class CartItemsAdmin(admin.ModelAdmin):
    list_display = ["cart_owner", "cart_item", "quantity"]
    list_editable = ["quantity"]


