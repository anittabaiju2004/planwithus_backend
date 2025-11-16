from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.shortcuts import redirect
from .models import tbl_admin

# Create your views here.
from django.shortcuts import render
from houseprojectapp.models import tbl_register, tbl_engineer
from django.db.models import Count

def index(request):
    # Count the number of users and engineers
    user_count = tbl_register.objects.filter(user_type='user').count()
    engineer_count = tbl_engineer.objects.count()

    # You can also count bookings if you have a booking model
    booking_count = 0  # Replace with your actual booking count if applicable

    context = {
        'user_count': user_count,
        'engineer_count': engineer_count,
        'booking_count': booking_count,
    }
    return render(request, 'adminapp/index.html', context)


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import tbl_admin  # make sure tbl_admin exists
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import tbl_admin

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Try to fetch the admin with matching email and password
            admin = tbl_admin.objects.get(email=email, password=password)
            # Save admin id in session
            request.session['admin_id'] = admin.id
            # Redirect to admin index page
            return redirect('index')  # Use the URL name for index page
        except tbl_admin.DoesNotExist:
            # Show error message
            messages.error(request, 'Invalid email or password')

    # For GET request or failed login
    return render(request, 'adminapp/login.html')

from django.shortcuts import redirect

def logout_view(request):
    # Clear session data (e.g., for admin, user, or engineer)
    request.session.flush()
    return redirect('login')  # Redirect to login page after logout


from django.shortcuts import render
from houseprojectapp.models import tbl_engineer, tbl_register  # adjust app name if needed

def view_users(request):
    users = tbl_register.objects.all()
    return render(request, 'adminapp/view_users.html', {'users': users})


def delete_user(request, user_id):
    user = get_object_or_404(tbl_register, id=user_id)
    user.delete()
    return redirect('view_users')

def view_engineers(request):
    engineers = tbl_engineer.objects.filter(status='pending')
    print("Engineers from DB:", engineers)
    return render(request, 'adminapp/view_engineers.html', {'engineers': engineers})

def approve_engineer(request, engineer_id):
    engineer = get_object_or_404(tbl_engineer, id=engineer_id)
    engineer.status = 'approved'
    engineer.save()
    messages.success(request, 'Engineer approved successfully.')
    return redirect('view_engineers')
def reject_engineer(request, engineer_id):
    engineer = get_object_or_404(tbl_engineer, id=engineer_id)
    engineer.status = 'rejected'
    engineer.save()
    messages.success(request, 'Engineer rejected successfully.')
    return redirect('view_engineers')

def approved_engineers(request):
    engineers = tbl_engineer.objects.filter(status='approved')
    print("Engineers from DB:", engineers)
    return render(request, 'adminapp/approved_engineers.html', {'engineers': engineers})

def rejected_engineers(request):
    engineers = tbl_engineer.objects.filter(status='rejected')
    print("Engineers from DB:", engineers)
    return render(request, 'adminapp/rejected_engineers.html', {'engineers': engineers})


from django.shortcuts import render, redirect
from .models import Category
from django.contrib import messages

def add_category(request):
    if request.method == 'POST':
        if 'add' in request.POST:
            name = request.POST.get('name')
            if name:
                Category.objects.create(name=name)
                messages.success(request, "Category added successfully.")
            else:
                messages.error(request, "Category name is required.")

        elif 'edit' in request.POST:
            category_id = request.POST.get('category_id')
            name = request.POST.get('edited_name')
            Category.objects.filter(id=category_id).update(name=name)
            messages.success(request, "Category updated successfully.")

        elif 'delete' in request.POST:
            category_id = request.POST.get('category_id')
            Category.objects.filter(id=category_id).delete()
            messages.success(request, "Category deleted successfully.")

    categories = Category.objects.all()
    return render(request, 'adminapp/add_category.html', {'categories': categories})




from django.http import HttpResponseRedirect

from .models import Products, ProductCategory
from django.shortcuts import render, redirect, get_object_or_404
from .models import ProductCategory

def add_product_category(request):
    if request.method == 'POST':
        if 'update_id' in request.POST:
            # Handle update
            cat_id = request.POST.get('update_id')
            category = get_object_or_404(ProductCategory, id=cat_id)
            category.name = request.POST.get('name')
            category.save()
        elif 'delete_id' in request.POST:
            # Handle delete
            cat_id = request.POST.get('delete_id')
            category = get_object_or_404(ProductCategory, id=cat_id)
            category.delete()
        else:
            # Handle add
            name = request.POST.get('name')
            if name:
                ProductCategory.objects.create(name=name)
        return redirect('add_product_category')

    categories = ProductCategory.objects.all()
    return render(request, 'adminapp/add_product_category.html', {'categories': categories})
