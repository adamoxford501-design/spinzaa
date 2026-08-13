import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import logging

# Configure logging to see errors in the console
logging.basicConfig(level=logging.INFO)

# Replace with your actual Bot Token
BOT_TOKEN = "8699495253:AAFPZY3OI39PuOwc1ogl6C4rjhIiJMOopSY"
bot = telebot.TeleBot(BOT_TOKEN)

# IMPORTANT: Replace this with the URL where your index.html is hosted!
# Example: "https://your-username.github.io/spinzaa-app/"
WEBAPP_URL = "https://superb-douhua-eb3833.netlify.app/" 

# Required channels configuration
REQUIRED_CHANNELS = [
    {
        "name": "Spinzaa Main",
        "link": "https://t.me/Spinzaamain",
        "id": "-1003930998102" # Make sure the bot is an ADMIN in this channel!
    },
    {
        "name": "Spinzaa Backup",
        "link": "https://t.me/spinzaabackup",
        "id": "-1004416499267" # Make sure the bot is an ADMIN in this channel!
    }
]

def check_membership(user_id):
    """
    Checks if a user is a member of all required channels.
    Returns True if subscribed to all, False otherwise.
    """
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            # 'left' and 'kicked' mean they are not in the channel
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            logging.error(f"Error checking channel {channel['id']} for user {user_id}: {e}")
            # If the bot is not an admin in the channel, it will throw an exception.
            # We return False to prevent access until the bot is made admin.
            return False
            
    return True

def get_join_keyboard():
    """Generates the inline keyboard prompting users to join the channels."""
    markup = InlineKeyboardMarkup(row_width=1)
    
    # Add a button for each required channel
    for channel in REQUIRED_CHANNELS:
        markup.add(InlineKeyboardButton(text=f"📢 Join {channel['name']}", url=channel['link']))
    
    # Add the verification button
    markup.add(InlineKeyboardButton(text="✅ I Have Joined", callback_data="check_join"))
    return markup

def get_play_keyboard(user_id, start_param=None):
    """Generates the inline keyboard with the Web App button."""
    markup = InlineKeyboardMarkup()
    
    # Pass the start_param to the Web App URL if it exists (for referrals)
    final_url = WEBAPP_URL
    if start_param:
        # Pass it as tgWebAppStartParam so the frontend can read it
        final_url = f"{WEBAPP_URL}?tgWebAppStartParam={start_param}"
        
    web_app = WebAppInfo(url=final_url)
    markup.add(InlineKeyboardButton(text="🎮 Play Spinzaa & Earn", web_app=web_app))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handles the /start command and checks for referral parameters."""
    user_id = message.from_user.id
    
    # Extract referral ID if someone clicked t.me/Spinzaa_Bot?start=123456
    start_param = None
    if len(message.text.split()) > 1:
        start_param = message.text.split()[1]

    # Check if the user is in the required channels
    if check_membership(user_id):
        # User is already a member, show them the play button
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
        # User needs to join channels
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
    """Handles the 'I Have Joined' button click."""
    user_id = call.from_user.id
    
    # Acknowledge the callback immediately to stop the loading spinner on the button
    bot.answer_callback_query(call.id, "Checking membership...")
    
    if check_membership(user_id):
        # Successfully joined
        success_text = (
            "🎉 *Verification Successful!*\n\n"
            "You are now ready to spin the wheel and earn daily cash rewards.\n\n"
            "🎁 Keep an eye on the channel, free ₹100 to ₹1000 gift codes are dropped daily!"
        )
        # Edit the previous message to replace the join buttons with the play button
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=success_text,
            parse_mode="Markdown",
            reply_markup=get_play_keyboard(user_id)
        )
    else:
        # Still not joined
        bot.send_message(
            call.message.chat.id, 
            "❌ *You haven't joined all the channels yet.*\n\nPlease make sure you join using the links provided.",
            parse_mode="Markdown"
        )

if __name__ == "__main__":
    print("🤖 Spinzaa Bot is running...")
    print("⚠️  Ensure you have run: pip install pyTelegramBotAPI")
    # Start polling for messages
    bot.infinity_polling()
