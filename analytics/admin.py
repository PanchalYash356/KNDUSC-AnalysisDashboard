from django.contrib import admin
from .models import Product, UploadedFile

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'product_name', 'zipcode', 'mrp', 'sale_price', 'brand', 'created_at')
    list_filter = ('zipcode', 'brand', 'created_at')
    search_fields = ('product_name', 'product_id', 'brand')
    readonly_fields = ('created_at',)

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')
    readonly_fields = ('uploaded_at',)