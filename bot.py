import os
import time
import threading
import requests
import traceback
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import re
from dotenv import load_dotenv
from flask import Flask

# تحميل المتغيرات من ملف .env
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN or TOKEN == "ضع_التوكن_هنا":
    print("الرجاء وضع توكن البوت الخاص بك في ملف .env")
    exit()

bot = telebot.TeleBot(TOKEN)

# تخزين لغات المستخدمين (في الذاكرة)
user_languages = {}

# نصوص اللغات
translations = {
    'en': {
        'choose_lang': "Please choose your language:",
        'welcome': "Welcome! 🤖\n\nSend me any TikTok video or post link, and I will download and send it to you directly here.",
        'no_url': "⚠️ I couldn't find a valid link in your message.",
        'fetching': "⏳ Fetching the video, please wait a moment...",
        'not_found': "❌ I couldn't find the file after downloading.",
        'error': "❌ Sorry, an error occurred during download or the link is invalid.\n\nMake sure the account is not private.",
        'invalid_link': "⚠️ Please send a valid TikTok link.",
        'lang_set': "✅ Language has been set to English."
    },
    'ar': {
        'choose_lang': "الرجاء اختيار لغتك:",
        'welcome': "مرحباً بك! 🤖\n\nأرسل لي أي رابط لفيديو أو بوست من تيك توك، وسأقوم بتحميله وإرساله لك مباشرة هنا.",
        'no_url': "⚠️ لم أتمكن من العثور على رابط صحيح في رسالتك.",
        'fetching': "⏳ جاري جلب الفيديو، يرجى الانتظار قليلاً...",
        'not_found': "❌ لم أتمكن من العثور على الملف بعد تحميله.",
        'error': "❌ عذراً، حدث خطأ أثناء التحميل أو أن الرابط غير صحيح.\n\nتأكد من أن الحساب ليس خاصاً (Private).",
        'invalid_link': "⚠️ الرجاء إرسال رابط تيك توك صحيح.",
        'lang_set': "✅ تم تعيين اللغة إلى العربية."
    },
    'es': {
        'choose_lang': "Por favor elige tu idioma:",
        'welcome': "¡Bienvenido! 🤖\n\nEnvíame cualquier enlace de video o publicación de TikTok, y lo descargaré y te lo enviaré directamente aquí.",
        'no_url': "⚠️ No pude encontrar un enlace válido en tu mensaje.",
        'fetching': "⏳ Obteniendo el video, por favor espera un momento...",
        'not_found': "❌ No pude encontrar el archivo después de descargarlo.",
        'error': "❌ Lo siento, ocurrió un error durante la descarga o el enlace no es válido.\n\nAsegúrate de que la cuenta no sea privada.",
        'invalid_link': "⚠️ Por favor, envía un enlace de TikTok válido.",
        'lang_set': "✅ El idioma se ha configurado en Español."
    },
    'fr': {
        'choose_lang': "Veuillez choisir votre langue :",
        'welcome': "Bienvenue ! 🤖\n\nEnvoyez-moi un lien vers une vidéo ou une publication TikTok, et je le téléchargerai et vous l'enverrai directement ici.",
        'no_url': "⚠️ Je n'ai pas pu trouver de lien valide dans votre message.",
        'fetching': "⏳ Récupération de la vidéo, veuillez patienter un moment...",
        'not_found': "❌ Je n'ai pas pu trouver le fichier après le téléchargement.",
        'error': "❌ Désolé, une erreur s'est produite lors du téléchargement ou le lien est invalide.\n\nAssurez-vous que le compte n'est pas privé.",
        'invalid_link': "⚠️ Veuillez envoyer un lien TikTok valide.",
        'lang_set': "✅ La langue a été définie sur Français."
    },
    'zh': {
        'choose_lang': "请选择您的语言：",
        'welcome': "欢迎！🤖\n\n发送任何TikTok视频或帖子的链接给我，我将下载并直接发送给您。",
        'no_url': "⚠️ 我无法在您的消息中找到有效的链接。",
        'fetching': "⏳ 正在获取视频，请稍候...",
        'not_found': "❌ 下载后我找不到文件。",
        'error': "❌ 抱歉，下载过程中发生错误或链接无效。\n\n请确保帐户不是私密的。",
        'invalid_link': "⚠️ 请发送有效的TikTok链接。",
        'lang_set': "✅ 语言已设置为中文。"
    },
    'hi': {
        'choose_lang': "कृपया अपनी भाषा चुनें:",
        'welcome': "स्वागत है! 🤖\n\nमुझे कोई भी टिकटॉक वीडियो या पोस्ट लिंक भेजें, और मैं इसे डाउनलोड करके सीधे आपको भेज दूंगा।",
        'no_url': "⚠️ मुझे आपके संदेश में कोई वैध लिंक नहीं मिला।",
        'fetching': "⏳ वीडियो प्राप्त किया जा रहा है, कृपया थोड़ी प्रतीक्षा करें...",
        'not_found': "❌ डाउनलोड करने के बाद मुझे फ़ाइल नहीं मिली।",
        'error': "❌ क्षमा करें, डाउनलोड के दौरान एक त्रुटि हुई या लिंक अमान्य है।\n\nसुनिश्चित करें कि खाता निजी नहीं है।",
        'invalid_link': "⚠️ कृपया एक वैध टिकटॉक लिंक भेजें।",
        'lang_set': "✅ भाषा हिंदी सेट कर दी गई है。"
    },
    'ru': {
        'choose_lang': "Пожалуйста, выберите ваш язык:",
        'welcome': "Добро пожаловать! 🤖\n\nОтправьте мне любую ссылку на видео или пост TikTok, и я скачаю и отправлю его вам прямо сюда.",
        'no_url': "⚠️ Я не смог найти действительную ссылку в вашем сообщении.",
        'fetching': "⏳ Получение видео, пожалуйста, подождите...",
        'not_found': "❌ Я не смог найти файл после скачивания.",
        'error': "❌ К сожалению, во время загрузки произошла ошибка или ссылка недействительна.\n\nУбедитесь, что учетная запись не является приватной.",
        'invalid_link': "⚠️ Пожалуйста, отправьте действительную ссылку TikTok.",
        'lang_set': "✅ Язык изменен на русский."
    },
    'de': {
        'choose_lang': "Bitte wähle deine Sprache:",
        'welcome': "Willkommen! 🤖\n\nSende mir einen TikTok-Video- oder Beitragslink, und ich werde ihn herunterladen und dir direkt hier senden.",
        'no_url': "⚠️ Ich konnte keinen gültigen Link in deiner Nachricht finden.",
        'fetching': "⏳ Video wird abgerufen, bitte warten...",
        'not_found': "❌ Ich konnte die Datei nach dem Herunterladen nicht finden.",
        'error': "❌ Entschuldigung, beim Herunterladen ist ein Fehler aufgetreten oder der Link ist ungültig.\n\nStelle sicher, dass das Konto nicht privat ist.",
        'invalid_link': "⚠️ Bitte sende einen gültigen TikTok-Link.",
        'lang_set': "✅ Die Sprache wurde auf Deutsch eingestellt."
    }
}

