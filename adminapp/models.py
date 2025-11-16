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
        

from django.db import models

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)

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
    



# houseprojectapp/models.py
from django.db import models

class HouseFeature(models.Model):
    name = models.CharField(max_length=100, unique=True)
    

    def __str__(self):
        return self.name
