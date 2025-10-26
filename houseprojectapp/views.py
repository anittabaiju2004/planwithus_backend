from django.shortcuts import render

from rest_framework import viewsets

from houseprojectapp.utils.material_budget import get_material_budget
from .models import UserRequest, tbl_register
from .models import tbl_engineer
from .serializers import CategoryImageSerializer, EngineerSerializer, UserRequestSerializer,UserLoginSerializer
from .serializers import RegisterSerializer
from rest_framework.response import Response
from rest_framework import status
#register user
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

#register engineer
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
#login as engineer and  user
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




#get images
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


#predict house

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



#view engineer profile
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




#update engineer profile
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


#update availability status
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


#View categories
from rest_framework.generics import ListAPIView
from .models import Category
from .serializers import CategorySerializer

class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



#view houses
from rest_framework.generics import ListAPIView
from adminapp.models import CategoryImage
from .serializers import CategoryImageSerializer

class HouseListView(ListAPIView):
    queryset = CategoryImage.objects.all()
    serializer_class = CategoryImageSerializer


#view product categories and products
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

#DOWNLOAD PREDICTION AS PDF
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



# ENGINEER ADD WORKS
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



#LIST OF HOUSE FEATURES
from adminapp.models import HouseFeature
from .serializers import HouseFeatureSerializer
class HouseFeatureListView(ListAPIView):
    queryset = HouseFeature.objects.all()
    serializer_class = HouseFeatureSerializer