def get_text(chat_id, key):
    lang = user_languages.get(chat_id, 'ar') # Default to Arabic
    return translations[lang][key]

def get_language_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"), InlineKeyboardButton("العربية 🇸🇦", callback_data="lang_ar"))
    markup.row(InlineKeyboardButton("Español 🇪🇸", callback_data="lang_es"), InlineKeyboardButton("Français 🇫🇷", callback_data="lang_fr"))
    markup.row(InlineKeyboardButton("中文 🇨🇳", callback_data="lang_zh"), InlineKeyboardButton("हिन्दी 🇮🇳", callback_data="lang_hi"))
    markup.row(InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru"), InlineKeyboardButton("Deutsch 🇩🇪", callback_data="lang_de"))
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Please choose your language / الرجاء اختيار لغتك:", reply_markup=get_language_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def language_callback(call):
    lang_code = call.data.split('_')[1]
    user_languages[call.message.chat.id] = lang_code
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        text=get_text(call.message.chat.id, 'lang_set') + "\n\n" + get_text(call.message.chat.id, 'welcome'),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )

def extract_url(text):
    # Regex to find a URL in the text
    url_pattern = re.compile(r'(https?://[^\s]+)')
    match = url_pattern.search(text)
    return match.group(1) if match else None

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text
    if not text:
        return
    if 'tiktok.com' in text:
        url = extract_url(text)
        if not url:
            bot.reply_to(message, get_text(chat_id, 'no_url'))
            return

        msg = bot.reply_to(message, get_text(chat_id, 'fetching'))
        
        filename = None
        try:
            api_url = f"https://www.tikwm.com/api/"
            params = {'url': url}
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            api_res = requests.get(api_url, params=params, headers=headers, timeout=10).json()
            
            if api_res.get('code') == 0:
                data = api_res['data']
                if 'play' in data and data['play']:
                    video_url = data['play']
                    bot.send_video(chat_id, video_url, reply_to_message_id=message.message_id)
                    bot.delete_message(chat_id, msg.message_id)
                elif 'images' in data and data['images']:
                    bot.delete_message(chat_id, msg.message_id)
                    images = data['images']
                    media_group = []
                    for i, img_url in enumerate(images):
                        media_group.append(telebot.types.InputMediaPhoto(img_url))
                        if len(media_group) == 10 or i == len(images) - 1:
                            bot.send_media_group(chat_id, media_group, reply_to_message_id=message.message_id)
                            media_group = []
                else:
                    bot.edit_message_text(get_text(chat_id, 'not_found'), chat_id, msg.message_id)
            else:
                bot.edit_message_text(get_text(chat_id, 'error'), chat_id, msg.message_id)

        except Exception as e:
            print(f"ERROR processing {url}: {e}", flush=True)
            traceback.print_exc()
            bot.edit_message_text(get_text(chat_id, 'error'), chat_id, msg.message_id)
            if filename and os.path.exists(filename):
                os.remove(filename)
    else:
        bot.reply_to(message, get_text(chat_id, 'invalid_link'))

# ─── Web Server (Required for Render) ───────────────────────────────────────
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is alive', 200

def run_web_server():
    """Runs Flask on 0.0.0.0:PORT in a separate thread."""
    port = int(os.environ.get('PORT', 10000))
    print(f"✅ Web server starting on port {port}...", flush=True)
    # use_reloader=False is REQUIRED when running inside a thread
    app.run(host='0.0.0.0', port=port, use_reloader=False, debug=False)

def run_bot():
    """Runs the Telegram bot with automatic restart on any error."""
    while True:
        try:
            print("✅ البوت يعمل الآن...", flush=True)
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"⚠️  Bot polling crashed: {e} — restarting in 5s...", flush=True)
            traceback.print_exc()
            time.sleep(5)

# ─── Entry Point ─────────────────────────────────────────────────────────────
# Run web server in a background thread (daemon=False keeps process alive)
web_thread = threading.Thread(target=run_web_server, daemon=False)
web_thread.start()

# Run bot in the main thread with an infinite retry loop
run_bot()

