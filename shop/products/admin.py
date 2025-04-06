from django.contrib import admin
from .models import Product, Review, Image

admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Image)