from django.urls import path
from . import views


urlpatterns = [
    path('', views.ShopHome.as_view(), name='home'),  # http://127.0.0.1:8000
    path("product/<slug:slug>/", views.ShowProduct.as_view(), name="show_product"),
    path("about/", views.about, name="about")
]