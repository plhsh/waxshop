from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


class PriceList(models.Model):
    product_name = models.CharField(max_length=100, verbose_name="Product")
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name="Slug")
    photo = models.ImageField(upload_to="staticfiles", default=None, blank=True, null=True, verbose_name="Photo")
    description = models.TextField(blank=True, verbose_name="Product description")
    on_sale = models.BooleanField(verbose_name="On sale now")
    price = models.PositiveIntegerField(verbose_name="Price")

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def get_absolute_url(self):
        return reverse('show_product', kwargs={'slug': self.slug})


class CartItems(models.Model):
    cart_owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                                   related_name='owned_carts', verbose_name="Cart owner")
    cart_item = models.ForeignKey('PriceList', on_delete=models.CASCADE,
                                  related_name='in_carts', verbose_name="Cart item")
    quantity = models.PositiveIntegerField(verbose_name="Quantity", default=1)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"{self.cart_owner} has {self.quantity} pieces of {self.cart_item} in the cart"
