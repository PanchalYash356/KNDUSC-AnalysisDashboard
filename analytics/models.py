# analytics/models.py
from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"

class Product(models.Model):
    zipcode = models.CharField(max_length=20, db_index=True)
    product_id = models.CharField(max_length=50, db_index=True)
    product_name = models.CharField(max_length=255, blank=True, null=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['zipcode', 'product_name']),
            models.Index(fields=['brand']),
        ]

    def __str__(self):
        return f"{self.product_name} ({self.zipcode})"

    @property
    def discount_percentage(self):
        if self.mrp and self.mrp > 0 and self.sale_price:
            return round(((float(self.mrp) - float(self.sale_price)) / float(self.mrp)) * 100, 2)
        return 0

    @property
    def discount_amount(self):
        if self.mrp and self.sale_price:
            return float(self.mrp) - float(self.sale_price)
        return 0