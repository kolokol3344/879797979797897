@echo off
chcp 65001

echo ==========================================
echo 1. СОЗДАЕМ ФАЙЛЫ ОБНОВЛЕНИЯ (MakeMigrations)
echo ==========================================
python manage.py makemigrations

echo.
echo ==========================================
echo 2. ОБНОВЛЯЕМ БАЗУ ДАННЫХ (Migrate)
echo ==========================================
python manage.py migrate

echo.
echo ==========================================
echo 3. ПРОВЕРКА СУПЕРПОЛЬЗОВАТЕЛЯ
echo ==========================================
:: Эта команда теперь знает, где настройки
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deborah_shop.settings'); import django; django.setup(); from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123') and print('Admin created')"

echo.
echo ==========================================
echo 🚀 ЗАПУСК СЕРВЕРА!
echo Админка: http://127.0.0.1:8000/admin
echo Логин: admin
echo Пароль: admin123
echo ==========================================
python manage.py runserver
pause