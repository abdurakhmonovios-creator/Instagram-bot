import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import yt_dlp
import os

BOT_TOKEN = "7758643689:AAERcGMbDgFAsc_XOHYYmYs-bpWDMRk6Nvs"
CHANNEL_USERNAME = "@abdrkhmnvv17"

async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    is_sub = await check_subscription(user_id, context.bot)

    if not is_sub:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔔 Obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
            [InlineKeyboardButton("🔄 Tekshirish", callback_data="check_sub")]
        ])
        await update.message.reply_text(
            "📌 Avval pastdagi kanalga obuna bo‘ling!\n➡️ Obuna bo‘lgach *Tekshirish* tugmasini bosing.",
            reply_markup=keyboard
        )
        return
    await update.message.reply_text("Bot faol ishlamoqda! Havola yuboring.")

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    is_sub = await check_subscription(user_id, context.bot)

    if is_sub:
        await query.edit_message_text("🎉 Siz obuna bo‘lgansiz!\nEndi havola yuborishingiz mumkin.")
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔔 Obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
            [InlineKeyboardButton("🔄 Tekshirish", callback_data="check_sub")]
        ])
        await query.edit_message_text(
            "❌ Hali obuna bo‘lmadingiz!\nAvval kanalga obuna bo‘ling 👇",
            reply_markup=keyboard
        )

async def handle_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    is_sub = await check_subscription(user_id, context.bot)
    if not is_sub:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔔 Obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
            [InlineKeyboardButton("🔄 Tekshirish", callback_data="check_sub")]
        ])
        await update.message.reply_text(
            "❌ Avval kanalga obuna bo‘ling!\nSo‘ng *Tekshirish* tugmasini bosing.",
            reply_markup=keyboard
        )
        return

    url = update.message.text.strip()
    if "instagram.com" not in url:
        await update.message.reply_text("❌ Iltimos, faqat Instagram havolasini yuboring!")
        return

    msg = await update.message.reply_text("⏳ Tayyorlanmoqda...")
    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'insta_video.mp4', 'noplaylist': True, 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            caption = info.get("description", "")
            ydl.download([url])

        await msg.edit_text("🚀 Yuborilmoqda...")
        with open("insta_video.mp4", "rb") as vid:
            await update.message.reply_video(video=vid, caption=caption)
        os.remove("insta_video.mp4")
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ Xato: {e}")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(CommandHandler("help", start))

    print("Bot ishga tushdi ✅")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()  # botni doimiy ishga tushirish

if __name__ == "__main__":
    # Windows friendly event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
