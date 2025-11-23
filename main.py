from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters
import yt_dlp
import os
import asyncio

BOT_TOKEN = "7758643689:AAERcGMbDgFAsc_XOHYYmYs-bpWDMRk6Nvs "  # tokenni shu yerga qo'yasiz
CHANNEL_USERNAME = "@abdrkhmnvv17"  # majburiy obuna kanali

# ---------------- Majburiy obuna tekshirish ---------------- #

async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ---------------- Start komandasi ---------------- #

async def start(update: Update, context: CallbackContext):
    user = update.effective_user

    # obuna tekshirish
    is_sub = await check_subscription(user.id, context.bot)

    if not is_sub:
        keyboard = [
            [InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
            [InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")]
        ]
        await update.message.reply_text(
            "👋 *Botdan foydalanish uchun avval kanalga obuna bo'ling!*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text("// Bot Faol Ishlamoqda ^^  Havola yuboring //")


# ---------------- Obuna tekshirish tugmasi ---------------- #

async def check_sub_callback(update: Update, context: CallbackContext):
    user = update.effective_user
    query = update.callback_query
    await query.answer()

    is_sub = await check_subscription(user.id, context.bot)

    if is_sub:
        await query.edit_message_text("🎉 Tabriklayman! Endi botdan foydalanishingiz mumkin!\n\nHavola yuboring👇")
    else:
        await query.edit_message_text("❌ Siz hali kanalga obuna bo'lmagansiz.\n\n@abdrkhmnvv17 kanaliga qo‘shiling!")
        

# ---------------- Instagram yuklab berish ---------------- #

async def handle_instagram(update: Update, context: CallbackContext):
    if not update.message or not update.message.text:
        return
    
    url = update.message.text.strip()

    # faqat instagram
    if "instagram.com" not in url:
        await update.message.reply_text("❌ Faqat Instagram havolasi yuboring!")
        return

    # obuna tekshirish
    user = update.effective_user
    is_sub = await check_subscription(user.id, context.bot)
    if not is_sub:
        await update.message.reply_text("❌ Avval @abdrkhmnvv17 kanaliga obuna bo'ling!")
        return

    msg = await update.message.reply_text("⏳ Tayyorlanmoqda...")

    try:
        ydl_opts = {
            "format": "best",
            "outtmpl": "insta.mp4",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            caption = info.get("description", "")

        await msg.edit_text("📤 Yuborilmoqda...")

        with open("insta.mp4", "rb") as f:
            await context.bot.send_video(
                chat_id=update.message.chat_id,
                video=f,
                caption=caption
            )

        await msg.delete()
        os.remove("insta.mp4")

    except Exception as e:
        await msg.edit_text(f"❌ Xato: {e}")


# ---------------- BOTNI ISHGA TUSHIRISH ---------------- #

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check_sub_callback, pattern="check_sub"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram))

print("Bot ishga tushdi!")
asyncio.run(app.run_polling())