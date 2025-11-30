from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from .models import Product, Category, Order, OrderItem, Profile, Review, SiteSettings
import uuid

def home(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    q = request.GET.get('q')
    if q: products = products.filter(Q(name__icontains=q))
    cat = request.GET.get('category')
    if cat: products = products.filter(category__slug=cat)
    favs = request.session.get('favorites', [])
    return render(request, 'store/index.html', {'products': products, 'categories': categories, 'fav_ids': favs})

def product_detail(request, product_id):
    p = get_object_or_404(Product, id=product_id)
    favs = request.session.get('favorites', [])
    related = Product.objects.filter(category=p.category).exclude(id=p.id)[:4]
    if request.method == 'POST' and request.user.is_authenticated:
        Review.objects.create(product=p, user=request.user, text=request.POST.get('text'), rating=int(request.POST.get('rating')))
        return redirect('product_detail', product_id=p.id)
    return render(request, 'store/product_detail.html', {'product': p, 'is_fav': p.id in favs, 'related_products': related})

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    messages.success(request, "Добавлено!")
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@require_POST
def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    str_id = str(product_id)
    action = request.POST.get('action')
    if action == 'add':
        cart[str_id] = cart.get(str_id, 0) + 1
    elif action == 'subtract':
        cart[str_id] = cart.get(str_id, 0) - 1
        if cart[str_id] <= 0:
            del cart[str_id]
    request.session['cart'] = cart
    return redirect('cart')

def cart_view(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(id=int(pid))
            total += p.price * qty
            products.append({'product': p, 'qty': qty, 'total': p.price * qty})
        except: pass
    settings = SiteSettings.objects.first()
    np_key = settings.nova_poshta_api_key if settings else ''
    return render(request, 'store/cart.html', {'cart_items': products, 'total_price': total, 'np_key': np_key})

def clear_cart(request):
    request.session['cart'] = {}
    return redirect('cart')

def checkout(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart: return redirect('home')
        
        phone = request.POST.get('phone')
        first_name = request.POST.get('first_name')
        pay_method = request.POST.get('payment')
        
        user = request.user if request.user.is_authenticated else None
        if not user:
            try: user = Profile.objects.get(phone=phone).user
            except:
                pw = str(uuid.uuid4())[:8]
                username = phone.replace('+', '')
                user = User.objects.create_user(username=username, password=pw, first_name=first_name)
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.phone = phone
                profile.save()
                messages.info(request, f"Аккаунт создан! Логин: {username}")

        total = 0
        items = []
        for pid, qty in cart.items():
            try:
                p = Product.objects.get(id=int(pid))
                total += p.price * qty
                items.append((p, qty))
            except: pass
            
        order = Order.objects.create(
            user=user,
            first_name=first_name,
            last_name=request.POST.get('last_name'),
            phone=phone,
            city=request.POST.get('city_name') or request.POST.get('city', 'Unknown'),
            city_ref=request.POST.get('city_ref', ''),
            nova_poshta=request.POST.get('warehouse_name') or request.POST.get('nova_poshta', 'Unknown'),
            warehouse_ref=request.POST.get('warehouse_ref', ''),
            payment_method=pay_method,
            total_price=total,
            source='site'
        )
        for p, qty in items: OrderItem.objects.create(order=order, product=p, price=p.price, quantity=qty)
        request.session['cart'] = {}
        
        if pay_method in ['wayforpay', 'liqpay']:
            return redirect('payment_process', order_id=order.id)
            
        return render(request, 'store/success.html', {'order': order})
    return redirect('cart')

def payment_process(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    settings = SiteSettings.objects.first()
    
    if order.payment_method == 'wayforpay':
        if settings and settings.wfp_merchant_login:
            return render(request, 'store/pay_wayforpay.html', {'order': order, 'settings': settings})
    
    if order.payment_method == 'liqpay':
        if settings and settings.liqpay_public_key:
            return render(request, 'store/pay_liqpay.html', {'order': order, 'settings': settings})
            
    return render(request, 'store/pay_mock.html', {'order': order})

def get_product_modal(request, product_id):
    p = get_object_or_404(Product, id=product_id)
    html = render_to_string('store/modal_content.html', {'product': p}, request=request)
    return JsonResponse({'html': html})

def toggle_favorite(request, product_id):
    favs = request.session.get('favorites', [])
    if product_id in favs: favs.remove(product_id)
    else: favs.append(product_id)
    request.session['favorites'] = favs
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def favorites_view(request):
    favs = request.session.get('favorites', [])
    products = Product.objects.filter(id__in=favs)
    return render(request, 'store/favorites.html', {'products': products})

def auth_view(request):
    if request.method == 'POST':
        if request.POST.get('action') == 'register':
            u = request.POST.get('username')
            p = request.POST.get('password')
            if User.objects.filter(username=u).exists(): messages.error(request, "Занято"); return redirect('auth')
            user = User.objects.create_user(username=u, password=p)
            profile = Profile.objects.get(user=user)
            profile.phone = '+380' + u
            profile.save()
            login(request, user)
            return redirect('profile')
        else:
            u = request.POST.get('username')
            p = request.POST.get('password')
            user = authenticate(username=u, password=p)
            if user: login(request, user); return redirect('profile')
            messages.error(request, "Ошибка")
    return render(request, 'store/auth.html')

@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/profile.html', {'orders': orders})

def logout_view(request):
    logout(request)
    return redirect('home')

def set_language(request, lang):
    """
    Зміна мови сайту (uk/en)
    Зберігає вибір у cookies на 1 рік
    """
    response = redirect(request.META.get('HTTP_REFERER', 'home'))
    response.set_cookie('lang', lang, max_age=365*24*60*60)  # 1 рік
    return response
    
def landing_page_view(request, slug):
    """Відображення промо-сторінки"""
    page = get_object_or_404(LandingPage, slug=slug, is_active=True)
    return render(request, 'store/landing_page.html', {'page': page})