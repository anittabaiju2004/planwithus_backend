from rest_framework import serializers
from .models import tbl_register, tbl_engineer

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_register
        fields = '__all__'


from rest_framework import serializers
from .models import tbl_engineer
class EngineerSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False)
    id_proof = serializers.FileField(required=False)

    class Meta:
        model = tbl_engineer
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if instance.profile_image:
            rep['profile_image'] = instance.profile_image.url  # returns "/media/..."
        if instance.id_proof:
            rep['id_proof'] = instance.id_proof.url

        return rep

class EngineerLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_engineer
        fields = ['email', 'password']

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        try:
            engineer = tbl_engineer.objects.get(email=email, password=password)
        except tbl_engineer.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        return engineer
    
class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_register
        fields = ['email', 'password']

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        try:
            user = tbl_register.objects.get(email=email, password=password)
        except tbl_register.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        return user
    



# serializers.py
from rest_framework import serializers
from adminapp.models import Category, CategoryImage, House, HouseImage
from .models import UserRequest
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

from houseprojectapp.models import tbl_register   # import your user model
from rest_framework import serializers
from houseprojectapp.models import tbl_register
from .models import UserRequest
from adminapp.models import Category

class UserRequestSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source='user',
        queryset=tbl_register.objects.all(),
        required=True
    )
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = UserRequest
        fields = ['id', 'user_id', 'category', 'cent', 'sqft', 'expected_amount', 'created_at']





from rest_framework import serializers
from adminapp.models import Category



# class HouseImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = HouseImage
class HouseImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = HouseImage
        fields = ['image']

    def get_image(self, obj):
        if obj.image:
            return obj.image.url  # This returns "/media/..." path
        return None


class HouseSerializer(serializers.ModelSerializer):
    images = HouseImageSerializer(many=True, read_only=True)

    class Meta:
        model = House
        fields = ['id', 'name', 'description', 'expected_amount', 'cent_range', 'sqft_range', 'images']


# serializers.py
# Profile Serializer
class EngineerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_engineer
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'password',
            'profile_image', 'id_proof', 'status', 'user_type', 'available'
        ]

from rest_framework import serializers
from .models import tbl_engineer

class AvailableStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_engineer
        fields = ['available']



from rest_framework import serializers
from adminapp.models import ProductCategory

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name']



from rest_framework import serializers
from adminapp.models import Products
class productSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'name', 'image', 'price', 'quantity', 'description', 'created_at']
        read_only_fields = ['created_at']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image:
            rep['image'] = instance.image.url  # returns "/media/..."
        return rep
    


    # serializers.py

class CategoryImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = CategoryImage
        fields = ['id', 'category', 'image','description']

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


from rest_framework import serializers
from .models import Work, WorkImage
from adminapp.models import HouseFeature, Category
from .models import tbl_engineer  # adjust import if needed

class WorkImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = WorkImage
        fields = ['id', 'image']

    def get_image(self, obj):
        return f"/media/{obj.image}" if obj.image else None

# houseprojectapp/serializers.py
from rest_framework import serializers
from .models import Work, WorkImage
from adminapp.models import HouseFeature, Category

class WorkSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(max_length=None, allow_empty_file=False, use_url=True),
        write_only=True
    )
    property_image = serializers.ImageField(required=False, allow_null=True)
    # accept list of feature IDs
    additional_features = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Work
        fields = [
            'id', 'engineer', 'project_name', 'category', 'cent', 'squarefeet',
            'expected_amount', 'additional_amount', 'total_amount',
            'additional_features', 'time_duration',
            'property_image', 'images'
        ]

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        features = validated_data.pop('additional_features', [])

        # store features as comma separated string
        validated_data['additional_features'] = ",".join(map(str, features))

        work = Work.objects.create(**validated_data)

        for img in images:
            WorkImage.objects.create(work=work, image=img)

        return work


class WorkReadSerializer(serializers.ModelSerializer):
    engineer = serializers.CharField(source='engineer.name')
    category = serializers.CharField(source='category.name')
    additional_features = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    property_image = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = [
            'id', 'engineer','engineer_id', 'project_name', 'category', 'cent', 'squarefeet',
            'expected_amount', 'additional_amount', 'total_amount',
            'additional_features', 'time_duration',
            'property_image', 'images'
        ]

    def get_additional_features(self, obj):
        ids = obj.get_feature_list()
        return list(HouseFeature.objects.filter(id__in=ids).values_list("name", flat=True))

    def get_images(self, obj):
        return [f"/media/{img.image}" for img in obj.images.all()]

    def get_property_image(self, obj):
        return f"/media/{obj.property_image}" if obj.property_image else None


class HouseFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseFeature
        fields = ['id', 'name']
        




# # serializers.py
# from rest_framework import serializers
# from .models import EngineerRequest, UserRequest, tbl_register, tbl_engineer

# # serializers.py
# class EngineerRequestSerializer(serializers.ModelSerializer):
#     suggestion = serializers.FileField(required=False, allow_null=True)

#     class Meta:
#         model = EngineerRequest
#         fields = [
#             "id", "user", "engineer", "user_request",
#             "start_date", "end_date", "suggestion", "status"
#         ]

