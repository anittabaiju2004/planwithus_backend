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

class EngineerRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE, related_name="engineer_requests")
    engineer = models.ForeignKey(tbl_engineer, on_delete=models.CASCADE, related_name="user_requests")
    user_request = models.ForeignKey(UserRequest, on_delete=models.CASCADE, related_name="engineer_requests")
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    suggestion = models.FileField(upload_to="suggestions/", null=True, blank=True)  # PDF upload
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_name = getattr(self.user, 'name', 'Unknown user')
        engineer_name = getattr(self.engineer, 'name', 'Unknown engineer')
        return f"Request from {user_name} to {engineer_name}"




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
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)  # Added category
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=100, default='pending')
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking - {self.product.name} by {self.user.name}"


# Checkout for bookings
class Checkout(models.Model):
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE)
    booking = models.ForeignKey(ProductBookings, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


# Cart
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
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=100, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} ({self.category.name}) - {self.user.name}"



# Cart Checkout
class CartCheckout(models.Model):
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE)
    booking = models.ForeignKey(Cart, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Cart Checkout - {self.booking.product.name} by {self.user.name}"

# Payment models
class Upi(models.Model):
    booking = models.OneToOneField(ProductBookings, on_delete=models.CASCADE, related_name="upi")
    status = models.CharField(max_length=20, default="success")
    upi_id = models.CharField(max_length=100)

    def __str__(self):
        return f"UPI Payment for Booking {self.booking.id} - {self.status}"


class Card(models.Model):
    booking = models.OneToOneField(ProductBookings, on_delete=models.CASCADE, related_name="card")
    status = models.CharField(max_length=20, default="success")
    card_holder_name = models.CharField(max_length=100)
    card_number = models.CharField(max_length=16)
    expiry_date = models.CharField(max_length=7)
    cvv = models.CharField(max_length=4)

    def __str__(self):
        return f"Card Payment for Booking {self.booking.id} - {self.status}"


class CartUpi(models.Model):
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE, related_name="upi_payments")
    status = models.CharField(max_length=20, default="success")
    upi_id = models.CharField(max_length=100)

    def __str__(self):
        return f"UPI Payment by User {self.user.id} - {self.status}"


class CartCard(models.Model):
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE, related_name="card_payments")
    status = models.CharField(max_length=20, default="success")
    card_holder_name = models.CharField(max_length=100)
    card_number = models.CharField(max_length=16)
    expiry_date = models.CharField(max_length=7)
    cvv = models.CharField(max_length=4)

    def __str__(self):
        return f"Card Payment by User {self.user.id} - {self.status}"
