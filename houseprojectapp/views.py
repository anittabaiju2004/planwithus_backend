from django.shortcuts import render

from rest_framework import viewsets

from houseprojectapp.utils.material_budget import get_material_budget
from .models import UserRequest, tbl_register
from .models import tbl_engineer
from .serializers import CategoryImageSerializer, EngineerSerializer, UserRequestSerializer,UserLoginSerializer
from .serializers import RegisterSerializer
from rest_framework.response import Response
from rest_framework import status

class RegisterViewSet(viewsets.ModelViewSet):
    queryset = tbl_register.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'User registered successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EngineerViewSet(viewsets.ModelViewSet):
    queryset = tbl_engineer.objects.all()
    serializer_class = EngineerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Engineer registered successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework.views import APIView

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        user_type = request.data.get('user_type')  # 'engineer' or 'user'

        if user_type == 'engineer':
            serializer = EngineerLoginSerializer(data=request.data)
            if serializer.is_valid():
                engineer = serializer.validated_data
                if engineer.status != 'approved':
                    return Response({'error': 'Your account is not approved yet.'}, status=status.HTTP_403_FORBIDDEN)

                return Response({
                    'message': 'Engineer login successful',
                    'engineer_id': engineer.id,
                    'name': engineer.name,
                    'email': engineer.email,
                    'status': engineer.status,
                    'available': engineer.available
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif user_type == 'user':
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data

                # Save user ID in session
                request.session['user_id'] = user.id

                return Response({
                    'message': 'User login successful',
                    'role': user.user_type,
                    'user_id': user.id,
                    'name': user.name,
                    'password': user.password,
                    'email': user.email,
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {'error': 'Invalid user_type. Must be "user" or "engineer".'},
                status=status.HTTP_400_BAD_REQUEST
            )





class GetImagesByRequestAPIView(APIView):
    def get(self, request, request_id):
        try:
            user_request = UserRequest.objects.get(id=request_id)
        except UserRequest.DoesNotExist:
            return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)

        matched_images = CategoryImage.objects.filter(category=user_request.category)

        serializer = CategoryImageSerializer(matched_images, many=True, context={'request': request})

        return Response({
            "request_id": request_id,
            "category_id": user_request.category.id,      # ✅ Return ID
            "category_name": user_request.category.name,  # ✅ Or return name
            "images": serializer.data
        }, status=status.HTTP_200_OK)




from houseprojectapp.utils.predict_plan import predict_house_type
from houseprojectapp.utils.predict_plan import predict_house_type
from rest_framework.response import Response
from rest_framework import status
from adminapp.models import House, Category
from houseprojectapp.serializers import HouseSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import joblib
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils.material_budget import get_material_budget

# Go one level up → houseprojectapp
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, 'ml_assets', 'plan_model2.pkl')
ENCODER_PATH = os.path.join(BASE_DIR, 'ml_assets', 'plan_encoder2.pkl')

plan_model = joblib.load(MODEL_PATH)
plan_encoder = joblib.load(ENCODER_PATH)
class HousePredictionView(APIView):
    def post(self, request):
        try:
            # Get values from request
            cent = request.data.get('cent')
            budget = request.data.get('budget')
            category_id = request.data.get('category_id')

            # Validate required fields
            if cent is None or budget is None or category_id is None:
                return Response(
                    {'error': 'cent, budget, and category_id are required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cent = float(cent)
            budget = float(budget)
            category_id = int(category_id)

            # Model prediction
            prediction = plan_model.predict([[cent, budget, category_id]])
            plan_type = plan_encoder.inverse_transform(prediction)[0]

            # Material & budget calculation
            material_data, total = get_material_budget(plan_type, cent)

            # Scale if total exceeds budget
            scaled = False
            if total > budget:
                scale_factor = budget / total
                scaled = True
                scaled_materials = {}
                for section, items in material_data.items():
                    scaled_materials[section] = []
                    for m in items:
                        qty = m["quantity"] * scale_factor
                        total_item = round(qty * m["rate"], 2)
                        scaled_materials[section].append({
                            "item": m["item"],
                            "quantity": round(qty, 2),
                            "rate": m["rate"],
                            "total": total_item
                        })
                material_data = scaled_materials
                total = budget

            return Response({
                'predicted_plan': plan_type,
                'total_estimated_budget': total,
                'materials': material_data,
                'category_id': category_id,
                'scaled_to_budget': scaled
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import tbl_engineer
from .serializers import EngineerLoginSerializer,EngineerProfileSerializer
from rest_framework.serializers import ModelSerializer


@api_view(['GET'])
def engineer_profile(request, engineer_id):
    try:
        engineer = tbl_engineer.objects.get(id=engineer_id)
    except tbl_engineer.DoesNotExist:
        return Response({"error": "Engineer not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = EngineerProfileSerializer(engineer)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT', 'PATCH'])
def update_engineer_profile(request, engineer_id):
    try:
        engineer = tbl_engineer.objects.get(id=engineer_id)
    except tbl_engineer.DoesNotExist:
        return Response({"error": "Engineer not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = EngineerProfileSerializer(engineer, data=request.data, partial=True)  # partial=True allows partial updates
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import tbl_engineer
from .serializers import AvailableStatusSerializer

@api_view(['PATCH'])
def update_availability(request, engineer_id):
    try:
        engineer = tbl_engineer.objects.get(id=engineer_id)
    except tbl_engineer.DoesNotExist:
        return Response({"error": "Engineer not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = AvailableStatusSerializer(engineer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.generics import ListAPIView
from .models import Category
from .serializers import CategorySerializer

class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

from rest_framework.generics import ListAPIView
from adminapp.models import CategoryImage
from .serializers import CategoryImageSerializer

class HouseListView(ListAPIView):
    queryset = CategoryImage.objects.all()
    serializer_class = CategoryImageSerializer



from rest_framework.generics import ListAPIView
from adminapp.models import ProductCategory,Products
from .serializers import ProductCategorySerializer, productSerializer

class ProductCategoryListView(ListAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

class ProductsListView(ListAPIView):
    queryset = Products.objects.all()
    serializer_class = productSerializer




from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from adminapp.models import Products
from .serializers import productSerializer

@api_view(['GET'])
def get_products_by_category(request, category_id):
    products = Products.objects.filter(category_id=category_id)
    serializer = productSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from .utils.predict_plan import predict_house_type
from .utils.material_budget import get_material_budget
from .models import UserRequest  # import your model
class DownloadPredictionPDF(APIView):
    def get(self, request, request_id):
        try:
            # Fetch the saved user request
            user_request = UserRequest.objects.get(id=request_id)

            sqft = float(user_request.sqft)
            cent = float(user_request.cent)
            budget = float(user_request.expected_amount)
            category_name = user_request.category.name
            user_name = user_request.user.name if user_request.user else "Guest"

            # Predict plan type using model
            plan_type = predict_house_type([[cent, budget, user_request.category.id]])


            # Get materials using updated function
            material_data, total = get_material_budget(plan_type, cent)

            # Create in-memory PDF
            buffer = BytesIO()
            p = canvas.Canvas(buffer)

            # Header
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, 800, " House Plan Prediction Report")
            p.setFont("Helvetica", 12)
            p.drawString(50, 780, f"Requested By: {user_name}")
            p.drawString(50, 760, f"Category: {category_name}")
            p.drawString(50, 740, f"Plan Type: {plan_type}")
            p.drawString(50, 720, f"Total Estimated Budget: ₹{total:,.2f}")
            p.drawString(50, 700, f"Sqft: {sqft} | Cent: {cent} | Budget: ₹{budget:,.2f}")

            # Materials section
            y = 680
            for section, materials in material_data.items():
                if not materials:
                    continue
                y -= 20
                p.setFont("Helvetica-Bold", 12)
                p.drawString(50, y, f"🔹 {section}")
                p.setFont("Helvetica", 10)
                for m in materials:
                    y -= 15
                    line = f"• {m['item']} - Qty: {m['quantity']}, Rate: ₹{m['rate']}, Total: ₹{m['total']}"
                    p.drawString(60, y, line)
                    if y < 100:  # new page if needed
                        p.showPage()
                        y = 800

            p.save()
            buffer.seek(0)

            return HttpResponse(
                buffer,
                content_type='application/pdf',
                headers={'Content-Disposition': 'attachment; filename="house_prediction_report.pdf"'}
            )

        except UserRequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# cart/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from adminapp.models import Products
from houseprojectapp.models import tbl_register
from .serializers import CartSerializer

class AddToCartAPIView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        user = tbl_register.objects.get(id=user_id)
        product = Products.objects.get(id=product_id)

        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)
        cart_item.save()

        return Response({"message": "Product added to cart."}, status=status.HTTP_201_CREATED)

class ViewCartAPIView(APIView):
    def get(self, request, user_id):
        cart = Cart.objects.filter(user_id=user_id).first()
        if not cart:
            return Response({"message": "Cart is empty."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)




# userapp/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem,tbl_register
from adminapp.models import Products

@api_view(['POST'])
def update_cart_quantity(request):
    user_id = request.data.get('user_id')
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity')

    if not user_id or not product_id or quantity is None:
        return Response({'error': 'user_id, product_id, and quantity are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = tbl_register.objects.get(id=user_id)
        product = Products.objects.get(id=product_id)
    except tbl_register.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Products.DoesNotExist:
        return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

    cart, _ = Cart.objects.get_or_create(user=user)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        if int(quantity) > 0:
            cart_item.quantity = quantity
            cart_item.save()
            return Response({'message': 'Cart updated successfully.'})
        else:
            cart_item.delete()
            return Response({'message': 'Item removed from cart as quantity is 0.'})
    except CartItem.DoesNotExist:
        if int(quantity) > 0:
            CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            return Response({'message': 'Item added to cart.'})
        else:
            return Response({'error': 'Quantity must be greater than 0 to add item.'}, status=status.HTTP_400_BAD_REQUEST)

from .models import Cart, Order, OrderItem
@api_view(['POST'])
def place_order(request):
    user_id = request.data.get('user_id')  # <-- from request body
    if not user_id:
        return Response({'error': 'User ID is required'}, status=400)

    try:
        user = tbl_register.objects.get(id=user_id)
    except tbl_register.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    cart = Cart.objects.filter(user=user).first()
    if not cart or not cart.items.exists():
        return Response({'error': 'Cart is empty'}, status=400)

    total_amount = sum(item.get_total_price() for item in cart.items.all())

    order = Order.objects.create(
        user=user,
        total_amount=total_amount,
        status='Pending',
        payment_status='Unpaid'
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    cart.items.all().delete()

    return Response({'message': 'Order placed successfully', 'order_id': order.id})


# payment/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
from .models import Order
from houseprojectapp.models import tbl_register

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user")
        order_id = request.data.get("order")

        try:
            user = tbl_register.objects.get(id=user_id)
            order = Order.objects.get(id=order_id, user=user)
        except tbl_register.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({"error": "Order not found for this user"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Update order payment status if not COD
        if serializer.validated_data["payment_method"] != "COD":
            order.payment_status = "Paid"
            order.status = "Processing"
            order.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)



# houseprojectapp/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Work
from .serializers import WorkSerializer

from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Work
from .serializers import WorkSerializer, WorkReadSerializer
class WorkViewSet(viewsets.ModelViewSet):
    queryset = Work.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return WorkReadSerializer   
        return WorkSerializer           




from adminapp.models import HouseFeature
from .serializers import HouseFeatureSerializer
class HouseFeatureListView(ListAPIView):
    queryset = HouseFeature.objects.all()
    serializer_class = HouseFeatureSerializer







# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import EngineerRequest
from .serializers import EngineerRequestSerializer, EngineerRequestReadSerializer
# views.py
from rest_framework import viewsets
from .models import EngineerRequest
from .serializers import EngineerRequestSerializer, EngineerRequestReadSerializer

class EngineerRequestViewSet(viewsets.ModelViewSet):
    queryset = EngineerRequest.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            # For GET requests → show expanded data
            return EngineerRequestReadSerializer
        # For POST/PUT/PATCH → show form with file field
        return EngineerRequestSerializer



# houseprojectapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserRequest, Work
from .serializers import UserRequestSerializer, WorkReadSerializer

class HouseSearchAPIView(APIView):
    def post(self, request):
        serializer = UserRequestSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user', None)
            category = serializer.validated_data['category']
            cent = serializer.validated_data['cent']
            sqft = serializer.validated_data['sqft']
            expected_amount = serializer.validated_data['expected_amount']

            # Save the request
            user_request = UserRequest.objects.create(
                user=user,
                category=category,
                cent=cent,
                sqft=sqft,
                expected_amount=expected_amount
            )

            # Directly filter works by exact cent value
            matched_works = Work.objects.filter(
                category=category,
                cent=cent
            )

            works_serializer = WorkReadSerializer(
                matched_works, many=True, context={'request': request}
            )

            return Response({
                'message': 'Submit successful',
                'request_id': user_request.id,
                'matched_works': works_serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# houseprojectapp/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Work
from .serializers import WorkReadSerializer

@api_view(['GET'])
def get_works_by_engineer(request, engineer_id):
    """
    Get all works of a given engineer by engineer_id
    """
    works = Work.objects.filter(engineer_id=engineer_id)
    if not works.exists():
        return Response(
            {"message": "No works found for this engineer."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = WorkReadSerializer(works, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



# houseprojectapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Work
from .serializers import WorkReadSerializer

class EngineerWorkDetailAPIView(APIView):
    def get(self, request, engineer_id, work_id):
        try:
            work = Work.objects.get(id=work_id, engineer_id=engineer_id)
        except Work.DoesNotExist:
            return Response(
                {"message": "Work not found for this engineer."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WorkReadSerializer(work, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)



# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserRequest
from .serializers import UserRequestSerializer
from houseprojectapp.models import tbl_register  # your user model

class UserRequestsByUserView(APIView):
    def get(self, request, user_id):
        try:
            user = tbl_register.objects.get(id=user_id)
        except tbl_register.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user_requests = UserRequest.objects.filter(user=user)
        serializer = UserRequestSerializer(user_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)






#Engineer booking


from rest_framework import viewsets
from .models import EngineerBooking
from .serializers import EngineerBookingSerializer, EngineerBookingReadSerializer

class EngineerBookingViewSet(viewsets.ModelViewSet):
    queryset = EngineerBooking.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return EngineerBookingReadSerializer
        return EngineerBookingSerializer