#     def to_representation(self, instance):
#         rep = super().to_representation(instance)
#         if instance.suggestion:
#             rep['suggestion'] = instance.suggestion.url  # returns /media/suggestions/...
#         return rep

# class EngineerRequestReadSerializer(serializers.ModelSerializer):
#     # expand user info
#     name = serializers.CharField(source="user.name", read_only=True)
#     phone = serializers.CharField(source="user.phone", read_only=True)
#     address = serializers.CharField(source="user.address", read_only=True)

#     # expand request info
#     cent = serializers.FloatField(source="user_request.cent", read_only=True)
#     sqft = serializers.FloatField(source="user_request.sqft", read_only=True)
#     expected_amount = serializers.DecimalField(source="user_request.expected_amount", max_digits=12, decimal_places=2, read_only=True)

#     suggestion = serializers.SerializerMethodField()

#     class Meta:
#         model = EngineerRequest
#         fields = [
#             "id", "user", "engineer",
#             "name", "phone", "address",
#             "cent", "sqft", "expected_amount",
#             "start_date", "end_date", "suggestion", "status"
#         ]

#     def get_suggestion(self, obj):
#         return obj.suggestion.url if obj.suggestion else None





from rest_framework import serializers
from .models import EngineerBooking
from rest_framework import serializers
from .models import EngineerBooking

class EngineerBookingSerializer(serializers.ModelSerializer):
    cent = serializers.CharField(read_only=True)
    sqft = serializers.CharField(read_only=True)
    expected_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    features = serializers.PrimaryKeyRelatedField(
        many=True, queryset=HouseFeature.objects.all()
    )  # allow posting feature IDs

    class Meta:
        model = EngineerBooking
        fields = '__all__'


class EngineerBookingReadSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    engineer_name = serializers.CharField(source='engineer.name', read_only=True)
    engineer_phone = serializers.CharField(source='engineer.phone', read_only=True)
    features = serializers.StringRelatedField(many=True, read_only=True)  # show feature names

    class Meta:
        model = EngineerBooking
        fields = [
            'id', 'user_name', 'user_phone', 'engineer_name', 'engineer_phone',
            'address', 'start_date', 'end_date', 'suggestion',
            'cent', 'sqft', 'expected_amount', 'features', 'created_at', 'status'
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.suggestion:
            rep['suggestion'] = instance.suggestion.url
        return rep


from rest_framework import serializers
from .models import Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    engineer_name = serializers.CharField(source='engineer.name', read_only=True)

    class Meta:
        model = Feedback
        fields = [
            'id',
            'user',
            'engineer',
            'user_name',
            'engineer_name',
            'rating',
            'comments',
            'created_at'
        ]
        read_only_fields = ['created_at']





from .serializers import *
from .models import *
# cart and booking serializers
# -----------------------------
# Booking & Cart Serializers
# -----------------------------
from rest_framework import serializers
from .models import ProductBookings

class ProductBookingSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    product_id = serializers.IntegerField(write_only=True)

    # ✅ Read-only fields for GET response
    product_name = serializers.CharField(source='product.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = ProductBookings
        fields = [
            'id', 'user_id', 'user_name',
            'product_id', 'product_name',
            'category_name', 'quantity',
            'total_price', 'status', 'booking_date'
        ]
# no need category in booking you can use the below simpler version
# class ProductBookingSerializer(serializers.ModelSerializer):
#     user_id = serializers.IntegerField()
#     product_id = serializers.IntegerField()

#     class Meta:
#         model = ProductBookings
#         fields = ['user_id', 'product_id', 'quantity']
class CartSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    product_id = serializers.IntegerField(write_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id', 'user_id', 'product_id',
            'product_name', 'category_name',
            'quantity', 'total_price', 'status', 'created_at'
        ]

# -----------------------------
# Checkout Serializers
# -----------------------------
class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkout
        fields = ['id', 'user', 'booking', 'created_at']
class CartCheckoutSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    product_name = serializers.CharField(source='booking.product.name', read_only=True)
    category_name = serializers.CharField(source='booking.category.name', read_only=True)
    total_price = serializers.DecimalField(source='booking.total_price', read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = CartCheckout
        fields = [
            'id', 'user', 'user_name', 'user_email',
            'booking', 'product_name', 'category_name',
            'total_price', 'created_at'
        ]


# -----------------------------
# Payment Serializers
# -----------------------------
class UpiPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upi
        fields = '__all__'


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'


class CartUpiSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartUpi
        fields = '__all__'


class CartCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartCard
        fields = '__all__'


# -----------------------------
# Payment Details for Bookings
# -----------------------------
class PaymentDetailsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = ProductBookings
        fields = ['id', 'user', 'user_name', 'user_email', 'user_phone', 'total_price', 'status']


class CartPaymentDetailsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'user_name', 'user_email', 'user_phone', 'total_price', 'status']


# -----------------------------
# Cart History Serializer
# -----------------------------
class CartHistorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'product_name', 'product_image', 'quantity', 'total_price', 'status', 'created_at']