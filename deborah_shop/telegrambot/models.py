from django.db import models
from django.contrib.auth.models import User
class TelegramUser(models.Model):
 telegram_id=models.BigIntegerField(unique=True)
 user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
 first_name=models.CharField(max_length=100, blank=True)
 username=models.CharField(max_length=100, blank=True)
 phone_number=models.CharField(max_length=20, blank=True)