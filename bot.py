import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import time
import threading
import os
from flask import Flask

# --- BOT CONFIGURATION ---
BOT_TOKEN = "8699495253:AAFPZY3OI39PuOwc1ogl6C4rjhIiJMOopSY"
ADMIN_CHAT_ID = "8457706605"
WEBAPP_URL = "https://your-hosted-webapp-url-here.com/"  # IMPORTANT: Replace with your actual hosted link!

bot = telebot.TeleBot(BOT_TOKEN)

REQUIRED_CHANNELS = [
    {"name": "Spinzaa Main", "id": "-1003930998102", "link": "https://t.me/Spinzaamain"},
    {"name": "Spinzaa Backup", "id": "-1004416499267", "link": "https://t.me/spinzaabackup"}
]

# --- FLASK SERVER FOR RENDER (Keeps the bot alive) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Spinzaa Bot is running successfully!"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- BOT LOGIC ---
def check_membership(user_id):
    """Strictly checks if a user is an active member of all required channels."""
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator', 'restricted']:
                return False
        except Exception as e:
            # If bot is not admin or user never interacted, it fails
            print(f"Error checking {channel['name']}: {e}")
            return False
    return True

def get_join_keyboard(ref_id=None):
    """Generates the inline keyboard for joining channels."""
    markup = InlineKeyboardMarkup()
    for channel in REQUIRED_CHANNELS:
        markup.add(InlineKeyboardButton(text=f"📢 Join {channel['name']}", url=channel['link']))
    
    # Pass the ref_id in the callback data so it isn't lost during verification
    cb_data = f"verify_{ref_id}" if ref_id else "verify_none"
    markup.add(InlineKeyboardButton(text="✅ Verify", callback_data=cb_data))
    return markup

def get_webapp_keyboard(ref_id=None):
    """Generates the keyboard with the Web App button."""
    markup = InlineKeyboardMarkup()
    
    # If they were referred, pass that ID to the webapp via startapp
    final_url = f"{WEBAPP_URL}?startapp={ref_id}" if ref_id else WEBAPP_URL
    
    markup.add(InlineKeyboardButton(
        text="🎮 Play Spinzaa", 
        web_app=WebAppInfo(url=final_url)
    ))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    # Extract referral ID if present (e.g., /start 123456)
    command_parts = message.text.split()
    ref_id = command_parts[1] if len(command_parts) > 1 else None

    # Force channel join check
    if not check_membership(user_id):
        welcome_text = (
            "Welcome to Spinzaa! —‌‌‌𝙩𝙤𝙗𝙞 ♛\n\n"
            "To Start Earning:\n"
            "1. Join channels below\n"
            "2. Click \"Verify\"\n"
            "3. Start Spinning & Earning!\n\n"
            "🇮🇳 India's most exciting earning app!\n"
            "🎁 Free ₹100 to ₹1000 gift codes will be shared in the channel daily! And this after verification"
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_join_keyboard(ref_id))
    else:
        success_text = (
            "🎉 Verification Successful!\n\n"
            "You are now ready to spin the wheel and earn daily cash rewards.\n\n"
            "🎁 Keep an eye on the channel, free ₹100 to ₹1000 gift codes are dropped daily!"
        )
        bot.send_message(message.chat.id, success_text, reply_markup=get_webapp_keyboard(ref_id))

@bot.callback_query_handler(func=lambda call: call.data.startswith('verify_'))
def handle_verification(call):
    user_id = call.from_user.id
    ref_id = call.data.split('_')[1]
    if ref_id == "none":
        ref_id = None

    if check_membership(user_id):
        bot.answer_callback_query(call.id, "Verification Successful! ✅")
        success_text = (
            "🎉 Verification Successful!\n\n"
            "You are now ready to spin the wheel and earn daily cash rewards.\n\n"
            "🎁 Keep an eye on the channel, free ₹100 to ₹1000 gift codes are dropped daily!"
        )
        bot.edit_message_text(
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            text=success_text, 
            reply_markup=get_webapp_keyboard(ref_id)
        )
    else:
        bot.answer_callback_query(call.id, "❌ Please join ALL channels first!", show_alert=True)

# --- ADMIN WITHDRAWAL HANDLERS ---
@bot.callback_query_handler(func=lambda call: call.data.startswith(('approve_', 'reject_')))
def handle_withdraw_actions(call):
    # Ensure only the admin can press these buttons
    if str(call.from_user.id) != ADMIN_CHAT_ID:
        bot.answer_callback_query(call.id, "You are not authorized.", show_alert=True)
        return

    data_parts = call.data.split('_')
    action = data_parts[0]
    target_user_id = data_parts[1]
    amount = data_parts[2]

    if action == "approve":
        msg = f"✅ <b>Withdrawal Approved!</b>\n\nYour withdrawal request for ₹{amount} has been processed and sent to your bank account."
        status_text = "✅ Approved"
    else:
        msg = f"❌ <b>Withdrawal Rejected</b>\n\nYour withdrawal request for ₹{amount} was rejected by the admin. Please contact support."
        status_text = "❌ Rejected"

    try:
        # Notify the user
        bot.send_message(chat_id=target_user_id, text=msg, parse_mode='HTML')
        bot.answer_callback_query(call.id, f"Successfully {action}d.")
        
        # Update the admin message so buttons disappear
        new_text = call.message.text + f"\n\n<b>Status:</b> {status_text}"
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=new_text,
            parse_mode='HTML'
        )
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error notifying user: {e}", show_alert=True)

# --- START BOTH SERVER AND BOT ---
if __name__ == "__main__":
    # Start the Flask web server in a background thread
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    
    print("Bot is starting...")
    # Start the Telegram bot
    bot.infinity_polling()
