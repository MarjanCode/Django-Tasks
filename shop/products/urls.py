from django.urls import path
from products.views import ProductListView, ProductDetailView


urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:product_id>/', ProductDetailView.as_view(), name='product-detail'),
]