#GET HOUSES BY REQUEST(CENT, SQFT, EXPECTED AMOUNT) BY USER
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

            # ✅ Check for existing similar request
            existing_request = UserRequest.objects.filter(
                user=user,
                category=category,
                cent=cent,
                sqft=sqft,
                expected_amount=expected_amount
            ).first()

            if existing_request:
                message = "Request already exists"
                user_request = existing_request
            else:
                user_request = UserRequest.objects.create(
                    user=user,
                    category=category,
                    cent=cent,
                    sqft=sqft,
                    expected_amount=expected_amount
                )
                message = "Submit successful"

            # Filter matching works
            matched_works = Work.objects.filter(category=category, cent=cent)
            works_serializer = WorkReadSerializer(
                matched_works, many=True, context={'request': request}
            )

            return Response({
                'message': message,
                'request_id': user_request.id,
                'matched_works': works_serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#GET WORKS BY ENGINEER
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


#VIEW FOR GET WORK DETAIL BY ENGINEER AND WORK ID
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


#USER REQUESTS BY USER ID
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

#ENGINEER VIEW BOOKINGS

class EngineerViewBooking(APIView):
    def get(self, request, engineer_id):
        """
        Return all bookings assigned to a specific engineer.
        """
        bookings = EngineerBooking.objects.filter(engineer_id=engineer_id).order_by('-created_at')
        serializer = EngineerBookingReadSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#ENGINEER UPDATE BOOKING STATUS
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import EngineerBooking

class EngineerUpdateStatus(APIView):
    def patch(self, request, booking_id):
        """
        Engineers can update booking status only.
        Example statuses: accepted, work_started, completed, rejected
        """
        try:
            booking = EngineerBooking.objects.get(id=booking_id)
        except EngineerBooking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get("status")
        if not new_status:
            return Response({"error": "Status field is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Update only the status
        booking.status = new_status
        booking.save()

        return Response({"message": "Status updated successfully", "new_status": booking.status}, status=status.HTTP_200_OK)



#FEEDBACK VIEWSET
from rest_framework import viewsets
from .models import Feedback
from .serializers import FeedbackSerializer

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().order_by('-created_at')
    serializer_class = FeedbackSerializer





#ENGINEER VIEW FEEDBACKS
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Feedback
from .serializers import FeedbackSerializer

class EngineerViewFeedback(APIView):
    """
    GET /engineer/view-feedback/<engineer_id>/
    Returns all feedback entries for a specific engineer.
    """
    def get(self, request, engineer_id):
        feedbacks = Feedback.objects.filter(engineer_id=engineer_id).order_by('-created_at')
        if not feedbacks.exists():
            return Response({"message": "No feedback found for this engineer"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = FeedbackSerializer(feedbacks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserRequest
from .serializers import UserRequestSerializer
from houseprojectapp.models import tbl_register

class UserRequestDetailByUserView(APIView):
    def get(self, request, user_id, request_id):
        try:
            user = tbl_register.objects.get(id=user_id)
        except tbl_register.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_request = UserRequest.objects.get(id=request_id, user=user)
        except UserRequest.DoesNotExist:
            return Response({"error": "UserRequest not found for this user"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserRequestSerializer(user_request)
        return Response(serializer.data, status=status.HTTP_200_OK)














#cart and booking views can be added here
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from adminapp.models import Products, ProductCategory
from .models import (
    tbl_register, ProductBookings, Cart, Checkout, CartCheckout,
    Upi, Card, CartUpi, CartCard
)
from .serializers import (
    ProductCategorySerializer, productSerializer,
    ProductBookingSerializer, CartSerializer,
    CheckoutSerializer, CartCheckoutSerializer,
    PaymentDetailsSerializer, CartPaymentDetailsSerializer,
    UpiPaymentSerializer, CardSerializer,
    CartUpiSerializer, CartCardSerializer
)

# -----------------------------
# Product Booking
# -----------------------------
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from adminapp.models import Products, ProductCategory
from houseprojectapp.models import tbl_register, ProductBookings
from .serializers import ProductBookingSerializer

class ProductBookingView(viewsets.ModelViewSet):
    serializer_class = ProductBookingSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']

            user = get_object_or_404(tbl_register, id=user_id)
            product = get_object_or_404(Products, id=product_id)
            category = product.category  # ✅ Automatically get from product

            if quantity > product.quantity:
                return Response(
                    {"status": "failed", "message": "Insufficient stock"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            total_price = product.price * quantity

            booking = ProductBookings.objects.create(
                user=user,
                category=category,  # ✅ FIXED
                product=product,
                quantity=quantity,
                total_price=total_price,
                status='pending'
            )

            # Update product stock
            product.quantity -= quantity
            product.save()

            return Response({
                "status": "success",
                "message": "Product booked successfully",
                "booking_id": booking.id,
                "total_price": total_price
            }, status=status.HTTP_201_CREATED)

        return Response(
            {"status": "failed", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

# -----------------------------
# Checkout for Booking
# -----------------------------
class CheckoutView(viewsets.ModelViewSet):
    serializer_class = CheckoutSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        booking = serializer.validated_data['booking']

        # advance_fee = booking.total_price * Decimal('0.10')
        checkout = Checkout.objects.create(
            user=user,
            booking=booking,
            # advance_fee=advance_fee
        )

        return Response({
            "status": "success",
            "message": "Checkout completed",
            "checkout_id": checkout.id,
            # "advance_fee": advance_fee
        }, status=status.HTTP_201_CREATED)


# -----------------------------
# Cart Management
# -----------------------------
class CartView(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not user_id or not product_id or quantity <= 0:
            return Response(
                {"status": "failed", "message": "User, Product, and Quantity are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(tbl_register, id=user_id)
        product = get_object_or_404(Products, id=product_id)
        category = product.category  # ✅ Get category from product

        if quantity > product.quantity:
            return Response(
                {"status": "failed", "message": "Insufficient stock"},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_price = product.price * quantity

        cart_item = Cart.objects.create(
            user=user,
            category=category,  # ✅ Add this line
            product=product,
            quantity=quantity,
            total_price=total_price,
            status="pending"
        )

        serializer = CartSerializer(cart_item)
        return Response({"status": "success", "cart_item": serializer.data}, status=status.HTTP_201_CREATED)


# -----------------------------
# Cart Checkout
# -----------------------------
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import CartCheckout, Cart, tbl_register
from .serializers import CartCheckoutSerializer

class CartCheckoutViewSet(viewsets.ModelViewSet):
    queryset = CartCheckout.objects.all()
    serializer_class = CartCheckoutSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user')
        booking_id = request.data.get('booking')

        try:
            user = tbl_register.objects.get(id=user_id)
            booking = Cart.objects.get(id=booking_id)
        except (tbl_register.DoesNotExist, Cart.DoesNotExist):
            return Response({'error': 'Invalid user or booking ID'}, status=status.HTTP_400_BAD_REQUEST)

        checkout = CartCheckout.objects.create(user=user, booking=booking)
        serializer = self.get_serializer(checkout)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# -----------------------------
# UPI & Card Payments
# -----------------------------
class UpiPaymentView(viewsets.ModelViewSet):
    serializer_class = UpiPaymentSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        booking_id = request.data.get("booking_id")
        upi_id = request.data.get("upi_id")
        if not booking_id or not upi_id:
            return Response({"message": "Booking ID and UPI ID required"}, 400)

        booking = get_object_or_404(ProductBookings, id=booking_id)

        if Upi.objects.filter(booking=booking).exists():
            return Response({"message": "Payment already exists"}, 400)

        upi_payment = Upi.objects.create(booking=booking, upi_id=upi_id, status="success")
        booking.status = "paid"
        booking.save()
        serializer = UpiPaymentSerializer(upi_payment)
        return Response({"status": "success", "data": serializer.data}, 201)


class CardPaymentView(viewsets.ModelViewSet):
    serializer_class = CardSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        booking_id = request.data.get("booking_id")
        booking = get_object_or_404(ProductBookings, id=booking_id)

        if Card.objects.filter(booking=booking).exists():
            return Response({"message": "Payment already exists"}, 400)

        card_payment = Card.objects.create(
            booking=booking,
            card_holder_name=request.data.get("card_holder_name"),
            card_number=request.data.get("card_number")[-4:],  # last 4 digits
            expiry_date=request.data.get("expiry_date"),
            cvv=request.data.get("cvv"),
            status="success"
        )

        booking.status = "paid"
        booking.save()
        serializer = CardSerializer(card_payment)
        return Response({"status": "success", "data": serializer.data}, 201)



# -----------------------------
# Cart Summary View
# -----------------------------
class CartSummaryView(viewsets.ViewSet):
    def list(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"status": "failed", "message": "User ID is required"}, status=400)

        user = tbl_register.objects.filter(id=user_id).first()
        if not user:
            return Response({"status": "failed", "message": "User not found"}, status=404)

        cart_items = Cart.objects.filter(user=user, status="pending")
        if not cart_items.exists():
            return Response({"status": "failed", "message": "No items in cart"}, status=404)

        total_price = sum(item.total_price for item in cart_items)
        advance_fee = total_price * Decimal('0.10')

        return Response({
            "status": "success",
            "user_id": user.id,
            "user_name": user.name,
            "user_email": user.email,
            "user_phone_number": getattr(user, 'phone_number', ''),
            "total_price": f"{total_price:.2f}",
            "advance_fee": f"{advance_fee:.2f}"
        }, status=200)


# -----------------------------
# View Cart Items
# -----------------------------
class ViewCartItems(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"status": "failed", "message": "User ID is required"}, status=400)

        cart_items = Cart.objects.filter(user_id=user_id, status="pending").select_related('product')
        if not cart_items.exists():
            return Response({"status": "success", "message": "No pending items in cart", "cart_items": [], "total_price": 0}, status=200)

        cart_data = []
        total_price = 0
        for item in cart_items:
            item_total_price = item.total_price
            total_price += item_total_price
            product_image_url = f"{settings.MEDIA_URL}{item.product.image}" if item.product.image else None

            cart_data.append({
                "id": item.id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "single_item_price": item.product.price,
                "item_total_price": item_total_price,
                "product_image": product_image_url,
                "status": item.status
            })

        return Response({"status": "success", "cart_items": cart_data, "total_price": total_price}, status=200)


# -----------------------------
# Remove Cart Item
# -----------------------------
class RemoveCartView(generics.DestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def destroy(self, request, *args, **kwargs):
        cart_id = request.query_params.get('id')
        if not cart_id:
            return Response({"status": "failed", "message": "Cart ID is required"}, status=400)

        try:
            cart_item = Cart.objects.get(id=cart_id)
            cart_item.delete()
            return Response({"status": "success", "message": "Cart item removed"}, status=200)
        except Cart.DoesNotExist:
            return Response({"status": "failed", "message": "Cart item not found"}, status=404)


# -----------------------------
# Cart UPI Payment
# -----------------------------
class CartUpiPaymentView(viewsets.ModelViewSet):
    serializer_class = CartUpiSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        upi_id = request.data.get("upi_id")

        if not user_id or not upi_id:
            return Response({"message": "User ID and UPI ID are required"}, status=400)

        user = get_object_or_404(tbl_register, id=user_id)
        cart_items = Cart.objects.filter(user=user, status="pending")
        if not cart_items.exists():
            return Response({"message": "No pending cart items"}, status=400)

        upi_payment = CartUpi.objects.create(user=user, upi_id=upi_id, status="success")
        cart_items.update(status="paid")

        serializer = CartUpiSerializer(upi_payment)
        return Response({"status": "success", "message": "UPI payment completed", "data": serializer.data}, status=201)


# -----------------------------
# Cart Card Payment
# -----------------------------
class CartCardPaymentView(viewsets.ModelViewSet):
    serializer_class = CartCardSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        card_holder_name = request.data.get("card_holder_name")
        card_number = request.data.get("card_number")
        expiry_date = request.data.get("expiry_date")
        cvv = request.data.get("cvv")

        if not all([user_id, card_holder_name, card_number, expiry_date, cvv]):
            return Response({"message": "All card fields are required"}, status=400)

        user = get_object_or_404(tbl_register, id=user_id)
        cart_items = Cart.objects.filter(user=user, status="pending")
        if not cart_items.exists():
            return Response({"message": "No pending cart items"}, status=400)

        card_payment = CartCard.objects.create(
            user=user,
            card_holder_name=card_holder_name,
            card_number=card_number[-4:],  # store last 4 digits
            expiry_date=expiry_date,
            cvv=cvv,
            status="success"
        )

        cart_items.update(status="paid")
        serializer = CartCardSerializer(card_payment)
        return Response({"status": "success", "message": "Card payment completed", "data": serializer.data}, status=201)



from rest_framework import viewsets
from rest_framework.response import Response
from .models import ProductBookings, Cart
from .serializers import PaymentDetailsSerializer, CartPaymentDetailsSerializer

# -----------------------------
# Payment List ViewSet
# -----------------------------
class PaymentListViewSet(viewsets.ViewSet):
    """
    Returns a list of all ProductBookings with user details and total price.
    """

    def list(self, request):
        # Optional: filter by user_id if passed in query params
        user_id = request.query_params.get('user_id', None)

        if user_id:
            bookings = ProductBookings.objects.filter(user_id=user_id)
            cart_items = Cart.objects.filter(user_id=user_id)
        else:
            bookings = ProductBookings.objects.all()
            cart_items = Cart.objects.all()

        # Serialize bookings
        booking_serializer = PaymentDetailsSerializer(bookings, many=True)
        cart_serializer = CartPaymentDetailsSerializer(cart_items, many=True)

        return Response({
            "status": "success",
            "bookings": booking_serializer.data,
            "cart_items": cart_serializer.data
        })
