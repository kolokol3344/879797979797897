from django.core.management.base import BaseCommand
from telegrambot.bot import run_bot
class Command(BaseCommand):
 help='Run Bot'
 def handle(self,*a,**o): run_bot()