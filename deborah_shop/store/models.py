from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse

# --- ШРИФТИ ---
FONT_CHOICES = [
    ('Playfair Display', 'Playfair Display (Classic)'),
    ('Cormorant Garamond', 'Cormorant Garamond (Luxury)'),
    ('Montserrat', 'Montserrat (Modern)'),
    ('Lato', 'Lato (Neutral)'),
    ('Open Sans', 'Open Sans'),
    ('Roboto', 'Roboto'),
    ('Oswald', 'Oswald (Bold)'),
    ('Merriweather', 'Merriweather'),
    ('Raleway', 'Raleway'),
    ('Nunito', 'Nunito'),
    ('Didot', 'Didot (Fashion)'),
    ('Bodoni Moda', 'Bodoni Moda'),
    ('Tenor Sans', 'Tenor Sans'),
    ('Italiana', 'Italiana'),
    ('Prata', 'Prata'),
    ('Marcellus', 'Marcellus'),
    ('Comfortaa', 'Comfortaa'),
    ('Caveat', 'Caveat'),
]

# --- КОНФІГУРАЦІЯ ---
class SiteSettings(models.Model):
    site_name = models.CharField("Назва сайту", max_length=50, default="DEBORAH")
    
    # Тікер (Біжуча стрічка)
    show_ticker = models.BooleanField("Показувати біжучу стрічку", default=True)
    ticker_bg_color = models.CharField("Фон стрічки (HEX)", max_length=20, default="#000000")
    
    # Дизайн
    brand_font = models.CharField("Шрифт Лого", max_length=50, choices=FONT_CHOICES, default='Playfair Display')
    headings_font = models.CharField("Шрифт Заголовків", max_length=50, choices=FONT_CHOICES, default='Playfair Display')
    body_font = models.CharField("Шрифт Тексту", max_length=50, choices=FONT_CHOICES, default='Lato')
    menu_font = models.CharField("Шрифт Меню", max_length=50, choices=FONT_CHOICES, default='Montserrat')

    header_bg_image = models.ImageField("Фон Шапки", upload_to='site/header/', blank=True, null=True)
    header_bg_color = models.CharField("Колір Шапки", max_length=20, default="#ffffff")
    hero_bg_image = models.ImageField("Фон Банера", upload_to='site/hero/', blank=True, null=True)
    hero_title = models.CharField("Заголовок Банера", max_length=100, default="Нова Колекція")
    body_bg_image = models.ImageField("Фон Сайта", upload_to='site/body/', blank=True, null=True)
    body_bg_color = models.CharField("Колір Фону", max_length=20, default="#f9f9f9")
    footer_bg_image = models.ImageField("Фон Футера", upload_to='site/footer/', blank=True, null=True)
    footer_bg_color = models.CharField("Колір Футера", max_length=20, default="#1a1a1a")
    footer_text_color = models.CharField("Текст Футера", max_length=20, default="#888888")
    
    # API Ключі
    nova_poshta_api_key = models.CharField("API Нової Пошти", max_length=100, blank=True)
    telegram_bot_token = models.CharField("TG Bot Token", max_length=100, blank=True)
    telegram_admin_id = models.CharField("TG Admin ID", max_length=50, blank=True)
    
    # Оплата
    wfp_merchant_login = models.CharField("WayForPay Login", max_length=100, blank=True)
    wfp_secret_key = models.CharField("WayForPay Secret", max_length=100, blank=True)
    liqpay_public_key = models.CharField("LiqPay Public", max_length=100, blank=True)
    liqpay_private_key = models.CharField("LiqPay Private", max_length=100, blank=True)
    
    # SEO
    meta_description = models.TextField("SEO Опис", blank=True)
    google_analytics_id = models.CharField("GA4 ID", max_length=50, blank=True)
    facebook_pixel_id = models.CharField("FB Pixel ID", max_length=50, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError('Дозволено лише одне налаштування')
        return super().save(*args, **kwargs)

    class Meta: verbose_name = "⚙️ Налаштування Сайту"; verbose_name_plural = "⚙️ Налаштування Сайту"
    def __str__(self): return "Конфігурація"

# --- МАГАЗИН ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField("Телефон", max_length=20, unique=True, null=True, blank=True)
    def __str__(self): return f"{self.user.username}"

class Category(models.Model):
    name = models.CharField("Назва", max_length=100)
    slug = models.SlugField(unique=True)
    def get_absolute_url(self): return f"/?category={self.slug}"
    class Meta: verbose_name = "Категорія"; verbose_name_plural = "Категорії"
    def __str__(self): return self.name

class Product(models.Model):
    SIZE_CHOICES = [('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')]
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField("Назва", max_length=200)
    price = models.DecimalField("Ціна", max_digits=10, decimal_places=0)
    old_price = models.DecimalField("Стара ціна", max_digits=10, decimal_places=0, blank=True, null=True)
    description = models.TextField("Опис", blank=True)
    image = models.ImageField("Фото", upload_to='products/', blank=True, null=True)
    sizes = models.CharField("Розміри", max_length=100, choices=SIZE_CHOICES, blank=True)
    colors = models.CharField("Кольори", max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_absolute_url(self): return reverse('product_detail', args=[str(self.id)])
    class Meta: verbose_name = "Товар"; verbose_name_plural = "Товари"; ordering = ['-created_at']
    def __str__(self): return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField("Фото", upload_to='products/gallery/')
    class Meta: verbose_name = "Галерея"; verbose_name_plural = "Галерея"

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: verbose_name = "Відгук"; verbose_name_plural = "Відгуки"

class Order(models.Model):
    STATUS_CHOICES = [('new', 'Новий'), ('sent', 'Відправлено'), ('done', 'Виконано')]
    PAYMENT_CHOICES = [('wayforpay', 'WayForPay'), ('liqpay', 'LiqPay'), ('cod', 'Накладений'), ('cash', 'Готівка')]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField("Ім'я", max_length=50)
    last_name = models.CharField("Прізвище", max_length=50)
    phone = models.CharField("Телефон", max_length=20)
    
    city = models.CharField("Місто", max_length=100)
    city_ref = models.CharField("Ref Міста", max_length=50, blank=True) 
    nova_poshta = models.CharField("Відділення", max_length=200)
    warehouse_ref = models.CharField("Ref Відділення", max_length=50, blank=True)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    tracking_number = models.CharField("ТТН", max_length=50, blank=True)
    
    total_price = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=10, default='site')

    class Meta: verbose_name = "Замовлення"; verbose_name_plural = "Замовлення"; ordering = ['-created_at']
    def __str__(self): return f"#{self.id} {self.first_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    quantity = models.PositiveIntegerField(default=1)
    def __str__(self): return f"{self.product.name} x {self.quantity}"
# --- LANDING PAGES (ПРОМО-СТОРІНКИ) ---

class LandingPage(models.Model):
    """Промо-сторінка з налаштовуваним дизайном"""
    
    BACKGROUND_TYPE_CHOICES = [
        ('color', 'Колір'),
        ('gradient', 'Градієнт'),
        ('image', 'Зображення'),
    ]
    
    title = models.CharField("Назва сторінки", max_length=200)
    slug = models.SlugField("URL (slug)", unique=True, max_length=200, 
                           help_text="Наприклад: summer-sale або new-collection")
    
    # Фон
    background_type = models.CharField("Тип фону", max_length=20, choices=BACKGROUND_TYPE_CHOICES, default='color')
    background_color = models.CharField("Колір фону", max_length=20, default="#ffffff", blank=True)
    background_gradient = models.CharField("Градієнт", max_length=200, blank=True,
                                          help_text="CSS градієнт, наприклад: linear-gradient(to right, #667eea, #764ba2)")
    background_image = models.ImageField("Зображення фону", upload_to='landing/backgrounds/', blank=True, null=True)
    
    # SEO
    meta_title = models.CharField("SEO Заголовок", max_length=200, blank=True)
    meta_description = models.TextField("SEO Опис", blank=True)
    
    is_active = models.BooleanField("Активна", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Промо-сторінка"
        verbose_name_plural = "📄 Промо-сторінки (Landing Pages)"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"/page/{self.slug}/"


class LandingBlock(models.Model):
    """Блок контенту на промо-сторінці"""
    
    BLOCK_TYPE_CHOICES = [
        ('text', 'Текстовий блок'),
        ('image', 'Зображення'),
        ('button', 'Кнопка'),
        ('products', 'Товари'),
    ]
    
    ALIGNMENT_CHOICES = [
        ('left', 'Ліворуч'),
        ('center', 'По центру'),
        ('right', 'Праворуч'),
    ]
    
    page = models.ForeignKey(LandingPage, on_delete=models.CASCADE, related_name='blocks')
    block_type = models.CharField("Тип блоку", max_length=20, choices=BLOCK_TYPE_CHOICES, default='text')
    
    # Текст
    text_content = models.TextField("Текст", blank=True)
    text_font = models.CharField("Шрифт", max_length=50, choices=FONT_CHOICES, default='Lato', blank=True)
    text_size = models.IntegerField("Розмір шрифту (px)", default=16, blank=True)
    text_color = models.CharField("Колір тексту", max_length=20, default="#000000", blank=True)
    text_alignment = models.CharField("Вирівнювання", max_length=10, choices=ALIGNMENT_CHOICES, default='center', blank=True)
    
    # Зображення
    image = models.ImageField("Зображення", upload_to='landing/blocks/', blank=True, null=True)
    image_width = models.IntegerField("Ширина зображення (%)", default=100, blank=True,
                                     help_text="Від 10 до 100")
    
    # Кнопка
    button_text = models.CharField("Текст кнопки", max_length=100, blank=True)
    button_link = models.CharField("Посилання кнопки", max_length=500, blank=True)
    button_color = models.CharField("Колір кнопки", max_length=20, default="#000000", blank=True)
    
    # Товари (вибір категорії)
    products_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,
                                         verbose_name="Категорія товарів")
    products_limit = models.IntegerField("Кількість товарів", default=4, blank=True)
    
    # Позиціонування
    position_top = models.IntegerField("Відступ зверху (%)", default=10, 
                                      help_text="Від 0 до 100")
    position_left = models.IntegerField("Відступ зліва (%)", default=10,
                                       help_text="Від 0 до 100")
    
    order = models.PositiveIntegerField("Порядок", default=0)
    
    class Meta:
        verbose_name = "Блок контенту"
        verbose_name_plural = "Блоки контенту"
        ordering = ['order']
    
    def __str__(self):
        return f"{self.get_block_type_display()} - {self.page.title}"


# Оновлюємо TickerItem для прив'язки до Landing Pages
class TickerItem(models.Model):
    image = models.ImageField("Банер для стрічки", upload_to='site/ticker/')
    
    # Додаємо вибір: URL або Landing Page
    link_type = models.CharField("Тип посилання", max_length=20, 
                                 choices=[('url', 'URL'), ('landing', 'Промо-сторінка')],
                                 default='url')
    link_url = models.CharField("URL посилання", max_length=500, blank=True,
                               help_text="Наприклад: /product/5/ або https://example.com")
    link_landing = models.ForeignKey(LandingPage, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name="Промо-сторінка")
    
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активний", default=True)

    class Meta: 
        verbose_name = "Банер стрічки"
        verbose_name_plural = "🎞️ Біжуча стрічка (Банери)"
        ordering = ['order']
    
    def __str__(self):
        return f"Банер {self.id} (Порядок: {self.order})"
    
    def get_link(self):
        """Повертає правильне посилання"""
        if self.link_type == 'landing' and self.link_landing:
            return self.link_landing.get_absolute_url()
        return self.link_url or "#"