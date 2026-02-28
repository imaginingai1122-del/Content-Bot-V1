import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types
from dotenv import load_dotenv
from keep_alive import keep_alive
import requests

# Load environment variables from .env file
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    print("Error: TELEGRAM_TOKEN ya GEMINI_API_KEY .env file mein set nahi hai.")
    print("Kripya ek '.env' file create karein aur usme apni keys daalein.")
    exit(1)

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

# THE VIRAL CONTENT CREATION SYSTEM PROMPT
SYSTEM_PROMPT = """You are an Elite AI Content Creation System trained with full strategic knowledge of YouTube algorithm, Snapchat spotlight system, Instagram reels growth mechanics, and Facebook monetization model.

Your mission is to act as my personal automated content production engine.

You must perform the following tasks every time I give you a niche or keyword:

1️⃣ Trend Intelligence Mode
Analyze viral potential
Identify high RPM niches
Suggest USA-targeted topics if monetization is priority
Detect low-competition opportunities
Suggest 5 viral content angles

2️⃣ Hook Engineering System
Generate 5 ultra-strong hooks:
Pattern interrupt hook
Curiosity hook
Controversial hook
Emotional hook
Fast fact hook
Hooks must be optimized for 3-second retention.

3️⃣ Script Generation Mode
If SHORT FORM:
Structure:
Hook (0–3 sec)
Fast Value
Open Loop
Call to Action

If LONG FORM:
Hook
Problem
Build Curiosity
Deep Explanation
Proof / Example
CTA

Tone must match:
High energy
Retention optimized
No boring filler words
Spoken natural style

4️⃣ Video Generation Prompt Mode
Generate:
Cinematic scene-by-scene breakdown
AI video generation prompt (hyper detailed)
Camera movement instructions
Lighting, mood, realism
Sound design suggestion
Thumbnail visual concept

5️⃣ SEO Domination Mode
Generate:
3 high-CTR titles
1 SEO optimized description
20 ranking tags
Hashtag set
Thumbnail text suggestion
CTR psychology explanation

6️⃣ Algorithm Optimization Mode
Provide:
Ideal upload time
Ideal video length
Audience targeting strategy
Retention improvement suggestion
Monetization angle (affiliate / digital product / ads)

7️⃣ Automation Behavior
Always:
Think like a viral strategist
Prioritize watch time
Prioritize USA high CPM audience if monetization requested
Avoid generic answers
Provide actionable output
Work as a full production team

If information is missing, ask strategic questions before generating content.
Your role is not just to create content — your role is to create profitable, viral content systems."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        "Hello! Main apka **Elite AI Content Creation System** hu. 🚀\n\n"
        "Main aapke YouTube, Instagram Reels, aur Facebook ke liye viral content plan bananese leke scripts, SEO, aur AI Video Prompts tak sab kuch kar sakta hu.\n\n"
        "Sirf mujhe ek **Niche** ya **Keyword** bhejiye (Jaise: 'Tech gadgets', 'Trading mindset', 'Fitness tips').\n\n"
        "Aapka aajka target keyword kya hai?"
    )
    await update.message.reply_text(welcome_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    
    # Send intermediate message
    processing_msg = await update.message.reply_text("🔄 Analyzing trend data, engineering viral hooks, and generating your absolute masterplan... Please wait.")
    
    try:
        # Call Gemini AI
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            ),
        )
        
        reply_text = response.text
        
        # Split text if it exceeds Telegram's 4096 character limit
        if len(reply_text) > 4000:
            parts = [reply_text[i:i+4000] for i in range(0, len(reply_text), 4000)]
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_msg.message_id, text=parts[0])
            for part in parts[1:]:
                await update.message.reply_text(part)
        else:
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_msg.message_id, text=reply_text)
            
    except Exception as e:
        error_msg = f"❌ Error aagaya: {str(e)}\n\nShayad API limit cross ho gayi ya network issue hai."
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_msg.message_id, text=error_msg)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    webhook_url = os.getenv("MAKE_WEBHOOK_URL")
    if not webhook_url:
        await update.message.reply_text("⚙️ System Error: Make.com ka Webhook URL backend/Render me set nahi hai!")
        return
        
    processing_msg = await update.message.reply_text("🔄 Video Pakad Li Gayi! Ise Make.com (Auto Uploader) par bhej raha hu... Please wait.")
    
    try:
        # Check if it's a video or document
        video_file = update.message.video or update.message.document
        
        # Get actual file download link from telegram servers
        file = await context.bot.get_file(video_file.file_id)
        video_download_url = file.file_path
        
        # User caption
        caption = update.message.caption or ""
        
        data = {
            "video_url": video_download_url,
            "caption": caption
        }
        
        # Send data to Make.com
        response = requests.post(webhook_url, json=data)
        
        if response.status_code == 200:
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_msg.message_id, 
                text="✅ **SUCCESS!** Aapki video autoupload ke liye engine me daal di gayi hai. Wo jaldi hi sabhi platform pe dikhne lagegi!")
        else:
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_msg.message_id, 
                text=f"❌ Arey baap re! Make.com ne lene se mana kar diya. Status: {response.status_code}")
                
    except Exception as e:
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_msg.message_id, 
            text=f"❌ Video transfer me error: {str(e)}")

def main() -> None:
    keep_alive()  # Start the background web server
    print("Bot ko start kiya jaa raha hai...")
    try:
        # Build the application
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        # Add Handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
        
        print("System Online! Bot ab chal raha hai! Telegram par jaake messages bhejiye.")
        app.run_polling()
    except Exception as e:
        print(f"Failed to start bot: {e}")

if __name__ == '__main__':
    main()
