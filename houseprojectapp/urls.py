# urls.py
from numpy import outer
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .views import (
    ProductBookingView,
   #  CheckoutView,
      CartPaymentViewSet,
    ViewCartItems,
    RemoveCartView,
)

from houseprojectapp.views import *

schema_view = get_schema_view(
   openapi.Info(
      title="Plan With Us App API",
      default_version='v1',
      description="API documentation for your project",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# Define the router and register the viewset
router = DefaultRouter()
router.register(r'register', RegisterViewSet, basename='register')
router.register(r'engineer', EngineerViewSet, basename='engineer')
router.register(r'works', WorkViewSet, basename='works')
router.register(r'book_engineer',EngineerBookingViewSet,basename='book_engineer')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'product-bookings', ProductBookingView, basename='product-booking')
router.register(r'cart-payments', CartPaymentViewSet, basename='cart-payments')
router.register(r'booking-payment', BookingPaymentView, basename='booking-payment')
# router.register(r'checkout', CheckoutView, basename='checkout')
urlpatterns = [
      path('', include(router.urls)),
      path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
      path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
      path('login/', LoginView.as_view(), name='login'),
      path('house-search/', HouseSearchAPIView.as_view(), name='house_search_api'),
      path('predict_house/', HousePredictionView.as_view(), name='predict_house'),
      path('get-images/<int:request_id>/', GetImagesByRequestAPIView.as_view(), name='get_images_by_request'),
      path('download-pdf/<int:request_id>/', DownloadPredictionPDF.as_view(), name='download-pdf'),
      path('categories/', CategoryListView.as_view(), name='category-list'),
      path('house-features/', HouseFeatureListView.as_view(), name='house-feature-list'),
      path('houses/', HouseListView.as_view(), name='house-list'),
      path('product-categories/', ProductCategoryListView.as_view(), name='product-category-list'),
      path('products/', views.ProductsListView.as_view(), name='product-list'),
      path('products/by-category/<int:category_id>/', views.get_products_by_category, name='products_by_category'),
      path('product/<int:product_id>/', ProductDetailView.as_view(), name='product-detail'),
      path('engineer/profile/<int:engineer_id>/', views.engineer_profile, name='engineer_profile'),
      path('engineer/profile/update/<int:engineer_id>/', views.update_engineer_profile, name='update_engineer_profile'),
      path('engineer/available-status/<int:engineer_id>/', views.update_availability, name='available_status'),
      path('engineer_works/<int:engineer_id>/', views.get_works_by_engineer, name='works-by-engineer'),
      path('engineers/<int:engineer_id>/works/<int:work_id>/', EngineerWorkDetailAPIView.as_view(), name='engineer-work-detail'),
      path('user-requests/<int:user_id>/', UserRequestsByUserView.as_view(), name='user-requests-by-user'),
      path('engineer/bookings/<int:engineer_id>/', EngineerViewBookingView.as_view(), name='engineer-view-bookings'),

      path('engineer_update_status/<int:booking_id>/', EngineerUpdateStatus.as_view(), name='engineer-update-status'),
      path('engineer/view-feedback/<int:engineer_id>/', EngineerViewFeedback.as_view(), name='engineer-view-feedback'),
      path('requests/<int:user_id>/<int:request_id>/', UserRequestDetailByUserView.as_view(), name='user-request-detail-by-user'),
      # path('payment-details/', PaymentListViewSet.as_view({'get': 'list'}), name='payment-details'),
      # Cart specific endpoints 
      # path('cart-summary/<int:user_id>/', CartSummaryView.as_view({'get': 'list'}), name='cart-summary'),
      path('view-cart-items/', ViewCartItems.as_view(), name='view-cart-items'),
      path('remove-cart-item/<int:id>/', RemoveCartView.as_view(), name='remove-cart-item'),

      # path('upi-payment/', UpiPaymentView.as_view({'post': 'create'}), name='upi-payment'),
      # path('card-payment/', CardPaymentView.as_view({'post': 'create'}), name='card-payment'),
      path('user-cart/<int:user_id>/', UserCartView.as_view({'get': 'list'}), name='user-cart'), 
      path('update-cart-quantity/', UpdateCartQuantityView.as_view(), name='update-cart-quantity'),
  
      path('my-orders/<int:user_id>/', views.MyOrdersView.as_view(), name='my-orders'),
      path('user/<int:user_id>/bookings/', UserBookingsAPIView.as_view(), name='user-bookings'),
   
      path('cart/<int:product_id>/', CartCreateView.as_view(), name='cart-create'),
      path("engineer/booking/reject/<int:booking_id>/", EngineerRejectBooking.as_view(),name='engineer_reject_booking'),
]

