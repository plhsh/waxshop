from django import forms
from .models import CartItems


class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItems
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'})
        }
