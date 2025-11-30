
import os
import django
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from asgiref.sync import sync_to_async
from store.models import Product, Category, Order, OrderItem, Profile, SiteSettings
from telegrambot.models import TelegramUser
from django.contrib.auth.models import User

USER_CARTS = {}

async def get_token():
    c = await sync_to_async(SiteSettings.objects.first)()
    return c.telegram_bot_token if c else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    tg, _ = await sync_to_async(TelegramUser.objects.get_or_create)(telegram_id=u.id, defaults={'first_name': u.first_name, 'username': u.username})
    kb = [[InlineKeyboardButton("👗 Каталог", callback_data='catalog')], [InlineKeyboardButton("🛒 Кошик", callback_data='cart')]]
    is_auth = await sync_to_async(lambda: tg.user is not None)()
    if not is_auth:
        mk = ReplyKeyboardMarkup([[KeyboardButton("📱 Авторизація", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Вітаю! Натисніть кнопку для входу:", reply_markup=mk)
    await update.message.reply_text("Меню:", reply_markup=InlineKeyboardMarkup(kb))

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = update.message.contact
    if c.user_id != update.effective_user.id: return
    ph = c.phone_number
    def link():
        phone = ph if ph.startswith('+380') else '+380' + ph.lstrip('380').replace('+', '')
        username = phone.replace('+', '')
        try: prof = Profile.objects.get(phone=phone)
        except:
            u = User.objects.create_user(username=username, password='123')
            prof, _ = Profile.objects.get_or_create(user=u)
            prof.phone = phone
            prof.save()
        tg = TelegramUser.objects.get(telegram_id=update.effective_user.id)
        tg.user = prof.user
        tg.phone_number = phone
        tg.save()
    await sync_to_async(link)()
    await update.message.reply_text("✅ Ви успішно увійшли!")

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    cats = await sync_to_async(list)(Category.objects.all())
    kb = [[InlineKeyboardButton(c.name, callback_data=f'cat_{c.id}')] for c in cats]
    kb.append([InlineKeyboardButton("🔙 Назад", callback_data='start')])
    await q.edit_message_text("Категорії:", reply_markup=InlineKeyboardMarkup(kb))

async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    cid = int(q.data.split('_')[1])
    prods = await sync_to_async(list)(Product.objects.filter(category_id=cid, is_active=True)[:5])
    if not prods: await q.edit_message_text("Порожньо", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data='catalog')]])); return
    for p in prods:
        txt = f"<b>{p.name}</b>
{p.description[:50]}
💰 <b>{p.price}</b>"
        await q.message.reply_text(txt, parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Купити", callback_data=f'add_{p.id}')]]))
    await q.message.reply_text("---", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data='catalog')]]))

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer("Додано")
    pid = int(q.data.split('_')[1])
    uid = q.from_user.id
    if uid not in USER_CARTS: USER_CARTS[uid] = {}
    USER_CARTS[uid][pid] = USER_CARTS[uid].get(pid, 0) + 1

async def cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    uid = q.from_user.id
    c = USER_CARTS.get(uid, {})
    if not c: await q.edit_message_text("Кошик порожній", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data='start')]])); return
    txt = "🛒 <b>КОШИК:</b>
"
    for pid, qty in c.items():
        p = await sync_to_async(Product.objects.get)(id=pid)
        txt += f"{p.name} x {qty} = {p.price*qty}
"
    kb = [[InlineKeyboardButton("✅ Замовити", callback_data='checkout')], [InlineKeyboardButton("❌ Очистити", callback_data='clear')]]
    await q.edit_message_text(txt, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    uid = q.from_user.id
    c = USER_CARTS.get(uid, {})
    if not c: return
    def mk_order():
        tg = TelegramUser.objects.get(telegram_id=uid)
        o = Order.objects.create(user=tg.user, first_name=tg.first_name, phone=tg.phone_number or "TG", city="Bot", nova_poshta="-", source='bot')
        tot = 0
        for pid, qty in c.items():
            p = Product.objects.get(id=pid)
            tot += p.price * qty
            OrderItem.objects.create(order=o, product=p, price=p.price, quantity=qty)
        o.total_price = tot
        o.save()
        return o
    o = await sync_to_async(mk_order)()
    USER_CARTS[uid] = {}
    await q.edit_message_text(f"Замовлення #{o.id} прийнято!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data='start')]]))

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_CARTS[update.callback_query.from_user.id] = {}
    await update.callback_query.answer("Очищено")
    await cart(update, context)

def run_bot():
    import asyncio
    t = asyncio.run(get_token())
    if not t: print("❌ TOKEN MISSING"); return
    app = Application.builder().token(t).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, contact))
    app.add_handler(CallbackQueryHandler(catalog, pattern='^catalog$'))
    app.add_handler(CallbackQueryHandler(products, pattern='^cat_'))
    app.add_handler(CallbackQueryHandler(add, pattern='^add_'))
    app.add_handler(CallbackQueryHandler(cart, pattern='^cart$'))
    app.add_handler(CallbackQueryHandler(clear, pattern='^clear$'))
    app.add_handler(CallbackQueryHandler(checkout, pattern='^checkout$'))
    app.add_handler(CallbackQueryHandler(start, pattern='^start$'))
    print("🤖 Bot Running...")
    app.run_polling()
