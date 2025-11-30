from .models import SiteSettings, TickerItem

def global_context(request):
    """
    Глобальний контекст для всіх шаблонів
    - Кількість товарів у кошику
    - Кількість товарів в обраному
    - Поточна мова (UK/EN)
    - Словник перекладів
    """
    cart = request.session.get('cart', {})
    favs = request.session.get('favorites', [])
    
    # Отримуємо мову з cookies (за замовчуванням українська)
    lang = request.COOKIES.get('lang', 'uk')
    
    # Словник перекладів для UK та EN
    translations = {
        'uk': {
            # Навігація
            'home': 'Головна',
            'collection': 'Колекція',
            'dresses': 'Сукні',
            'lingerie': 'Білизна',
            'accessories': 'Аксесуари',
            'sale': 'Розпродаж',
            
            # Користувач
            'favorites': 'Обране',
            'cart': 'Кошик',
            'profile': 'Кабінет',
            'login': 'Вхід',
            'logout': 'Вихід',
            'register': 'Реєстрація',
            
            # Дії
            'add_to_cart': 'Додати в кошик',
            'quick_view': 'Швидкий перегляд',
            'view_details': 'Детальніше',
            'checkout': 'Оформити замовлення',
            'continue_shopping': 'Продовжити покупки',
            'clear_cart': 'Очистити кошик',
            
            # Оформлення
            'total': 'Разом',
            'subtotal': 'Проміжний підсумок',
            'payment': 'Оплата',
            'delivery': 'Доставка',
            'city': 'Місто',
            'warehouse': 'Відділення',
            'select_city': 'Оберіть місто',
            'select_warehouse': 'Оберіть відділення',
            
            # Форми
            'first_name': "Ім'я",
            'last_name': 'Прізвище',
            'phone': 'Телефон',
            'email': 'Email',
            'password': 'Пароль',
            'confirm_password': 'Підтвердіть пароль',
            
            # Повідомлення
            'order_placed': 'Дякуємо за замовлення!',
            'empty_cart': 'Кошик порожній',
            'no_products': 'Товарів немає',
            'added_to_cart': 'Додано в кошик!',
            'removed_from_cart': 'Видалено з кошика',
            
            # Товар
            'details': 'Деталі',
            'composition': 'Склад',
            'care': 'Догляд',
            'delivery_returns': 'Доставка та повернення',
            'reviews': 'Відгуки',
            'related': 'Рекомендовані товари',
            'size': 'Розмір',
            'color': 'Колір',
            'select_size': 'Оберіть розмір',
            'select_color': 'Оберіть колір',
            'in_stock': 'В наявності',
            'out_of_stock': 'Немає в наявності',
            
            # Інше
            'search': 'Пошук',
            'filter': 'Фільтр',
            'sort': 'Сортувати',
            'all': 'Всі',
            'new': 'Новинки',
            'free_shipping': 'Безкоштовна доставка від 2000 грн',
        },
        'en': {
            # Navigation
            'home': 'Home',
            'collection': 'Collection',
            'dresses': 'Dresses',
            'lingerie': 'Lingerie',
            'accessories': 'Accessories',
            'sale': 'Sale',
            
            # User
            'favorites': 'Favorites',
            'cart': 'Cart',
            'profile': 'Profile',
            'login': 'Login',
            'logout': 'Logout',
            'register': 'Register',
            
            # Actions
            'add_to_cart': 'Add to Cart',
            'quick_view': 'Quick View',
            'view_details': 'View Details',
            'checkout': 'Checkout',
            'continue_shopping': 'Continue Shopping',
            'clear_cart': 'Clear Cart',
            
            # Checkout
            'total': 'Total',
            'subtotal': 'Subtotal',
            'payment': 'Payment',
            'delivery': 'Delivery',
            'city': 'City',
            'warehouse': 'Warehouse',
            'select_city': 'Select city',
            'select_warehouse': 'Select warehouse',
            
            # Forms
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone': 'Phone',
            'email': 'Email',
            'password': 'Password',
            'confirm_password': 'Confirm Password',
            
            # Messages
            'order_placed': 'Thank you for your order!',
            'empty_cart': 'Your cart is empty',
            'no_products': 'No products',
            'added_to_cart': 'Added to cart!',
            'removed_from_cart': 'Removed from cart',
            
            # Product
            'details': 'Details',
            'composition': 'Composition',
            'care': 'Care Instructions',
            'delivery_returns': 'Delivery & Returns',
            'reviews': 'Reviews',
            'related': 'Related Products',
            'size': 'Size',
            'color': 'Color',
            'select_size': 'Select size',
            'select_color': 'Select color',
            'in_stock': 'In Stock',
            'out_of_stock': 'Out of Stock',
            
            # Other
            'search': 'Search',
            'filter': 'Filter',
            'sort': 'Sort',
            'all': 'All',
            'new': 'New Arrivals',
            'free_shipping': 'Free shipping over 2000 UAH',
        }
    }
    
    return {
        'cart_count': sum(cart.values()), 
        'fav_count': len(favs),
        'lang': lang,
        't': translations.get(lang, translations['uk'])
    }

def site_settings(request):
    """
    Налаштування сайту та біжуча стрічка
    """
    try:
        ticker_items = TickerItem.objects.filter(is_active=True)
    except:
        ticker_items = []
    
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None
    
    return {
        'settings': settings,
        'ticker_items': ticker_items
    }