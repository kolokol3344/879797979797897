
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Order, SiteSettings
from telegrambot.models import TelegramUser
import requests

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created: Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=Order)
def notify_admin(sender, instance, created, **kwargs):
    if created:
        conf = SiteSettings.objects.first()
        if conf and conf.telegram_bot_token and conf.telegram_admin_id:
            msg = f"🔥 Замовлення #{instance.id}
💰 {instance.total_price} грн
📞 {instance.phone}
📍 {instance.city}, {instance.nova_poshta}"
            try: requests.post(f"https://api.telegram.org/bot{conf.telegram_bot_token}/sendMessage", data={'chat_id': conf.telegram_admin_id, 'text': msg})
            except: pass

@receiver(pre_save, sender=Order)
def tracking_alert(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Order.objects.get(pk=instance.pk)
            if instance.tracking_number and instance.tracking_number != old.tracking_number:
                conf = SiteSettings.objects.first()
                if not conf: return
                msg = f"🚚 Замовлення #{instance.id} відправлено!
📦 ТТН: {instance.tracking_number}"
                if instance.user:
                    tg = TelegramUser.objects.filter(user=instance.user).first()
                    if tg: requests.post(f"https://api.telegram.org/bot{conf.telegram_bot_token}/sendMessage", data={'chat_id': tg.telegram_id, 'text': msg})
        except: pass
