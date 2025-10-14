from django.db import models

# Create your models here.

class tbl_admin(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    email = models.EmailField()

    def __str__(self):
        return self.username
    


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
        
class House(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    expected_amount = models.CharField(max_length=255, null=True, blank=True)
    cent_range = models.CharField(max_length=20, null=True, blank=True)  # e.g. "4-5", "3.5-7"
    sqft_range = models.CharField(max_length=20, null=True, blank=True)  # e.g. "1000-1500"


class HouseImage(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='house_images/')
    
from django.db import models

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Product_table(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product_images/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Product_tbl(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product_images/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    


class Products(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product_images/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    


class CategoryImage(models.Model):
    category = models.OneToOneField(Category, on_delete=models.CASCADE, related_name='image')
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/')
    name=models.CharField(max_length=100, null=True, blank=True)



# houseprojectapp/models.py
from django.db import models

class HouseFeature(models.Model):
    name = models.CharField(max_length=100, unique=True)
    

    def __str__(self):
        return self.name
