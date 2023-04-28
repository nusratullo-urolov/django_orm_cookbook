from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.models import Product


# Register your models here.

@admin.register(Product)
class AppsProduct(ModelAdmin):
    pass