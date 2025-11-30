from django.urls import path
from . import views

urlpatterns = [
    # Головна та навігація
    path('', views.home, name='home'),
    
    # Промо-сторінки
    path('page/<slug:slug>/', views.landing_page_view, name='landing_page'),
    
    # Мультимовність
    path('set-lang/<str:lang>/', views.set_language, name='set_language'),
    
    # Автентифікація
    path('auth/', views.auth_view, name='auth'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Товари
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('modal/<int:product_id>/', views.get_product_modal, name='get_product_modal'),
    
    # Кошик та обране
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('fav/toggle/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('cart/', views.cart_view, name='cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    
    # Оформлення та оплата
    path('checkout/', views.checkout, name='checkout'),
    path('pay/<int:order_id>/', views.payment_process, name='payment_process'),
]