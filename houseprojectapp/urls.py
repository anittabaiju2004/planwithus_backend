# urls.py
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter


from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

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
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'works', WorkViewSet, basename='works')
router.register(r'engineer-requests', EngineerRequestViewSet, basename='engineer-request')


urlpatterns = [
   path('', include(router.urls)),
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

   path('login/', LoginView.as_view(), name='login'),
   path('house-search/', HouseSearchAPIView.as_view(), name='house_search_api'),
   path('predict_house/', HousePredictionView.as_view(), name='predict_house'),
   path('get-images/<int:request_id>/', GetImagesByRequestAPIView.as_view(), name='get_images_by_request'),

   # path('download-prediction/', DownloadPredictionPDF.as_view(), name='download_prediction_pdf'),
   # path('download-pdf/', DownloadPredictionPDF.as_view(), name='download-pdf'),
    path('download-pdf/<int:request_id>/', DownloadPredictionPDF.as_view(), name='download-pdf'),
   
   path('categories/', CategoryListView.as_view(), name='category-list'),
   path('house-features/', HouseFeatureListView.as_view(), name='house-feature-list'),


   path('houses/', HouseListView.as_view(), name='house-list'),


   path('product-categories/', ProductCategoryListView.as_view(), name='product-category-list'),
   path('products/', views.ProductsListView.as_view(), name='product-list'),
   path('products/by-category/<int:category_id>/', views.get_products_by_category, name='products_by_category'),

   



   path('engineer/profile/<int:engineer_id>/', views.engineer_profile, name='engineer_profile'),
   path('engineer/profile/update/<int:engineer_id>/', views.update_engineer_profile, name='update_engineer_profile'),
   path('engineer/available-status/<int:engineer_id>/', views.update_availability, name='available_status'),
   
   path('engineer_works/<int:engineer_id>/', views.get_works_by_engineer, name='works-by-engineer'),

   
   path('add-to-cart/', AddToCartAPIView.as_view(), name='add-to-cart'),
   path('view-cart/<int:user_id>/', ViewCartAPIView.as_view(), name='view-cart'),
   path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
   path('place-order/', views.place_order, name='place_order'),
   # path('generate-house-image/', GenerateHouseImageAPIView.as_view(), name='generate-house-image'),
   path('engineers/<int:engineer_id>/works/<int:work_id>/', EngineerWorkDetailAPIView.as_view(), name='engineer-work-detail'),

]

