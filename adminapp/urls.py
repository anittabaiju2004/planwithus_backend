from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('view-users/', views.view_users, name='view_users'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('view-engineers/', views.view_engineers, name='view_engineers'),
    path('approve-engineer/<int:engineer_id>/', views.approve_engineer, name='approve_engineer'),
    path('reject-engineer/<int:engineer_id>/', views.reject_engineer, name='reject_engineer'),
    path('approved-engineers/', views.approved_engineers, name='approved_engineers'),
    path('rejected-engineers/', views.rejected_engineers, name='rejected_engineers'),
    path('add-category/', views.add_category, name='add_category'),
    path('add_house/', views.add_house, name='add_house'),
    path('manage_houses/', views.manage_houses, name='manage_houses'),
    path('house-image/<int:image_id>/update/', views.update_house_image, name='update_house_image'),
    path('add-product/', views.add_product, name='add_product'),
    path('products/', views.product_list, name='product_list'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('add_product_category/', views.add_product_category, name='add_product_category'),
    path('manage-category-images/', views.manage_category_images, name='manage_category_images'),
    path('features/', views.manage_features, name='feature_list'),
    path('features/add/', views.manage_features, {'action': 'add'}, name='add_feature'),
    path('features/edit/<int:feature_id>/', views.manage_features, {'action': 'edit'}, name='edit_feature'),
    path('features/delete/<int:feature_id>/', views.manage_features, {'action': 'delete'}, name='delete_feature'),
    path('admin-all-orders/', views.admin_all_orders, name='admin-all-orders'),
    path('view_bookings/', views.view_bookings, name='view_bookings'),
    
]
