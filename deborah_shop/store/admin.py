from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django import forms
from django.db.models import Sum, Count
from .models import Category, Product, ProductImage, Order, OrderItem, Profile, SiteSettings, Review, TickerItem, FONT_CHOICES
import csv
from django.http import HttpResponse
from .models import LandingPage, LandingBlock

# ==========================================
# CUSTOM ACTIONS
# ==========================================

def export_orders_csv(modeladmin, request, queryset):
    """Експорт замовлень у CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'
    response.write('\ufeff'.encode('utf8'))  # BOM для Excel
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Дата', 'Клієнт', 'Телефон', 'Місто', 'Сума', 'Статус', 'ТТН', 'Джерело'])
    
    for o in queryset:
        writer.writerow([
            o.id,
            o.created_at.strftime('%d.%m.%Y %H:%M'),
            f"{o.first_name} {o.last_name}",
            o.phone,
            o.city,
            o.total_price,
            o.get_status_display(),
            o.tracking_number or '-',
            o.source
        ])
    return response
export_orders_csv.short_description = "📥 Експорт в Excel (CSV)"


def mark_as_sent(modeladmin, request, queryset):
    """Позначити як відправлені"""
    queryset.update(status='sent')
mark_as_sent.short_description = "📦 Позначити як 'Відправлено'"


def mark_as_done(modeladmin, request, queryset):
    """Позначити як виконані"""
    queryset.update(status='done')
mark_as_done.short_description = "✅ Позначити як 'Виконано'"


# ==========================================
# SITE SETTINGS ADMIN
# ==========================================

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = '__all__'
        widgets = {
            'header_bg_color': forms.TextInput(attrs={'type': 'color', 'style': 'width: 100px;'}),
            'body_bg_color': forms.TextInput(attrs={'type': 'color', 'style': 'width: 100px;'}),
            'footer_bg_color': forms.TextInput(attrs={'type': 'color', 'style': 'width: 100px;'}),
            'footer_text_color': forms.TextInput(attrs={'type': 'color', 'style': 'width: 100px;'}),
            'ticker_bg_color': forms.TextInput(attrs={'type': 'color', 'style': 'width: 100px;'}),
        }


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsForm
    readonly_fields = ('fonts_preview',)
    
    fieldsets = (
        ('🔍 ПРЕВЬЮ ШРИФТІВ', {
            'fields': ('fonts_preview',),
            'classes': ('collapse',)
        }),
        ('⚙️ Основні налаштування', {
            'fields': ('site_name',)
        }),
        ('🎨 Дизайн', {
            'fields': (
                'brand_font',
                'headings_font', 
                'body_font',
                'menu_font',
            )
        }),
        ('📸 Фони та кольори', {
            'fields': (
                ('header_bg_image', 'header_bg_color'),
                ('hero_bg_image', 'hero_title'),
                ('body_bg_image', 'body_bg_color'),
                ('footer_bg_image', 'footer_bg_color', 'footer_text_color'),
            )
        }),
        ('🎞️ Біжуча стрічка', {
            'fields': (
                'show_ticker',
                'ticker_bg_color',
            )
        }),
        ('📦 Нова Пошта', {
            'fields': ('nova_poshta_api_key',)
        }),
        ('💳 Оплата', {
            'fields': (
                ('wfp_merchant_login', 'wfp_secret_key'),
                ('liqpay_public_key', 'liqpay_private_key'),
            )
        }),
        ('📱 Telegram', {
            'fields': (
                'telegram_bot_token',
                'telegram_admin_id',
            )
        }),
        ('🔍 SEO & Аналітика', {
            'fields': (
                'meta_description',
                'google_analytics_id',
                'facebook_pixel_id',
            )
        }),
    )

    def fonts_preview(self, instance):
        all_fonts = [f[0] for f in FONT_CHOICES]
        font_families = '|'.join([f.replace(' ', '+') for f in all_fonts])
        
        html = f'<link href="https://fonts.googleapis.com/css2?family={font_families}&display=swap" rel="stylesheet">'
        html += '<div style="display:flex; flex-wrap:wrap; gap:10px; background:#f5f5f5; padding:15px; border-radius:8px;">'
        
        for font, name in FONT_CHOICES:
            html += f'''
            <div style="background:white; padding:15px; border:1px solid #ddd; border-radius: 5px; width: 220px;">
                <div style="font-weight:bold; font-size:11px; color:#888; text-transform: uppercase;">{name}</div>
                <div style="font-family: '{font}', sans-serif; font-size:28px; margin-top:8px; color: #000;">DEBORAH</div>
                <div style="font-family: '{font}', sans-serif; font-size:14px; color: #666; margin-top: 5px;">The quick brown fox...</div>
            </div>
            '''
        html += '</div>'
        return mark_safe(html)
    
    fonts_preview.short_description = "Приклади шрифтів"

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


# ==========================================
# LANDING PAGES ADMIN
# ==========================================


class LandingBlockInline(admin.StackedInline):
    model = LandingBlock
    extra = 1
    fields = [
        'block_type',
        ('text_content', 'text_font', 'text_size', 'text_color', 'text_alignment'),
        ('image', 'image_width'),
        ('button_text', 'button_link', 'button_color'),
        ('products_category', 'products_limit'),
        ('position_top', 'position_left', 'order'),
    ]
    classes = ['collapse']


@admin.register(LandingPage)
class LandingPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'url_preview', 'is_active', 'blocks_count', 'created_at']
    list_filter = ['is_active', 'background_type', 'created_at']
    search_fields = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LandingBlockInline]
    
    fieldsets = (
        ('📋 Основна інформація', {
            'fields': ('title', 'slug', 'is_active')
        }),
        ('🎨 Фон сторінки', {
            'fields': ('background_type', 'background_color', 'background_gradient', 'background_image')
        }),
        ('🔍 SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    def url_preview(self, obj):
        url = obj.get_absolute_url()
        return format_html(
            '<a href="{}" target="_blank" style="background: #f0f0f0; padding: 3px 8px; border-radius: 3px; text-decoration: none; color: #007bff;">🔗 {}</a>',
            url, url
        )
    url_preview.short_description = "URL"
    
    def blocks_count(self, obj):
        count = obj.blocks.count()
        return format_html(
            '<span style="background: #17a2b8; color: white; padding: 3px 8px; border-radius: 10px; font-size: 11px;">{} блоків</span>',
            count
        )
    blocks_count.short_description = "Контент"


@admin.register(TickerItem)
class TickerItemAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'link_display', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'link_type']
    
    fieldsets = (
        (None, {
            'fields': ('image', 'order', 'is_active')
        }),
        ('🔗 Посилання', {
            'fields': ('link_type', 'link_url', 'link_landing'),
            'description': 'Оберіть тип посилання: URL (звичайна адреса) або Промо-сторінка'
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height: 50px; border-radius: 3px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Превью"
    
    def link_display(self, obj):
        link = obj.get_link()
        if obj.link_type == 'landing' and obj.link_landing:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">📄 {}</span>',
                obj.link_landing.title
            )
        return format_html('<code style="background: #f0f0f0; padding: 3px 6px; border-radius: 3px;">{}</code>', link[:40])
    link_display.short_description = "Посилання"

# ==========================================
# CATEGORY ADMIN
# ==========================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def product_count(self, obj):
        count = obj.product_set.count()
        return format_html(
            '<span style="background: #007bff; color: white; padding: 3px 8px; border-radius: 10px; font-size: 11px;">{}</span>',
            count
        )
    product_count.short_description = "Товарів"


# ==========================================
# PRODUCT ADMIN
# ==========================================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 60px; border-radius: 3px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Превью"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_tag', 'name', 'category', 'price_display', 'old_price', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    date_hierarchy = 'created_at'
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('category', 'name', 'description')
        }),
        ('Ціна', {
            'fields': (('price', 'old_price'),)
        }),
        ('Характеристики', {
            'fields': (('sizes', 'colors'),)
        }),
        ('Зображення', {
            'fields': ('image',)
        }),
        ('Налаштування', {
            'fields': ('is_active',)
        }),
    )
    
    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 70px; height: 90px; object-fit: cover; border-radius: 5px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return format_html('<div style="width: 70px; height: 90px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 5px; font-size: 10px; color: #999;">NO PHOTO</div>')
    image_tag.short_description = "Фото"
    
    def price_display(self, obj):
        return format_html('<strong style="color: #28a745; font-size: 14px;">{} ₴</strong>', obj.price)
    price_display.short_description = "Ціна"


# ==========================================
# ORDER ADMIN
# ==========================================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'quantity', 'price', 'total']
    readonly_fields = ['total']
    can_delete = False
    
    def total(self, obj):
        return format_html('<strong>{} ₴</strong>', obj.price * obj.quantity)
    total.short_description = "Сума"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id_display', 'created_display', 'customer', 'phone', 'city', 'total_display', 'status_badge', 'tracking_number', 'source_badge']
    list_filter = ['status', 'payment_method', 'source', 'created_at']
    search_fields = ['id', 'first_name', 'last_name', 'phone', 'tracking_number']
    list_editable = ['tracking_number']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    actions = [export_orders_csv, mark_as_sent, mark_as_done]
    
    fieldsets = (
        ('📋 Інформація про замовлення', {
            'fields': ('id', 'created_at', 'source')
        }),
        ('👤 Клієнт', {
            'fields': (('first_name', 'last_name'), 'phone', 'user')
        }),
        ('📍 Доставка', {
            'fields': ('city', 'city_ref', 'nova_poshta', 'warehouse_ref')
        }),
        ('💰 Оплата та статус', {
            'fields': (('payment_method', 'total_price'), ('status', 'tracking_number'))
        }),
    )
    
    readonly_fields = ['id', 'created_at', 'source']
    
    def id_display(self, obj):
        return format_html('<strong style="color: #007bff;">#{}</strong>', obj.id)
    id_display.short_description = "ID"
    
    def created_display(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')
    created_display.short_description = "Дата"
    
    def customer(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    customer.short_description = "Клієнт"
    
    def total_display(self, obj):
        return format_html('<strong style="color: #28a745; font-size: 14px;">{} ₴</strong>', obj.total_price)
    total_display.short_description = "Сума"
    
    def status_badge(self, obj):
        colors = {
            'new': '#007bff',
            'sent': '#ffc107',
            'done': '#28a745'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 5px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = "Статус"
    
    def source_badge(self, obj):
        icons = {
            'site': '🌐',
            'bot': '🤖'
        }
        return format_html(
            '<span style="font-size: 18px;" title="{}">{}</span>',
            'Сайт' if obj.source == 'site' else 'Telegram',
            icons.get(obj.source, '❓')
        )
    source_badge.short_description = "Джерело"


# ==========================================
# REVIEW ADMIN
# ==========================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating_stars', 'text_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'text']
    date_hierarchy = 'created_at'
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #ffc107; font-size: 16px;">{}</span>', stars)
    rating_stars.short_description = "Рейтинг"
    
    def text_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    text_preview.short_description = "Текст"


# ==========================================
# PROFILE ADMIN
# ==========================================

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'orders_count', 'total_spent']
    search_fields = ['user__username', 'phone']
    
    def orders_count(self, obj):
        count = obj.user.order_set.count()
        return format_html(
            '<span style="background: #17a2b8; color: white; padding: 3px 8px; border-radius: 10px; font-size: 11px;">{}</span>',
            count
        )
    orders_count.short_description = "Замовлень"
    
    def total_spent(self, obj):
        total = obj.user.order_set.aggregate(total=Sum('total_price'))['total'] or 0
        return format_html('<strong style="color: #28a745;">{} ₴</strong>', total)
    total_spent.short_description = "Всього витрачено"


# ==========================================
# ADMIN SITE CUSTOMIZATION
# ==========================================

admin.site.site_header = "🛍️ DEBORAH - Адміністрування"
admin.site.site_title = "DEBORAH Admin"
admin.site.index_title = "Панель управління магазином"