from django.shortcuts import render, redirect, get_object_or_404
from .models import Products, ProductCategory

def add_product(request):
    categories = ProductCategory.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        category_id = request.POST.get('category_id')

        try:
            category = ProductCategory.objects.get(id=category_id)
        except ProductCategory.DoesNotExist:
            return render(request, 'adminapp/add_product.html', {
                'categories': categories,
                'error': "Invalid category selected."
            })

        Products.objects.create(
            name=name,
            price=price,
            quantity=quantity,
            description=description,
            image=image,
            category=category
        )
        return redirect('product_list')  # or wherever you want to go next

    return render(request, 'adminapp/add_product.html', {'categories': categories})


from .models import Products, ProductCategory

def product_list(request):
    category_id = request.GET.get('category')
    categories = ProductCategory.objects.all()

    if category_id:
        products = Products.objects.filter(category_id=category_id)
    else:
        products = Products.objects.all()

    return render(request, 'adminapp/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None
    })


from django.shortcuts import render, redirect, get_object_or_404
from .models import Products, ProductCategory

def edit_product(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    categories = ProductCategory.objects.all()

    if request.method == 'POST':
        product.category_id = request.POST.get('category')
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.quantity = request.POST.get('quantity')
        product.description = request.POST.get('description')

        if request.FILES.get('image'):
            product.image = request.FILES['image']

        product.save()
        return redirect('product_list')

    return render(request, 'adminapp/edit_product.html', {
        'product': product,
        'categories': categories
    })

def delete_product(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    product.delete()
    return redirect('product_list')




# houseprojectapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import HouseFeature

def manage_features(request, action=None, feature_id=None):
    # ADD feature
    if action == "add" and request.method == "POST":
        name = request.POST.get('name')
        if HouseFeature.objects.filter(name=name).exists():
            messages.error(request, "Feature already exists!")
        else:
            HouseFeature.objects.create(name=name)
            messages.success(request, "Feature added successfully!")
        return redirect('feature_list')

    # EDIT feature
    if action == "edit":
        feature = get_object_or_404(HouseFeature, id=feature_id)
        if request.method == "POST":
            feature.name = request.POST.get('name')
            feature.save()
            messages.success(request, "Feature updated successfully!")
            return redirect('feature_list')
        return render(request, 'adminapp/manage_features.html', {
            'features': HouseFeature.objects.all(),
            'edit_feature': feature
        })

    # DELETE feature
    if action == "delete":
        feature = get_object_or_404(HouseFeature, id=feature_id)
        feature.delete()
        messages.success(request, "Feature deleted successfully!")
        return redirect('feature_list')

    # LIST all features
    features = HouseFeature.objects.all()
    return render(request, 'adminapp/manage_features.html', {'features': features})



from houseprojectapp.models import ProductBookings, Cart, CartPayment
def admin_all_orders(request):
    # ========== SINGLE PRODUCT BOOKINGS ==========
    booking_orders = []
    bookings = ProductBookings.objects.select_related(
        'user', 'product', 'category'
    ).all().order_by('-booking_date')

    for booking in bookings:
        payment = getattr(booking, 'payment', None)

        booking_orders.append({
            'id': booking.id,
            'user': booking.user.name,
            'category': booking.category.name,
            'product': booking.product.name,
            'quantity': booking.quantity,
            'total_price': booking.total_price,
            'status': booking.status,
            'payment_type': payment.payment_type.upper() if payment else "PENDING",
            'payment_status': payment.status if payment else "pending",
            'date': booking.booking_date,
        })

    # ========== CART ORDERS ==========
    cart_orders = []
    carts = Cart.objects.select_related(
        'user', 'product', 'category'
    ).all().order_by('-created_at')

    for cart in carts:
        payment = CartPayment.objects.filter(
            user=cart.user, cart_ids__contains=[cart.id]
        ).first()

        cart_orders.append({
            'id': cart.id,
            'user': cart.user.name,
            'category': cart.category.name,
            'product': cart.product.name,
            'quantity': cart.quantity,
            'total_price': cart.total_price,
            'status': cart.status,
            'payment_type': payment.payment_type.upper() if payment else "PENDING",
            'payment_status': payment.status if payment else "pending",
            'date': cart.created_at,
        })

    return render(request, 'adminapp/admin_all_orders.html', {
        'booking_orders': booking_orders,
        'cart_orders': cart_orders
    })


from django.shortcuts import render
from houseprojectapp.models import EngineerBooking

def view_bookings(request):
    bookings = EngineerBooking.objects.all().order_by('-created_at')
    return render(request, 'adminapp/view_bookings.html', {'bookings': bookings})
