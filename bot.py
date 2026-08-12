import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.error import BadRequest

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration constants
BOT_TOKEN = "8699495253:AAFPZY3OI39PuOwc1ogl6C4rjhIiJMOopSY"
CHANNEL_ID = -1003930998102
CHANNEL_LINK = "https://t.me/Spinzaamain"

# IMPORTANT: Replace this with your exact Netlify URL!
MINI_APP_URL = "https://superb-lolly-41d792.netlify.app/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command and prompts user to join the channel."""
    user = update.effective_user
    username = user.first_name or "User"
    
    welcome_text = (
        f"<b>Welcome to Spinzaa! {username}</b>\n\n"
        f"To Start Earning:\n"
        f"1. Join channel below\n"
        f"2. Click \"Verify\"\n"
        f"3. Start Spinning & Earning!\n\n"
        f"🇮🇳 <b>India's most exciting earning app!</b>\n"
        f"🎁 <i>Free ₹100 to ₹1000 gift codes will be shared in the channel daily!</i>"
    )
    
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Verify", callback_data="verify_membership")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode="HTML", reply_markup=reply_markup)

async def verify_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifies if the user has joined the Telegram channel."""
    query = update.callback_query
    user_id = query.from_user.id
    
    try:
        # Check user status in the channel (requires bot to be admin in the channel)
        chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        status = chat_member.status
        
        # Valid member statuses in Telegram
        if status in ['member', 'administrator', 'creator']:
            success_text = (
                "🎉 <b>Verification Successful!</b>\n\n"
                "You are now ready to spin the wheel and earn daily cash rewards.\n\n"
                "<i>🎁 Keep an eye on the channel, free ₹100 to ₹1000 gift codes are dropped daily!</i>"
            )
            
            # Inline button to open the React Web App Mini App inside Telegram
            keyboard = [
                [InlineKeyboardButton("🎡 Spin Now", web_app=WebAppInfo(url=MINI_APP_URL))]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.edit_text(success_text, parse_mode="HTML", reply_markup=reply_markup)
        else:
            await query.answer("❌ You haven't joined the channel yet! Please join first.", show_alert=True)
            
    except BadRequest as e:
        logger.error(f"Error checking channel membership: {e}")
        # This usually means the bot is not an admin in the channel yet.
        await query.answer("⚠️ Verification Error. Ensure the bot is an admin in the channel.", show_alert=True)
    except Exception as e:
        logger.error(f"Unknown Error: {e}")
        await query.answer("⚠️ Could not verify right now. Try again later.", show_alert=True)

def main():
    """Start the bot."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(verify_membership, pattern="^verify_membership$"))

    print("Spinzaa Telegram Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
