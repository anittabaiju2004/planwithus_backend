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
    




# cart/models.py

from django.db import models
from adminapp.models import Products  # Your product model
from houseprojectapp.models import tbl_register  # Your user model


class Cart(models.Model):
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.name}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.product.price * self.quantity


# order/models.py
from django.db import models
from .models import tbl_register
from adminapp.models import Products,HouseFeature

class Order(models.Model):
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Completed')  # Pending, Completed, Cancelled
    address = models.TextField()
    payment_status = models.CharField(max_length=20, default='Unpaid')  # Unpaid, Paid

    def __str__(self):
        return f"Order {self.id} by {self.user.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # store price at the time of order

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"

    def get_total_price(self):
        return self.price * self.quantity

# payment/models.py
from django.db import models
from .models import Order
from houseprojectapp.models import tbl_register

class Payment(models.Model):
    PAYMENT_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('UPI', 'UPI Payment'),
        ('CARD', 'Card Payment'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # UPI
    upi_id = models.CharField(max_length=100, blank=True, null=True)

    # Card
    card_number = models.CharField(max_length=20, blank=True, null=True)
    cardholder_name = models.CharField(max_length=100, blank=True, null=True)
    expiry_date = models.CharField(max_length=7, blank=True, null=True)  # MM/YYYY
    cvv = models.CharField(max_length=4, blank=True, null=True)

    payment_status = models.CharField(max_length=20, default="Paid")  # Pending, Paid, Failed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.payment_method}"


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






from django.db import models
from .models import tbl_register, tbl_engineer, UserRequest

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

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically copy fields from linked UserRequest if available
        if self.user_request:
            self.cent = self.user_request.cent
            self.sqft = self.user_request.sqft
            self.expected_amount = self.user_request.expected_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking by {self.user.name} for {self.engineer.name}"
