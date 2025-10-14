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
class UserRequestSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source='user',  # map "user_id" from request → "user" in model
        queryset=tbl_register.objects.all(),
        required=True
    )
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    cent = serializers.FloatField()
    sqft = serializers.FloatField()
    expected_amount = serializers.DecimalField(max_digits=12, decimal_places=2)




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



# cart/serializers.py

from rest_framework import serializers
from .models import Cart, CartItem
from adminapp.models import Products
from .serializers import productSerializer  # your product serializer

class CartItemSerializer(serializers.ModelSerializer):
    product = productSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'get_total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items', 'total_amount']

    def get_total_amount(self, obj):
        return sum(item.get_total_price() for item in obj.items.all())


# order/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem
from .serializers import productSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = productSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price', 'get_total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'total_amount', 'status', 'payment_status', 'address', 'items']



# payment/serializers.py
from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

    def validate(self, data):
        method = data.get("payment_method")

        if method == "UPI" and not data.get("upi_id"):
            raise serializers.ValidationError({"upi_id": "UPI ID is required for UPI payment."})
        if method == "CARD":
            required_fields = ["card_number", "cardholder_name", "expiry_date", "cvv"]
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({field: f"{field} is required for Card payment."})

        return data

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
        




# serializers.py
from rest_framework import serializers
from .models import EngineerRequest, UserRequest, tbl_register, tbl_engineer

# serializers.py
class EngineerRequestSerializer(serializers.ModelSerializer):
    suggestion = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = EngineerRequest
        fields = [
            "id", "user", "engineer", "user_request",
            "start_date", "end_date", "suggestion", "status"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.suggestion:
            rep['suggestion'] = instance.suggestion.url  # returns /media/suggestions/...
        return rep

class EngineerRequestReadSerializer(serializers.ModelSerializer):
    # expand user info
    name = serializers.CharField(source="user.name", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)
    address = serializers.CharField(source="user.address", read_only=True)

    # expand request info
    cent = serializers.FloatField(source="user_request.cent", read_only=True)
    sqft = serializers.FloatField(source="user_request.sqft", read_only=True)
    expected_amount = serializers.DecimalField(source="user_request.expected_amount", max_digits=12, decimal_places=2, read_only=True)

    suggestion = serializers.SerializerMethodField()

    class Meta:
        model = EngineerRequest
        fields = [
            "id", "user", "engineer",
            "name", "phone", "address",
            "cent", "sqft", "expected_amount",
            "start_date", "end_date", "suggestion", "status"
        ]

    def get_suggestion(self, obj):
        return obj.suggestion.url if obj.suggestion else None
