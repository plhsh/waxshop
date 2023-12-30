from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DetailView, ListView

from django.views.generic.edit import FormView
from .models import CartItems, PriceList
from django.contrib.auth import get_user_model
from .forms import CartItemForm


class ShowProduct(DetailView):
    model = PriceList
    extra_context = {"title": "Surf Wax"}


class ShopHome(ListView):
    model = PriceList
    # template_name = "pricelist_list.html" # no need to redefine default template_name used by Django
    extra_context = {"title": "Surf Wax"}

    def get(self, request, *args, **kwargs):
        cart = request.session.get("cart", {})
        print(cart, "GET")
        request.session['cart'] = cart
        request.session.save()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product')
        quantity = request.POST.get('quantity')
        cart = request.session.get("cart", {})
        print(cart, "POST")
        if int(quantity):
            cart[product_id] = quantity
        else:
            cart.pop(product_id, None)
        request.session['cart'] = cart
        # request.session.save()
        print(f"Quantity of the product with id {product_id} updated to {quantity} pieces in the current user's cart")
        return HttpResponseRedirect(self.request.path_info)


def about(request):
    return render(request, "shop/about.html")


@login_required
def cart(request):
    current_user = request.user
    cart = request.session.get("cart", {})
    print(cart)
    if cart:
        total_items = 0
        total_amount = 0
        try:
            order_items = {}
            for p in cart:
                product = PriceList.objects.get(pk=int(p))
                quantity = int(cart[p])
                order_items.setdefault(product.product_name, quantity)
                total_items += quantity
                total_amount += product.price * quantity
                c = CartItems.objects.create(cart_owner=current_user, cart_item=product, quantity=quantity)
                print(c)
                print(total_items, total_amount)
            context = {'order_items': order_items, 'total_items': total_items, 'total_amount': total_amount}
        except:
            print("error")
    else:
        context = {}

    return render(request, "shop/cart.html", context=context)


@login_required
def confirm(request):
    return redirect('home')
