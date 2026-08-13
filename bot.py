import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import logging
import os
from flask import Flask
import threading

# Configure logging to see errors in the console
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8699495253:AAFPZY3OI39PuOwc1ogl6C4rjhIiJMOopSY"
bot = telebot.TeleBot(BOT_TOKEN)

# IMPORTANT: Replace this with the exact URL where your index.html is hosted!
WEBAPP_URL = "https://gentle-pasca-68fdcd.netlify.app/" 

# Channel configuration (Bot MUST be Admin in both channels!)
REQUIRED_CHANNELS = [
    {
        "name": "Spinzaa Main",
        "link": "https://t.me/Spinzaamain",
        "id": "-1003930998102"
    },
    {
        "name": "Spinzaa Backup",
        "link": "https://t.me/spinzaabackup",
        "id": "-1004416499267"
    }
]

def check_membership(user_id):
    """Checks if a user is a member of all required channels."""
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            logging.error(f"Error checking channel {channel['id']} for user {user_id}: {e}")
            return False
            
    return True

def get_join_keyboard():
    """Generates inline keyboard prompting users to join required channels."""
    markup = InlineKeyboardMarkup(row_width=1)
    for channel in REQUIRED_CHANNELS:
        markup.add(InlineKeyboardButton(text=f"📢 Join {channel['name']}", url=channel['link']))
    
    markup.add(InlineKeyboardButton(text="✅ Verify", callback_data="check_join"))
    return markup

def get_play_keyboard(user_id, start_param=None):
    """Generates inline keyboard with the Web App launcher button."""
    markup = InlineKeyboardMarkup()
    final_url = WEBAPP_URL
    if start_param:
        final_url = f"{WEBAPP_URL}?tgWebAppStartParam={start_param}"
        
    web_app = WebAppInfo(url=final_url)
    markup.add(InlineKeyboardButton(text="🎮 Play Spinzaa & Earn", web_app=web_app))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handles the /start command and passes referral parameters."""
    user_id = message.from_user.id
    
    start_param = None
    if len(message.text.split()) > 1:
        start_param = message.text.split()[1]

    if check_membership(user_id):
        welcome_text = (
            "🎉 *Verification Successful!*\n\n"
            "You are now ready to spin the wheel and earn daily cash rewards.\n\n"
            "🎁 Keep an eye on the channel, free ₹100 to ₹1000 gift codes are dropped daily!"
        )
        bot.send_message(
            message.chat.id, 
            welcome_text, 
            parse_mode="Markdown", 
            reply_markup=get_play_keyboard(user_id, start_param)
        )
    else:
        join_text = (
            "Welcome to Spinzaa! —‌‌‌𝙩𝙤𝙗𝙞 ♛\n\n"
            "To Start Earning:\n"
            "1. Join channel below\n"
            "2. Click \"Verify\"\n"
            "3. Start Spinning & Earning!\n\n"
            "🇮🇳 India's most exciting earning app!\n"
            "🎁 Free ₹100 to ₹1000 gift codes will be shared in the channel daily!"
        )
        bot.send_message(
            message.chat.id, 
            join_text, 
            parse_mode="Markdown", 
            reply_markup=get_join_keyboard()
        )

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def verify_join(call):
    """Handles verification button click."""
    user_id = call.from_user.id
    bot.answer_callback_query(call.id, "Checking membership...")
    
    if check_membership(user_id):
        success_text = (
            "🎉 *Verification Successful!*\n\n"
            "You are now ready to spin the wheel and earn daily cash rewards.\n\n"
            "🎁 Keep an eye on the channel, free ₹100 to ₹1000 gift codes are dropped daily!"
        )
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=success_text,
            parse_mode="Markdown",
            reply_markup=get_play_keyboard(user_id)
        )
    else:
        bot.send_message(
            call.message.chat.id, 
            "❌ *You haven't joined all channels yet.*\n\nPlease join both channels to continue.",
            parse_mode="Markdown"
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_") or call.data.startswith("reject_"))
def handle_admin_withdrawal_action(call):
    """Handles admin click on Approve or Reject withdrawal request buttons."""
    data_parts = call.data.split("_")
    action = data_parts[0]
    user_id = data_parts[1]
    amount = data_parts[2]
    
    if action == "approve":
        bot.answer_callback_query(call.id, "Withdrawal Approved!")
        bot.send_message(
            user_id,
            f"✅ <b>Withdrawal Successful!</b>\n\nYour request for <b>₹{amount}</b> has been approved and processed to your bank account.",
            parse_mode="HTML"
        )
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"{call.message.text}\n\n✅ <b>STATUS: APPROVED BY ADMIN</b>",
            parse_mode="HTML"
        )
    elif action == "reject":
        bot.answer_callback_query(call.id, "Withdrawal Rejected!")
        bot.send_message(
            user_id,
            f"❌ <b>Withdrawal Rejected!</b>\n\nYour request for <b>₹{amount}</b> was rejected. Please check your bank details.",
            parse_mode="HTML"
        )
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"{call.message.text}\n\n❌ <b>STATUS: REJECTED BY ADMIN</b>",
            parse_mode="HTML"
        )

app = Flask(__name__)

@app.route('/')
def index():
    return "Spinzaa Bot & Server running smoothly!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    print("🤖 Spinzaa Bot starting...")
    
    # Start web server thread
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()
    
    print("✅ Web server active!")
    bot.infinity_polling()
