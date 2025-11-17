from django.db import models

# Create your models here.

class tbl_register(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    user_type = models.CharField(default='user', max_length=50)


    def __str__(self):
        return self.name
    


class tbl_engineer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    profile_image = models.ImageField(upload_to='engineer_profiles/')
    id_proof = models.FileField(upload_to='engineer_id_proofs/')
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    user_type = models.CharField(default='engineer', max_length=50)
    available = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    


from django.db import models
from adminapp.models import Category  # or your custom user model 

class UserRequest(models.Model):
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    cent = models.FloatField()
    sqft = models.FloatField()
    expected_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_name = getattr(self.user, 'name', 'Unknown user')
        category_name = getattr(self.category, 'name', 'Unknown category')
        return f"{user_name} request - {category_name}"
    
# houseprojectapp/models.py
from django.db import models
from adminapp.models import Category, HouseFeature
from .models import tbl_engineer

class Work(models.Model):
    engineer = models.ForeignKey(tbl_engineer, on_delete=models.CASCADE, related_name='works')
    project_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='works')
    cent = models.DecimalField(max_digits=10, decimal_places=2)
    squarefeet = models.DecimalField(max_digits=10, decimal_places=2)
    expected_amount = models.DecimalField(max_digits=12, decimal_places=2)
    additional_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    # store as comma separated list (e.g., "1,2,3")
    additional_features = models.CharField(max_length=255, blank=True, null=True)

    time_duration = models.CharField(max_length=100)  
    property_image = models.ImageField(upload_to='property_images/', null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project_name} - {self.engineer.name}"

    def get_feature_list(self):
        """Return additional features as list of integers"""
        if self.additional_features:
            return [int(fid) for fid in self.additional_features.split(",") if fid.strip().isdigit()]
        return []


class WorkImage(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='work_proofs/')

    def __str__(self):
        return f"Image for {self.work.project_name}"

# models.py
from django.db import models
from .models import tbl_register, tbl_engineer, UserRequest

from adminapp.models import HouseFeature  # import your HouseFeature model

class EngineerBooking(models.Model):
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE, related_name="engineer_bookings")
    engineer = models.ForeignKey(tbl_engineer, on_delete=models.CASCADE, related_name="bookings")
    user_request = models.ForeignKey(UserRequest, on_delete=models.CASCADE, related_name="bookings", null=True, blank=True)

    address = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    suggestion = models.FileField(upload_to="engineer_suggestions/", null=True, blank=True)

    cent = models.CharField(max_length=50, null=True, blank=True)
    sqft = models.CharField(max_length=50, null=True, blank=True)
    expected_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=50, default='pending')
    
    # Add features field
    features = models.ManyToManyField(HouseFeature, blank=True, related_name="bookings")
    reject_reason = models.TextField(null=True, blank=True)


    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.user_request:
            self.cent = self.user_request.cent
            self.sqft = self.user_request.sqft
            self.expected_amount = self.user_request.expected_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking by {self.user.name} for {self.engineer.name}"



class Feedback(models.Model):
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE)
    engineer = models.ForeignKey(tbl_engineer, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.name} for {self.engineer.name}"
    







#Cart and Orders models can be added 
from adminapp.models import ProductCategory, Products
from houseprojectapp.models import tbl_register
# Product Bookings
from django.db import models
from houseprojectapp.models import tbl_register
from adminapp.models import Products, ProductCategory


class ProductBookings(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("assigned", "Assigned"),
        ("completed", "Completed"),
        ("user_meet", "User Met"),
        ("make_payment", "Payment Made"),
        ("user_leave", "User Left from Shop"),
    ]

    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=100, default='completed')
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking - {self.product.name} by {self.user.name}"


# ✅ Unified Payment Model (supports UPI, Card, COD)
class BookingPayment(models.Model):
    PAYMENT_CHOICES = [
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('cash', 'Cash on Delivery'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    payment_choice=models.CharField(max_length=20,default='booking_payment')

    booking = models.OneToOneField(ProductBookings, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='completed')
    # UPI fields
    upi_id = models.CharField(max_length=100, blank=True, null=True)

    # Card fields
    card_holder_name = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=16, blank=True, null=True)
    expiry_date = models.CharField(max_length=7, blank=True, null=True)
    cvv = models.CharField(max_length=4, blank=True, null=True)

    # Amount (provided by Flutter)
    total_amount = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment_type.upper()} Payment for Booking {self.booking.id} - {self.status}"

class Cart(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("assigned", "Assigned"),
        ("completed", "Completed"),
        ("user_meet", "User Met"),
        ("full paid", "Full Paid"),
    ]

    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.FloatField(null=True, blank=True)  # Changed to FloatField
    status = models.CharField(max_length=100, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} ({self.category.name}) - {self.user.name}"

from django.db import models
from houseprojectapp.models import tbl_register


class CartPayment(models.Model):
    PAYMENT_CHOICES = [
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('cash', 'Cash on Delivery'),  # ✅ Added COD option
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    payment_choice=models.CharField(max_length=20,default='cart_payment')
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE)
    cart_ids = models.JSONField(default=list)  # ✅ store multiple cart IDs as JSON [1, 2, 3]
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='completed')

    # UPI fields
    upi_id = models.CharField(max_length=100, blank=True, null=True)

    # Card fields
    card_holder_name = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=16, blank=True, null=True)
    expiry_date = models.CharField(max_length=7, blank=True, null=True)
    cvv = models.CharField(max_length=4, blank=True, null=True)

    total_amount = models.FloatField(default=0)  # Flutter sends this, not calculated server-side
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment ({self.payment_type}) by {self.user.name} - {self.status}"
