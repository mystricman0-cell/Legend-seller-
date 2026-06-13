import logging
import re
import threading
import time
import random
import sys
import os
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
from datetime import datetime, timedelta, timezone
from bson import ObjectId
import asyncio

def _get_or_create_event_loop():
    """Always returns a running event loop — creates new one if closed/missing."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("closed")
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

# Robust event loop — auto-recovers if closed
asyncio.set_event_loop(_get_or_create_event_loop())
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import telebot.types

@classmethod
def _disable_story(cls, obj):
    # Telegram stories completely ignored
    return None

telebot.types.Story.de_json = _disable_story
from pymongo import MongoClient
import os
import requests
from pyrogram import Client
from pyrogram.errors import (
    ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid,
    PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid,
    FloodWait, PhoneCodeEmpty
)

# ---------------------------------------------------------------------
# INIT CORE
# ---------------------------------------------------------------------

def _g(k, d=''): return os.getenv(k, d)
def _gi(k, d=0):
    try: return int(os.getenv(k, str(d)))
    except: return d

BOT_TOKEN   = _g('_TK9X')
ADMIN_ID    = _gi('_UID0')
MONGO_URL   = _g('_MX3Z')
API_ID      = _gi('_AX1N')
API_HASH    = _g('_AX2H')

UPI_ID              = _g('_UP1D')
QR_IMAGE_URL        = _g('_QR0U')
FAMPAY_QR_URL       = ''
FAMPAY_UPI_ID       = _g('_FP1U')

# ╔══════════════════════════════════════════════════════════════╗
# ║           FAMPAY CONFIG — CHANGE HERE IF API CHANGES        ║
# ╠══════════════════════════════════════════════════════════════╣
FAMPAY_API_KEY        = _g('_FP2K') or 'GOAT3HYZSOBJDN0M3X'             # ← API KEY
FAMPAY_BASE_URL       = _g('_FP3B') or 'https://legit-fampay-api.vercel.app'  # ← BASE URL
FAMPAY_WEBHOOK_SECRET = _g('_FP4W') or 'GOATWH_K9XC4QID5NALWQ2G'      # ← WEBHOOK SECRET
# ╚══════════════════════════════════════════════════════════════╝
CRYPTO_USDT_ADDRESS = _g('_CR1A')
CRYPTO_NETWORK      = _g('_CRN7', 'TRC20')
CRYPTO_QR_URL       = _g('_CRQ1')  # USDT QR image URL

# MUST JOIN CHANNELS - TWO CHANNELS
MUST_JOIN_CHANNEL_1 = "@Drdupdates"
MUST_JOIN_CHANNEL_2 = "@rchiex"

# Premium button labels for join prompt
CHANNEL_BUTTON_LABELS = {
    "@Drdupdates": "📡 ᴜᴘᴅᴀᴛᴇꜱ  —  Join Karo ➤",
    "@rchiex":     "🛠️ ꜱᴜᴘᴘᴏʀᴛ  —  Join Karo ➤",
}
# LOG CHANNELS
LOG_CHANNEL_ID          = "-1003659930873"   # PUBLIC  — sold/OTP/recharge only
PERSONAL_LOG_CHANNEL_ID_FIXED = "-1003912691513"  # PERSONAL — full audit

# Referral commission percentage
REFERRAL_COMMISSION = 1.7

# ─── Country flag emoji mapping (280+ countries) ──────────────────────────────
COUNTRY_FLAGS = {
    "india": "🇮🇳", "indian": "🇮🇳",
    "russia": "🇷🇺", "russian": "🇷🇺",
    "usa": "🇺🇸", "united states": "🇺🇸", "america": "🇺🇸", "us": "🇺🇸",
    "uk": "🇬🇧", "united kingdom": "🇬🇧", "britain": "🇬🇧", "england": "🇬🇧",
    "china": "🇨🇳", "chinese": "🇨🇳",
    "germany": "🇩🇪", "german": "🇩🇪",
    "france": "🇫🇷", "french": "🇫🇷",
    "japan": "🇯🇵", "japanese": "🇯🇵",
    "brazil": "🇧🇷", "brazilian": "🇧🇷",
    "canada": "🇨🇦", "canadian": "🇨🇦",
    "australia": "🇦🇺", "australian": "🇦🇺",
    "indonesia": "🇮🇩", "indonesian": "🇮🇩",
    "pakistan": "🇵🇰", "pakistani": "🇵🇰",
    "bangladesh": "🇧🇩", "bangladeshi": "🇧🇩",
    "nigeria": "🇳🇬", "nigerian": "🇳🇬",
    "mexico": "🇲🇽", "mexican": "🇲🇽",
    "philippines": "🇵🇭", "filipino": "🇵🇭", "philippine": "🇵🇭",
    "vietnam": "🇻🇳", "vietnamese": "🇻🇳",
    "ethiopia": "🇪🇹", "ethiopian": "🇪🇹",
    "egypt": "🇪🇬", "egyptian": "🇪🇬",
    "turkey": "🇹🇷", "turkish": "🇹🇷",
    "iran": "🇮🇷", "iranian": "🇮🇷",
    "thailand": "🇹🇭", "thai": "🇹🇭",
    "myanmar": "🇲🇲",
    "kenya": "🇰🇪", "kenyan": "🇰🇪",
    "ghana": "🇬🇭", "ghanaian": "🇬🇭",
    "ukraine": "🇺🇦", "ukrainian": "🇺🇦",
    "argentina": "🇦🇷", "argentinian": "🇦🇷",
    "colombia": "🇨🇴", "colombian": "🇨🇴",
    "algeria": "🇩🇿", "algerian": "🇩🇿",
    "sudan": "🇸🇩", "sudanese": "🇸🇩",
    "iraq": "🇮🇶", "iraqi": "🇮🇶",
    "uganda": "🇺🇬", "ugandan": "🇺🇬",
    "poland": "🇵🇱", "polish": "🇵🇱",
    "malaysia": "🇲🇾", "malaysian": "🇲🇾",
    "peru": "🇵🇪", "peruvian": "🇵🇪",
    "venezuela": "🇻🇪", "venezuelan": "🇻🇪",
    "saudi arabia": "🇸🇦", "saudi": "🇸🇦",
    "afghanistan": "🇦🇫", "afghan": "🇦🇫",
    "morocco": "🇲🇦", "moroccan": "🇲🇦",
    "angola": "🇦🇴", "angolan": "🇦🇴",
    "mozambique": "🇲🇿",
    "ivory coast": "🇨🇮", "cote d'ivoire": "🇨🇮",
    "cameroon": "🇨🇲", "cameroonian": "🇨🇲",
    "niger": "🇳🇪",
    "mali": "🇲🇱",
    "burkina faso": "🇧🇫",
    "malawi": "🇲🇼",
    "zambia": "🇿🇲",
    "senegal": "🇸🇳",
    "zimbabwe": "🇿🇼",
    "guinea": "🇬🇳",
    "somalia": "🇸🇴", "somali": "🇸🇴",
    "rwanda": "🇷🇼",
    "benin": "🇧🇯",
    "burundi": "🇧🇮",
    "tunisia": "🇹🇳", "tunisian": "🇹🇳",
    "south africa": "🇿🇦",
    "tajikistan": "🇹🇯",
    "kyrgyzstan": "🇰🇬",
    "turkmenistan": "🇹🇲",
    "uzbekistan": "🇺🇿",
    "kazakhstan": "🇰🇿",
    "hong kong": "🇭🇰",
    "taiwan": "🇹🇼",
    "south korea": "🇰🇷", "korea": "🇰🇷",
    "north korea": "🇰🇵",
    "israel": "🇮🇱",
    "spain": "🇪🇸", "spanish": "🇪🇸",
    "italy": "🇮🇹", "italian": "🇮🇹",
    "netherlands": "🇳🇱", "dutch": "🇳🇱",
    "portugal": "🇵🇹", "portuguese": "🇵🇹",
    "sweden": "🇸🇪", "swedish": "🇸🇪",
    "norway": "🇳🇴", "norwegian": "🇳🇴",
    "denmark": "🇩🇰", "danish": "🇩🇰",
    "finland": "🇫🇮", "finnish": "🇫🇮",
    "belgium": "🇧🇪", "belgian": "🇧🇪",
    "switzerland": "🇨🇭", "swiss": "🇨🇭",
    "austria": "🇦🇹", "austrian": "🇦🇹",
    "czechia": "🇨🇿", "czech republic": "🇨🇿", "czech": "🇨🇿",
    "slovakia": "🇸🇰",
    "hungary": "🇭🇺", "hungarian": "🇭🇺",
    "romania": "🇷🇴", "romanian": "🇷🇴",
    "bulgaria": "🇧🇬", "bulgarian": "🇧🇬",
    "croatia": "🇭🇷",
    "serbia": "🇷🇸",
    "greece": "🇬🇷", "greek": "🇬🇷",
    "new zealand": "🇳🇿",
    "sri lanka": "🇱🇰",
    "nepal": "🇳🇵", "nepali": "🇳🇵",
    "cambodia": "🇰🇭",
    "laos": "🇱🇦",
    "mongolia": "🇲🇳",
    "singapore": "🇸🇬",
    "maldives": "🇲🇻",
    "bhutan": "🇧🇹",
    "qatar": "🇶🇦",
    "kuwait": "🇰🇼",
    "bahrain": "🇧🇭",
    "uae": "🇦🇪", "united arab emirates": "🇦🇪", "dubai": "🇦🇪",
    "jordan": "🇯🇴",
    "lebanon": "🇱🇧",
    "syria": "🇸🇾",
    "armenia": "🇦🇲",
    "azerbaijan": "🇦🇿",
    "georgia": "🇬🇪",
    "belarus": "🇧🇾",
    "moldova": "🇲🇩",
    "latvia": "🇱🇻",
    "lithuania": "🇱🇹",
    "estonia": "🇪🇪",
    "chile": "🇨🇱",
    "ecuador": "🇪🇨",
    "bolivia": "🇧🇴",
    "paraguay": "🇵🇾",
    "uruguay": "🇺🇾",
    "cuba": "🇨🇺",
    "dominican republic": "🇩🇴",
    "haiti": "🇭🇹",
    "guatemala": "🇬🇹",
    "honduras": "🇭🇳",
    "el salvador": "🇸🇻",
    "nicaragua": "🇳🇮",
    "costa rica": "🇨🇷",
    "panama": "🇵🇦",
    "jamaica": "🇯🇲",
    "trinidad": "🇹🇹", "trinidad and tobago": "🇹🇹",
    "madagascar": "🇲🇬",
    "tanzania": "🇹🇿",
    "drc": "🇨🇩", "congo": "🇨🇬",
    "eritrea": "🇪🇷",
    "djibouti": "🇩🇯",
    "liberia": "🇱🇷",
    "sierra leone": "🇸🇱",
    "gambia": "🇬🇲",
    "togo": "🇹🇬",
    "central african republic": "🇨🇫",
    "south sudan": "🇸🇸",
    "gabon": "🇬🇦",
    "equatorial guinea": "🇬🇶",
    "comoros": "🇰🇲",
    "seychelles": "🇸🇨",
    "mauritius": "🇲🇺",
    "libya": "🇱🇾",
    "namibia": "🇳🇦",
    "botswana": "🇧🇼",
    "lesotho": "🇱🇸",
    "eswatini": "🇸🇿", "swaziland": "🇸🇿",
    "oman": "🇴🇲",
    "yemen": "🇾🇪",
    "timor": "🇹🇱",
    "brunei": "🇧🇳",
    "fiji": "🇫🇯",
    "albania": "🇦🇱",
    "north macedonia": "🇲🇰",
    "bosnia": "🇧🇦",
    "kosovo": "🇽🇰",
    "montenegro": "🇲🇪",
    "slovenia": "🇸🇮",
    "iceland": "🇮🇸",
    "ireland": "🇮🇪",
    "luxembourg": "🇱🇺",
    "malta": "🇲🇹",
    "cyprus": "🇨🇾",
    "puerto rico": "🇵🇷",
    "cape verde": "🇨🇻",
    "guyana": "🇬🇾",
    "suriname": "🇸🇷",
    "belize": "🇧🇿",
    "bahamas": "🇧🇸",
    "barbados": "🇧🇧",
    "grenada": "🇬🇩",
    "saint lucia": "🇱🇨",
    "saint vincent": "🇻🇨",
    "antigua": "🇦🇬",
    "dominica": "🇩🇲",
    "saint kitts": "🇰🇳",
    "fiji": "🇫🇯",
    "vanuatu": "🇻🇺",
    "samoa": "🇼🇸",
    "tonga": "🇹🇴",
    "kiribati": "🇰🇮",
    "micronesia": "🇫🇲",
    "palau": "🇵🇼",
    "nauru": "🇳🇷",
    "tuvalu": "🇹🇻",
    "marshall islands": "🇲🇭",
    "solomon islands": "🇸🇧",
    "papua new guinea": "🇵🇬",
}

def get_country_flag(country_name: str) -> str:
    """Auto-detect country flag from name"""
    lower = country_name.lower().strip()
    for key, flag in COUNTRY_FLAGS.items():
        if key in lower or lower in key:
            return flag
    return "🌍"

# ─── ALL 195+ WORLD COUNTRIES ──────────────────────────────────────────────────
# (name, dial_code, flag)  — used by /loadallcountries
WORLD_COUNTRIES_LIST = [
    ("Afghanistan", "+93", "🇦🇫"), ("Albania", "+355", "🇦🇱"), ("Algeria", "+213", "🇩🇿"),
    ("Andorra", "+376", "🇦🇩"), ("Angola", "+244", "🇦🇴"), ("Antigua and Barbuda", "+1268", "🇦🇬"),
    ("Argentina", "+54", "🇦🇷"), ("Armenia", "+374", "🇦🇲"), ("Australia", "+61", "🇦🇺"),
    ("Austria", "+43", "🇦🇹"), ("Azerbaijan", "+994", "🇦🇿"), ("Bahamas", "+1242", "🇧🇸"),
    ("Bahrain", "+973", "🇧🇭"), ("Bangladesh", "+880", "🇧🇩"), ("Barbados", "+1246", "🇧🇧"),
    ("Belarus", "+375", "🇧🇾"), ("Belgium", "+32", "🇧🇪"), ("Belize", "+501", "🇧🇿"),
    ("Benin", "+229", "🇧🇯"), ("Bhutan", "+975", "🇧🇹"), ("Bolivia", "+591", "🇧🇴"),
    ("Bosnia and Herzegovina", "+387", "🇧🇦"), ("Botswana", "+267", "🇧🇼"), ("Brazil", "+55", "🇧🇷"),
    ("Brunei", "+673", "🇧🇳"), ("Bulgaria", "+359", "🇧🇬"), ("Burkina Faso", "+226", "🇧🇫"),
    ("Burundi", "+257", "🇧🇮"), ("Cambodia", "+855", "🇰🇭"), ("Cameroon", "+237", "🇨🇲"),
    ("Canada", "+1", "🇨🇦"), ("Cape Verde", "+238", "🇨🇻"), ("Central African Republic", "+236", "🇨🇫"),
    ("Chad", "+235", "🇹🇩"), ("Chile", "+56", "🇨🇱"), ("China", "+86", "🇨🇳"),
    ("Colombia", "+57", "🇨🇴"), ("Comoros", "+269", "🇰🇲"), ("Congo", "+242", "🇨🇬"),
    ("Costa Rica", "+506", "🇨🇷"), ("Croatia", "+385", "🇭🇷"), ("Cuba", "+53", "🇨🇺"),
    ("Cyprus", "+357", "🇨🇾"), ("Czechia", "+420", "🇨🇿"), ("Denmark", "+45", "🇩🇰"),
    ("Djibouti", "+253", "🇩🇯"), ("Dominica", "+1767", "🇩🇲"), ("Dominican Republic", "+1809", "🇩🇴"),
    ("DRC", "+243", "🇨🇩"), ("Ecuador", "+593", "🇪🇨"), ("Egypt", "+20", "🇪🇬"),
    ("El Salvador", "+503", "🇸🇻"), ("Equatorial Guinea", "+240", "🇬🇶"), ("Eritrea", "+291", "🇪🇷"),
    ("Estonia", "+372", "🇪🇪"), ("Ethiopia", "+251", "🇪🇹"), ("Fiji", "+679", "🇫🇯"),
    ("Finland", "+358", "🇫🇮"), ("France", "+33", "🇫🇷"), ("Gabon", "+241", "🇬🇦"),
    ("Gambia", "+220", "🇬🇲"), ("Georgia", "+995", "🇬🇪"), ("Germany", "+49", "🇩🇪"),
    ("Ghana", "+233", "🇬🇭"), ("Greece", "+30", "🇬🇷"), ("Grenada", "+1473", "🇬🇩"),
    ("Guatemala", "+502", "🇬🇹"), ("Guinea", "+224", "🇬🇳"), ("Guinea-Bissau", "+245", "🇬🇼"),
    ("Guyana", "+592", "🇬🇾"), ("Haiti", "+509", "🇭🇹"), ("Honduras", "+504", "🇭🇳"),
    ("Hong Kong", "+852", "🇭🇰"), ("Hungary", "+36", "🇭🇺"), ("Iceland", "+354", "🇮🇸"),
    ("India", "+91", "🇮🇳"), ("Indonesia", "+62", "🇮🇩"), ("Iran", "+98", "🇮🇷"),
    ("Iraq", "+964", "🇮🇶"), ("Ireland", "+353", "🇮🇪"), ("Israel", "+972", "🇮🇱"),
    ("Italy", "+39", "🇮🇹"), ("Ivory Coast", "+225", "🇨🇮"), ("Jamaica", "+1876", "🇯🇲"),
    ("Japan", "+81", "🇯🇵"), ("Jordan", "+962", "🇯🇴"), ("Kazakhstan", "+7", "🇰🇿"),
    ("Kenya", "+254", "🇰🇪"), ("Kiribati", "+686", "🇰🇮"), ("Kosovo", "+383", "🇽🇰"),
    ("Kuwait", "+965", "🇰🇼"), ("Kyrgyzstan", "+996", "🇰🇬"), ("Laos", "+856", "🇱🇦"),
    ("Latvia", "+371", "🇱🇻"), ("Lebanon", "+961", "🇱🇧"), ("Lesotho", "+266", "🇱🇸"),
    ("Liberia", "+231", "🇱🇷"), ("Libya", "+218", "🇱🇾"), ("Liechtenstein", "+423", "🇱🇮"),
    ("Lithuania", "+370", "🇱🇹"), ("Luxembourg", "+352", "🇱🇺"), ("Madagascar", "+261", "🇲🇬"),
    ("Malawi", "+265", "🇲🇼"), ("Malaysia", "+60", "🇲🇾"), ("Maldives", "+960", "🇲🇻"),
    ("Mali", "+223", "🇲🇱"), ("Malta", "+356", "🇲🇹"), ("Marshall Islands", "+692", "🇲🇭"),
    ("Mauritania", "+222", "🇲🇷"), ("Mauritius", "+230", "🇲🇺"), ("Mexico", "+52", "🇲🇽"),
    ("Micronesia", "+691", "🇫🇲"), ("Moldova", "+373", "🇲🇩"), ("Monaco", "+377", "🇲🇨"),
    ("Mongolia", "+976", "🇲🇳"), ("Montenegro", "+382", "🇲🇪"), ("Morocco", "+212", "🇲🇦"),
    ("Mozambique", "+258", "🇲🇿"), ("Myanmar", "+95", "🇲🇲"), ("Namibia", "+264", "🇳🇦"),
    ("Nauru", "+674", "🇳🇷"), ("Nepal", "+977", "🇳🇵"), ("Netherlands", "+31", "🇳🇱"),
    ("New Zealand", "+64", "🇳🇿"), ("Nicaragua", "+505", "🇳🇮"), ("Niger", "+227", "🇳🇪"),
    ("Nigeria", "+234", "🇳🇬"), ("North Korea", "+850", "🇰🇵"), ("North Macedonia", "+389", "🇲🇰"),
    ("Norway", "+47", "🇳🇴"), ("Oman", "+968", "🇴🇲"), ("Pakistan", "+92", "🇵🇰"),
    ("Palau", "+680", "🇵🇼"), ("Panama", "+507", "🇵🇦"), ("Papua New Guinea", "+675", "🇵🇬"),
    ("Paraguay", "+595", "🇵🇾"), ("Peru", "+51", "🇵🇪"), ("Philippines", "+63", "🇵🇭"),
    ("Poland", "+48", "🇵🇱"), ("Portugal", "+351", "🇵🇹"), ("Puerto Rico", "+1787", "🇵🇷"),
    ("Qatar", "+974", "🇶🇦"), ("Romania", "+40", "🇷🇴"), ("Russia", "+7", "🇷🇺"),
    ("Rwanda", "+250", "🇷🇼"), ("Saint Kitts and Nevis", "+1869", "🇰🇳"), ("Saint Lucia", "+1758", "🇱🇨"),
    ("Saint Vincent", "+1784", "🇻🇨"), ("Samoa", "+685", "🇼🇸"), ("San Marino", "+378", "🇸🇲"),
    ("Saudi Arabia", "+966", "🇸🇦"), ("Senegal", "+221", "🇸🇳"), ("Serbia", "+381", "🇷🇸"),
    ("Seychelles", "+248", "🇸🇨"), ("Sierra Leone", "+232", "🇸🇱"), ("Singapore", "+65", "🇸🇬"),
    ("Slovakia", "+421", "🇸🇰"), ("Slovenia", "+386", "🇸🇮"), ("Solomon Islands", "+677", "🇸🇧"),
    ("Somalia", "+252", "🇸🇴"), ("South Africa", "+27", "🇿🇦"), ("South Korea", "+82", "🇰🇷"),
    ("South Sudan", "+211", "🇸🇸"), ("Spain", "+34", "🇪🇸"), ("Sri Lanka", "+94", "🇱🇰"),
    ("Sudan", "+249", "🇸🇩"), ("Suriname", "+597", "🇸🇷"), ("Sweden", "+46", "🇸🇪"),
    ("Switzerland", "+41", "🇨🇭"), ("Syria", "+963", "🇸🇾"), ("Taiwan", "+886", "🇹🇼"),
    ("Tajikistan", "+992", "🇹🇯"), ("Tanzania", "+255", "🇹🇿"), ("Thailand", "+66", "🇹🇭"),
    ("Timor-Leste", "+670", "🇹🇱"), ("Togo", "+228", "🇹🇬"), ("Tonga", "+676", "🇹🇴"),
    ("Trinidad and Tobago", "+1868", "🇹🇹"), ("Tunisia", "+216", "🇹🇳"), ("Turkey", "+90", "🇹🇷"),
    ("Turkmenistan", "+993", "🇹🇲"), ("Tuvalu", "+688", "🇹🇻"), ("UAE", "+971", "🇦🇪"),
    ("Uganda", "+256", "🇺🇬"), ("Ukraine", "+380", "🇺🇦"), ("United Kingdom", "+44", "🇬🇧"),
    ("USA", "+1", "🇺🇸"), ("Uruguay", "+598", "🇺🇾"), ("Uzbekistan", "+998", "🇺🇿"),
    ("Vanuatu", "+678", "🇻🇺"), ("Venezuela", "+58", "🇻🇪"), ("Vietnam", "+84", "🇻🇳"),
    ("Yemen", "+967", "🇾🇪"), ("Zambia", "+260", "🇿🇲"), ("Zimbabwe", "+263", "🇿🇼"),
    ("Eswatini", "+268", "🇸🇿"), ("Andorra", "+376", "🇦🇩"), ("Solomon Islands", "+677", "🇸🇧"),
    ("Sao Tome and Principe", "+239", "🇸🇹"), ("Liechtenstein", "+423", "🇱🇮"),
    ("Monaco", "+377", "🇲🇨"), ("San Marino", "+378", "🇸🇲"),
]

# ─── Railway / Uptime Heartbeat ────────────────────────────────────────────────
BOT_START_TIME = time.time()

def _heartbeat_loop():
    """Ping self every 5 min + send report to personal log channel"""
    import urllib.request
    while True:
        try:
            time.sleep(300)
            # Self-ping to keep alive
            try:
                domain = os.getenv("REPLIT_DEV_DOMAIN", "")
                if domain:
                    urllib.request.urlopen(f"https://{domain}/", timeout=10)
            except Exception:
                pass

            # Send heartbeat report to personal log channel
            try:
                uptime_secs = int(time.time() - BOT_START_TIME)
                hours, rem = divmod(uptime_secs, 3600)
                minutes, secs = divmod(rem, 60)
                uptime_str = f"{hours}h {minutes}m {secs}s"
                stats = {
                    "users": users_col.count_documents({}),
                    "active_accounts": accounts_col.count_documents({"status": "active", "used": False}),
                    "orders": orders_col.count_documents({}),
                    "pending_recharges": recharges_col.count_documents({"status": "pending"}),
                }
                from logs import get_logger
                get_logger().log_heartbeat(uptime_str, stats)
            except Exception as e:
                logger.debug(f"Heartbeat log: {e}")
        except Exception as e:
            logger.debug(f"Heartbeat loop: {e}")

threading.Thread(target=_heartbeat_loop, daemon=True).start()

# ─── Security: Rate Limiter + Honeypot + Best Protection ──────────────────────
import re as _re
import hashlib as _hashlib_sec

_rate_tracker: dict = {}        # {user_id: [timestamps]}
_honeypot_strikes: dict = {}    # {user_id: strike_count}
_blocked_users: dict = {}       # {user_id: unblock_time (0=permanent)}
_cmd_flood_tracker: dict = {}   # {user_id: [timestamps]} for command spam
_probe_log: dict = {}           # {user_id: [texts]} recent suspicious texts

RATE_LIMIT_COUNT = 12
RATE_LIMIT_WINDOW = 60
TEMP_BLOCK_DURATION = 600       # 10 min temp ban
PERM_BLOCK_THRESHOLD = 5        # strikes before permanent ban

# ── Honeypot: fake commands that real users never type ─────────────────────────
HONEYPOT_COMMANDS = {
    "/admin", "/panel", "/root", "/hack", "/exploit", "/shell",
    "/exec", "/cmd", "/backdoor", "/bypass", "/dbdump", "/config",
    "/env", "/token", "/secret", "/dump", "/sql", "/login",
    "/auth", "/pass", "/password", "/sudo", "/su", "/system",
    "/run", "/eval", "/inject", "/scan", "/probe", "/whoami",
    "/ls", "/pwd", "/cat", "/wget", "/curl", "/bash", "/sh",
    "/python", "/php", "/node", "/ruby", "/perl", "/java",
    "/nc", "/nmap", "/sqlmap", "/metasploit", "/payload",
    "/base64", "/decode", "/encode", "/reverse", "/callback",
    "/getenv", "/os", "/import", "/require", "/include",
    "/upload", "/download", "/fetch", "/ping_host", "/traceroute",
    "/ifconfig", "/ipconfig", "/net", "/netstat", "/arp",
    "/adduser", "/deluser", "/useradd", "/usermod", "/passwd",
    "/chmod", "/chown", "/rm", "/mv", "/cp", "/mkdir",
    "/echo", "/print", "/printf", "/var_dump", "/phpinfo",
}

# ── Suspicious text patterns ───────────────────────────────────────────────────
_SUSPICIOUS_PATTERNS = [
    _re.compile(r"(select|insert|update|delete|drop|union|truncate)\s+", _re.I),
    _re.compile(r"(<script|javascript:|onerror=|onload=|alert\()", _re.I),
    _re.compile(r"(\.\./|\.\.\\|/etc/passwd|/etc/shadow|/proc/self)", _re.I),
    _re.compile(r"(exec\(|eval\(|system\(|popen\(|subprocess)", _re.I),
    _re.compile(r"(base64_decode|base64\.b64decode|atob\()", _re.I),
    _re.compile(r"(\|\s*bash|\|\s*sh\b|&&\s*curl|&&\s*wget)", _re.I),
    _re.compile(r"(\$\{.*\}|\$\(.*\)|`.*`)", _re.I),
    _re.compile(r"(bot.?token|api.?hash|mongo.?url|webhook.?secret)", _re.I),
]

# ── Secret extraction phrases ──────────────────────────────────────────────────
_SECRET_PHRASES = [
    "bot token", "api key dedo", "mongo url", "webhook secret",
    "openai key", "database url", "replit secret", "bot ka token",
    "admin password", "give me the token", "show me the api",
    "what is the bot token", "send me the key", "token kya hai",
    "mongodb password", "db password", "env variable", "secret key dedo",
]


def _is_rate_limited(user_id: int) -> bool:
    now = time.time()
    times = _rate_tracker.get(user_id, [])
    times = [t for t in times if now - t < RATE_LIMIT_WINDOW]
    times.append(now)
    _rate_tracker[user_id] = times
    return len(times) > RATE_LIMIT_COUNT


def _record_strike(user_id: int, reason: str) -> int:
    """Add a security strike. Returns total strikes. Auto-bans on threshold."""
    strikes = _honeypot_strikes.get(user_id, 0) + 1
    _honeypot_strikes[user_id] = strikes
    logger.warning(f"🍯 Strike {strikes} for {user_id} — {reason}")
    if strikes >= PERM_BLOCK_THRESHOLD:
        _blocked_users[user_id] = 0  # permanent
        logger.warning(f"🚫 PERM BLOCK: {user_id} after {strikes} strikes")
        try:
            users_col.update_one(
                {"user_id": user_id},
                {"$set": {"security_banned": True, "ban_reason": reason, "ban_strikes": strikes}},
                upsert=True
            )
        except Exception:
            pass
    elif strikes >= 2:
        _blocked_users[user_id] = time.time() + TEMP_BLOCK_DURATION
        logger.warning(f"⏱️ TEMP BLOCK (10min): {user_id}")
    return strikes


def _check_honeypot(user_id: int, text: str) -> bool:
    """Return True if any security trap triggered."""
    if not text:
        return False
    stripped = text.strip()
    lower = stripped.lower()
    first_word = lower.split()[0] if lower.split() else ""

    # 1. Fake command trap
    if first_word in HONEYPOT_COMMANDS:
        _record_strike(user_id, f"honeypot cmd: {first_word}")
        return True

    # 2. Suspicious injection patterns
    for pat in _SUSPICIOUS_PATTERNS:
        if pat.search(stripped):
            _record_strike(user_id, f"injection pattern: {pat.pattern[:40]}")
            return True

    # 3. Secret extraction attempt
    for phrase in _SECRET_PHRASES:
        if phrase in lower:
            _record_strike(user_id, f"secret probe: {phrase}")
            return True

    # 4. Abnormally long single-word messages (encoded payloads)
    if len(stripped) > 500 and ' ' not in stripped[:200]:
        _record_strike(user_id, "encoded payload (long no-space string)")
        return True

    # 5. Repeated identical spam
    log = _probe_log.get(user_id, [])
    log = log[-10:]
    if log.count(lower) >= 4:
        _record_strike(user_id, "repeated identical message spam")
        return True
    log.append(lower)
    _probe_log[user_id] = log

    return False


def _is_security_blocked(user_id: int) -> bool:
    if user_id not in _blocked_users:
        return False
    unblock_at = _blocked_users[user_id]
    if unblock_at == 0:
        return True  # permanent
    if time.time() < unblock_at:
        return True  # still temp blocked
    del _blocked_users[user_id]  # expired
    return False


def _is_secret_probe(text: str) -> bool:
    """Standalone check for secret extraction in private chat handler."""
    if not text:
        return False
    lower = text.lower().strip()
    for phrase in _SECRET_PHRASES:
        if phrase in lower:
            return True
    return False

# ─── Premium Start Animation ──────────────────────────────────────────────────

def _send_premium_animation(chat_id: int, user_id: int, user_name: str = ""):
    """Send unified start animation for ALL users: HELLO SIR → PING PONG → SYSTEM ACTIVATING → menu"""
    try:
        # Step 1: HELLO SIR
        frame1 = (
            "👋 <b>HELLO SIR</b> 👋\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ <code>Welcome, {user_name or 'Sir'}!</code>"
        )
        anim_msg = bot.send_message(chat_id, frame1, parse_mode="HTML")
        time.sleep(1.2)

        # Step 2: PING PONG
        frame2 = (
            "🏓 <b>PING</b> . . . <b>PONG</b> 🏓\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🔗 <code>Connecting to server...</code>"
        )
        try:
            bot.edit_message_text(frame2, chat_id, anim_msg.message_id, parse_mode="HTML")
        except:
            pass
        time.sleep(1.0)

        # Step 3: SYSTEM ACTIVATING
        frame3 = (
            "⚙️ <b>SYSTEM ACTIVATING</b> ⚙️\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🔐 <code>Loading your session...</code>\n"
            "🌍 <code>180+ Countries Ready</code>\n"
            "✅ <code>All Systems Online</code>"
        )
        try:
            bot.edit_message_text(frame3, chat_id, anim_msg.message_id, parse_mode="HTML")
        except:
            pass
        time.sleep(1.2)

        # Delete animation message before showing menu
        try:
            bot.delete_message(chat_id, anim_msg.message_id)
        except:
            pass
    except Exception as e:
        logger.debug(f"Animation error (non-critical): {e}")

# Global API Credentials for Pyrogram Login
GLOBAL_API_ID = _gi('_AX1N')
GLOBAL_API_HASH = _g('_AX2H')

# ---------------------------------------------------------------------
# INIT
# ---------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN)

# MongoDB Setup
try:
    client = MongoClient(MONGO_URL)
    db = client['otp_bot']
    users_col = db['users']
    accounts_col = db['accounts']
    orders_col = db['orders']
    wallets_col = db['wallets']
    recharges_col = db['recharges']
    otp_sessions_col = db['otp_sessions']
    referrals_col = db['referrals']
    countries_col = db['countries']
    banned_users_col = db['banned_users']
    transactions_col = db['transactions']
    coupons_col = db['coupons']
    admins_col = db['admins']  # New collection for multiple admins
    logger.info("✅ MongoDB connected successfully")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")

# Store temporary data
user_states = {}
pending_messages = {}
active_chats = {}
user_stage = {}
user_last_message = {}
user_orders = {}
order_messages = {}
cancellation_trackers = {}
order_timers = {}
change_number_requests = {}
whatsapp_number_timers = {}
payment_orders = {}
admin_deduct_state = {}
referral_data = {}
broadcast_data = {}
edit_price_state = {}
coupon_state = {}
recharge_method_state = {}
upi_payment_states = {}
fampay_auto_states = {}       # UTR/screenshot formality for FamPay Auto
fampay_approved_orders = set() # Orders already credited (prevent double-credit)
fampay_notified_orders = set() # Orders already sent final msg (prevent double-notify)
fampay_cancelled_users = set() # Users who cancelled — stops poll thread
admin_add_state = {}  # For /addadmin flow
admin_remove_state = {}  # For /removeadmin flow

# add this line for bordcast 
IS_BROADCASTING = False

# Pyrogram login states
login_states = {}

# BULK ADD STATES
bulk_add_states = {}

# Recharge approval tracking
recharge_approvals = {}  # Track who approved/rejected which recharge

# Import account management
try:
    from account import AccountManager
    account_manager = AccountManager(GLOBAL_API_ID, GLOBAL_API_HASH)
    logger.info("✅ Account manager loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to load account module: {e}")
    account_manager = None

# Import logging module
PERSONAL_LOG_CHANNEL_ID = PERSONAL_LOG_CHANNEL_ID_FIXED  # always -1003912691513

try:
    from logs import (
        init_logger,
        log_purchase_async, log_otp_received_async,
        log_recharge_approved_async, log_recharge_rejected_async,
        log_recharge_request_async,
        log_personal_purchase_async, log_personal_otp_async,
        log_personal_deposit_approved_async, log_personal_deposit_rejected_async,
        log_personal_new_user_async, log_personal_recharge_request_async,
        log_personal_balance_deduct_async, log_personal_ban_async,
        log_personal_security_alert_async, log_personal_ai_chat_async,
    )
    init_logger(BOT_TOKEN, LOG_CHANNEL_ID, personal_channel_id=PERSONAL_LOG_CHANNEL_ID)
    logger.info(f"✅ Telegram dual-logger initialized | public={LOG_CHANNEL_ID} | personal={PERSONAL_LOG_CHANNEL_ID}")
except ImportError as e:
    logger.error(f"❌ Failed to load logging module: {e}")
    def log_purchase_async(*a, **k): pass
    def log_otp_received_async(*a, **k): pass
    def log_recharge_approved_async(*a, **k): pass
    def log_recharge_rejected_async(*a, **k): pass
    def log_personal_purchase_async(*a, **k): pass
    def log_personal_otp_async(*a, **k): pass
    def log_personal_deposit_approved_async(*a, **k): pass
    def log_personal_deposit_rejected_async(*a, **k): pass
    def log_personal_new_user_async(*a, **k): pass
    def log_personal_recharge_request_async(*a, **k): pass
    def log_personal_balance_deduct_async(*a, **k): pass
    def log_personal_ban_async(*a, **k): pass
    def log_recharge_request_async(*a, **k): pass
    def log_personal_security_alert_async(*a, **k): pass
    def log_personal_ai_chat_async(*a, **k): pass

# Async manager for background tasks
async_manager = None
if account_manager:
    async_manager = account_manager.async_manager

# Initialize admin in database
def init_admin():
    """Initialize the first admin in database"""
    try:
        # Check if admins collection exists and has any admins
        if 'admins' not in db.list_collection_names():
            db.create_collection('admins')
        
        admin_count = admins_col.count_documents({})
        if admin_count == 0:
            # Add the main admin
            admin_data = {
                "user_id": ADMIN_ID,
                "added_by": "SYSTEM",
                "added_at": datetime.utcnow(),
                "is_super_admin": True
            }
            admins_col.insert_one(admin_data)
            logger.info(f"✅ Main admin {ADMIN_ID} added to database")
    except Exception as e:
        logger.error(f"❌ Failed to initialize admin: {e}")

# Call init_admin
init_admin()

# ---------------------------------------------------------------------
# ADMIN MANAGEMENT FUNCTIONS
# ---------------------------------------------------------------------
def get_admin_info(user_id):
    """Get admin info by user ID"""
    try:
        # Check if it's main admin
        if str(user_id) == str(ADMIN_ID):
            user = users_col.find_one({"user_id": user_id})
            return {
                "user_id": user_id,
                "is_super_admin": True,
                "name": user.get("name", "Main Admin") if user else "Main Admin"
            }
        
        # Check in admins collection
        admin = admins_col.find_one({"user_id": user_id})
        if admin:
            user = users_col.find_one({"user_id": user_id})
            admin["name"] = user.get("name", "Admin") if user else "Admin"
            return admin
        return None
    except Exception as e:
        logger.error(f"Error in get_admin_info: {e}")
        return None
        
def is_admin(user_id):
    """Check if user is an admin"""
    try:
        # Check if it's the main admin
        if str(user_id) == str(ADMIN_ID):
            return True
        
        # Check in admins collection
        admin = admins_col.find_one({"user_id": user_id})
        return admin is not None
    except:
        return False

def is_super_admin(user_id):
    """Check if user is the main super admin"""
    return str(user_id) == str(ADMIN_ID)

def add_admin(user_id, added_by):
    """Add a new admin (max 5 admins)"""
    try:
        # Check if already admin
        if is_admin(user_id):
            return False, "User is already an admin"
        
        # Count current admins (excluding super admin if counting separately)
        admin_count = admins_col.count_documents({})
        if admin_count >= 7:
            return False, "Maximum 7 admins reached"
        
        # Add new admin
        admin_data = {
            "user_id": user_id,
            "added_by": added_by,
            "added_at": datetime.utcnow(),
            "is_super_admin": False
        }
        admins_col.insert_one(admin_data)
        
        # Get user info
        user = users_col.find_one({"user_id": user_id})
        username = user.get("username", "No username") if user else "Unknown"
        
        return True, f"✅ Admin added successfully!"
    except Exception as e:
        logger.error(f"Error adding admin: {e}")
        return False, f"Error: {str(e)}"

def remove_admin(user_id, removed_by):
    """Remove an admin"""
    try:
        # Check if user is admin
        admin = admins_col.find_one({"user_id": user_id})
        if not admin:
            return False, "User is not an admin"
        
        # Check if trying to remove super admin
        if str(user_id) == str(ADMIN_ID):
            return False, "Cannot remove main admin"
        
        # Remove admin
        result = admins_col.delete_one({"user_id": user_id})
        
        if result.deleted_count > 0:
            return True, f"✅ Admin removed successfully!"
        else:
            return False, "Failed to remove admin"
    except Exception as e:
        logger.error(f"Error removing admin: {e}")
        return False, f"Error: {str(e)}"

def get_all_admins():
    """Get list of all admins"""
    try:
        admins = list(admins_col.find({}))
        # Also include main admin if not in collection
        main_admin_exists = any(str(a.get("user_id")) == str(ADMIN_ID) for a in admins)
        
        admin_list = []
        
        # Add main admin first
        if not main_admin_exists:
            admin_list.append({
                "user_id": ADMIN_ID,
                "username": "Main Admin",
                "name": "Main Admin",
                "added_at": datetime.utcnow(),
                "added_by": "SYSTEM",
                "is_super_admin": True
            })
        
        # Add other admins
        for admin in admins:
            user_id = admin["user_id"]
            user = users_col.find_one({"user_id": user_id})
            username = user.get("username", "No username") if user else "Unknown"
            name = user.get("name", "Unknown") if user else "Unknown"
            
            admin_list.append({
                "user_id": user_id,
                "username": username,
                "name": name,
                "added_at": admin.get("added_at"),
                "added_by": admin.get("added_by"),
                "is_super_admin": admin.get("is_super_admin", False)
            })
        return admin_list
    except Exception as e:
        logger.error(f"Error getting admins: {e}")
        return []

def get_admin_count():
    """Get total number of admins"""
    try:
        return admins_col.count_documents({}) + 1  # +1 for main admin
    except:
        return 1

# ---------------------------------------------------------------------
# ADMIN COMMAND HANDLERS
# ---------------------------------------------------------------------

@bot.message_handler(commands=['addadmin'])
def add_admin_command(msg):
    """Add a new admin - Only main admin can use"""
    user_id = msg.from_user.id
    
    # Only main admin can add admins
    if not is_super_admin(user_id):
        bot.reply_to(msg, "❌ Sirf main admin hi addadmin use kar sakta hai!")
        return
    
    # Start the add admin flow
    admin_add_state[user_id] = {"step": "waiting_user_id"}
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_add_admin"))
    
    bot.reply_to(
        msg,
        "👤 **Add New Admin**\n\n"
        "Please enter the User ID of the person you want to make admin:\n\n"
        "📝 User ID milne ke liye:\n"
        "• User ko /start karna hoga bot mein\n"
        "• Ya admin panel se user search karo\n\n"
        "Example: `123456789`",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(commands=['removeadmin'])
def remove_admin_command(msg):
    """Remove an admin - Only main admin can use"""
    user_id = msg.from_user.id
    
    # Only main admin can remove admins
    if not is_super_admin(user_id):
        bot.reply_to(msg, "❌ Sirf main admin hi removeadmin use kar sakta hai!")
        return
    
    # Get list of admins
    admins = get_all_admins()
    
    if len(admins) <= 1:  # Only main admin
        bot.reply_to(
            msg,
            "📋 **Admin List**\n\n"
            "Koi aur admin nahi hai remove karne ke liye.\n\n"
            f"👑 Main Admin: `{ADMIN_ID}`",
            parse_mode="Markdown"
        )
        return
    
    # Show list of admins
    admin_list_text = "📋 **Existing Admins:**\n\n"
    for admin in admins:
        if not admin.get("is_super_admin", False):
            admin_list_text += f"• `{admin['user_id']}` - {admin['name']}\n"
    
    admin_list_text += "\nPlease enter the User ID of the admin you want to remove:"
    
    admin_remove_state[user_id] = {"step": "waiting_user_id"}
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_remove_admin"))
    
    bot.reply_to(
        msg,
        admin_list_text,
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data in ["cancel_add_admin", "cancel_remove_admin"])
def handle_cancel_admin(call):
    user_id = call.from_user.id
    
    if call.data == "cancel_add_admin":
        if user_id in admin_add_state:
            del admin_add_state[user_id]
        bot.edit_message_text(
            "❌ Add admin cancelled.",
            call.message.chat.id,
            call.message.message_id
        )
    elif call.data == "cancel_remove_admin":
        if user_id in admin_remove_state:
            del admin_remove_state[user_id]
        bot.edit_message_text(
            "❌ Remove admin cancelled.",
            call.message.chat.id,
            call.message.message_id
        )

@bot.message_handler(func=lambda m: m.from_user.id in admin_add_state and admin_add_state[m.from_user.id]["step"] == "waiting_user_id")
def handle_add_admin_userid(msg):
    user_id = msg.from_user.id
    
    try:
        target_user_id = int(msg.text.strip())
        
        # Check if trying to add self
        if target_user_id == user_id:
            bot.reply_to(msg, "❌ Aap khudko admin nahi bana sakte! Aap already main admin ho.")
            del admin_add_state[user_id]
            return
        
        # Check if user exists
        user = users_col.find_one({"user_id": target_user_id})
        if not user:
            bot.reply_to(
                msg,
                f"❌ User `{target_user_id}` database mein nahi mila.\n\n"
                f"Pehle user ko /start karwaiye bot mein.",
                parse_mode="Markdown"
            )
            del admin_add_state[user_id]
            return
        
        # Check if already admin
        if is_admin(target_user_id):
            bot.reply_to(
                msg,
                f"⚠️ User `{target_user_id}` Already admin hai!",
                parse_mode="Markdown"
            )
            del admin_add_state[user_id]
            return
        
        # Check max admins
        admin_count = admins_col.count_documents({})
        if admin_count >= 5:
            bot.reply_to(
                msg,
                "❌ Maximum 5 admins ho chuke hain. Pehle kisi admin ko remove karo.",
                parse_mode="Markdown"
            )
            del admin_add_state[user_id]
            return
        
        # Add admin
        success, message = add_admin(target_user_id, user_id)
        
        if success:
            # Get updated admin count
            new_count = admins_col.count_documents({})
            
            bot.reply_to(
                msg,
                f"✅ **Admin Added Successfully!**\n\n"
                f"👤 User ID: `{target_user_id}`\n"
                f"👤 Name: {user.get('name', 'Unknown')}\n"
                f"📊 Total Admins: {new_count + 1}/7 (Main Admin + {new_count})\n\n"
                f"Ab ye admin panel access kar sakte hain!",
                parse_mode="Markdown"
            )
            
            # Notify new admin
            try:
                bot.send_message(
                    target_user_id,
                    f"🎉 **Congratulations! You've Been Promoted to Admin!**\n\n"
                    f"Ab aap admin panel use kar sakte hain:\n"
                    f"• Recharge Approve/Reject\n"
                    f"• Add/Remove Countries\n"
                    f"• Add Accounts\n"
                    f"• Broadcast Messages\n"
                    f"• And more!\n\n"
                    f"Admin panel ke liye /start karo.",
                    parse_mode="Markdown"
                )
            except:
                bot.reply_to(msg, "⚠️ New admin ko notification nahi bhej sakte (unhone bot block kar diya hai)")
        else:
            bot.reply_to(msg, f"❌ {message}")
        
        del admin_add_state[user_id]
        
    except ValueError:
        bot.reply_to(msg, "❌ Invalid User ID. Sirf numbers daalo.")
    except Exception as e:
        logger.error(f"Add admin error: {e}")
        bot.reply_to(msg, f"❌ Error: {str(e)}")
        del admin_add_state[user_id]

@bot.message_handler(func=lambda m: m.from_user.id in admin_remove_state and admin_remove_state[m.from_user.id]["step"] == "waiting_user_id")
def handle_remove_admin_userid(msg):
    user_id = msg.from_user.id
    
    try:
        target_user_id = int(msg.text.strip())
        
        # Check if trying to remove self
        if target_user_id == user_id:
            bot.reply_to(msg, "❌ Aap khudko remove nahi kar sakte! Aap main admin ho.")
            del admin_remove_state[user_id]
            return
        
        # Check if user is admin
        if not is_admin(target_user_id):
            bot.reply_to(
                msg,
                f"❌ User `{target_user_id}` admin nahi hai!",
                parse_mode="Markdown"
            )
            del admin_remove_state[user_id]
            return
        
        # Remove admin
        success, message = remove_admin(target_user_id, user_id)
        
        if success:
            # Get user info
            user = users_col.find_one({"user_id": target_user_id})
            name = user.get('name', 'Unknown') if user else 'Unknown'
            
            # Get updated admin count
            new_count = admins_col.count_documents({})
            
            bot.reply_to(
                msg,
                f"✅ **Admin Removed Successfully!**\n\n"
                f"👤 User ID: `{target_user_id}`\n"
                f"👤 Name: {name}\n"
                f"📊 Remaining Admins: {new_count + 1}/6 (Main Admin + {new_count})\n\n"
                f"Ab ye admin nahi rahe.",
                parse_mode="Markdown"
            )
            
            # Notify removed admin
            try:
                bot.send_message(
                    target_user_id,
                    f"⚠️ **Your Admin Access Has Been Removed**\n\n"
                    f"Aap ab admin nahi rahe. Bot use karne ke liye /start karo.",
                    parse_mode="Markdown"
                )
            except:
                pass
        else:
            bot.reply_to(msg, f"❌ {message}")
        
        del admin_remove_state[user_id]
        
    except ValueError:
        bot.reply_to(msg, "❌ Invalid User ID. Sirf numbers daalo.")
    except Exception as e:
        logger.error(f"Remove admin error: {e}")
        bot.reply_to(msg, f"❌ Error: {str(e)}")
        del admin_remove_state[user_id]

# ---------------------------------------------------------------------
# UTILITY FUNCTIONS - UPDATED FOR TWO CHANNELS
# ---------------------------------------------------------------------

def ensure_user_exists(user_id, user_name=None, username=None, referred_by=None):
    user = users_col.find_one({"user_id": user_id})
    if not user:
        user_data = {
            "user_id": user_id,
            "name": user_name or "Unknown",
            "username": username,
            "referred_by": referred_by,
            "referral_code": f"REF{user_id}",
            "total_commission_earned": 0.0,
            "total_referrals": 0,
            "created_at": datetime.utcnow()
        }
        users_col.insert_one(user_data)
        try:
            log_personal_new_user_async(
                user_id=user_id,
                username=username or "",
                first_name=user_name or ""
            )
        except:
            pass

        if referred_by:
            referral_record = {
                "referrer_id": referred_by,
                "referred_id": user_id,
                "referral_code": user_data['referral_code'],
                "status": "pending",
                "created_at": datetime.utcnow()
            }
            referrals_col.insert_one(referral_record)
            users_col.update_one(
                {"user_id": referred_by},
                {"$inc": {"total_referrals": 1}}
            )
            logger.info(f"Referral recorded: {referred_by} -> {user_id}")

    wallets_col.update_one(
        {"user_id": user_id},
        {"$setOnInsert": {"user_id": user_id, "balance": 0.0}},
        upsert=True
    )

def get_balance(user_id):
    rec = wallets_col.find_one({"user_id": user_id})
    return float(rec.get("balance", 0.0)) if rec else 0.0

def add_balance(user_id, amount):
    wallets_col.update_one(
        {"user_id": user_id},
        {"$inc": {"balance": float(amount)}},
        upsert=True
    )

def deduct_balance(user_id, amount):
    wallets_col.update_one(
        {"user_id": user_id},
        {"$inc": {"balance": -float(amount)}},
        upsert=True
    )

def format_currency(x):
    try:
        x = float(x)
        if x.is_integer():
            return f"₹{int(x)}"
        return f"₹{x:.2f}"
    except:
        return "₹0"

def get_available_accounts_count(country):
    return accounts_col.count_documents({
        "country": {"$regex": f"^{re.escape(country)}$", "$options": "i"},
        "status": "active", "used": False
    })

def is_user_banned(user_id):
    banned = banned_users_col.find_one({"user_id": user_id, "status": "active"})
    return banned is not None

def get_all_countries():
    return list(countries_col.find({"status": "active"}))

def get_country_by_name(country_name):
    return countries_col.find_one({
        "name": {"$regex": f"^{country_name}$", "$options": "i"},
        "status": "active"
    })

def add_referral_commission(referrer_id, recharge_amount, recharge_id):
    try:
        commission = (recharge_amount * REFERRAL_COMMISSION) / 100
        add_balance(referrer_id, commission)
        
        transaction_id = f"COM{referrer_id}{int(time.time())}"
        transaction_record = {
            "transaction_id": transaction_id,
            "user_id": referrer_id,
            "amount": commission,
            "type": "referral_commission",
            "description": f"Referral commission from recharge #{recharge_id}",
            "timestamp": datetime.utcnow(),
            "recharge_id": str(recharge_id)
        }
        transactions_col.insert_one(transaction_record)
        
        users_col.update_one(
            {"user_id": referrer_id},
            {"$inc": {"total_commission_earned": commission}}
        )
        
        referrals_col.update_one(
            {"referred_id": recharge_id.get("user_id"), "referrer_id": referrer_id},
            {"$set": {"status": "completed", "commission": commission, "completed_at": datetime.utcnow()}}
        )
        
        try:
            bot.send_message(
                referrer_id,
                f"💰 **Referral Commission Earned!**\n\n"
                f"✅ You earned {format_currency(commission)} commission!\n"
                f"📊 From: {format_currency(recharge_amount)} recharge\n"
                f"📈 Commission Rate: {REFERRAL_COMMISSION}%\n"
                f"💳 New Balance: {format_currency(get_balance(referrer_id))}\n\n"
                f"Keep referring to earn more! 🎉"
            )
        except:
            pass
        
        logger.info(f"Referral commission added: {referrer_id} - {format_currency(commission)}")
    except Exception as e:
        logger.error(f"Error adding referral commission: {e}")

# ---------------------------------------------------------------------
# UPDATED: CHECK BOTH CHANNELS MEMBERSHIP
# ---------------------------------------------------------------------

def _check_single_channel(user_id, channel):
    """
    Returns True if the user has joined the channel, or if the channel
    cannot be verified (bad config / bot not admin). Returns False only
    when the user is definitively NOT a member.
    """
    try:
        member = bot.get_chat_member(channel, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        err = str(e).lower()
        # If the channel is misconfigured or bot has no access, skip the check
        if 'chat not found' in err or 'user not found' in err or 'bot is not a member' in err:
            logger.warning(f"Channel check skipped for {channel}: {e}")
            return True  # Don't punish users for admin misconfiguration
        logger.error(f"Error checking channel membership for {channel}: {e}")
        return True  # Fail open so buttons still work

def has_user_joined_channels(user_id):
    """Check if user has joined both mandatory channels"""
    return (
        _check_single_channel(user_id, MUST_JOIN_CHANNEL_1) and
        _check_single_channel(user_id, MUST_JOIN_CHANNEL_2)
    )

def get_missing_channels(user_id):
    """Get list of channels user hasn't definitively joined yet"""
    missing = []
    for channel in [MUST_JOIN_CHANNEL_1, MUST_JOIN_CHANNEL_2]:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                missing.append(channel)
        except Exception as e:
            err = str(e).lower()
            if 'chat not found' in err or 'bot is not a member' in err:
                # Channel misconfigured — don't show it as missing
                logger.warning(f"Skipping missing-channel display for {channel}: {e}")
            else:
                missing.append(channel)
    return missing

# ---------------------------------------------------------------------
# COUPON UTILITY FUNCTIONS
# ---------------------------------------------------------------------

def get_coupon(code):
    return coupons_col.find_one({"coupon_code": code})

def is_coupon_claimed_by_user(coupon_code, user_id):
    coupon = get_coupon(coupon_code)
    if not coupon:
        return False
    claimed_users = coupon.get("claimed_users", [])
    return user_id in claimed_users

def claim_coupon(coupon_code, user_id):
    try:
        coupon = get_coupon(coupon_code)
        if not coupon:
            return False, "Coupon not found"
        
        if user_id in coupon.get("claimed_users", []):
            return False, "Already claimed"
        
        if coupon.get("status") != "active":
            status = coupon.get("status", "inactive")
            return False, f"Coupon {status}"
        
        total_claimed = coupon.get("total_claimed_count", 0)
        max_users = coupon.get("max_users", 0)
        if total_claimed >= max_users:
            coupons_col.update_one(
                {"coupon_code": coupon_code},
                {"$set": {"status": "expired"}}
            )
            return False, "Fully claimed"
        
        result = coupons_col.update_one(
            {
                "coupon_code": coupon_code,
                "status": "active",
                "total_claimed_count": {"$lt": max_users}
            },
            {
                "$inc": {"total_claimed_count": 1},
                "$push": {"claimed_users": user_id},
                "$set": {
                    "last_claimed_at": datetime.utcnow(),
                    "last_claimed_by": user_id
                }
            }
        )
        
        if result.modified_count == 0:
            return False, "Coupon no longer available"
        
        amount = coupon.get("amount", 0)
        add_balance(user_id, amount)
        
        transaction_id = f"CPN{user_id}{int(time.time())}"
        transaction_record = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "amount": amount,
            "type": "coupon_redeem",
            "description": f"Coupou redeem: {coupon_code}",
            "coupon_code": coupon_code,
            "timestamp": datetime.utcnow()
        }
        transactions_col.insert_one(transaction_record)
        
        updated_coupon = get_coupon(coupon_code)
        if updated_coupon and updated_coupon.get("total_claimed_count", 0) >= max_users:
            coupons_col.update_one(
                {"coupon_code": coupon_code},
                {"$set": {"status": "expired"}}
            )
        
        return True, amount
    except Exception as e:
        logger.error(f"Error claiming coupon: {e}")
        return False, "Error processing coupon"

def create_coupon(code, amount, max_users, created_by):
    try:
        if amount < 1:
            return False, "Amount must be at least ₹1"
        if max_users < 1:
            return False, "Max users must be at least 1"
        
        existing = get_coupon(code)
        if existing:
            return False, "Coupon code already exists"
        
        coupon_data = {
            "coupon_code": code,
            "amount": float(amount),
            "max_users": int(max_users),
            "total_claimed_count": 0,
            "claimed_users": [],
            "status": "active",
            "created_at": datetime.utcnow(),
            "created_by": created_by
        }
        coupons_col.insert_one(coupon_data)
        return True, "Coupon created successfully"
    except Exception as e:
        logger.error(f"Error creating coupon: {e}")
        return False, f"Error: {str(e)}"

def remove_coupon(code, removed_by):
    try:
        coupon = get_coupon(code)
        if not coupon:
            return False, "Coupon not found"
        
        result = coupons_col.update_one(
            {"coupon_code": code},
            {"$set": {
                "status": "removed",
                "removed_at": datetime.utcnow(),
                "removed_by": removed_by
            }}
        )
        
        if result.modified_count == 0:
            return False, "Failed to remove coupon"
        return True, "Coupon removed successfully"
    except Exception as e:
        logger.error(f"Error removing coupon: {e}")
        return False, f"Error: {str(e)}"

def get_coupon_status(code):
    coupon = get_coupon(code)
    if not coupon:
        return None
    
    claimed = coupon.get("total_claimed_count", 0)
    max_users = coupon.get("max_users", 0)
    remaining = max(0, max_users - claimed)
    
    return {
        "code": coupon.get("coupon_code"),
        "amount": coupon.get("amount", 0),
        "max_users": max_users,
        "claimed": claimed,
        "remaining": remaining,
        "status": coupon.get("status", "unknown"),
        "created_at": coupon.get("created_at"),
        "created_by": coupon.get("created_by"),
        "claimed_users": coupon.get("claimed_users", [])[:10]
    }

# ---------------------------------------------------------------------
# ENHANCED RECHARGE APPROVAL FUNCTIONS
# ---------------------------------------------------------------------

def process_recharge_approval(admin_id, req_id, action):
    """Process recharge approval/rejection with tracking"""
    try:
        # Get recharge request
        req = recharges_col.find_one({"req_id": req_id})
        if not req:
            return False, "Request not found", None
        
        # Check if already processed
        if req.get("status") != "pending":
            return False, f"Request already {req.get('status')}", None
        
        # Get admin info
        admin_info = get_admin_info(admin_id)
        admin_name = f"Admin {admin_id}"
        if admin_info:
            user = users_col.find_one({"user_id": admin_id})
            if user:
                admin_name = user.get("name", f"Admin {admin_id}")
        
        user_target = req.get("user_id")
        amount = float(req.get("amount", 0))
        
        # Track this approval
        approval_key = f"{req_id}_{action}"
        
        # Check if another admin already processed this (via tracking)
        if approval_key in recharge_approvals:
            prev_admin = recharge_approvals[approval_key]
            return False, f"Already {action}ed by {prev_admin['admin_name']}", None
        
        if action == "approve":
            # Add balance to user
            add_balance(user_target, amount)
            
            # Update recharge status
            recharges_col.update_one(
                {"req_id": req_id},
                {"$set": {
                    "status": "approved", 
                    "processed_at": datetime.utcnow(), 
                    "processed_by": admin_id,
                    "processed_by_name": admin_name
                }}
            )
            
            # ✅ Notify USER about approval
            try:
                new_bal = get_balance(user_target)
                bot.send_message(
                    user_target,
                    f"✅ <b>Recharge Approved!</b>\n\n"
                    f"💰 <b>Amount:</b> {format_currency(amount)}\n"
                    f"🔢 <b>UTR:</b> <code>{req.get('utr') or 'N/A'}</code>\n"
                    f"👮 <b>Approved By:</b> Admin\n"
                    f"💳 <b>New Balance:</b> {format_currency(new_bal)}\n\n"
                    f"🎉 Your wallet has been recharged successfully!",
                    parse_mode="HTML"
                )
            except Exception as _ne:
                logger.warning(f"Could not notify user {user_target} of approval: {_ne}")
            
            # Log approval (public + personal)
            try:
                log_recharge_approved_async(
                    user_id=user_target,
                    amount=amount,
                    method=req.get("method", "UPI"),
                    utr=req.get("utr")
                )
            except:
                pass
            try:
                _u = users_col.find_one({"user_id": user_target}) or {}
                log_personal_deposit_approved_async(
                    user_id=user_target,
                    username=_u.get("username") or "",
                    amount=amount,
                    method=req.get("method", "UPI"),
                    utr=req.get("utr") or "",
                    admin_name=admin_name
                )
            except:
                pass
            
            # Add referral commission if applicable
            user_data = users_col.find_one({"user_id": user_target})
            if user_data and user_data.get("referred_by"):
                add_referral_commission(user_data["referred_by"], amount, req)
            
            # Mark this approval in tracking
            recharge_approvals[approval_key] = {
                "admin_id": admin_id,
                "admin_name": admin_name,
                "timestamp": datetime.utcnow()
            }
            
            return True, f"✅ Recharge approved by {admin_name}", {
                "admin_name": admin_name,
                "admin_id": admin_id,
                "action": "approved"
            }
            
        else:  # cancel/reject
            # Update recharge status
            recharges_col.update_one(
                {"req_id": req_id},
                {"$set": {
                    "status": "cancelled", 
                    "processed_at": datetime.utcnow(), 
                    "processed_by": admin_id,
                    "processed_by_name": admin_name
                }}
            )
            
            # ❌ Notify USER about rejection
            try:
                bot.send_message(
                    user_target,
                    f"❌ <b>Recharge Rejected!</b>\n\n"
                    f"💰 <b>Amount:</b> {format_currency(amount)}\n"
                    f"🔢 <b>UTR:</b> <code>{req.get('utr') or 'N/A'}</code>\n"
                    f"📋 <b>Request ID:</b> <code>{req_id}</code>\n\n"
                    f"⚠️ Your recharge has been rejected by admin.\n"
                    f"If you believe this is a mistake, please contact support.",
                    parse_mode="HTML"
                )
            except Exception as _ne:
                logger.warning(f"Could not notify user {user_target} of rejection: {_ne}")
            
            # Log rejection (public + personal)
            try:
                log_recharge_rejected_async(
                    user_id=user_target,
                    amount=amount,
                    method=req.get("method", "UPI"),
                    utr=req.get("utr")
                )
            except:
                pass
            try:
                _u2 = users_col.find_one({"user_id": user_target}) or {}
                log_personal_deposit_rejected_async(
                    user_id=user_target,
                    username=_u2.get("username") or "",
                    amount=amount,
                    method=req.get("method", "UPI"),
                    utr=req.get("utr") or "",
                    admin_name=admin_name
                )
            except:
                pass

            # Mark this rejection in tracking
            recharge_approvals[approval_key] = {
                "admin_id": admin_id,
                "admin_name": admin_name,
                "timestamp": datetime.utcnow()
            }

            return True, f"❌ Recharge rejected by {admin_name}", {
                "admin_name": admin_name,
                "admin_id": admin_id,
                "action": "rejected"
            }
            
    except Exception as e:
        logger.error(f"Error in recharge approval: {e}")
        return False, f"Error: {str(e)}", None

# ---------------------------------------------------------------------
# UI HELPER FUNCTIONS - FIXED
# ---------------------------------------------------------------------

def edit_or_resend(chat_id, message_id, text, markup=None, parse_mode=None, photo_url=None):
    """Edit message if possible, otherwise delete and send new"""
    try:
        if photo_url:
            # For photos, we need to send new message
            try:
                bot.delete_message(chat_id, message_id)
            except:
                pass
            return bot.send_photo(chat_id, photo_url, caption=text, parse_mode=parse_mode, reply_markup=markup)
        else:
            # For text messages, try to edit first
            try:
                return bot.edit_message_text(
                    text,
                    chat_id=chat_id,
                    message_id=message_id,
                    parse_mode=parse_mode,
                    reply_markup=markup
                )
            except Exception as e:
                # If edit fails, delete and send new
                try:
                    bot.delete_message(chat_id, message_id)
                except:
                    pass
                return bot.send_message(chat_id, text, parse_mode=parse_mode, reply_markup=markup)
    except Exception as e:
        logger.error(f"Error in edit_or_resend: {e}")
        return bot.send_message(chat_id, text, parse_mode=parse_mode, reply_markup=markup)

def clean_ui_and_send_menu(chat_id, user_id, text=None, markup=None):
    """Clean UI and send main menu - FIXED: Always deletes old message"""
    try:
        # ALWAYS try to delete the previous message
        if user_id in user_last_message:
            try:
                bot.delete_message(chat_id, user_last_message[user_id])
            except:
                pass
        
        # Main menu caption with expandable blockquotes
        caption = (
            "🥂 <b>Welcome To Otp Bot By ♔ MR √ Darklord$🇮🇳 ☂</b> 🥂\n"
            "<blockquote expandable>\n"
            "- Automatic OTPs 📍\n"
            "- Easy to Use 🥂🥂\n"
            "- 24/7 Support 👨‍🔧\n"
            "- Instant Payment Approvals 🧾\n"
            "</blockquote>\n"
            "<blockquote expandable>\n"
            "🚀 <b>How to use Bot :</b>\n"
            "1️⃣ Recharge\n"
            "2️⃣ Select Country\n"
            "3️⃣ Buy Account\n"
            "4️⃣ Get Number & Login through Telegram / Telegram X / Turbotel\n"
            "5️⃣ Receive OTP & You're Done ✅\n"
            "</blockquote>\n"
            "🚀 <b>Enjoy Fast Account Buying Experience!</b>"
        )
        
        if markup is None:
            markup = InlineKeyboardMarkup(row_width=2)
            # Row 1: 2 buttons
            markup.add(
                InlineKeyboardButton("🛒 Buy Account", callback_data="buy_account"),
                InlineKeyboardButton("💰 Balance", callback_data="balance")
            )
            # Row 2: 1 button
            markup.add(
                InlineKeyboardButton("💳 Recharge", callback_data="recharge")
            )
            # Row 3: 2 buttons
            markup.add(
                InlineKeyboardButton("👥 Refer Friends", callback_data="refer_friends"),
                InlineKeyboardButton("🎁 Redeem", callback_data="redeem_coupon")
            )
            # Row 4: 1 button
            markup.add(
                InlineKeyboardButton("🛠️ Support", callback_data="support")
            )
            # Row 5: 1 button (only for admin)
            if is_admin(user_id):
                markup.add(InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel"))
        
        # Send new message (TEXT ONLY - NO PHOTO)
        sent_msg = bot.send_message(
            chat_id,
            text or caption,
            parse_mode="HTML",
            reply_markup=markup,
            disable_web_page_preview=True
        )
        user_last_message[user_id] = sent_msg.message_id
        return sent_msg
    except Exception as e:
        logger.error(f"Error in clean_ui_and_send_menu: {e}")
        # Fallback
        try:
            sent_msg = bot.send_message(chat_id, text or caption, parse_mode="HTML", reply_markup=markup)
            user_last_message[user_id] = sent_msg.message_id
            return sent_msg
        except:
            pass

# ---------------------------------------------------------------------
# BALANCE TRANSFER FUNCTIONS
# ---------------------------------------------------------------------

def transfer_balance(sender_id, receiver_id, amount):
    """Balance transfer function"""
    try:
        # Sender ka balance check
        sender_balance = get_balance(sender_id)
        
        if sender_balance < amount:
            return False, "Insufficient balance"
        
        if amount <= 0:
            return False, "Amount must be greater than 0"
        
        if sender_id == receiver_id:
            return False, "Cannot send to yourself"
        
        # Check if receiver exists
        receiver = users_col.find_one({"user_id": receiver_id})
        if not receiver:
            return False, "Receiver user not found"
        
        # Transfer balance
        deduct_balance(sender_id, amount)
        add_balance(receiver_id, amount)
        
        # Transaction record
        transaction_id = f"TRF{int(time.time())}{sender_id}"
        transaction_record = {
            "transaction_id": transaction_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "amount": amount,
            "type": "transfer",
            "timestamp": datetime.utcnow()
        }
        transactions_col.insert_one(transaction_record)
        
        return True, f"✅ {format_currency(amount)} transferred successfully!"
        
    except Exception as e:
        logger.error(f"Transfer error: {e}")
        return False, f"Error: {str(e)}"

# ---------------------------------------------------------------------
# BOT HANDLERS - UPDATED WITH TWO CHANNELS
# ---------------------------------------------------------------------

@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    logger.info(f"Start command from user {user_id}")
    
    if is_user_banned(user_id):
        try:
            bot.delete_message(msg.chat.id, msg.message_id)
        except:
            pass
        return
    
    # Check if user has joined BOTH channels
    if not has_user_joined_channels(user_id):
        missing_channels = get_missing_channels(user_id)
        
        caption = """<b>🚀 Join Both Channels First!</b> 

📢 To use this bot, you must join our official channels.

👉 Get updates, new features & support from our channels.

Click the buttons below to join both channels, then press VERIFY ✅"""
        
        markup = InlineKeyboardMarkup(row_width=2)
        
        # Add premium-style buttons for each missing channel
        for channel in missing_channels:
            label = CHANNEL_BUTTON_LABELS.get(channel, f"📢 Join {channel}")
            markup.add(InlineKeyboardButton(
                label,
                url=f"https://t.me/{channel[1:]}"
            ))
        
        markup.add(InlineKeyboardButton("✅ Verify Join", callback_data="verify_join"))
        
        try:
            bot.send_message(
                user_id,
                caption,
                parse_mode="HTML",
                reply_markup=markup
            )
        except Exception as e:
            logger.error(f"Error sending join message: {e}")
        return
    
    referred_by = None
    if len(msg.text.split()) > 1:
        referral_code = msg.text.split()[1]
        if referral_code.startswith('REF'):
            try:
                referrer_id = int(referral_code[3:])
                referrer = users_col.find_one({"user_id": referrer_id})
                if referrer:
                    referred_by = referrer_id
                    logger.info(f"Referral detected: {referrer_id} -> {user_id}")
            except:
                pass
    
    ensure_user_exists(user_id, msg.from_user.first_name, msg.from_user.username, referred_by)

    # Security check
    if _is_security_blocked(user_id):
        return

    # Animation runs first, THEN menu (sequential — no background thread)
    _send_premium_animation(user_id, user_id, msg.from_user.first_name or "")
    clean_ui_and_send_menu(user_id, user_id)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    
    if is_user_banned(user_id):
        bot.answer_callback_query(call.id, "🚫 Your account is banned", show_alert=True)
        return
    
    logger.info(f"Callback received: {data} from user {user_id}")
    
    try:
        if data == "verify_join":
            # Check if user has joined BOTH channels
            if has_user_joined_channels(user_id):
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except:
                    pass
                clean_ui_and_send_menu(call.message.chat.id, user_id)
                bot.answer_callback_query(call.id, "✅ Verified! Welcome to the bot.", show_alert=True)
            else:
                missing_channels = get_missing_channels(user_id)
                
                caption = """<b>🚀 Join Both Channels First!</b> 

📢 To use this bot, you must join our official channels.

👉 Get updates, new features & support from our channels.

Click the buttons below to join both channels, then press VERIFY ✅"""
                
                markup = InlineKeyboardMarkup(row_width=2)
                
                # Add premium-style buttons for each missing channel
                for channel in missing_channels:
                    label = CHANNEL_BUTTON_LABELS.get(channel, f"📢 Join {channel}")
                    markup.add(InlineKeyboardButton(
                        label,
                        url=f"https://t.me/{channel[1:]}"
                    ))
                
                markup.add(InlineKeyboardButton("✅ Verify Join", callback_data="verify_join"))
                
                try:
                    bot.edit_message_text(
                        caption,
                        call.message.chat.id,
                        call.message.message_id,
                        parse_mode="HTML",
                        reply_markup=markup
                    )
                except:
                    pass
                
                missing_list = "\n".join([f"• {ch}" for ch in missing_channels])
                bot.answer_callback_query(
                    call.id, 
                    f"❌ Please join these channels first:\n{missing_list}", 
                    show_alert=True
                )
        
        elif data == "buy_account":
            if not has_user_joined_channels(user_id):
                missing_channels = get_missing_channels(user_id)
                missing_list = "\n".join([f"• {ch}" for ch in missing_channels])
                bot.answer_callback_query(
                    call.id, 
                    f"❌ Please join:\n{missing_list}", 
                    show_alert=True
                )
                start(call.message)
                return
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            show_countries(call.message.chat.id)
        
        elif data == "balance":
            if not has_user_joined_channels(user_id):
                missing_channels = get_missing_channels(user_id)
                missing_list = "\n".join([f"• {ch}" for ch in missing_channels])
                bot.answer_callback_query(
                    call.id, 
                    f"❌ Please join:\n{missing_list}", 
                    show_alert=True
                )
                start(call.message)
                return
            
            balance = get_balance(user_id)
            user_data = users_col.find_one({"user_id": user_id}) or {}
            commission_earned = user_data.get("total_commission_earned", 0)
            
            message = f"💰 **Your Balance:** {format_currency(balance)}\n\n"
            message += f"📊 **Referral Stats:**\n"
            message += f"• Total Commission Earned: {format_currency(commission_earned)}\n"
            message += f"• Total Referrals: {user_data.get('total_referrals', 0)}\n"
            message += f"• Commission Rate: {REFERRAL_COMMISSION}%\n\n"
            message += f"Your Referral Code: `{user_data.get('referral_code', 'REF' + str(user_id))}`"
            
            # Sirf Send Balance aur Back button
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("📤 Send Balance", callback_data="send_balance_menu")
            )
            markup.add(
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_menu")
            )
            
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            
            sent_msg = bot.send_message(
                call.message.chat.id,
                message,
                parse_mode="Markdown",
                reply_markup=markup
            )
            user_last_message[user_id] = sent_msg.message_id
        
        elif data == "send_balance_menu":
            if not has_user_joined_channels(user_id):
                missing_channels = get_missing_channels(user_id)
                missing_list = "\n".join([f"• {ch}" for ch in missing_channels])
                bot.answer_callback_query(
                    call.id, 
                    f"❌ Please join:\n{missing_list}", 
                    show_alert=True
                )
                start(call.message)
                return
            
            balance = get_balance(user_id)
            
            message = f"📤 **Send Balance - Step 1/2**\n\n"
            message += f"💰 Your Current Balance: {format_currency(balance)}\n\n"
            message += f"Please enter the **Receiver's User ID**:\n"
            message += f"_(Only numeric ID, e.g., 123456789)_"
            
            # Sirf Back button
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("⬅️ Back to Balance", callback_data="balance"))
            
            edit_or_resend(
                call.message.chat.id,
                call.message.message_id,
                message,
                markup=markup,
                parse_mode="Markdown"
            )
            
            # Set user state for user ID input
            user_stage[user_id] = "waiting_receiver_id"
        
        elif data == "transfer_confirm":
            # Transfer confirmation screen
            transfer_data = user_states.get(user_id, {})
            if not transfer_data or "receiver_id" not in transfer_data or "amount" not in transfer_data:
                bot.answer_callback_query(call.id, "❌ Session expired", show_alert=True)
                clean_ui_and_send_menu(call.message.chat.id, user_id)
                return
            
            receiver_id = transfer_data["receiver_id"]
            receiver_name = transfer_data.get("receiver_name", f"ID: {receiver_id}")
            amount = transfer_data["amount"]
            sender_balance = get_balance(user_id)
            
            message = f"📤 **Confirm Transfer**\n\n"
            message += f"👤 Receiver: {receiver_name}\n"
            message += f"🆔 Receiver ID: `{receiver_id}`\n"
            message += f"💰 Amount: {format_currency(amount)}\n"
            message += f"💳 Your Balance: {format_currency(sender_balance)}\n\n"
            message += f"Are you sure you want to proceed?"
            
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("✅ Confirm", callback_data="transfer_execute"),
                InlineKeyboardButton("❌ Cancel", callback_data="balance")
            )
            
            edit_or_resend(
                call.message.chat.id,
                call.message.message_id,
                message,
                markup=markup,
                parse_mode="Markdown"
            )
        
        elif data == "transfer_execute":
            # Execute transfer
            transfer_data = user_states.get(user_id, {})
            if not transfer_data or "receiver_id" not in transfer_data or "amount" not in transfer_data:
                bot.answer_callback_query(call.id, "❌ Session expired", show_alert=True)
                clean_ui_and_send_menu(call.message.chat.id, user_id)
                return
            
            receiver_id = transfer_data["receiver_id"]
            receiver_name = transfer_data.get("receiver_name", f"ID: {receiver_id}")
            amount = transfer_data["amount"]
            
            success, message_text = transfer_balance(user_id, receiver_id, amount)
            
            if success:
                # Get updated balances
                sender_new_balance = get_balance(user_id)
                receiver_new_balance = get_balance(receiver_id)
                
                # Message for sender
                sender_message = f"✅ **Transfer Successful!**\n\n"
                sender_message += f"👤 Sent to: {receiver_name}\n"
                sender_message += f"🆔 Receiver ID: `{receiver_id}`\n"
                sender_message += f"💰 Amount Sent: {format_currency(amount)}\n"
                sender_message += f"💳 Your New Balance: {format_currency(sender_new_balance)}\n\n"
                
                # Sirf Back to Balance button
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("⬅️ Back to Balance", callback_data="balance"))
                
                edit_or_resend(
                    call.message.chat.id,
                    call.message.message_id,
                    sender_message,
                    markup=markup,
                    parse_mode="Markdown"
                )
                
                # Send notification to receiver
                try:
                    # Get sender name
                    sender = users_col.find_one({"user_id": user_id})
                    sender_name = sender.get("name", "Unknown") if sender else "Unknown"
                    
                    receiver_message = f"📥 **Balance Received!**\n\n"
                    receiver_message += f"👤 From: {sender_name}\n"
                    receiver_message += f"🆔 Sender ID: `{user_id}`\n"
                    receiver_message += f"💰 Amount Received: {format_currency(amount)}\n"
                    receiver_message += f"💳 Your New Balance: {format_currency(receiver_new_balance)}\n\n"
                    
                    # Sirf Close button for receiver
                    receiver_markup = InlineKeyboardMarkup()
                    receiver_markup.add(InlineKeyboardButton("❌ Close", callback_data="back_to_menu"))
                    
                    bot.send_message(
                        receiver_id,
                        receiver_message,
                        parse_mode="Markdown",
                        reply_markup=receiver_markup
                    )
                except Exception as e:
                    logger.warning(f"Could not notify receiver {receiver_id}: {e}")
                
            else:
                # Transfer failed
                markup = InlineKeyboardMarkup()
                markup.add(
                    InlineKeyboardButton("🔄 Try Again", callback_data="send_balance_menu"),
                    InlineKeyboardButton("⬅️ Back to Balance", callback_data="balance")
                )
                
                edit_or_resend(
                    call.message.chat.id,
                    call.message.message_id,
                    f"❌ **Transfer Failed!**\n\n{message_text}",
                    markup=markup,
                    parse_mode="Markdown"
                )
            
            # Clear transfer state
            if user_id in user_states:
                user_states.pop(user_id, None)
            if user_id in user_stage:
                user_stage.pop(user_id, None)
        
        elif data == "redeem_coupon":
            if not has_user_joined_channels(user_id):
                missing_channels = get_missing_channels(user_id)
                missing_list = "\n".join([f"• {ch}" for ch in missing_channels])
                bot.answer_callback_query(
                    call.id, 
                    f"❌ Please join:\n{missing_list}", 
                    show_alert=True
                )
                start(call.message)
                return
            
            msg_text = "🎟 **Redeem Coupon**\n\nEnter your coupon code:"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("⬅️ Back", callback_data="back_to_menu"))
            
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            
            sent_msg = bot.send_message(
                call.message.chat.id,
                msg_text,
                parse_mode="Markdown",
                reply_markup=markup
            )
            user_last_message[user_id] = sent_msg.message_id
            user_stage[user_id] = "waiting_coupon"
        
        elif data == "recharge":
            if not has_user_joined_channels(user_id):
                missing_channels = get_missing_channels(user_id)
                missing_list = "\n".join([f"• {ch}" for ch in missing_channels])
                bot.answer_callback_query(
                    call.id, 
                    f"❌ Please join:\n{missing_list}", 
                    show_alert=True
                )
                start(call.message)
                return
            
            show_recharge_methods(call.message.chat.id, call.message.message_id, user_id)
        
        elif data == "refer_friends":
            if not has_user_joined_channels(user_id):
                missing_channels = get_missing_channels(user_id)
                missing_list = "\n".join([f"• {ch}" for ch in missing_channels])
                bot.answer_callback_query(
                    call.id, 
                    f"❌ Please join:\n{missing_list}", 
                    show_alert=True
                )
                start(call.message)
                return
            
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            show_referral_info(user_id, call.message.chat.id)
        
        elif data == "support":
            if not has_user_joined_channels(user_id):
                missing_channels = get_missing_channels(user_id)
                missing_list = "\n".join([f"• {ch}" for ch in missing_channels])
                bot.answer_callback_query(
                    call.id, 
                    f"❌ Please join:\n{missing_list}", 
                    show_alert=True
                )
                start(call.message)
                return
            
            msg_text = "🛠️ Support: @rchiex"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("⬅️ Back", callback_data="back_to_menu"))
            
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            
            sent_msg = bot.send_message(
                call.message.chat.id,
                msg_text,
                reply_markup=markup
            )
            user_last_message[user_id] = sent_msg.message_id
        
        elif data == "toggle_ai_mode":
            bot.answer_callback_query(call.id, "⚠️ Feature removed.", show_alert=False)

        elif data == "admin_panel":
            if is_admin(user_id):
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except:
                    pass
                show_admin_panel(call.message.chat.id)
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data.startswith("bulk_account_"):
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
                return
            
            country_name = data.replace("bulk_account_", "")
            
            bulk_add_states[user_id] = {
                "mode": "bulk",
                "country": country_name,
                "phone_numbers": [],
                "current_index": 0,
                "total_numbers": 0,
                "success_count": 0,
                "failed_count": 0,
                "failed_numbers": [],
                "current_client": None,
                "current_phone_code_hash": None,
                "current_phone": None,
                "current_manager": None,
                "password_attempts": 0,
                "message_id": call.message.message_id,
                "step": "waiting_numbers",
                "chat_id": call.message.chat.id,
                "is_processing": False
            }
            
            edit_or_resend(
                call.message.chat.id,
                call.message.message_id,
                f"📦 **Bulk Account Addition**\n\n"
                f"🌍 Country: {country_name}\n\n"
                "📱 Enter phone numbers (one per line):\n"
                "Format:\n"
                "+91XXXXXXXXXX\n"
                "+91828XXXXXXX\n"
                "+91999XXXXXXX\n\n"
                "⚠️ Max 50 numbers at once\n"
                "⚠️ Include country code\n"
                "⚠️ One number per line",
                markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_bulk")
                )
            )
        
        elif data.startswith("single_account_"):
            country_name = data.replace("single_account_", "")
            login_states[user_id]["country"] = country_name
            login_states[user_id]["step"] = "phone"
            login_states[user_id]["mode"] = "single"
            
            edit_or_resend(
                call.message.chat.id,
                call.message.message_id,
                f"🌍 Country: {country_name}\n\n"
                "📱 Enter phone number with country code:\n"
                "Example: +919876543210",
                markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_login")
                )
            )
        
        elif data == "start_bulk_add":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
                return
            
            if user_id not in bulk_add_states:
                bot.answer_callback_query(call.id, "❌ Session expired", show_alert=True)
                return
            
            state = bulk_add_states[user_id]
            if not state.get("phone_numbers"):
                bot.answer_callback_query(call.id, "❌ No phone numbers to process", show_alert=True)
                return
            
            bot.answer_callback_query(call.id, "🚀 Starting bulk account addition...")
            start_bulk_processing(user_id)
        
        elif data == "cancel_bulk":
            handle_cancel_bulk(call)
        
        elif data == "pause_bulk":
            if user_id in bulk_add_states:
                bulk_add_states[user_id]["is_processing"] = False
                bot.answer_callback_query(call.id, "⏸️ Processing paused", show_alert=True)
        
        elif data == "resume_bulk":
            if user_id in bulk_add_states:
                bulk_add_states[user_id]["is_processing"] = True
                bot.answer_callback_query(call.id, "▶️ Processing resumed", show_alert=True)
                process_next_bulk_number(user_id)
        
        elif data == "skip_bulk_number":
            if user_id in bulk_add_states:
                state = bulk_add_states[user_id]
                state["failed_count"] += 1
                state["failed_numbers"].append({
                    "number": state.get("current_phone", "Unknown"),
                    "reason": "Skipped by admin"
                })
                
                if state.get("current_client") and account_manager:
                    try:
                        asyncio.run(account_manager.pyrogram_manager.safe_disconnect(state["current_client"]))
                    except:
                        pass
                
                state["current_index"] += 1
                state["password_attempts"] = 0
                bot.answer_callback_query(call.id, "⏭️ Number skipped", show_alert=True)
                process_next_bulk_number(user_id)
        
        elif data.startswith("country_raw_"):
            if not has_user_joined_channels(user_id):
                missing_channels = get_missing_channels(user_id)
                missing_list = "\n".join([f"• {ch}" for ch in missing_channels])
                bot.answer_callback_query(
                    call.id, 
                    f"❌ Please join:\n{missing_list}", 
                    show_alert=True
                )
                start(call.message)
                return
            
            country_name = data.replace("country_raw_", "")
            show_country_details(user_id, country_name, call.message.chat.id, call.message.message_id, call.id)
        
        elif data.startswith("buy_"):
            if not has_user_joined_channels(user_id):
                missing_channels = get_missing_channels(user_id)
                missing_list = "\n".join([f"• {ch}" for ch in missing_channels])
                bot.answer_callback_query(
                    call.id, 
                    f"❌ Please join:\n{missing_list}", 
                    show_alert=True
                )
                start(call.message)
                return
            
            account_id = data.split("_", 1)[1]
            process_purchase(user_id, account_id, call.message.chat.id, call.message.message_id, call.id)
        
        elif data.startswith("logout_session_"):
            session_id = data.split("_", 2)[2]
            handle_logout_session(user_id, session_id, call.message.chat.id, call.id)
        
        elif data.startswith("get_otp_"):
            if not has_user_joined_channels(user_id):
                missing_channels = get_missing_channels(user_id)
                missing_list = "\n".join([f"• {ch}" for ch in missing_channels])
                bot.answer_callback_query(
                    call.id, 
                    f"❌ Please join:\n{missing_list}", 
                    show_alert=True
                )
                start(call.message)
                return
            
            session_id = data.split("_", 2)[2]
            get_latest_otp(user_id, session_id, call.message.chat.id, call.id)
        
        elif data == "back_to_countries":
            if not has_user_joined_channels(user_id):
                missing_channels = get_missing_channels(user_id)
                missing_list = "\n".join([f"• {ch}" for ch in missing_channels])
                bot.answer_callback_query(
                    call.id, 
                    f"❌ Please join:\n{missing_list}", 
                    show_alert=True
                )
                start(call.message)
                return
            
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            show_countries(call.message.chat.id)
        
        elif data == "back_to_menu":
            clean_ui_and_send_menu(call.message.chat.id, user_id)
        
        elif data == "recharge_upi":
            if not has_user_joined_channels(user_id):
                missing_channels = get_missing_channels(user_id)
                missing_list = "\n".join([f"• {ch}" for ch in missing_channels])
                bot.answer_callback_query(
                    call.id, 
                    f"❌ Please join:\n{missing_list}", 
                    show_alert=True
                )
                start(call.message)
                return
            
            recharge_method_state[user_id] = "upi"
            edit_or_resend(
                call.message.chat.id,
                call.message.message_id,
                "💳 Enter recharge amount for UPI (minimum ₹5):",
                markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("❌ Cancel", callback_data="back_to_menu")
                )
            )
            bot.register_next_step_handler(call.message, process_recharge_amount)

        elif data == "recharge_fampay_manual":
            recharge_method_state[user_id] = "fampay"
            edit_or_resend(
                call.message.chat.id,
                call.message.message_id,
                "💜 Enter recharge amount for FamPay (minimum ₹5):",
                markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("❌ Cancel", callback_data="back_to_menu")
                )
            )
            bot.register_next_step_handler(call.message, process_recharge_amount)

        elif data == "recharge_fampay_auto":
            if not FAMPAY_API_KEY or not FAMPAY_BASE_URL:
                bot.answer_callback_query(call.id, "⚠️ UPI Auto not configured yet.", show_alert=True)
                return
            edit_or_resend(
                call.message.chat.id,
                call.message.message_id,
                "⚡ <b>UPI Auto (QR)</b>\n\nEnter recharge amount (minimum ₹5):",
                markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("❌ Cancel", callback_data="back_to_menu")
                ),
                parse_mode="HTML"
            )
            recharge_method_state[user_id] = "fampay_auto"
            bot.register_next_step_handler(call.message, process_fampay_auto_amount)

        elif data.startswith("fp_icheck_"):
            # ── Instant payment check — user pressed "Maine Pay Kar Diya" ──────
            cb_order_id = data[len("fp_icheck_"):]   # partial order_id (first 30 chars)

            # Resolve full order_id + amount + chat_id from memory or DB
            order_id = None
            amount   = 0
            chat_id  = call.message.chat.id

            # 1. Check in-memory state
            st = fampay_auto_states.get(user_id)
            if st and st.get("order_id", "").startswith(cb_order_id):
                order_id = st["order_id"]
                amount   = st["amount"]
                chat_id  = st["chat_id"]

            # 2. Fallback to MongoDB
            if not order_id:
                try:
                    rec = recharges_col.find_one(
                        {"user_id": user_id, "status": "pending", "method": "UPI Auto"},
                        sort=[("created_at", -1)]
                    )
                    if rec and rec.get("order_id", "").startswith(cb_order_id):
                        order_id = rec["order_id"]
                        amount   = rec.get("amount", 0)
                        chat_id  = rec.get("chat_id", call.message.chat.id)
                except Exception:
                    pass

            if not order_id:
                bot.answer_callback_query(
                    call.id,
                    "⚠️ Order nahi mila. Shayad expire ho gaya ya already credited hai.",
                    show_alert=True
                )
                return

            # Already credited?
            if order_id in fampay_approved_orders:
                bot.answer_callback_query(call.id, "✅ Already credit ho chuka hai!", show_alert=True)
                return

            bot.answer_callback_query(call.id, "🔍 FamPay se check ho raha hai...", show_alert=False)

            # ── Run instant check in background so callback doesn't timeout ──
            def _instant_check_job():
                status = fp_check_status(order_id)
                logger.info(f"fp_icheck callback: order={order_id} status={status} user={user_id}")

                if status == "success":
                    fp_credit_wallet(chat_id, user_id, order_id, amount)

                elif status == "expired":
                    if order_id not in fampay_notified_orders:
                        fampay_notified_orders.add(order_id)
                        retry_mu = InlineKeyboardMarkup(row_width=1)
                        retry_mu.add(
                            InlineKeyboardButton("🔄 Naya Payment Karo", callback_data="recharge_fampay_auto"),
                            InlineKeyboardButton("📞 Admin Se Contact Karo", url="https://t.me/ID_GMS_SELLER_bot"),
                        )
                        try:
                            bot.send_message(
                                chat_id,
                                f"❌ <b>Order Expire Ho Gaya</b>\n\n"
                                f"🆔 <code>{order_id}</code>\n"
                                f"💰 ₹{int(amount)}\n\n"
                                f"Agar aapne pay kiya tha toh admin se order ID share karein.",
                                parse_mode="HTML",
                                reply_markup=retry_mu
                            )
                        except Exception:
                            pass

                else:  # pending
                    retry_mu = InlineKeyboardMarkup(row_width=1)
                    retry_mu.add(
                        InlineKeyboardButton("🔄 Dobara Check Karo", callback_data=f"fp_icheck_{order_id[:30]}"),
                    )
                    try:
                        bot.send_message(
                            chat_id,
                            f"⏳ <b>Payment Abhi Nahi Mili</b>\n\n"
                            f"🆔 <code>{order_id}</code>\n\n"
                            f"Pay karne ke <b>1-2 minute baad</b> dobara check karein.\n"
                            f"Bot khud bhi automatically check karta rehta hai.\n\n"
                            f"<i>Ya /checkpayment {order_id} command use karein.</i>",
                            parse_mode="HTML",
                            reply_markup=retry_mu
                        )
                    except Exception:
                        pass

            threading.Thread(target=_instant_check_job, daemon=True).start()

        elif data == "recharge_crypto":
            if not CRYPTO_USDT_ADDRESS:
                bot.answer_callback_query(call.id, "⚠️ Crypto payment not configured yet. Contact admin.", show_alert=True)
                return
            usdt_rate = get_usdt_inr_rate()
            rate_line = f"📈 <b>Live Rate:</b> 1 USDT = ₹{usdt_rate:.2f}\n" if usdt_rate > 0 else ""
            min_usdt_inr = f"≈ ₹{(0.09 * usdt_rate):.2f}" if usdt_rate > 0 else ""
            crypto_text = (
                "💎 <b>Crypto Payment (USDT)</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n\n"
                "<blockquote>"
                f"🪙 <b>Token:</b> USDT\n"
                f"🌐 <b>Network:</b> {CRYPTO_NETWORK}\n"
                f"{rate_line}"
                f"📋 <b>Address:</b>\n<code>{CRYPTO_USDT_ADDRESS}</code>"
                "</blockquote>\n\n"
                "📌 <b>Steps:</b>\n"
                "1️⃣ Scan QR or copy address above\n"
                "2️⃣ Send USDT & take screenshot\n"
                "3️⃣ Send screenshot + TxID to admin\n\n"
                f"⚠️ <i>Min 0.09 USDT {min_usdt_inr}. Wrong network = funds lost!</i>"
            )
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{os.getenv('ADMIN_USERNAME', '')}"),
                InlineKeyboardButton("⬅️ Back", callback_data="recharge")
            )
            # Delete old message and send photo with QR
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            try:
                bot.send_photo(
                    call.message.chat.id,
                    CRYPTO_QR_URL,
                    caption=crypto_text,
                    parse_mode="HTML",
                    reply_markup=markup
                )
            except:
                bot.send_message(call.message.chat.id, crypto_text, parse_mode="HTML", reply_markup=markup)
        
        elif data == "upi_deposited":
            user_id = call.from_user.id
            amount = upi_payment_states.get(user_id, {}).get("amount", 0)
            if amount <= 0:
                bot.answer_callback_query(call.id, "❌ Invalid amount", show_alert=True)
                return
            
            bot.answer_callback_query(call.id, "📝 Please send your 12-digit UTR number", show_alert=False)
            
            upi_payment_states[user_id] = {
                "step": "waiting_utr",
                "amount": amount,
                "chat_id": call.message.chat.id
            }
            
            bot.send_message(
                call.message.chat.id,
                "📝 **Step 1: Enter UTR**\n\n"
                "Please send your 12-digit UTR number:\n"
                "_(Sent by your bank after payment)_"
            )
        
        elif data.startswith("approve_rech|") or data.startswith("cancel_rech|"):
            if is_admin(user_id):
                parts = data.split("|")
                action = parts[0]
                req_id = parts[1] if len(parts) > 1 else None
                
                # Process approval/rejection
                success, message, admin_info = process_recharge_approval(user_id, req_id, 
                                                                        "approve" if action == "approve_rech" else "reject")
                
                if success:
                    bot.answer_callback_query(call.id, message, show_alert=True)
                    
                    # Delete the original admin message
                    try:
                        bot.delete_message(call.message.chat.id, call.message.message_id)
                    except:
                        pass
                    
                    # Send new message showing which admin approved/rejected
                    admin_action_msg = f"✅ **Recharge Request Processed**\n\n"
                    admin_action_msg += f"📋 Request ID: `{req_id}`\n"
                    admin_action_msg += f"👤 Processed by: {admin_info['admin_name']}\n"
                    admin_action_msg += f"🆔 Admin ID: `{admin_info['admin_id']}`\n"
                    admin_action_msg += f"📌 Action: **{admin_info['action'].upper()}**\n"
                    admin_action_msg += f"⏰ Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
                    
                    bot.send_message(
                        call.message.chat.id,
                        admin_action_msg,
                        parse_mode="Markdown"
                    )
                else:
                    bot.answer_callback_query(call.id, f"❌ {message}", show_alert=True)
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data == "add_account":
            logger.info(f"Add account button clicked by user {user_id}")
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
                return
            
            login_states[user_id] = {
                "step": "select_country",
                "message_id": call.message.message_id,
                "chat_id": call.message.chat.id
            }
            
            countries = get_all_countries()
            if not countries:
                bot.answer_callback_query(call.id, "❌ No countries available. Add a country first.", show_alert=True)
                return
            
            markup = InlineKeyboardMarkup(row_width=2)
            for country in countries:
                markup.add(InlineKeyboardButton(
                    country['name'],
                    callback_data=f"login_country_{country['name']}"
                ))
            markup.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_login"))
            
            edit_or_resend(
                call.message.chat.id,
                call.message.message_id,
                "🌍 **Select Country for Account**\n\nChoose country:",
                markup=markup
            )
        
        elif data.startswith("login_country_"):
            handle_login_country_selection(call)
        
        elif data == "cancel_login":
            handle_cancel_login(call)
        
        elif data == "out_of_stock":
            bot.answer_callback_query(call.id, "❌ Out of Stock! No accounts available.", show_alert=True)

        elif data.startswith("countries_page_"):
            try:
                pg = int(data.split("_")[-1])
            except:
                pg = 1
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            show_countries(call.message.chat.id, page=pg)

        elif data == "admin_permissions":
            if is_super_admin(user_id):
                show_admin_permissions(call.message.chat.id)
            else:
                bot.answer_callback_query(call.id, "❌ Owner only", show_alert=True)

        elif data.startswith("view_admin_perm_"):
            if is_super_admin(user_id):
                target_id = int(data.split("_")[-1])
                show_admin_perm_detail(call.message.chat.id, target_id)
            else:
                bot.answer_callback_query(call.id, "❌ Owner only", show_alert=True)

        elif data.startswith("toggle_perm_"):
            if is_super_admin(user_id):
                parts = data.split("_", 3)
                # toggle_perm_{admin_id}_{perm_key}
                target_id = int(parts[2])
                perm_key = parts[3]
                adm = admins_col.find_one({"user_id": target_id})
                if adm:
                    perms = adm.get("permissions", {})
                    current = perms.get(perm_key, True)
                    perms[perm_key] = not current
                    admins_col.update_one({"user_id": target_id}, {"$set": {"permissions": perms}})
                    status = "🟢 ON" if not current else "🔴 OFF"
                    bot.answer_callback_query(call.id, f"{perm_key}: {status}", show_alert=False)
                    show_admin_perm_detail(call.message.chat.id, target_id)
                    try:
                        bot.delete_message(call.message.chat.id, call.message.message_id)
                    except:
                        pass

        elif data.startswith("perm_all_on_") or data.startswith("perm_all_off_"):
            if is_super_admin(user_id):
                enable = data.startswith("perm_all_on_")
                target_id = int(data.split("_")[-1])
                new_perms = {k: enable for k in PERMISSION_LABELS}
                admins_col.update_one({"user_id": target_id}, {"$set": {"permissions": new_perms}})
                bot.answer_callback_query(call.id, f"All permissions {'enabled' if enable else 'disabled'}", show_alert=False)
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except:
                    pass
                show_admin_perm_detail(call.message.chat.id, target_id)

        elif data == "cleanmongo_confirm":
            if is_super_admin(user_id):
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(
                    InlineKeyboardButton("✅ Yes, Clean Now", callback_data="cleanmongo_run"),
                    InlineKeyboardButton("❌ Cancel", callback_data="admin_panel")
                )
                bot.send_message(
                    call.message.chat.id,
                    "⚠️ <b>MongoDB Cleanup</b>\n\n"
                    "This will remove:\n"
                    "• Expired OTP sessions (>2 hours)\n"
                    "• Used accounts older than 30 days\n"
                    "• Old processed recharge requests (>60 days)\n"
                    "• Old orders (>60 days)\n\n"
                    "<b>Are you sure?</b>",
                    reply_markup=markup, parse_mode="HTML"
                )

        elif data == "cleanmongo_run":
            if is_super_admin(user_id):
                bot.answer_callback_query(call.id, "🗑 Cleaning...", show_alert=False)
                try:
                    results = _run_mongo_cleanup()
                    total = sum(results.values())
                    db_info = _get_db_stats()
                    bot.send_message(
                        call.message.chat.id,
                        f"✅ <b>MongoDB Cleanup Complete!</b>\n\n"
                        f"🗑 OTP Sessions: <b>{results['otp_sessions']}</b>\n"
                        f"🗑 Used Accounts: <b>{results['used_accounts']}</b>\n"
                        f"🗑 Old Recharges: <b>{results['old_recharges']}</b>\n"
                        f"🗑 Old Orders: <b>{results['old_orders']}</b>\n"
                        f"🗑 Old Transactions: <b>{results['old_transactions']}</b>\n"
                        f"🗑 Old Referrals: <b>{results['old_referrals']}</b>\n"
                        f"🗑 Old Coupons: <b>{results['old_coupons']}</b>\n\n"
                        f"📦 <b>Total Removed:</b> {total}\n"
                        f"💾 <b>DB:</b> <code>{db_info}</code>",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    bot.send_message(call.message.chat.id, f"❌ Cleanup error: {e}")

        elif data == "cleanempty_confirm":
            if is_admin(user_id):
                bot.answer_callback_query(call.id, "🗑 Removing empty countries...", show_alert=False)
                try:
                    all_countries = get_all_countries()
                    empty = [c for c in all_countries if get_available_accounts_count(c['name']) == 0]
                    if not empty:
                        bot.send_message(call.message.chat.id,
                            "✅ <b>Kuch bhi remove nahi karna!</b>\nSabhi countries mein already stock hai.",
                            parse_mode="HTML")
                    else:
                        removed = []
                        for c in empty:
                            countries_col.update_one(
                                {"name": c['name']},
                                {"$set": {"status": "inactive", "removed_at": datetime.utcnow()}}
                            )
                            accounts_col.delete_many({"country": {"$regex": f"^{re.escape(c['name'])}$", "$options": "i"}})
                            removed.append(c['name'])
                        lines = "\n".join([f"• {n}" for n in removed])
                        markup = InlineKeyboardMarkup()
                        markup.add(InlineKeyboardButton("⬅️ Back to Admin", callback_data="admin_panel"))
                        bot.send_message(
                            call.message.chat.id,
                            f"✅ <b>{len(removed)} Empty Countries Removed!</b>\n\n"
                            f"<b>Removed:</b>\n{lines}\n\n"
                            f"Yeh countries ab buy aur manage section mein nahi dikhenge.",
                            reply_markup=markup, parse_mode="HTML"
                        )
                except Exception as e:
                    bot.send_message(call.message.chat.id, f"❌ Error removing empty countries: {e}")
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)

        elif data in ("clearacc_sold", "clearacc_active", "clearacc_all"):
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
                return
            bot.answer_callback_query(call.id, "🗑 Clearing...", show_alert=False)
            try:
                if data == "clearacc_sold":
                    res = accounts_col.delete_many({"used": True})
                    label = "Sold accounts"
                elif data == "clearacc_active":
                    res = accounts_col.delete_many({"status": "active", "used": False})
                    label = "Active accounts"
                else:
                    res = accounts_col.delete_many({})
                    label = "All accounts"
                bot.send_message(
                    call.message.chat.id,
                    f"✅ <b>{label} cleared!</b>\n\n"
                    f"🗑️ Deleted: <b>{res.deleted_count}</b> accounts\n"
                    f"📱 Remaining: <b>{accounts_col.count_documents({})}</b>",
                    parse_mode="HTML"
                )
            except Exception as e:
                bot.send_message(call.message.chat.id, f"❌ Error: {e}")

        elif data == "edit_price":
            if is_admin(user_id):
                bot.answer_callback_query(call.id, "Processing...")
                show_edit_price_country_selection(call.message.chat.id, call.message.message_id)
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data.startswith("edit_price_country_"):
            if is_admin(user_id):
                country_name = data.replace("edit_price_country_", "")
                show_edit_price_details(call.message.chat.id, call.message.message_id, country_name)
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data.startswith("edit_price_confirm_"):
            if is_admin(user_id):
                country_name = data.replace("edit_price_confirm_", "")
                edit_price_state[user_id] = {"country": country_name, "step": "waiting_price"}
                try:
                    country = get_country_by_name(country_name)
                    if country:
                        current_price = country.get("price", 0)
                        edit_or_resend(
                            call.message.chat.id,
                            call.message.message_id,
                            f"🌍 Country: {country_name}\n💰 Current Price: {format_currency(current_price)}\n\n"
                            f"Enter new price for {country_name}:",
                            markup=InlineKeyboardMarkup().add(
                                InlineKeyboardButton("❌ Cancel", callback_data="manage_countries")
                            )
                        )
                    else:
                        bot.answer_callback_query(call.id, "❌ Country not found", show_alert=True)
                except:
                    pass
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data == "cancel_edit_price":
            if is_admin(user_id):
                show_country_management(call.message.chat.id)
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data == "admin_coupon_menu":
            if is_admin(user_id):
                bot.answer_callback_query(call.id, "🎟 Coupon Management")
                show_coupon_management(call.message.chat.id, call.message.message_id)
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data == "admin_create_coupon":
            if is_admin(user_id):
                bot.answer_callback_query(call.id, "Creating coupon...")
                coupon_state[user_id] = {"step": "ask_code"}
                edit_or_resend(
                    call.message.chat.id,
                    call.message.message_id,
                    "🎟 **Create Coupon**\n\nEnter coupon code:",
                    markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("❌ Cancel", callback_data="admin_coupon_menu")
                    ),
                    parse_mode="Markdown"
                )
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data == "admin_remove_coupon":
            if is_admin(user_id):
                bot.answer_callback_query(call.id, "Removing coupon...")
                coupon_state[user_id] = {"step": "ask_remove_code"}
                edit_or_resend(
                    call.message.chat.id,
                    call.message.message_id,
                    "🗑 **Remove Coupon**\n\nEnter coupon code to remove:",
                    markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("❌ Cancel", callback_data="admin_coupon_menu")
                    ),
                    parse_mode="Markdown"
                )
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data == "admin_coupon_status":
            if is_admin(user_id):
                bot.answer_callback_query(call.id, "Checking coupon status...")
                coupon_state[user_id] = {"step": "ask_status_code"}
                edit_or_resend(
                    call.message.chat.id,
                    call.message.message_id,
                    "📊 **Coupon Status**\n\nEnter coupon code to check:",
                    markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("❌ Cancel", callback_data="admin_coupon_menu")
                    ),
                    parse_mode="Markdown"
                )
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data == "broadcast_menu":
            if is_admin(user_id):
                global IS_BROADCASTING
                bot.answer_callback_query(call.id, "📢 Broadcast Panel Opened")
                status_txt = "🔴 BUSY (broadcast chal raha hai)" if IS_BROADCASTING else "🟢 Ready"
                broadcast_msg = (
                    "📢 <b>Broadcast Panel</b>\n\n"
                    f"📡 Status: {status_txt}\n\n"
                    "<b>Broadcast kaise karein:</b>\n"
                    "1. Koi bhi message yahan send karo\n"
                    "2. Us message ko reply karke likho: <code>/sendbroadcast</code>\n\n"
                    "✅ Message bina 'Forwarded from' tag ke jayega\n\n"
                    "Agar stuck ho jaye: <code>/resetbroadcast</code>"
                )
                bot.send_message(call.message.chat.id, broadcast_msg, parse_mode="HTML")
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data == "refund_start":
            if is_admin(user_id):
                bot.answer_callback_query(call.id, "Processing...")
                msg = bot.send_message(call.message.chat.id, "💸 Enter user ID for refund:")
                bot.register_next_step_handler(msg, ask_refund_user)
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data == "ranking":
            if is_admin(user_id):
                bot.answer_callback_query(call.id, "📊 Generating ranking...")
                show_user_ranking(call.message.chat.id)
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data == "message_user":
            if is_admin(user_id):
                bot.answer_callback_query(call.id, "👤 Enter user ID to send message:")
                msg = bot.send_message(call.message.chat.id, "👤 Enter user ID to send message:")
                bot.register_next_step_handler(msg, ask_message_content)
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data == "admin_deduct_start":
            if is_admin(user_id):
                bot.answer_callback_query(call.id, "Processing...")
                admin_deduct_state[user_id] = {"step": "ask_user_id"}
                msg = bot.send_message(call.message.chat.id, "👤 Enter User ID whose balance you want to deduct:")
                if user_id in broadcast_data:
                    del broadcast_data[user_id]
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data == "ban_user":
            if is_admin(user_id):
                bot.answer_callback_query(call.id, "Processing...")
                msg = bot.send_message(call.message.chat.id, "🚫 Enter User ID to ban:")
                bot.register_next_step_handler(msg, ask_ban_user)
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data == "unban_user":
            if is_admin(user_id):
                bot.answer_callback_query(call.id, "Processing...")
                msg = bot.send_message(call.message.chat.id, "✅ Enter User ID to unban:")
                bot.register_next_step_handler(msg, ask_unban_user)
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data == "manage_countries":
            if is_admin(user_id):
                bot.answer_callback_query(call.id, "Processing...")
                show_country_management(call.message.chat.id)
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)

        elif data.startswith("mgmt_page_"):
            if is_admin(user_id):
                try:
                    pg = int(data.split("_")[-1])
                except:
                    pg = 1
                show_country_management(call.message.chat.id, page=pg)

        elif data == "mgmt_show_empty":
            if is_admin(user_id):
                show_country_management(call.message.chat.id, page=1, show_empty=True)

        elif data.startswith("mgmt_empty_page_"):
            if is_admin(user_id):
                try:
                    pg = int(data.split("_")[-1])
                except:
                    pg = 1
                show_country_management(call.message.chat.id, page=pg, show_empty=True)

        elif data.startswith("mgmt_country_"):
            if is_admin(user_id):
                country_name = data[len("mgmt_country_"):]
                country = get_country_by_name(country_name)
                cnt = get_available_accounts_count(country_name)
                if country:
                    markup = InlineKeyboardMarkup(row_width=1)
                    markup.add(InlineKeyboardButton("⬅️ Back", callback_data="manage_countries"))
                    bot.send_message(
                        call.message.chat.id,
                        f"🌍 <b>{country_name}</b>\n\n"
                        f"💰 Price: <b>{format_currency(country['price'])}</b>\n"
                        f"📦 Stock: <b>{cnt}</b> accounts",
                        reply_markup=markup, parse_mode="HTML"
                    )
        
        elif data == "add_country":
            if is_admin(user_id):
                bot.answer_callback_query(call.id, "Processing...")
                msg = bot.send_message(call.message.chat.id, "🌍 Enter country name to add:")
                bot.register_next_step_handler(msg, ask_country_name)
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        elif data == "remove_country":
            if is_admin(user_id):
                bot.answer_callback_query(call.id, "Processing...")
                show_country_removal(call.message.chat.id)
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)

        elif data.startswith("rmv_page_"):
            if is_admin(user_id):
                try:
                    pg = int(data.split("_")[-1])
                except:
                    pg = 1
                show_country_removal(call.message.chat.id, page=pg)
        
        elif data.startswith("remove_country_"):
            if is_admin(user_id):
                country_name = data.split("_", 2)[2]
                result = remove_country(country_name, call.message.chat.id, call.message.message_id)
                bot.answer_callback_query(call.id, result, show_alert=True)
            else:
                bot.answer_callback_query(call.id, "❌ Unauthorized", show_alert=True)
        
        else:
            bot.answer_callback_query(call.id, "❌ Unknown action", show_alert=True)
    
    except Exception as e:
        logger.error(f"Callback error: {e}")
        try:
            bot.answer_callback_query(call.id, "❌ Error occurred", show_alert=True)
            if is_admin(user_id):
                bot.send_message(call.message.chat.id, f"Callback handler error:\n{e}")
        except:
            pass

# ---------------------------------------------------------------------
# BULK ACCOUNT FUNCTIONS
# ---------------------------------------------------------------------

def handle_cancel_bulk(call):
    user_id = call.from_user.id
    
    if user_id in bulk_add_states:
        state = bulk_add_states[user_id]
        
        if state.get("current_client") and account_manager:
            try:
                asyncio.run(account_manager.pyrogram_manager.safe_disconnect(state["current_client"]))
            except:
                pass
        
        del bulk_add_states[user_id]
    
    edit_or_resend(
        call.message.chat.id,
        call.message.message_id,
        "❌ Bulk account addition cancelled.",
        markup=None
    )
    show_admin_panel(call.message.chat.id)

@bot.message_handler(func=lambda m: bulk_add_states.get(m.from_user.id, {}).get("step") == "waiting_numbers")
def handle_bulk_numbers_input(msg):
    user_id = msg.from_user.id
    
    if user_id not in bulk_add_states:
        return
    
    state = bulk_add_states[user_id]
    if state.get("step") != "waiting_numbers":
        return
    
    text = msg.text.strip()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    valid_numbers = []
    invalid_numbers = []
    
    for line in lines[:500]:
        cleaned = line.strip()
        if cleaned.startswith('+') and len(cleaned) >= 7:
            valid_numbers.append(cleaned)
        elif re.match(r'^\d{7,15}$', cleaned):
            valid_numbers.append('+' + cleaned)
        else:
            invalid_numbers.append(cleaned)
    
    if not valid_numbers:
        bot.send_message(
            msg.chat.id,
            "❌ No valid phone numbers found.\n"
            "Please enter numbers with country code (one per line).\n"
            "Example: +79123456789 or +8613800138000"
        )
        return
    
    state["phone_numbers"] = valid_numbers
    state["total_numbers"] = len(valid_numbers)
    state["step"] = "confirm_numbers"
    
    message = f"📦 **Bulk Account Addition**\n\n"
    message += f"🌍 Country: {state['country']}\n"
    message += f"📱 Total Numbers: {len(valid_numbers)}\n"
    
    if invalid_numbers:
        message += f"⚠️ Invalid (skipped): {len(invalid_numbers)}\n"
    
    message += f"\n**First 5 numbers:**\n"
    for i, num in enumerate(valid_numbers[:5], 1):
        message += f"{i}. `{num}`\n"
    
    if len(valid_numbers) > 5:
        message += f"... and {len(valid_numbers) - 5} more\n"
    
    message += f"\nClick below to start adding accounts:"
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("▶️ Start Adding Accounts", callback_data="start_bulk_add"),
        InlineKeyboardButton("✏️ Edit Numbers", callback_data="edit_bulk_numbers")
    )
    markup.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_bulk"))
    
    sent_msg = bot.send_message(msg.chat.id, message, parse_mode="Markdown", reply_markup=markup)
    state["message_id"] = sent_msg.message_id
    user_last_message[user_id] = sent_msg.message_id

def start_bulk_processing(user_id):
    if user_id not in bulk_add_states:
        return
    
    state = bulk_add_states[user_id]
    state["is_processing"] = True
    
    edit_or_resend(
        state["chat_id"],
        state["message_id"],
        f"🚀 **Bulk Processing Started**\n\n"
        f"🌍 Country: {state['country']}\n"
        f"📱 Total: {state['total_numbers']} numbers\n"
        f"⏳ Processing first number...",
        markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("⏸️ Pause", callback_data="pause_bulk"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_bulk")
        )
    )
    
    process_next_bulk_number(user_id)

def process_next_bulk_number(user_id):
    if user_id not in bulk_add_states:
        return
    
    state = bulk_add_states[user_id]
    
    if not state.get("is_processing", True):
        return
    
    if state["current_index"] >= state["total_numbers"]:
        show_bulk_summary(user_id)
        return
    
    phone_number = state["phone_numbers"][state["current_index"]]
    state["current_phone"] = phone_number
    state["password_attempts"] = 0
    
    progress = state["current_index"] + 1
    total = state["total_numbers"]
    percentage = (progress / total) * 100
    
    edit_or_resend(
        state["chat_id"],
        state["message_id"],
        f"🔄 **Processing Number {progress}/{total}**\n\n"
        f"📱 Phone: `{phone_number}`\n"
        f"📊 Progress: {progress}/{total} ({percentage:.1f}%)\n"
        f"✅ Success: {state['success_count']}\n"
        f"❌ Failed: {state['failed_count']}\n\n"
        f"⏳ Sending OTP...",
        markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("⏸️ Pause", callback_data="pause_bulk"),
            InlineKeyboardButton("⏭️ Skip", callback_data="skip_bulk_number"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_bulk")
        )
    )
    
    send_bulk_otp(user_id, phone_number)

def send_bulk_otp(user_id, phone_number):
    try:
        if not account_manager:
            bulk_number_failed(user_id, "Account module not loaded")
            return
        
        state = bulk_add_states[user_id]
        
        result = account_manager.bulk_send_code_sync(phone_number)
        
        if result.get("success"):
            state["current_client"] = result["client"]
            state["current_phone_code_hash"] = result["phone_code_hash"]
            state["current_manager"] = result["manager"]
            state["step"] = "waiting_bulk_otp"
            
            edit_or_resend(
                state["chat_id"],
                state["message_id"],
                f"📱 Phone: `{phone_number}`\n\n"
                f"✅ OTP sent!\n"
                f"Please enter the OTP received for this number:\n\n"
                f"_(Type 'skip' to skip this number)_",
                markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("⏭️ Skip This Number", callback_data="skip_bulk_number"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_bulk")
                )
            )
        else:
            error_msg = result.get("error", "Unknown error")
            bulk_number_failed(user_id, f"Failed to send OTP: {error_msg}")
    
    except Exception as e:
        logger.error(f"Bulk send OTP error: {e}")
        bulk_number_failed(user_id, f"Error: {str(e)}")

def bulk_number_failed(user_id, reason):
    if user_id not in bulk_add_states:
        return
    
    state = bulk_add_states[user_id]
    state["failed_count"] += 1
    state["failed_numbers"].append({
        "number": state.get("current_phone", "Unknown"),
        "reason": reason
    })
    
    if state.get("current_client") and account_manager:
        try:
            asyncio.run(account_manager.pyrogram_manager.safe_disconnect(state["current_client"]))
        except:
            pass
    
    state["current_index"] += 1
    state["password_attempts"] = 0
    process_next_bulk_number(user_id)

def bulk_number_success(user_id):
    if user_id not in bulk_add_states:
        return
    
    state = bulk_add_states[user_id]
    state["success_count"] += 1
    
    if state.get("current_client") and account_manager:
        try:
            asyncio.run(account_manager.pyrogram_manager.safe_disconnect(state["current_client"]))
        except:
            pass
    
    state["current_index"] += 1
    state["password_attempts"] = 0
    process_next_bulk_number(user_id)

@bot.message_handler(func=lambda m: bulk_add_states.get(m.from_user.id, {}).get("step") == "waiting_bulk_otp")
def handle_bulk_otp_input(msg):
    user_id = msg.from_user.id
    
    if user_id not in bulk_add_states:
        return
    
    state = bulk_add_states[user_id]
    if state.get("step") != "waiting_bulk_otp":
        return
    
    otp_code = msg.text.strip()
    
    if otp_code.lower() == 'skip':
        bulk_number_failed(user_id, "Skipped by admin")
        return
    
    if not otp_code.isdigit() or len(otp_code) != 5:
        bot.send_message(
            msg.chat.id,
            "❌ Invalid OTP format. Please enter 5-digit OTP or type 'skip' to skip:"
        )
        return
    
    try:
        result = account_manager.bulk_verify_otp_sync(
            state["current_client"],
            state["current_phone"],
            state["current_phone_code_hash"],
            otp_code,
            state["current_manager"]
        )
        
        if result.get("success"):
            save_bulk_account(user_id)
        
        elif result.get("status") == "password_required":
            state["step"] = "waiting_bulk_password"
            state["password_attempts"] = 0
            
            edit_or_resend(
                state["chat_id"],
                state["message_id"],
                f"📱 Phone: `{state['current_phone']}`\n\n"
                f"🔐 2FA Password required!\n"
                f"Enter your 2-step verification password:\n\n"
                f"_(Type 'skip' to skip this number)_",
                markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("⏭️ Skip This Number", callback_data="skip_bulk_number"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_bulk")
                )
            )
        
        else:
            error_msg = result.get("error", "OTP verification failed")
            bulk_number_failed(user_id, f"OTP error: {error_msg}")
    
    except Exception as e:
        logger.error(f"Bulk OTP verification error: {e}")
        bulk_number_failed(user_id, f"OTP error: {str(e)}")

@bot.message_handler(func=lambda m: bulk_add_states.get(m.from_user.id, {}).get("step") == "waiting_bulk_password")
def handle_bulk_password_input(msg):
    user_id = msg.from_user.id
    
    if user_id not in bulk_add_states:
        return
    
    state = bulk_add_states[user_id]
    if state.get("step") != "waiting_bulk_password":
        return
    
    password = msg.text.strip()
    
    if password.lower() == 'skip':
        bulk_number_failed(user_id, "Skipped by admin")
        return
    
    if not password:
        bot.send_message(
            msg.chat.id,
            "❌ Password cannot be empty. Enter 2FA password or type 'skip' to skip:"
        )
        return
    
    state["password_attempts"] = state.get("password_attempts", 0) + 1
    
    if state["password_attempts"] > 2:
        bulk_number_failed(user_id, "Max password attempts exceeded")
        return
    
    try:
        result = account_manager.bulk_verify_password_sync(
            state["current_client"],
            password,
            state["current_manager"]
        )
        
        if result.get("success"):
            save_bulk_account(user_id, password)
        else:
            error_msg = result.get("error", "Incorrect password")
            
            if state["password_attempts"] >= 2:
                bulk_number_failed(user_id, f"Password error: {error_msg}")
            else:
                attempts_left = 2 - state["password_attempts"]
                bot.send_message(
                    msg.chat.id,
                    f"❌ Incorrect password. {attempts_left} attempt(s) left.\n"
                    f"Enter password again or type 'skip' to skip:"
                )
    
    except Exception as e:
        logger.error(f"Bulk password verification error: {e}")
        bulk_number_failed(user_id, f"Password error: {str(e)}")

def save_bulk_account(user_id, password=None):
    if user_id not in bulk_add_states:
        return
    
    state = bulk_add_states[user_id]
    
    try:
        success, message = account_manager.bulk_save_account_sync(
            state["current_client"],
            state["current_phone"],
            state["country"],
            user_id,
            state["current_manager"],
            accounts_col,
            password
        )
        
        if success:
            progress = state["current_index"] + 1
            total = state["total_numbers"]
            
            edit_or_resend(
                state["chat_id"],
                state["message_id"],
                f"✅ **Number {progress}/{total} Added Successfully!**\n\n"
                f"📱 Phone: `{state['current_phone']}`\n"
                f"🌍 Country: {state['country']}\n"
                f"🔐 2FA: {'✅ Enabled' if password else '❌ Disabled'}\n\n"
                f"📊 Progress: {progress}/{total}\n"
                f"✅ Success: {state['success_count'] + 1}\n"
                f"❌ Failed: {state['failed_count']}\n\n"
                f"⏳ Moving to next number...",
                markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("⏸️ Pause", callback_data="pause_bulk"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_bulk")
                )
            )
            
            bulk_number_success(user_id)
        
        else:
            bulk_number_failed(user_id, f"Save error: {message}")
    
    except Exception as e:
        logger.error(f"Bulk save account error: {e}")
        bulk_number_failed(user_id, f"Save error: {str(e)}")

def show_bulk_summary(user_id):
    if user_id not in bulk_add_states:
        return
    
    state = bulk_add_states[user_id]
    
    summary = f"📊 **Bulk Processing Complete!**\n\n"
    summary += f"🌍 Country: {state['country']}\n"
    summary += f"📱 Total Numbers: {state['total_numbers']}\n"
    summary += f"✅ Successfully Added: {state['success_count']}\n"
    summary += f"❌ Failed/Skipped: {state['failed_count']}\n\n"
    
    if state['failed_numbers']:
        summary += f"**Failed Numbers:**\n"
        for i, failed in enumerate(state['failed_numbers'][:10], 1):
            summary += f"{i}. {failed['number']} - {failed['reason']}\n"
        
        if len(state['failed_numbers']) > 10:
            summary += f"... and {len(state['failed_numbers']) - 10} more\n"
    
    summary += f"\n⏰ Completed at: {datetime.utcnow().strftime('%H:%M:%S')}"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 Admin Panel", callback_data="admin_panel"))
    
    edit_or_resend(
        state["chat_id"],
        state["message_id"],
        summary,
        markup=markup
    )
    
    del bulk_add_states[user_id]

# ---------------------------------------------------------------------
# EXISTING FUNCTIONS
# ---------------------------------------------------------------------

def handle_login_country_selection(call):
    user_id = call.from_user.id
    
    if user_id not in login_states:
        bot.answer_callback_query(call.id, "❌ Session expired", show_alert=True)
        return
    
    country_name = call.data.replace("login_country_", "")
    
    login_states[user_id]["country"] = country_name
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ Single Account", callback_data=f"single_account_{country_name}"),
        InlineKeyboardButton("📦 Bulk Accounts", callback_data=f"bulk_account_{country_name}")
    )
    markup.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_login"))
    
    edit_or_resend(
        call.message.chat.id,
        call.message.message_id,
        f"🌍 Country: {country_name}\n\n"
        "📱 Select account adding mode:",
        markup=markup
    )

def handle_cancel_login(call):
    user_id = call.from_user.id
    
    if user_id in login_states:
        state = login_states[user_id]
        if "client" in state:
            try:
                if account_manager and account_manager.pyrogram_manager:
                    import asyncio
                    asyncio.run(account_manager.pyrogram_manager.safe_disconnect(state["client"]))
            except:
                pass
        login_states.pop(user_id, None)
    
    edit_or_resend(
        call.message.chat.id,
        call.message.message_id,
        "❌ Login cancelled.",
        markup=None
    )
    show_admin_panel(call.message.chat.id)

def handle_logout_session(user_id, session_id, chat_id, callback_id):
    try:
        if not account_manager:
            bot.answer_callback_query(callback_id, "❌ Account module not loaded", show_alert=True)
            return
        
        bot.answer_callback_query(callback_id, "🔄 Logging out...", show_alert=False)
        success, message = account_manager.logout_session_sync(
            session_id, user_id, otp_sessions_col, accounts_col, orders_col
        )
        
        if success:
            try:
                bot.delete_message(chat_id, callback_id.message.message_id)
            except:
                pass
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu"))
            
            sent_msg = bot.send_message(
                chat_id,
                "✅ **Logged Out Successfully!**\n\n"
                "You have been logged out from this session.\n"
                "Order marked as completed.\n\n"
                "Thank you for using our service!",
                reply_markup=markup
            )
            user_last_message[user_id] = sent_msg.message_id
        else:
            bot.answer_callback_query(callback_id, f"❌ {message}", show_alert=True)
    except Exception as e:
        logger.error(f"Logout handler error: {e}")
        bot.answer_callback_query(callback_id, "❌ Error logging out", show_alert=True)

def get_latest_otp(user_id, session_id, chat_id, callback_id):
    try:
        session_data = otp_sessions_col.find_one({"session_id": session_id})
        if not session_data:
            bot.answer_callback_query(callback_id, "❌ Session not found", show_alert=True)
            return
        
        # ALWAYS fetch fresh OTP, don't use cached
        bot.answer_callback_query(callback_id, "🔍 Searching for latest OTP...", show_alert=False)
        
        session_string = session_data.get("session_string")
        if not session_string:
            bot.answer_callback_query(callback_id, "❌ No session string found", show_alert=True)
            return
        
        # Always fetch new OTP
        otp_code = account_manager.get_latest_otp_sync(session_string)
        
        if not otp_code:
            bot.answer_callback_query(callback_id, "❌ No OTP received yet. Please wait...", show_alert=True)
            return
        
        # Update database with the new OTP
        otp_sessions_col.update_one(
            {"session_id": session_id},
            {"$set": {
                "has_otp": True,
                "last_otp": otp_code,
                "last_otp_time": datetime.utcnow(),
                "status": "otp_received"
            }}
        )
        
        try:
            from logs import log_otp_received_async
            order = orders_col.find_one({"session_id": session_id})
            if order:
                log_otp_received_async(
                    user_id=user_id,
                    phone=session_data.get('phone', 'N/A'),
                    otp_code=otp_code,
                    country=order.get('country', 'Unknown'),
                    price=order.get('price', 0)
                )
        except:
            pass
        
        account_id = session_data.get("account_id")
        account = None
        two_step_password = ""
        if account_id:
            try:
                account = accounts_col.find_one({"_id": ObjectId(account_id)})
                if account:
                    two_step_password = account.get("two_step_password", "")
            except:
                pass
        
        # Build OTP message with tap-to-copy format
        fa_password = two_step_password or (account.get("two_step_password", "") if account else "")

        message = "✅ <b>Latest OTP Received!</b>\n\n"
        message += f"📱 Phone: <code>{session_data.get('phone', 'N/A')}</code>\n"
        message += f"🔢 OTP Code: <code>{otp_code}</code>\n"
        if fa_password:
            message += f"🔐 2FA Password: <code>{fa_password}</code>\n"
        message += f"\n⏰ Time: {datetime.utcnow().strftime('%H:%M:%S')}"
        message += "\n\n<i>💡 Tap any value above to copy it instantly!</i>"
        message += "\n\n📲 Open Telegram X → enter phone → enter OTP above."

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔄 Refresh OTP", callback_data=f"get_otp_{session_id}"),
            InlineKeyboardButton("🚪 Logout", callback_data=f"logout_session_{session_id}")
        )
        
        try:
            bot.edit_message_text(
                message,
                chat_id,
                callback_id.message.message_id,
                parse_mode="HTML",
                reply_markup=markup
            )
        except:
            sent_msg = bot.send_message(
                chat_id,
                message,
                parse_mode="HTML",
                reply_markup=markup
            )
            user_last_message[user_id] = sent_msg.message_id

        bot.answer_callback_query(callback_id, "✅ OTP fetched! Tap code to copy.", show_alert=False)
    except Exception as e:
        logger.error(f"Get OTP error: {e}")
        bot.answer_callback_query(callback_id, "❌ Error getting OTP", show_alert=True)

# ---------------------------------------------------------------------
# COUPON MANAGEMENT FUNCTIONS
# ---------------------------------------------------------------------

def show_coupon_management(chat_id, message_id=None):
    if not is_admin(chat_id):
        bot.send_message(chat_id, "❌ Unauthorized access")
        return
    
    text = "🎟 **Coupon Management**\n\nChoose an option:"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ Add Coupon", callback_data="admin_create_coupon"),
        InlineKeyboardButton("❌ Remove Coupon", callback_data="admin_remove_coupon")
    )
    markup.add(
        InlineKeyboardButton("📊 Coupon Status", callback_data="admin_coupon_status"),
        InlineKeyboardButton("⬅️ Back to Admin", callback_data="admin_panel")
    )
    
    if message_id:
        edit_or_resend(
            chat_id,
            message_id,
            text,
            markup=markup,
            parse_mode="Markdown"
        )
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

# ---------------------------------------------------------------------
# COUPON MESSAGE HANDLERS
# ---------------------------------------------------------------------

@bot.message_handler(func=lambda m: user_stage.get(m.from_user.id) == "waiting_coupon")
def handle_coupon_input(msg):
    user_id = msg.from_user.id
    
    if user_stage.get(user_id) != "waiting_coupon":
        return
    
    coupon_code = msg.text.strip().upper()
    user_stage.pop(user_id, None)
    
    success, result = claim_coupon(coupon_code, user_id)
    
    if success:
        amount = result
        new_balance = get_balance(user_id)
        text = f"✅ **Coupon Redeemed Successfully!**\n\n"
        text += f"🎟 Coupon Code: `{coupon_code}`\n"
        text += f"💰 Amount Added: {format_currency(amount)}\n"
        text += f"💳 New Balance: {format_currency(new_balance)}\n\n"
        text += f"Thank you for using our service! 🎉"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu"))
        
        sent_msg = bot.send_message(
            msg.chat.id,
            text,
            parse_mode="Markdown",
            reply_markup=markup
        )
        user_last_message[user_id] = sent_msg.message_id
    else:
        error_msg = result
        if error_msg == "Coupon not found":
            response = "❌ **Invalid Coupon Code**\n\n"
            response += "The coupon code you entered does not exist.\n"
            response += "Please check the code and try again."
        elif error_msg == "Already claimed":
            response = "⚠️ **Coupon Already Claimed**\n\n"
            response += "You have already claimed this coupon code.\n"
            response += "Each coupon can only be claimed once per user."
        elif error_msg == "Fully claimed":
            response = "🚫 **Coupon Fully Claimed**\n\n"
            response += "This coupon has been claimed by all eligible users.\n"
            response += "No more claims are available."
        elif error_msg in ["removed", "expired"]:
            response = f"🚫 **Coupon {error_msg.capitalize()}**\n\n"
            response += "This coupon is no longer valid for redemption.\n"
            response += "It may have been removed or expired."
        else:
            response = f"❌ **Error:** {error_msg}"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅️ Back", callback_data="back_to_menu"))
        
        sent_msg = bot.send_message(
            msg.chat.id,
            response,
            parse_mode="Markdown",
            reply_markup=markup
        )
        user_last_message[user_id] = sent_msg.message_id

@bot.message_handler(func=lambda m: coupon_state.get(m.from_user.id, {}).get("step") == "ask_code")
def handle_coupon_code_input(msg):
    user_id = msg.from_user.id
    
    if user_id not in coupon_state or coupon_state[user_id]["step"] != "ask_code":
        return
    
    if not is_admin(user_id):
        bot.send_message(msg.chat.id, "❌ Unauthorized access")
        coupon_state.pop(user_id, None)
        return
    
    code = msg.text.strip().upper()
    if not code:
        bot.send_message(msg.chat.id, "❌ Coupon code cannot be empty. Enter coupon code:")
        return
    
    existing = get_coupon(code)
    if existing:
        bot.send_message(
            msg.chat.id,
            f"❌ Coupon code `{code}` already exists.\n\nEnter a different coupon code:"
        )
        return
    
    coupon_state[user_id] = {
        "step": "ask_amount",
        "code": code
    }
    
    bot.send_message(
        msg.chat.id,
        f"🎟 Coupon Code: `{code}`\n\n"
        f"💰 Enter coupon amount (minimum ₹1):"
    )

@bot.message_handler(func=lambda m: coupon_state.get(m.from_user.id, {}).get("step") == "ask_amount")
def handle_coupon_amount_input(msg):
    user_id = msg.from_user.id
    
    if user_id not in coupon_state or coupon_state[user_id]["step"] != "ask_amount":
        return
    
    if not is_admin(user_id):
        bot.send_message(msg.chat.id, "❌ Unauthorized access")
        coupon_state.pop(user_id, None)
        return
    
    try:
        amount = float(msg.text.strip())
        if amount < 1:
            bot.send_message(msg.chat.id, "❌ Amount must be at least ₹1. Enter amount:")
            return
        
        coupon_state[user_id] = {
            "step": "ask_max_users",
            "code": coupon_state[user_id]["code"],
            "amount": amount
        }
        
        bot.send_message(
            msg.chat.id,
            f"🎟 Coupon Code: `{coupon_state[user_id]['code']}`\n"
            f"💰 Amount: {format_currency(amount)}\n\n"
            f"👥 Enter number of users who can claim this coupon (minimum 1):"
        )
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Invalid amount. Enter numbers only (e.g., 100):")

@bot.message_handler(func=lambda m: coupon_state.get(m.from_user.id, {}).get("step") == "ask_max_users")
def handle_coupon_max_users_input(msg):
    user_id = msg.from_user.id
    
    if user_id not in coupon_state or coupon_state[user_id]["step"] != "ask_max_users":
        return
    
    if not is_admin(user_id):
        bot.send_message(msg.chat.id, "❌ Unauthorized access")
        coupon_state.pop(user_id, None)
        return
    
    try:
        max_users = int(msg.text.strip())
        if max_users < 1:
            bot.send_message(msg.chat.id, "❌ Must be at least 1 user. Enter number:")
            return
        
        code = coupon_state[user_id]["code"]
        amount = coupon_state[user_id]["amount"]
        
        success, message = create_coupon(code, amount, max_users, user_id)
        
        if success:
            text = f"✅ **Coupon Created Successfully!**\n\n"
            text += f"🎟 Code: `{code}`\n"
            text += f"💰 Amount: {format_currency(amount)}\n"
            text += f"👥 Max Users: {max_users}\n\n"
            text += f"Coupon is now active and ready for users to redeem."
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🎟 Coupon Management", callback_data="admin_coupon_menu"))
            
            bot.send_message(
                msg.chat.id,
                text,
                parse_mode="Markdown",
                reply_markup=markup
            )
        else:
            bot.send_message(
                msg.chat.id,
                f"❌ Failed to create coupon: {message}\n\n"
                f"Try again or contact support."
            )
        
        coupon_state.pop(user_id, None)
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Invalid number. Enter whole numbers only (e.g., 100):")

@bot.message_handler(func=lambda m: coupon_state.get(m.from_user.id, {}).get("step") == "ask_remove_code")
def handle_coupon_remove_input(msg):
    user_id = msg.from_user.id
    
    if user_id not in coupon_state or coupon_state[user_id]["step"] != "ask_remove_code":
        return
    
    if not is_admin(user_id):
        bot.send_message(msg.chat.id, "❌ Unauthorized access")
        coupon_state.pop(user_id, None)
        return
    
    code = msg.text.strip().upper()
    
    success, message = remove_coupon(code, user_id)
    
    if success:
        text = f"✅ **Coupon Removed Successfully!**\n\n"
        text += f"🎟 Code: `{code}`\n"
        text += f"🚫 Status: Removed\n\n"
        text += f"This coupon can no longer be claimed by users."
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🎟 Coupon Management", callback_data="admin_coupon_menu"))
        
        bot.send_message(
            msg.chat.id,
            text,
            parse_mode="Markdown",
            reply_markup=markup
        )
    else:
        if message == "Coupon not found":
            response = f"❌ **Coupon Not Found**\n\n"
            response += f"Coupon code `{code}` does not exist.\n"
            response += f"Please check the code and try again."
        else:
            response = f"❌ **Error:** {message}"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🎟 Coupon Management", callback_data="admin_coupon_menu"))
        
        bot.send_message(
            msg.chat.id,
            response,
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    coupon_state.pop(user_id, None)

@bot.message_handler(func=lambda m: coupon_state.get(m.from_user.id, {}).get("step") == "ask_status_code")
def handle_coupon_status_input(msg):
    user_id = msg.from_user.id
    
    if user_id not in coupon_state or coupon_state[user_id]["step"] != "ask_status_code":
        return
    
    if not is_admin(user_id):
        bot.send_message(msg.chat.id, "❌ Unauthorized access")
        coupon_state.pop(user_id, None)
        return
    
    code = msg.text.strip().upper()
    
    status = get_coupon_status(code)
    
    if not status:
        text = f"❌ **Coupon Not Found**\n\n"
        text += f"Coupon code `{code}` does not exist.\n"
        text += f"Please check the code and try again."
    else:
        status_text = status["status"].capitalize()
        if status["status"] == "active":
            status_text = "🟢 Active"
        elif status["status"] == "expired":
            status_text = "🔴 Expired"
        elif status["status"] == "removed":
            status_text = "⚫ Removed"
        
        text = f"📊 **Coupon Details**\n\n"
        text += f"🎟 Code: `{status['code']}`\n"
        text += f"💰 Amount: {format_currency(status['amount'])}\n"
        text += f"👥 Max Users: {status['max_users']}\n"
        text += f"✅ Claimed: {status['claimed']}\n"
        text += f"🔄 Remaining: {status['remaining']}\n"
        text += f"📊 Status: {status_text}\n"
        text += f"📅 Created: {status['created_at'].strftime('%Y-%m-%d %H:%M') if status['created_at'] else 'N/A'}\n"
        
        if status['claimed'] > 0:
            text += f"\n👤 Recent Users (first 10):\n"
            for i, uid in enumerate(status['claimed_users'][:10], 1):
                text += f"{i}. User ID: {uid}\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎟 Coupon Management", callback_data="admin_coupon_menu"))
    
    bot.send_message(
        msg.chat.id,
        text,
        parse_mode="Markdown",
        reply_markup=markup
    )
    
    coupon_state.pop(user_id, None)

# ---------------------------------------------------------------------
# RECHARGE METHODS FUNCTIONS - UPDATED WITH TOTAL AND TODAY RECHARGE
# ---------------------------------------------------------------------

def show_recharge_methods(chat_id, message_id, user_id):
    total_recharge = 0
    today_recharge = 0
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    for recharge in recharges_col.find({"user_id": user_id, "status": "approved"}):
        amount = float(recharge.get("amount", 0))
        total_recharge += amount
        rd = recharge.get("created_at") or recharge.get("submitted_at")
        if rd and rd >= today_start:
            today_recharge += amount

    bal = get_balance(user_id)

    text = (
        "💎 <b>Recharge Wallet</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 <b>Current Balance:</b> {format_currency(bal)}\n"
        f"📊 <b>Total Deposited:</b> {format_currency(total_recharge)}\n"
        f"📅 <b>Today's Deposit:</b> {format_currency(today_recharge)}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "⬇️ <b>Select Payment Method:</b>"
    )

    markup = InlineKeyboardMarkup(row_width=1)
    if FAMPAY_API_KEY and FAMPAY_BASE_URL:
        markup.add(InlineKeyboardButton("⚡ UPI Auto (QR)", callback_data="recharge_fampay_auto"))
    markup.add(InlineKeyboardButton("💳 UPI Manual", callback_data="recharge_upi"))
    markup.add(InlineKeyboardButton("💎 Crypto (USDT)", callback_data="recharge_crypto"))
    markup.add(InlineKeyboardButton("⬅️ Back", callback_data="back_to_menu"))

    edit_or_resend(chat_id, message_id, text, markup=markup, parse_mode="HTML")

# ---------------------------------------------------------------------
# FAMPAY AUTO-PAY API FUNCTIONS
# ---------------------------------------------------------------------

def get_usdt_inr_rate() -> float:
    """Fetch live USDT→INR rate from CoinGecko"""
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=inr",
            timeout=8
        )
        return float(r.json()["tether"]["inr"])
    except Exception:
        return 0.0

# ═══════════════════════════════════════════════════════════════════════
# AUTO UPI (FAMPAY) — COMPLETE REWRITE
# Flow: User enters amount → API generates QR → user scans & pays →
#       background thread polls API every 6s → auto-credit on success
#       Webhook endpoint also handles instant server-push confirmation
# ═══════════════════════════════════════════════════════════════════════

def _fp_api_request(method: str, path: str, extra_params: dict = None,
                    key_param: str = None):
    """
    Central FamPay API caller.
    CONFIRMED endpoint→param mapping (tested live):
      /api/qr     → 'api'     param works
      /api/verify → 'api_key' param works
    Pass key_param to skip the fallback loop and use the correct param directly.
    """
    base = FAMPAY_BASE_URL.rstrip('/')
    url  = f"{base}{path}"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    # If caller knows the correct param, use it directly (no wasted retry)
    if key_param:
        variants = [{key_param: FAMPAY_API_KEY}]
    else:
        # Generic fallback: try api first, then api_key
        variants = [{"api": FAMPAY_API_KEY}, {"api_key": FAMPAY_API_KEY}]

    for kv in variants:
        qp = dict(kv)
        if extra_params:
            qp.update(extra_params)
        try:
            if method.upper() == "GET":
                resp = requests.get(url, params=qp, headers=headers,
                                    timeout=20, allow_redirects=True)
            else:
                resp = requests.post(url, json=qp, headers=headers,
                                     timeout=20, allow_redirects=True)

            logger.info(f"FamPay [{method} {path} param={list(kv.keys())[0]}] "
                        f"→ {resp.status_code} | {resp.text[:300]}")

            if resp.status_code not in (200, 201):
                continue
            try:
                data = resp.json()
            except Exception:
                continue
            if isinstance(data, dict) and data.get("status") == "error":
                logger.warning(f"FamPay param '{list(kv.keys())[0]}' rejected: "
                               f"{data.get('message','')}")
                continue
            return data
        except Exception as e:
            logger.warning(f"FamPay request error [{method} {url}]: {e}")
            continue
    return None


def fp_generate_order(amount: float):
    """
    Create a new FamPay payment order.
    Returns dict with order_id + qr_url, or None on failure.
    """
    amt_int = int(amount)
    base    = FAMPAY_BASE_URL.rstrip('/')

    # CONFIRMED: /api/qr with 'api' param works on legit-fampay-api
    attempts = [
        ("GET",  "/api/qr",       {"amount": amt_int}, "api"),
        ("GET",  "/api/generate", {"amount": amt_int}, None),
        ("GET",  "/api/create",   {"amount": amt_int}, None),
        ("POST", "/api/qr",       {"amount": amt_int}, "api"),
        ("POST", "/api/generate", {"amount": amt_int}, None),
    ]

    for method, path, extra, kp in attempts:
        raw = _fp_api_request(method, path, extra_params=extra, key_param=kp)
        if not raw:
            continue
        order = _fp_extract_order(raw)
        if order:
            logger.info(f"FamPay order created [{method} {path}]: {order}")
            return order

    logger.error(f"FamPay fp_generate_order: all attempts failed for amount={amt_int}")
    return None


def _fp_extract_order(raw: dict):
    """Extract order_id + qr_url from any API response shape."""
    if not isinstance(raw, dict):
        return None
    # Shape 1: {"status":"success","data":{"order_id":...,"qr_url":...}}
    if raw.get("status") == "success" and isinstance(raw.get("data"), dict):
        d = raw["data"]
        if d.get("order_id"):
            return {"order_id": d["order_id"], "qr_url": d.get("qr_url", "")}
    # Shape 2: flat {"order_id":...,"qr_url":...}
    if raw.get("order_id"):
        return {"order_id": raw["order_id"], "qr_url": raw.get("qr_url", "")}
    # Shape 3: {"success":true,"order_id":...}
    if raw.get("success") and raw.get("order_id"):
        return {"order_id": raw["order_id"], "qr_url": raw.get("qr_url", "")}
    return None


def fp_check_status(order_id: str):
    """
    Poll payment status. Returns "success" / "pending" / "expired".

    CONFIRMED: Only /api/verify with api_key param works on legit-fampay-api.
    Response format:
      pending → {"status":"pending","message":"Payment not received yet.","order_id":"...","expires_in_ms":N}
      success → {"status":"success","message":"Payment received!","order_id":"...","amount":N}
      expired → {"status":"expired", ...}
    """
    _PAID    = {"success", "paid", "completed", "credited", "done",
                "approved", "settled", "confirmed"}
    _DEAD    = {"expired", "failed", "cancelled", "canceled",
                "rejected", "refunded", "timeout", "timed_out"}

    # CONFIRMED: /api/verify with 'api_key' param works on legit-fampay-api
    raw = _fp_api_request("GET", "/api/verify",
                          extra_params={"order_id": order_id}, key_param="api_key")
    if not isinstance(raw, dict):
        logger.warning(f"FamPay verify: no response for order {order_id} — keep polling")
        return "pending"

    # Response is flat (no nested data block): {"status":"...","message":"...","order_id":"..."}
    status = str(raw.get("status") or "").strip().lower()
    logger.info(f"FamPay verify order={order_id} status={status!r} "
                f"msg={raw.get('message','')!r} expires_in_ms={raw.get('expires_in_ms','')}")

    if status in _PAID:
        return "success"
    if status in _DEAD:
        return "expired"
    # "pending" or anything else → keep polling
    return "pending"


def fp_credit_wallet(chat_id: int, user_id: int, order_id: str, amount: float):
    """
    Credit user wallet once. Thread-safe via fampay_approved_orders set.
    Saves to DB and notifies user.
    """
    if order_id in fampay_approved_orders:
        return
    fampay_approved_orders.add(order_id)
    fampay_auto_states.pop(user_id, None)

    add_balance(user_id, amount)
    new_bal = get_balance(user_id)

    # Persist to DB
    try:
        recharges_col.update_one(
            {"order_id": order_id},
            {"$set": {
                "status": "approved",
                "method": "UPI Auto",
                "auto_approved": True,
                "processed_at": datetime.utcnow(),
                "new_balance": new_bal,
            }},
            upsert=True
        )
        recharges_col.update_one(
            {"order_id": order_id},
            {"$setOnInsert": {
                "req_id": f"FP_{order_id}",
                "user_id": user_id,
                "amount": amount,
                "created_at": datetime.utcnow(),
            }},
            upsert=True
        )
    except Exception as db_err:
        logger.error(f"FamPay DB write error: {db_err}")

    # Notify user
    try:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
        bot.send_message(
            chat_id,
            f"✅ <b>Payment Confirmed!</b>\n\n"
            f"💰 <b>Amount Credited:</b> {format_currency(amount)}\n"
            f"💳 <b>New Wallet Balance:</b> {format_currency(new_bal)}\n"
            f"🆔 <b>Order:</b> <code>{order_id}</code>\n\n"
            f"🎉 Aapka wallet turant credit ho gaya!",
            parse_mode="HTML",
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"FamPay credit notify error: {e}")

    # Log to channel
    try:
        log_recharge_approved_async(user_id=user_id, amount=amount, method="UPI Auto", utr=order_id)
    except Exception:
        pass


def fp_reject_and_notify(chat_id: int, user_id: int, order_id: str, amount: float, reason: str = "expired"):
    """Tell user payment failed/expired and give admin escalation option."""
    if order_id in fampay_notified_orders:
        return
    fampay_notified_orders.add(order_id)
    fampay_auto_states.pop(user_id, None)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔄 Try Again", callback_data="recharge_fampay_auto"))
    markup.add(InlineKeyboardButton("💳 UPI Manual", callback_data="recharge_upi"))
    markup.add(InlineKeyboardButton("📞 Contact Admin", url="https://t.me/ID_GMS_SELLER_bot"))
    try:
        bot.send_message(
            chat_id,
            f"❌ <b>Payment {reason.title()}</b>\n\n"
            f"💰 <b>Amount:</b> {format_currency(amount)}\n"
            f"🆔 <b>Order:</b> <code>{order_id}</code>\n\n"
            f"Agar aapne actually pay kiya hai toh admin se contact karein "
            f"aur order ID share karein.\n\n"
            f"Warna neeche se dobara try karein:",
            parse_mode="HTML",
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"FamPay reject notify error: {e}")


def fp_poll_thread(chat_id: int, user_id: int, order_id: str, amount: float, timeout: int = 480):
    """
    Background thread: polls /api/verify every 4 seconds for up to timeout seconds.
    QR expires in 5 min; we poll for 8 min to handle edge cases.
    Credits wallet on success, notifies on expiry/timeout.
    """
    deadline = time.time() + timeout
    interval = 4          # check every 4 seconds — fast detection
    poll_count = 0
    while time.time() < deadline:
        time.sleep(interval)
        poll_count += 1
        # Cancelled by user
        if user_id in fampay_cancelled_users:
            fampay_cancelled_users.discard(user_id)
            logger.info(f"FamPay poll: user {user_id} cancelled after {poll_count} polls")
            return
        # Already handled (e.g. manual /checkpayment triggered credit)
        if order_id in fampay_approved_orders or order_id in fampay_notified_orders:
            return
        status = fp_check_status(order_id)
        logger.info(f"FamPay poll #{poll_count} [{order_id}]: {status}")
        if status == "success":
            fp_credit_wallet(chat_id, user_id, order_id, amount)
            return
        elif status == "expired":
            fp_reject_and_notify(chat_id, user_id, order_id, amount, reason="expired")
            return
        # "pending" → keep polling
    # Timeout reached
    logger.warning(f"FamPay poll timeout [{order_id}] after {poll_count} polls")
    if order_id not in fampay_approved_orders and order_id not in fampay_notified_orders:
        fp_reject_and_notify(chat_id, user_id, order_id, amount, reason="timed out")


# ── Amount input handler ──────────────────────────────────────────────

def process_fampay_auto_amount(msg):
    """User sends amount → generate order → show QR → start poll thread."""
    try:
        amount = float(msg.text.strip())
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Sirf number likhein (e.g. 100):")
        bot.register_next_step_handler(msg, process_fampay_auto_amount)
        return

    if amount < 5:
        bot.send_message(msg.chat.id, "❌ Minimum recharge ₹5 hai. Dobara enter karein:")
        bot.register_next_step_handler(msg, process_fampay_auto_amount)
        return

    user_id = msg.from_user.id

    # Animated status
    anim = bot.send_message(
        msg.chat.id,
        "⚙️ <b>UPI Auto System</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🔗 <code>FamPay server se connect ho raha hai...</code>",
        parse_mode="HTML"
    )
    time.sleep(0.8)
    try:
        bot.edit_message_text(
            "⚡ <b>QR Generate Ho Raha Hai</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 <code>₹{int(amount)} ka payment link bana raha hai...</code>",
            msg.chat.id, anim.message_id, parse_mode="HTML"
        )
    except Exception:
        pass
    time.sleep(0.7)

    order = fp_generate_order(amount)

    try:
        bot.delete_message(msg.chat.id, anim.message_id)
    except Exception:
        pass

    if not order or not order.get("order_id"):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💳 UPI Manual Try Karein", callback_data="recharge_upi"))
        bot.send_message(
            msg.chat.id,
            "❌ <b>QR Generate Nahi Hua</b>\n\n"
            "FamPay server se connection fail hua.\n"
            "Thodi der baad try karein ya UPI Manual use karein.",
            parse_mode="HTML",
            reply_markup=markup
        )
        return

    order_id = order["order_id"]
    qr_url = order.get("qr_url", "")

    # Truncate order_id for callback_data (max 64 chars total)
    cb_order = order_id[:30]

    caption = (
        f"⚡ <b>UPI Auto Pay</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Amount:</b> {format_currency(amount)}\n"
        f"🆔 <b>Order ID:</b> <code>{order_id}</code>\n\n"
        f"📋 <b>Steps:</b>\n"
        f"1️⃣ Neeche QR scan karein kisi bhi UPI app se\n"
        f"2️⃣ Exactly ₹{int(amount)} pay karein\n"
        f"3️⃣ Pay karne ke baad <b>✅ Maine Pay Kar Diya</b> dabayein\n\n"
        f"⏰ <i>QR 5 minute mein expire ho jayega</i>"
    )

    qr_markup = InlineKeyboardMarkup(row_width=1)
    qr_markup.add(
        InlineKeyboardButton("✅ Maine Pay Kar Diya — Check Karo!", callback_data=f"fp_icheck_{cb_order}"),
        InlineKeyboardButton("❌ Cancel", callback_data="back_to_menu"),
    )

    if qr_url:
        try:
            bot.send_photo(msg.chat.id, qr_url, caption=caption,
                           parse_mode="HTML", reply_markup=qr_markup)
        except Exception:
            bot.send_message(msg.chat.id,
                             caption + f"\n\n🔗 QR Link: {qr_url}",
                             parse_mode="HTML", reply_markup=qr_markup)
    else:
        bot.send_message(msg.chat.id, caption, parse_mode="HTML", reply_markup=qr_markup)

    # Waiting message with manual check button
    wait_markup = InlineKeyboardMarkup(row_width=1)
    wait_markup.add(
        InlineKeyboardButton("🔄 Manually Check Karo", callback_data=f"fp_icheck_{cb_order}"),
    )
    bot.send_message(
        msg.chat.id,
        "⏳ <b>Payment ka wait kar raha hoon...</b>\n\n"
        "✅ Pay karne ke baad upar wala button dabayein\n"
        "<i>Ya bot khud bhi har 4 second mein check karta rahega.</i>",
        parse_mode="HTML",
        reply_markup=wait_markup
    )

    # Save state in memory
    fampay_auto_states[user_id] = {
        "step": "polling",
        "amount": amount,
        "order_id": order_id,
        "chat_id": msg.chat.id,
    }

    # ── BUG FIX: Save order to MongoDB IMMEDIATELY ──────────────────
    # Webhook handler does recharges_col.find_one({"order_id":...})
    # If not in DB, webhook misses user and credit never happens.
    try:
        recharges_col.update_one(
            {"order_id": order_id},
            {"$setOnInsert": {
                "order_id": order_id,
                "user_id": user_id,
                "chat_id": msg.chat.id,
                "amount": amount,
                "method": "UPI Auto",
                "status": "pending",
                "created_at": datetime.utcnow(),
            }},
            upsert=True
        )
        logger.info(f"FamPay order saved to DB: {order_id} | user={user_id} | amount={amount}")
    except Exception as db_err:
        logger.error(f"FamPay DB pre-save error: {db_err}")

    # Start background polling thread (8 min window)
    threading.Thread(
        target=fp_poll_thread,
        args=(msg.chat.id, user_id, order_id, amount, 480),
        daemon=True
    ).start()

# ---------------------------------------------------------------------
# PROCESS RECHARGE AMOUNT FUNCTION - FIXED DATABASE ISSUE
# ---------------------------------------------------------------------

def process_recharge_amount(msg):
    try:
        amount = float(msg.text)
        if amount < 5:
            bot.send_message(msg.chat.id, "❌ Minimum recharge ₹5 hai. Dobara enter karein:")
            bot.register_next_step_handler(msg, process_recharge_amount)
            return
        
        user_id = msg.from_user.id
        
        method = recharge_method_state.get(user_id, "upi")

        if method == "upi":
            display_upi = UPI_ID if UPI_ID else "[ UPI ID not set ]"
            display_qr = QR_IMAGE_URL if QR_IMAGE_URL else None

            caption = (
                "<blockquote>💳 <b>UPI Payment Details</b>\n\n"
                f"💰 <b>Amount:</b> {format_currency(amount)}\n"
                f"📱 <b>UPI ID:</b> <code>{display_upi}</code>\n\n"
                "📋 <b>Instructions:</b>\n"
                f"1. Scan QR code OR send {format_currency(amount)} to above UPI\n"
                "2. After payment, click <b>Deposited ✅</b>\n"
                "3. Submit UTR + screenshot</blockquote>"
            )
        else:
            display_upi = FAMPAY_UPI_ID if FAMPAY_UPI_ID else "[ FamPay UPI not set ]"
            display_qr = FAMPAY_QR_URL if FAMPAY_QR_URL else None

            caption = (
                "<blockquote>💜 <b>FamPay Payment Details</b>\n\n"
                f"💰 <b>Amount:</b> {format_currency(amount)}\n"
                f"📱 <b>FamPay UPI:</b> <code>{display_upi}</code>\n\n"
                "📋 <b>Instructions:</b>\n"
                f"1. Scan QR OR send {format_currency(amount)} to above ID\n"
                "2. After payment, click <b>Deposited ✅</b>\n"
                "3. Submit UTR + screenshot</blockquote>"
            )

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💰 Deposited ✅", callback_data="upi_deposited"))

        upi_payment_states[user_id] = {
            "amount": amount,
            "step": "qr_shown"
        }

        if display_qr:
            try:
                bot.send_photo(
                    msg.chat.id,
                    display_qr,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=markup
                )
            except Exception as qr_err:
                logger.warning(f"QR photo send failed ({qr_err}), sending text fallback")
                bot.send_message(
                    msg.chat.id,
                    caption,
                    parse_mode="HTML",
                    reply_markup=markup
                )
        else:
            bot.send_message(
                msg.chat.id,
                caption,
                parse_mode="HTML",
                reply_markup=markup
            )
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Invalid amount. Enter numbers only:")
        bot.register_next_step_handler(msg, process_recharge_amount)

# FIXED UTR HANDLER - Now properly checks and stores in database
@bot.message_handler(func=lambda m: upi_payment_states.get(m.from_user.id, {}).get("step") == "waiting_utr")
def handle_utr_input(msg):
    user_id = msg.from_user.id
    
    if user_id not in upi_payment_states or upi_payment_states[user_id]["step"] != "waiting_utr":
        return
    
    utr = msg.text.strip()
    
    if not utr.isdigit() or len(utr) != 12:
        bot.send_message(msg.chat.id, "❌ Invalid UTR. Please enter a valid 12-digit UTR number:")
        return
    
    # Store UTR and move to screenshot step
    upi_payment_states[user_id]["utr"] = utr
    upi_payment_states[user_id]["step"] = "waiting_screenshot"
    
    bot.send_message(
        msg.chat.id,
        "✅ UTR Received!\n\n"
        "📸 Step 2: Send Screenshot\n\n"
        "Now please send the payment screenshot from your bank app:\n"
        "_(Make sure screenshot shows amount, date, and UTR)_"
    )

# FIXED SCREENSHOT HANDLER - Now properly saves to database
@bot.message_handler(content_types=['photo'], func=lambda m: upi_payment_states.get(m.from_user.id, {}).get("step") == "waiting_screenshot")
def handle_screenshot_input(msg):
    user_id = msg.from_user.id
    
    if user_id not in upi_payment_states or upi_payment_states[user_id]["step"] != "waiting_screenshot":
        return
    
    try:
        screenshot_file_id = msg.photo[-1].file_id
        
        amount = upi_payment_states[user_id]["amount"]
        utr = upi_payment_states[user_id].get("utr", "")
        
        # Generate unique request ID
        req_id = f"R{int(time.time())}{user_id}"
        
        # Save to database with proper fields
        recharge_data = {
            "user_id": user_id,
            "amount": amount,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "method": "upi",
            "utr": utr,
            "screenshot": screenshot_file_id,
            "submitted_at": datetime.utcnow(),
            "req_id": req_id
        }
        
        recharge_id = recharges_col.insert_one(recharge_data).inserted_id
        
        # Update with req_id
        recharges_col.update_one(
            {"_id": ObjectId(recharge_id)},
            {"$set": {"req_id": req_id}}
        )
        
        # Get all admins to send notification
        all_admins = get_all_admins()
        
        admin_caption = f"""📋 **UPI Payment Request** 

👤 User: {user_id}
💰 Amount: {format_currency(amount)}
🔢 UTR: {utr}
📅 Submitted: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
🆔 Request ID: {req_id}

✅ Both UTR and Screenshot received."""

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_rech|{req_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"cancel_rech|{req_id}")
        )
        
        # Send to all admins
        for admin in all_admins:
            admin_user_id = admin["user_id"]
            try:
                bot.send_photo(
                    admin_user_id,
                    screenshot_file_id,
                    caption=admin_caption,
                    parse_mode="HTML",
                    reply_markup=markup
                )
            except Exception as e:
                logger.error(f"Failed to send recharge notification to admin {admin_user_id}: {e}")
        
        bot.send_message(
            msg.chat.id,
            f"✅ **Payment Proof Submitted Successfully!**\n\n"
            f"📋 **Details:**\n"
            f"💰 Amount: {format_currency(amount)}\n"
            f"🔢 UTR: {utr}\n"
            f"📸 Screenshot: ✅ Received\n\n"
            f"⏳ **Status:** Admin verification pending\n"
            f"🆔 Request ID: `{req_id}`\n\n"
            f"Admin will review and approve soon. Thank you! 🎉"
        )
        
        # Log recharge request (personal)
        try:
            _ru = users_col.find_one({"user_id": user_id}) or {}
            log_personal_recharge_request_async(
                user_id=user_id,
                username=_ru.get("username") or "",
                amount=amount,
                utr=utr,
                method="UPI"
            )
        except:
            pass

        # Clear state after successful submission
        upi_payment_states.pop(user_id, None)

    except Exception as e:
        logger.error(f"Screenshot handler error: {e}")
        bot.send_message(msg.chat.id, f"❌ Error submitting payment: {str(e)}")

# =============================================================
# FAMPAY WEBHOOK ENDPOINT — instant server-push confirmation
# Registered at /fampay/webhook — FamPay calls this when paid
# =============================================================

def _fp_webhook_handler():
    """Flask route handler for FamPay webhook push."""
    import hmac as _hmac, hashlib as _hashlib
    try:
        raw_body = flask_request.get_data(as_text=True)
        # Verify webhook signature if secret set
        if FAMPAY_WEBHOOK_SECRET:
            sig = flask_request.headers.get("X-Webhook-Signature", "")
            if sig:
                body_bytes = raw_body.encode() if isinstance(raw_body, str) else raw_body
                expected = _hmac.new(
                    FAMPAY_WEBHOOK_SECRET.encode(), body_bytes, _hashlib.sha256
                ).hexdigest()
                if sig != expected:
                    logger.warning("FamPay webhook: invalid signature — ignoring")
                    return "INVALID", 403

        data = flask_request.get_json(silent=True) or {}
        order_id = data.get("order_id") or data.get("orderId", "")
        status   = (data.get("status") or "").lower()
        amount   = float(data.get("amount") or 0)
        logger.info(f"FamPay webhook received: order={order_id} status={status} amount={amount}")

        if status == "success" and order_id:
            # Find which user owns this order
            record = recharges_col.find_one({"order_id": order_id})
            if record:
                user_id  = record["user_id"]
                chat_id  = record.get("chat_id", user_id)
                amt      = record.get("amount", amount)
                fp_credit_wallet(chat_id, user_id, order_id, amt)
            else:
                # Check in-memory states
                for uid, st in list(fampay_auto_states.items()):
                    if st.get("order_id") == order_id:
                        fp_credit_wallet(st["chat_id"], uid, order_id, st["amount"])
                        break
        return "OK", 200
    except Exception as e:
        logger.error(f"FamPay webhook error: {e}")
        return "ERROR", 500

# =============================================================
# RECEIVER ID INPUT HANDLER - FIXED NAME DISPLAY
# =============================================================

@bot.message_handler(func=lambda m: user_stage.get(m.from_user.id) == "waiting_receiver_id")
def handle_receiver_id(msg):
    user_id = msg.from_user.id
    
    if user_stage.get(user_id) != "waiting_receiver_id":
        return
    
    try:
        receiver_id = int(msg.text.strip())
        
        # Check if receiver exists in database
        receiver = users_col.find_one({"user_id": receiver_id})
        if not receiver:
            bot.send_message(
                msg.chat.id,
                f"❌ User ID `{receiver_id}` not found in database!\n\nPlease enter a valid User ID:",
                parse_mode="Markdown"
            )
            return
        
        # Get receiver's name - properly formatted
        receiver_name = receiver.get("name", "Unknown")
        receiver_username = receiver.get("username", "")
        
        if receiver_username:
            receiver_display = f"{receiver_name} (@{receiver_username})"
        else:
            receiver_display = receiver_name
        
        # Store receiver info in user_states
        user_states[user_id] = {
            "receiver_id": receiver_id,
            "receiver_name": receiver_display
        }
        
        # Move to amount input
        user_stage[user_id] = "waiting_transfer_amount"
        
        balance = get_balance(user_id)
        
        message = f"📤 **Send Balance - Step 2/2**\n\n"
        message += f"👤 Receiver: {receiver_display}\n"
        message += f"🆔 Receiver ID: `{receiver_id}`\n"
        message += f"💰 Your Balance: {format_currency(balance)}\n\n"
        message += f"Please enter the **Amount** to send:"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅️ Back", callback_data="send_balance_menu"))
        
        bot.send_message(
            msg.chat.id,
            message,
            parse_mode="Markdown",
            reply_markup=markup
        )
        
    except ValueError:
        bot.send_message(
            msg.chat.id,
            "❌ Invalid User ID! Please enter a numeric ID only:\nExample: `123456789`",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Receiver ID error: {e}")
        bot.send_message(msg.chat.id, f"❌ Error: {str(e)}")

# =============================================================
# TRANSFER AMOUNT INPUT HANDLER
# =============================================================

@bot.message_handler(func=lambda m: user_stage.get(m.from_user.id) == "waiting_transfer_amount")
def handle_transfer_amount(msg):
    user_id = msg.from_user.id
    
    if user_stage.get(user_id) != "waiting_transfer_amount":
        return
    
    try:
        amount = float(msg.text.strip())
        
        # Get stored data
        transfer_data = user_states.get(user_id, {})
        receiver_id = transfer_data.get("receiver_id")
        receiver_name = transfer_data.get("receiver_name", f"ID: {receiver_id}")
        
        if not receiver_id:
            bot.send_message(msg.chat.id, "❌ Session expired! Please start again.")
            user_stage.pop(user_id, None)
            user_states.pop(user_id, None)
            return
        
        # Validate amount
        if amount <= 0:
            bot.send_message(msg.chat.id, "❌ Amount must be greater than 0!\nPlease enter valid amount:")
            return
        
        sender_balance = get_balance(user_id)
        if amount > sender_balance:
            bot.send_message(
                msg.chat.id, 
                f"❌ Insufficient balance! You have {format_currency(sender_balance)}\nPlease enter smaller amount:"
            )
            return
        
        # Update transfer data with amount
        transfer_data["amount"] = amount
        user_states[user_id] = transfer_data
        
        # Show confirmation
        confirm_message = f"📤 **Confirm Transfer**\n\n"
        confirm_message += f"👤 Receiver: {receiver_name}\n"
        confirm_message += f"🆔 Receiver ID: `{receiver_id}`\n"
        confirm_message += f"💰 Amount to Send: {format_currency(amount)}\n"
        confirm_message += f"💳 Your Balance: {format_currency(sender_balance)}\n"
        confirm_message += f"💳 Balance After: {format_currency(sender_balance - amount)}\n\n"
        confirm_message += f"Are you sure you want to proceed?"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ Confirm Transfer", callback_data="transfer_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="balance")
        )
        
        bot.send_message(
            msg.chat.id,
            confirm_message,
            parse_mode="Markdown",
            reply_markup=markup
        )
        
        user_stage.pop(user_id, None)
        
    except ValueError:
        bot.send_message(
            msg.chat.id,
            "❌ Invalid amount! Please enter numbers only:\nExample: `100`",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Transfer amount error: {e}")
        bot.send_message(msg.chat.id, f"❌ Error: {str(e)}")

# ---------------------------------------------------------------------
# EDIT PRICE FUNCTIONS
# ---------------------------------------------------------------------

def show_edit_price_country_selection(chat_id, message_id=None):
    if not is_admin(chat_id):
        bot.send_message(chat_id, "❌ Unauthorized access")
        return
    
    countries = get_all_countries()
    if not countries:
        text = "❌ No countries available to edit."
        if message_id:
            edit_or_resend(
                chat_id,
                message_id,
                text,
                markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("⬅️ Back", callback_data="manage_countries")
                )
            )
        else:
            bot.send_message(chat_id, text)
        return
    
    text = "✏️ **Edit Country Price**\n\nSelect a country to edit its price:"
    markup = InlineKeyboardMarkup(row_width=2)
    for country in countries:
        markup.add(InlineKeyboardButton(
            f"{country['name']} - {format_currency(country['price'])}",
            callback_data=f"edit_price_country_{country['name']}"
        ))
    markup.add(InlineKeyboardButton("⬅️ Back", callback_data="manage_countries"))
    
    if message_id:
        edit_or_resend(
            chat_id,
            message_id,
            text,
            markup=markup,
            parse_mode="Markdown"
        )
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

def show_edit_price_details(chat_id, message_id, country_name):
    if not is_admin(chat_id):
        bot.send_message(chat_id, "❌ Unauthorized access")
        return
    
    country = get_country_by_name(country_name)
    if not country:
        edit_or_resend(
            chat_id,
            message_id,
            f"❌ Country '{country_name}' not found.",
            markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("⬅️ Back", callback_data="edit_price")
            )
        )
        return
    
    text = f"✏️ **Edit Price for {country_name}**\n\n"
    text += f"🌍 Country: {country_name}\n"
    text += f"💰 Current Price: {format_currency(country['price'])}\n"
    text += f"📊 Available Accounts: {get_available_accounts_count(country_name)}\n\n"
    text += f"Click below to edit the price:"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        "✏️ Edit Price",
        callback_data=f"edit_price_confirm_{country_name}"
    ))
    markup.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit_price"))
    
    edit_or_resend(
        chat_id,
        message_id,
        text,
        markup=markup,
        parse_mode="Markdown"
    )

# ---------------------------------------------------------------------
# MESSAGE HANDLER FOR LOGIN FLOW
# ---------------------------------------------------------------------

@bot.message_handler(func=lambda m: login_states.get(m.from_user.id, {}).get("step") in ["phone", "waiting_otp", "waiting_password"])
def handle_login_flow_messages(msg):
    user_id = msg.from_user.id
    
    if user_id not in login_states:
        return
    
    state = login_states[user_id]
    step = state["step"]
    chat_id = state["chat_id"]
    message_id = state["message_id"]
    
    if step == "phone":
        phone = msg.text.strip()
        if not phone.startswith('+'):
            phone = '+' + phone
        if len(phone) < 6:
            bot.send_message(chat_id, "❌ Invalid phone number. Enter with country code:\nExample: +919876543210 or +86XXXXXXXXXX or +7XXXXXXXXXX")
            return
        
        if not account_manager:
            try:
                bot.edit_message_text(
                    "❌ Account module not loaded. Please contact admin.",
                    chat_id, message_id
                )
            except:
                pass
            login_states.pop(user_id, None)
            return
        
        try:
            success, message = account_manager.pyrogram_login_flow_sync(
                login_states, accounts_col, user_id, phone, chat_id, message_id, state["country"]
            )
            
            if success:
                try:
                    bot.edit_message_text(
                        f"📱 Phone: {phone}\n\n"
                        "📩 OTP sent! Enter the OTP you received:",
                        chat_id, message_id,
                        reply_markup=InlineKeyboardMarkup().add(
                            InlineKeyboardButton("❌ Cancel", callback_data="cancel_login")
                        )
                    )
                except:
                    pass
            else:
                try:
                    bot.edit_message_text(
                        f"❌ Failed to send OTP: {message}\n\nPlease try again.",
                        chat_id, message_id
                    )
                except:
                    pass
                login_states.pop(user_id, None)
        
        except Exception as e:
            logger.error(f"Login flow error: {e}")
            try:
                bot.edit_message_text(
                    f"❌ Error: {str(e)}\n\nPlease try again.",
                    chat_id, message_id
                )
            except:
                pass
            login_states.pop(user_id, None)
    
    elif step == "waiting_otp":
        otp = msg.text.strip()
        if not otp.isdigit() or not (4 <= len(otp) <= 8):
            bot.send_message(chat_id, "❌ Invalid OTP format. Enter OTP (4-8 digits):")
            return
        
        if not account_manager:
            try:
                bot.edit_message_text(
                    "❌ Account module not loaded. Please contact admin.",
                    chat_id, message_id
                )
            except:
                pass
            login_states.pop(user_id, None)
            return
        
        try:
            success, message = account_manager.verify_otp_and_save_sync(
                login_states, accounts_col, user_id, otp
            )
            
            if success:
                country = state["country"]
                phone = state["phone"]
                try:
                    bot.edit_message_text(
                        f"✅ **Account Added Successfully!**\n\n"
                        f"🌍 Country: {country}\n"
                        f"📱 Phone: {phone}\n"
                        f"🔐 Session: Generated\n\n"
                        f"Account is now available for purchase!",
                        chat_id, message_id
                    )
                except:
                    pass
                login_states.pop(user_id, None)
            
            elif message == "password_required":
                try:
                    bot.edit_message_text(
                        f"📱 Phone: {state['phone']}\n\n"
                        "🔐 2FA Password required!\n"
                        "Enter your 2-step verification password:",
                        chat_id, message_id,
                        reply_markup=InlineKeyboardMarkup().add(
                            InlineKeyboardButton("❌ Cancel", callback_data="cancel_login")
                        )
                    )
                except:
                    pass
            
            else:
                try:
                    bot.edit_message_text(
                        f"❌ OTP verification failed: {message}\n\nPlease try again.",
                        chat_id, message_id
                    )
                except:
                    pass
                login_states.pop(user_id, None)
        
        except Exception as e:
            logger.error(f"OTP verification error: {e}")
            try:
                bot.edit_message_text(
                    f"❌ Error: {str(e)}\n\nPlease try again.",
                    chat_id, message_id
                )
            except:
                pass
            login_states.pop(user_id, None)
    
    elif step == "waiting_password":
        password = msg.text.strip()
        if not password:
            bot.send_message(chat_id, "❌ Password cannot be empty. Enter 2FA password:")
            return
        
        if not account_manager:
            try:
                bot.edit_message_text(
                    "❌ Account module not loaded. Please contact admin.",
                    chat_id, message_id
                )
            except:
                pass
            login_states.pop(user_id, None)
            return
        
        try:
            success, message = account_manager.verify_2fa_password_sync(
                login_states, accounts_col, user_id, password
            )
            
            if success:
                country = state["country"]
                phone = state["phone"]
                try:
                    bot.edit_message_text(
                        f"✅ **Account Added Successfully!**\n\n"
                        f"🌍 Country: {country}\n"
                        f"📱 Phone: {phone}\n"
                        f"🔐 2FA: Enabled\n"
                        f"🔐 Session: Generated\n\n"
                        f"Account is now available for purchase!",
                        chat_id, message_id
                    )
                except:
                    pass
                login_states.pop(user_id, None)
            
            else:
                try:
                    bot.edit_message_text(
                        f"❌ 2FA password failed: {message}\n\nPlease try again.",
                        chat_id, message_id
                    )
                except:
                    pass
                login_states.pop(user_id, None)
        
        except Exception as e:
            logger.error(f"2FA verification error: {e}")
            try:
                bot.edit_message_text(
                    f"❌ Error: {str(e)}\n\nPlease try again.",
                    chat_id, message_id
                )
            except:
                pass
            login_states.pop(user_id, None)

# ---------------------------------------------------------------------
# EDIT PRICE MESSAGE HANDLER
# ---------------------------------------------------------------------

@bot.message_handler(func=lambda m: edit_price_state.get(m.from_user.id, {}).get("step") == "waiting_price")
def handle_edit_price_input(msg):
    user_id = msg.from_user.id
    
    if user_id not in edit_price_state or edit_price_state[user_id]["step"] != "waiting_price":
        return
    
    if not is_admin(user_id):
        bot.send_message(msg.chat.id, "❌ Unauthorized access")
        edit_price_state.pop(user_id, None)
        return
    
    try:
        new_price = float(msg.text.strip())
        if new_price <= 0:
            bot.send_message(msg.chat.id, "❌ Price must be greater than 0. Enter valid price:")
            return
        
        country_name = edit_price_state[user_id]["country"]
        
        result = countries_col.update_one(
            {"name": country_name, "status": "active"},
            {"$set": {"price": new_price, "updated_at": datetime.utcnow(), "updated_by": user_id}}
        )
        
        if result.modified_count > 0:
            bot.send_message(
                msg.chat.id,
                f"✅ Price updated successfully!\n\n"
                f"🌍 Country: {country_name}\n"
                f"💰 New Price: {format_currency(new_price)}\n\n"
                f"Price has been updated for all users."
            )
        else:
            bot.send_message(
                msg.chat.id,
                f"❌ Failed to update price. Country '{country_name}' not found or already has same price."
            )
        
        edit_price_state.pop(user_id, None)
        show_country_management(msg.chat.id)
    
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Invalid price format. Enter numbers only (e.g., 99.99):")

# ---------------------------------------------------------------------
# REFERRAL SYSTEM FUNCTIONS
# ---------------------------------------------------------------------

def show_referral_info(user_id, chat_id):
    user_data = users_col.find_one({"user_id": user_id}) or {}
    referral_code = user_data.get('referral_code', f'REF{user_id}')
    total_commission = user_data.get('total_commission_earned', 0)
    total_referrals = user_data.get('total_referrals', 0)
    
    referral_link = f"https://t.me/{bot.get_me().username}?start={referral_code}"
    
    message = f"👥 **Refer & Earn {REFERRAL_COMMISSION}% Commission!**\n\n"
    message += f"📊 **Your Stats:**\n"
    message += f"• Total Referrals: {total_referrals}\n"
    message += f"• Total Commission Earned: {format_currency(total_commission)}\n"
    message += f"• Commission Rate: {REFERRAL_COMMISSION}% per recharge\n\n"
    message += f"🔗 **Your Referral Link:**\n`{referral_link}`\n\n"
    message += f"📝 **How it works:**\n"
    message += f"1. Share your referral link with friends\n"
    message += f"2. When they join using your link\n"
    message += f"3. You earn {REFERRAL_COMMISSION}% of EVERY recharge they make!\n"
    message += f"4. Commission credited instantly\n\n"
    message += f"💰 **Example:** If a friend recharges ₹1000, you earn ₹{1000 * REFERRAL_COMMISSION / 100}!\n\n"
    message += f"Start sharing and earning today! 🎉"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📤 Share Link", url=f"https://t.me/share/url?url={referral_link}&text=Join%20this%20awesome%20OTP%20bot%20to%20buy%20Telegram%20accounts!"))
    markup.add(InlineKeyboardButton("⬅️ Back", callback_data="back_to_menu"))
    
    sent_msg = bot.send_message(chat_id, message, parse_mode="Markdown", reply_markup=markup)
    user_last_message[user_id] = sent_msg.message_id

# ---------------------------------------------------------------------
# ADMIN MANAGEMENT FUNCTIONS
# ---------------------------------------------------------------------

def show_admin_panel(chat_id):
    user_id = chat_id

    if not is_admin(user_id):
        bot.send_message(chat_id, "❌ Unauthorized access")
        return

    total_accounts = accounts_col.count_documents({})
    active_accounts = accounts_col.count_documents({"status": "active", "used": False})
    total_users = users_col.count_documents({})
    total_orders = orders_col.count_documents({})
    banned_users = banned_users_col.count_documents({"status": "active"})
    active_countries = countries_col.count_documents({"status": "active"})
    total_admins = get_admin_count()
    pending_recharges = recharges_col.count_documents({"status": "pending"})

    text = (
        "👑 <b>Admin Panel</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📊 <b>Live Statistics:</b>\n"
        f"├ 📦 Total Accounts: <b>{total_accounts}</b>\n"
        f"├ ✅ Available: <b>{active_accounts}</b>\n"
        f"├ 👥 Users: <b>{total_users}</b>\n"
        f"├ 🛒 Orders: <b>{total_orders}</b>\n"
        f"├ ⏳ Pending Recharges: <b>{pending_recharges}</b>\n"
        f"├ 🚫 Banned: <b>{banned_users}</b>\n"
        f"├ 🌍 Countries: <b>{active_countries}</b>\n"
        f"└ 👮 Admins: <b>{total_admins}/6</b>\n\n"
        "🛠️ <b>Management Tools:</b>"
    )

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ Add Account", callback_data="add_account"),
        InlineKeyboardButton("📢 Broadcast", callback_data="broadcast_menu")
    )
    markup.add(
        InlineKeyboardButton("💸 Refund", callback_data="refund_start"),
        InlineKeyboardButton("📊 Ranking", callback_data="ranking")
    )
    markup.add(
        InlineKeyboardButton("💬 Message User", callback_data="message_user"),
        InlineKeyboardButton("💳 Deduct Balance", callback_data="admin_deduct_start")
    )
    markup.add(
        InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
        InlineKeyboardButton("✅ Unban User", callback_data="unban_user")
    )
    markup.add(
        InlineKeyboardButton("🌍 Manage Countries", callback_data="manage_countries"),
        InlineKeyboardButton("🎟 Coupon Management", callback_data="admin_coupon_menu")
    )
    if is_super_admin(user_id):
        markup.add(
            InlineKeyboardButton("👮 Admin Permissions", callback_data="admin_permissions"),
            InlineKeyboardButton("🗑 Clean MongoDB", callback_data="cleanmongo_confirm")
        )

    # Show current admins list for super admin
    if is_super_admin(user_id):
        admins = get_all_admins()
        admin_lines = "\n\n👥 <b>Current Admins:</b>\n"
        for adm in admins:
            role = "👑 Owner" if adm.get("is_super_admin") else "👤 Admin"
            uname = adm.get("username") or "N/A"
            admin_lines += f"{role}: <code>{adm['user_id']}</code> (@{uname})\n"
        text += admin_lines

    sent_msg = bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    user_last_message[user_id] = sent_msg.message_id


def show_admin_permissions(chat_id):
    """Admin Permission Management UI"""
    if not is_super_admin(chat_id):
        bot.send_message(chat_id, "❌ Only owner can manage permissions.")
        return

    admins = get_all_admins()
    non_super = [a for a in admins if not a.get("is_super_admin")]

    text = (
        "👮 <b>Admin Permission Manager</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    PERMISSION_LABELS = {
        "can_approve_recharge": "✅ Approve Recharge",
        "can_reject_recharge": "❌ Reject Recharge",
        "can_ban_user": "🚫 Ban/Unban Users",
        "can_add_account": "➕ Add Accounts",
        "can_manage_countries": "🌍 Manage Countries",
        "can_broadcast": "📢 Broadcast",
        "can_deduct_balance": "💳 Deduct Balance",
        "can_refund": "💸 Refund",
    }

    if not non_super:
        text += "No sub-admins yet.\n\nAdd admins with /addadmin first."
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅️ Back", callback_data="admin_panel"))
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
        return

    markup = InlineKeyboardMarkup(row_width=1)
    for adm in non_super:
        uid = adm["user_id"]
        uname = adm.get("username") or str(uid)
        perms = adm.get("permissions", {})
        perm_count = sum(1 for v in perms.values() if v)
        total_perms = len(PERMISSION_LABELS)
        markup.add(InlineKeyboardButton(
            f"👤 @{uname} — {perm_count}/{total_perms} perms",
            callback_data=f"view_admin_perm_{uid}"
        ))

    markup.add(InlineKeyboardButton("⬅️ Back to Admin Panel", callback_data="admin_panel"))

    text += "Select an admin to manage their permissions:"
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


PERMISSION_LABELS = {
    "can_approve_recharge": "✅ Approve Recharge",
    "can_reject_recharge": "❌ Reject Recharge",
    "can_ban_user": "🚫 Ban/Unban",
    "can_add_account": "➕ Add Accounts",
    "can_manage_countries": "🌍 Manage Countries",
    "can_broadcast": "📢 Broadcast",
    "can_deduct_balance": "💳 Deduct Balance",
    "can_refund": "💸 Refund",
}


def show_admin_perm_detail(chat_id, target_admin_id):
    """Show permission toggles for a specific admin"""
    if not is_super_admin(chat_id):
        return
    adm = admins_col.find_one({"user_id": int(target_admin_id)})
    if not adm:
        bot.send_message(chat_id, "❌ Admin not found.")
        return
    perms = adm.get("permissions", {})
    uname = adm.get("username") or str(target_admin_id)
    text = (
        f"👤 <b>Admin: @{uname}</b>\n"
        f"🆔 ID: <code>{target_admin_id}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Toggle permissions below:"
    )
    markup = InlineKeyboardMarkup(row_width=1)
    for perm_key, perm_label in PERMISSION_LABELS.items():
        enabled = perms.get(perm_key, True)
        icon = "🟢" if enabled else "🔴"
        markup.add(InlineKeyboardButton(
            f"{icon} {perm_label}",
            callback_data=f"toggle_perm_{target_admin_id}_{perm_key}"
        ))
    markup.add(
        InlineKeyboardButton("🔓 Enable All", callback_data=f"perm_all_on_{target_admin_id}"),
        InlineKeyboardButton("🔒 Disable All", callback_data=f"perm_all_off_{target_admin_id}")
    )
    markup.add(InlineKeyboardButton("⬅️ Back", callback_data="admin_permissions"))
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


def admin_has_permission(admin_id, perm_key: str) -> bool:
    """Check if an admin has a specific permission (super admin always yes)"""
    if is_super_admin(admin_id):
        return True
    adm = admins_col.find_one({"user_id": int(admin_id)})
    if not adm:
        return False
    perms = adm.get("permissions", {})
    return perms.get(perm_key, True)

def show_country_management(chat_id, page=1, show_empty=False):
    if not is_admin(chat_id):
        bot.send_message(chat_id, "❌ Unauthorized access")
        return

    all_countries = get_all_countries()
    # By default only show countries WITH stock; show_empty=True shows 0-stock ones
    if show_empty:
        countries = [c for c in all_countries if get_available_accounts_count(c['name']) == 0]
        section_label = "📭 Empty Countries (0 Stock)"
    else:
        countries = [c for c in all_countries if get_available_accounts_count(c['name']) > 0]
        section_label = "🌍 Country Management (In Stock)"

    PAGE_SIZE = 8
    total = len(countries)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(1, min(page, total_pages))
    start_idx = (page - 1) * PAGE_SIZE
    page_countries = countries[start_idx:start_idx + PAGE_SIZE]

    markup = InlineKeyboardMarkup(row_width=1)

    if not countries:
        if show_empty:
            text = "📭 <b>Empty Countries</b>\n\n✅ Sabhi countries mein stock available hai!"
        else:
            text = "🌍 <b>Country Management</b>\n\n❌ Kisi bhi country mein stock nahi. Pehle accounts add karo."
    else:
        text = (
            f"<b>{section_label}</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━</code>\n"
            f"📋 Total: <b>{total}</b> | Page <b>{page}/{total_pages}</b>\n\n"
            f"Tap a country to see its details:"
        )
        for country in page_countries:
            cnt = get_available_accounts_count(country['name'])
            stock_icon = "✅" if cnt > 0 else "❌"
            markup.add(InlineKeyboardButton(
                f"{stock_icon} {country['name']} | {format_currency(country['price'])} | {cnt} acc",
                callback_data=f"mgmt_country_{country['name']}"
            ))

    # Pagination nav
    nav = []
    if show_empty:
        if page > 1:
            nav.append(InlineKeyboardButton("◀️ Prev", callback_data=f"mgmt_empty_page_{page-1}"))
        if page < total_pages:
            nav.append(InlineKeyboardButton("▶️ Next", callback_data=f"mgmt_empty_page_{page+1}"))
    else:
        if page > 1:
            nav.append(InlineKeyboardButton("◀️ Prev", callback_data=f"mgmt_page_{page-1}"))
        if page < total_pages:
            nav.append(InlineKeyboardButton("▶️ Next", callback_data=f"mgmt_page_{page+1}"))
    if nav:
        markup.add(*nav)

    if not show_empty:
        markup.add(InlineKeyboardButton("📭 Empty Countries", callback_data="mgmt_show_empty"))
        markup.add(
            InlineKeyboardButton("➕ Add Country", callback_data="add_country"),
            InlineKeyboardButton("✏️ Edit Price", callback_data="edit_price")
        )
        markup.add(InlineKeyboardButton("➖ Remove Country", callback_data="remove_country"))
    else:
        markup.add(
            InlineKeyboardButton("➕ Add Country", callback_data="add_country"),
            InlineKeyboardButton("➖ Remove Country", callback_data="remove_country")
        )
        markup.add(InlineKeyboardButton("📦 In-Stock Countries", callback_data="manage_countries"))

    markup.add(InlineKeyboardButton("⬅️ Back to Admin", callback_data="admin_panel"))

    sent_msg = bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    user_last_message[chat_id] = sent_msg.message_id

def ask_country_name(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Unauthorized access")
        return
    
    country_name = message.text.strip()
    user_states[message.chat.id] = {
        "step": "ask_country_price",
        "country_name": country_name
    }
    bot.send_message(message.chat.id, f"💰 Enter price for {country_name}:")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get("step") == "ask_country_price")
def ask_country_price(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Unauthorized access")
        return
    
    try:
        price = float(message.text.strip())
        user_data = user_states.get(message.chat.id)
        country_name = user_data.get("country_name")
        
        flag = get_country_flag(country_name)
        display_name = f"{flag} {country_name}"

        country_data = {
            "name": display_name,
            "price": price,
            "status": "active",
            "created_at": datetime.utcnow(),
            "created_by": message.from_user.id,
            "flag": flag
        }
        countries_col.insert_one(country_data)

        del user_states[message.chat.id]
        bot.send_message(
            message.chat.id,
            f"✅ **Country Added Successfully!**\n\n"
            f"{flag} Country: {country_name}\n"
            f"💰 Price: {format_currency(price)}\n"
            f"🏷 Saved as: {display_name}\n\n"
            f"Country is now available for users to purchase accounts."
        )
        show_country_management(message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid price. Please enter a number:")

def show_country_removal(chat_id, page=1):
    if not is_admin(chat_id):
        bot.send_message(chat_id, "❌ Unauthorized access")
        return

    countries = get_all_countries()
    if not countries:
        bot.send_message(chat_id, "❌ No countries available to remove.")
        return

    PAGE_SIZE = 8
    total = len(countries)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(1, min(page, total_pages))
    page_countries = countries[(page-1)*PAGE_SIZE : page*PAGE_SIZE]

    markup = InlineKeyboardMarkup(row_width=2)
    for country in page_countries:
        markup.add(InlineKeyboardButton(
            f"🗑 {country['name']}",
            callback_data=f"remove_country_{country['name']}"
        ))

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("◀️ Prev", callback_data=f"rmv_page_{page-1}"))
    if page < total_pages:
        nav.append(InlineKeyboardButton("▶️ Next", callback_data=f"rmv_page_{page+1}"))
    if nav:
        markup.add(*nav)

    markup.add(InlineKeyboardButton("⬅️ Back", callback_data="manage_countries"))

    sent_msg = bot.send_message(
        chat_id,
        f"🗑️ <b>Remove Country</b>\n"
        f"Page <b>{page}/{total_pages}</b> — Select a country to remove:",
        reply_markup=markup, parse_mode="HTML"
    )
    user_last_message[chat_id] = sent_msg.message_id

def remove_country(country_name, chat_id, message_id=None):
    if not is_admin(chat_id):
        return "❌ Unauthorized access"
    
    try:
        result = countries_col.update_one(
            {"name": country_name, "status": "active"},
            {"$set": {"status": "inactive", "removed_at": datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            accounts_col.delete_many({"country": country_name})
            
            if message_id:
                try:
                    bot.delete_message(chat_id, message_id)
                except:
                    pass
            
            bot.send_message(chat_id, f"✅ Country '{country_name}' and all its accounts have been removed.")
            show_country_management(chat_id)
            return f"✅ {country_name} removed successfully"
        else:
            return f"❌ Country '{country_name}' not found or already removed"
    except Exception as e:
        logger.error(f"Error removing country: {e}")
        return f"❌ Error removing country: {str(e)}"

def ask_ban_user(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Unauthorized access")
        return
    
    try:
        user_id_to_ban = int(message.text.strip())
        
        user = users_col.find_one({"user_id": user_id_to_ban})
        if not user:
            bot.send_message(message.chat.id, "❌ User not found in database.")
            return
        
        already_banned = banned_users_col.find_one({"user_id": user_id_to_ban, "status": "active"})
        if already_banned:
            bot.send_message(message.chat.id, "⚠️ User is already banned.")
            return
        
        ban_record = {
            "user_id": user_id_to_ban,
            "banned_by": message.from_user.id,
            "reason": "Admin banned",
            "status": "active",
            "banned_at": datetime.utcnow()
        }
        banned_users_col.insert_one(ban_record)

        try:
            _bu = users_col.find_one({"user_id": user_id_to_ban}) or {}
            _adm_u = users_col.find_one({"user_id": message.from_user.id}) or {}
            log_personal_ban_async(
                user_id=user_id_to_ban,
                username=_bu.get("username") or "",
                action="banned",
                admin_name=_adm_u.get("name") or f"Admin {message.from_user.id}"
            )
        except:
            pass

        bot.send_message(message.chat.id, f"✅ User {user_id_to_ban} has been banned.")

        try:
            bot.send_message(
                user_id_to_ban,
                "🚫 **Your Account Has Been Banned**\n\n"
                "You have been banned from using this bot.\n"
                "Contact admin @rchiex if you believe this is a mistake."
            )
        except:
            pass
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid user ID. Please enter numeric ID only.")

def ask_unban_user(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Unauthorized access")
        return
    
    try:
        user_id_to_unban = int(message.text.strip())
        
        ban_record = banned_users_col.find_one({"user_id": user_id_to_unban, "status": "active"})
        if not ban_record:
            bot.send_message(message.chat.id, "⚠️ User is not banned.")
            return
        
        banned_users_col.update_one(
            {"user_id": user_id_to_unban, "status": "active"},
            {"$set": {"status": "unbanned", "unbanned_at": datetime.utcnow(), "unbanned_by": message.from_user.id}}
        )
        
        bot.send_message(message.chat.id, f"✅ User {user_id_to_unban} has been unbanned.")
        
        try:
            bot.send_message(
                user_id_to_unban,
                "✅ **Your Account Has Been Unbanned**\n\n"
                "Your account access has been restored.\n"
                "You can now use the bot normally."
            )
        except:
            pass
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid user ID. Please enter numeric ID only.")

def _run_mongo_cleanup():
    """Clean expired/old data from MongoDB collections"""
    now = datetime.utcnow()

    # OTP sessions older than 2 hours
    r1 = otp_sessions_col.delete_many({"created_at": {"$lt": now - timedelta(hours=2)}})

    # Used accounts older than 30 days
    r2 = accounts_col.delete_many({"used": True, "used_at": {"$lt": now - timedelta(days=30)}})

    # Old processed recharge requests (>60 days)
    r3 = recharges_col.delete_many({
        "status": {"$in": ["approved", "cancelled"]},
        "processed_at": {"$lt": now - timedelta(days=60)}
    })

    # Old orders (>60 days)
    r4 = orders_col.delete_many({"created_at": {"$lt": now - timedelta(days=60)}})

    # Old transactions (>90 days)
    r5 = transactions_col.delete_many({"created_at": {"$lt": now - timedelta(days=90)}})

    # Old referral records (>90 days)
    r6 = referrals_col.delete_many({"created_at": {"$lt": now - timedelta(days=90)}})

    # Expired/used coupons older than 30 days
    r7 = coupons_col.delete_many({
        "status": {"$in": ["used", "expired", "disabled"]},
        "created_at": {"$lt": now - timedelta(days=30)}
    })

    return {
        "otp_sessions": getattr(r1, 'deleted_count', 0),
        "used_accounts": getattr(r2, 'deleted_count', 0),
        "old_recharges": getattr(r3, 'deleted_count', 0),
        "old_orders": getattr(r4, 'deleted_count', 0),
        "old_transactions": getattr(r5, 'deleted_count', 0),
        "old_referrals": getattr(r6, 'deleted_count', 0),
        "old_coupons": getattr(r7, 'deleted_count', 0),
    }


def _get_db_stats():
    """Return DB size info as a string"""
    try:
        stats = db.command("dbStats")
        size_mb = stats.get("dataSize", 0) / (1024 * 1024)
        storage_mb = stats.get("storageSize", 0) / (1024 * 1024)
        collections = stats.get("collections", 0)
        objects = stats.get("objects", 0)
        return f"{size_mb:.2f} MB data | {storage_mb:.2f} MB storage | {objects} docs | {collections} cols"
    except:
        return "N/A"


def _auto_cleanup_scheduler():
    """Background thread — runs cleanup every 24 hours automatically"""
    while True:
        time.sleep(86400)  # 24 hours
        try:
            results = _run_mongo_cleanup()
            total = sum(results.values())
            logger.info(f"[Auto-Cleanup] Removed {total} stale records: {results}")
        except Exception as e:
            logger.error(f"[Auto-Cleanup] Error: {e}")


def show_user_ranking(chat_id):
    if not is_admin(chat_id):
        bot.send_message(chat_id, "❌ Unauthorized access")
        return
    
    try:
        users_ranking = []
        all_wallets = wallets_col.find()
        
        for wallet in all_wallets:
            user_id_rank = wallet.get("user_id")
            balance = float(wallet.get("balance", 0))
            
            if balance > 0:
                user = users_col.find_one({"user_id": user_id_rank}) or {}
                name = user.get("name", "Unknown")
                username_db = user.get("username")
                users_ranking.append({
                    "user_id": user_id_rank,
                    "balance": balance,
                    "name": name,
                    "username": username_db
                })
        
        users_ranking.sort(key=lambda x: x["balance"], reverse=True)
        
        ranking_text = "📊 **User Ranking by Wallet Balance**\n\n"
        if not users_ranking:
            ranking_text = "📊 No users found with balance greater than zero."
        else:
            for index, user_data in enumerate(users_ranking[:20], 1):
                user_link = f"<a href='tg://user?id={user_data['user_id']}'>{user_data['user_id']}</a>"
                username_display = f"@{user_data['username']}" if user_data['username'] else "No Username"
                ranking_text += f"{index}. {user_link} - {username_display}\n"
                ranking_text += f" 💰 Balance: {format_currency(user_data['balance'])}\n\n"
        
        bot.send_message(chat_id, ranking_text, parse_mode="HTML")
    except Exception as e:
        logger.exception("Error in ranking:")
        bot.send_message(chat_id, f"❌ Error generating ranking: {str(e)}")

# ---------------------------------------------------------------------
# BROADCAST FUNCTION - NEW CLEAN SYSTEM (copy_message, users only, no forward tag)
# ---------------------------------------------------------------------

@bot.message_handler(commands=['resetbroadcast'])
def handle_resetbroadcast_command(msg):
    """Reset stuck IS_BROADCASTING flag"""
    global IS_BROADCASTING
    if not is_admin(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Unauthorized")
        return
    IS_BROADCASTING = False
    bot.send_message(msg.chat.id, "✅ Broadcast reset ho gaya. Ab naya broadcast kar sakte ho.")

@bot.message_handler(commands=['sendbroadcast'])
def handle_sendbroadcast_command(msg):
    """Handle /sendbroadcast — copies message to all users (no forward tag)"""
    global IS_BROADCASTING

    if not is_admin(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Unauthorized")
        return

    if IS_BROADCASTING:
        bot.send_message(msg.chat.id, "⚠️ Ek broadcast pehle se chal raha hai. Rukko ya /resetbroadcast karo.")
        return

    if not msg.reply_to_message:
        bot.send_message(
            msg.chat.id,
            "📢 <b>Broadcast System</b>\n\n"
            "Kisi bhi message ko reply karke yeh command bhejo:\n\n"
            "<code>/sendbroadcast</code> — Sabko bhejo (bina forward tag)\n\n"
            "Agar broadcast stuck ho jaye: <code>/resetbroadcast</code>",
            parse_mode="HTML"
        )
        return

    source = msg.reply_to_message

    status_msg = bot.send_message(
        msg.chat.id,
        "📡 <b>Broadcast Shuru Ho Raha Hai...</b>\n\n"
        "⏳ Users fetch ho rahe hain...",
        parse_mode="HTML"
    )

    IS_BROADCASTING = True

    threading.Thread(
        target=broadcast_worker,
        args=(source, msg.chat.id, status_msg.message_id),
        daemon=True
    ).start()


def broadcast_worker(source_msg, admin_chat_id, status_msg_id):
    """Broadcast worker — copy_message to all users (no 'Forwarded from' tag)"""
    global IS_BROADCASTING

    try:
        # Collect all user IDs
        user_ids = set()
        for user in users_col.find({}, {"user_id": 1}):
            uid = user.get("user_id")
            if uid:
                user_ids.add(uid)
        try:
            for adm in admins_col.find({}, {"user_id": 1}):
                aid = adm.get("user_id")
                if aid:
                    user_ids.add(aid)
        except:
            pass

        total = len(user_ids)
        sent = 0
        failed = 0

        bot.edit_message_text(
            f"📡 <b>Broadcasting...</b>\n\n"
            f"👥 Total Users: <b>{total}</b>\n"
            f"⏳ Sending...",
            admin_chat_id,
            status_msg_id,
            parse_mode="HTML"
        )

        for uid in user_ids:
            try:
                bot.copy_message(
                    chat_id=uid,
                    from_chat_id=source_msg.chat.id,
                    message_id=source_msg.message_id
                )
                sent += 1
            except Exception as e:
                failed += 1
                logger.debug(f"Broadcast skip {uid}: {e}")

            # Progress update every 25 users
            if (sent + failed) % 25 == 0:
                try:
                    bot.edit_message_text(
                        f"📡 <b>Broadcasting...</b>\n\n"
                        f"✅ Sent: <b>{sent}</b>\n"
                        f"❌ Failed: <b>{failed}</b>\n"
                        f"👥 Total: <b>{total}</b>",
                        admin_chat_id,
                        status_msg_id,
                        parse_mode="HTML"
                    )
                except:
                    pass

            time.sleep(0.05)  # Anti-flood

        # Final report
        bot.edit_message_text(
            f"✅ <b>Broadcast Complete!</b>\n\n"
            f"✅ Sent: <b>{sent}</b>\n"
            f"❌ Failed: <b>{failed}</b>\n"
            f"👥 Total: <b>{total}</b>\n"
            f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}",
            admin_chat_id,
            status_msg_id,
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Broadcast worker error: {e}")
        try:
            bot.edit_message_text(
                f"❌ <b>Broadcast Failed</b>\n\nError: {str(e)}",
                admin_chat_id,
                status_msg_id,
                parse_mode="HTML"
            )
        except:
            pass
    finally:
        IS_BROADCASTING = False

# ---------------------------------------------------------------------
# OTHER FUNCTIONS
# ---------------------------------------------------------------------

def ask_refund_user(message):
    try:
        refund_user_id = int(message.text)
        msg = bot.send_message(message.chat.id, "💰 Enter refund amount:")
        bot.register_next_step_handler(msg, process_refund, refund_user_id)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid user ID. Please enter numeric ID only.")

def process_refund(message, refund_user_id):
    try:
        amount = float(message.text)
        user = users_col.find_one({"user_id": refund_user_id})
        
        if not user:
            bot.send_message(message.chat.id, "⚠️ User not found in database.")
            return
        
        add_balance(refund_user_id, amount)
        new_balance = get_balance(refund_user_id)
        bot.send_message(
            message.chat.id,
            f"✅ Refunded {format_currency(amount)} to user {refund_user_id}\n"
            f"💰 New Balance: {format_currency(new_balance)}"
        )
        
        try:
            bot.send_message(
                refund_user_id,
                f"💸 {format_currency(amount)} refunded to your wallet!\n"
                f"💰 New Balance: {format_currency(new_balance)} ✅"
            )
        except Exception:
            bot.send_message(message.chat.id, "⚠️ Could not DM the user (maybe blocked).")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid amount entered. Please enter a number.")
    except Exception as e:
        logger.exception("Error in process_refund:")
        bot.send_message(message.chat.id, f"Error processing refund: {e}")

def ask_message_content(msg):
    try:
        target_user_id = int(msg.text)
        user_exists = users_col.find_one({"user_id": target_user_id})
        if not user_exists:
            bot.send_message(msg.chat.id, "❌ User not found in database.")
            return
        
        bot.send_message(msg.chat.id, f"💬 Now send the message (text, photo, video, or document) for user {target_user_id}:")
        bot.register_next_step_handler(msg, process_user_message, target_user_id)
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Invalid user ID. Please enter numeric ID only.")

def process_user_message(msg, target_user_id):
    try:
        text = getattr(msg, "text", None) or getattr(msg, "caption", "") or ""
        is_photo = bool(getattr(msg, "photo", None))
        is_video = getattr(msg, "video", None) is not None
        is_document = getattr(msg, "document", None) is not None
        
        try:
            if is_photo and getattr(msg, "photo", None):
                bot.send_photo(target_user_id, photo=msg.photo[-1].file_id, caption=text or "")
            elif is_video and getattr(msg, "video", None):
                bot.send_video(target_user_id, video=msg.video.file_id, caption=text or "")
            elif is_document and getattr(msg, "document", None):
                bot.send_document(target_user_id, document=msg.document.file_id, caption=text or "")
            else:
                bot.send_message(target_user_id, f"💌 Message from Admin:\n{text}")
            bot.send_message(msg.chat.id, f"✅ Message sent successfully to user {target_user_id}")
        except Exception as e:
            bot.send_message(msg.chat.id, f"❌ Failed to send message to user {target_user_id}. User may have blocked the bot.")
    except Exception as e:
        logger.exception("Error in process_user_message:")
        bot.send_message(msg.chat.id, f"Error sending message: {e}")

# ---------------------------------------------------------------------
# COUNTRY SELECTION FUNCTIONS
# ---------------------------------------------------------------------

def show_countries(chat_id, page=1):
    if not has_user_joined_channels(chat_id):
        start(bot.send_message(chat_id, "/start"))
        return

    all_countries = get_all_countries()
    # Only show countries that have at least 1 account in stock
    countries = [c for c in all_countries if get_available_accounts_count(c['name']) > 0]

    if not countries:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅️ Back", callback_data="back_to_menu"))
        sent_msg = bot.send_message(
            chat_id,
            "🌍 <b>Select Country</b>\n\n❌ Abhi koi bhi country available nahi hai. Baad mein try karo.",
            reply_markup=markup, parse_mode="HTML"
        )
        user_last_message[chat_id] = sent_msg.message_id
        return

    PAGE_SIZE = 5
    total = len(countries)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(1, min(page, total_pages))
    start_idx = (page - 1) * PAGE_SIZE
    page_countries = countries[start_idx:start_idx + PAGE_SIZE]

    bal = get_balance(chat_id)
    text = (
        "🛒 <b>Buy SpamFree Telegram accounts:</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"• <b>Total balance:</b> {format_currency(bal)}\n"
        f"• <b>Server:</b> Server (1)\n"
        f"• <b>Page {page} of {total_pages}</b>\n"
        f"<a href='https://t.me/+IV9iBTi_CSBlODU8'>✅ Successful Purchases</a>"
    )

    markup = InlineKeyboardMarkup(row_width=1)
    for country in page_countries:
        acnt = get_available_accounts_count(country['name'])
        btn_text = f"{country['name']} | {format_currency(country['price'])}"
        if acnt == 0:
            btn_text += " ❌"
        markup.add(InlineKeyboardButton(btn_text, callback_data=f"country_raw_{country['name']}"))

    # Pagination row
    nav_btns = []
    if page > 1:
        nav_btns.append(InlineKeyboardButton("◀️ Prev", callback_data=f"countries_page_{page - 1}"))
    if page < total_pages:
        nav_btns.append(InlineKeyboardButton("▶️ Next", callback_data=f"countries_page_{page + 1}"))
    if nav_btns:
        markup.add(*nav_btns)

    markup.add(InlineKeyboardButton("🏠 Home", callback_data="back_to_menu"))

    sent_msg = bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML",
                                disable_web_page_preview=True)
    user_last_message[chat_id] = sent_msg.message_id

def show_country_details(user_id, country_name, chat_id, message_id, callback_id):
    try:
        country = get_country_by_name(country_name)
        if not country:
            bot.answer_callback_query(callback_id, "❌ Country not found", show_alert=True)
            return

        accounts_count = get_available_accounts_count(country_name)
        bal = get_balance(user_id)
        flag = get_country_flag(country_name)

        text = (
            f"<blockquote>"
            f"🌍 <b>Country:</b> {country_name} {flag}\n"
            f"📦 <b>Stock:</b> {accounts_count} accounts\n"
            f"💰 <b>Price:</b> {format_currency(country['price'])}"
            f"</blockquote>\n\n"
            f"💵 <b>Your Balance:</b> {format_currency(bal)}\n\n"
        )

        if bal < country['price']:
            shortage = country['price'] - bal
            text += (
                f"❌ <b>Insufficient Balance!</b>\n"
                f"Shortage: {format_currency(shortage)}\n\n"
            )

        markup = InlineKeyboardMarkup(row_width=1)
        if accounts_count > 0:
            accounts = list(accounts_col.find({
                "country": {"$regex": f"^{re.escape(country_name)}$", "$options": "i"},
                "status": "active", "used": False
            }))
            buy_cb = f"buy_{accounts[0]['_id']}" if accounts else "out_of_stock"
            markup.add(InlineKeyboardButton("🛒 Buy Account", callback_data=buy_cb))
        else:
            markup.add(InlineKeyboardButton("❌ Out of Stock", callback_data="out_of_stock"))

        if bal < country['price']:
            markup.add(InlineKeyboardButton("💳 Recharge", callback_data="recharge"))

        markup.add(
            InlineKeyboardButton("⬅️ Back", callback_data="back_to_countries"),
            InlineKeyboardButton("🏠 Home", callback_data="back_to_menu")
        )

        edit_or_resend(chat_id, message_id, text, markup=markup, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Country details error: {e}")
        bot.answer_callback_query(callback_id, "❌ Error loading country details", show_alert=True)

# ---------------------------------------------------------------------
# PROCESS PURCHASE FUNCTION
# ---------------------------------------------------------------------

def process_purchase(user_id, account_id, chat_id, message_id, callback_id):
    try:
        try:
            account = accounts_col.find_one({"_id": ObjectId(account_id)})
        except Exception:
            account = accounts_col.find_one({"_id": account_id})
        
        if not account:
            bot.answer_callback_query(callback_id, "❌ Account not available", show_alert=True)
            return
        
        if account.get('used', False):
            bot.answer_callback_query(callback_id, "❌ Account already sold out", show_alert=True)
            try:
                bot.delete_message(chat_id, message_id)
            except:
                pass
            show_countries(chat_id)
            return
        
        country = get_country_by_name(account['country'])
        if not country:
            bot.answer_callback_query(callback_id, "❌ Country not found", show_alert=True)
            return
        
        price = country['price']
        balance = get_balance(user_id)
        
        if balance < price:
            needed = price - balance
            bot.answer_callback_query(
                callback_id,
                f"❌ Insufficient balance!\nNeed: {format_currency(price)}\nHave: {format_currency(balance)}\nRequired: {format_currency(needed)} more",
                show_alert=True
            )
            return
        
        deduct_balance(user_id, price)
        
        try:
            from logs import log_purchase_async
            log_purchase_async(
                user_id=user_id,
                country=account['country'],
                price=price,
                phone=account.get('phone', 'N/A')
            )
        except:
            pass
        
        session_id = f"otp_{user_id}_{int(time.time())}"
        otp_session = {
            "session_id": session_id,
            "user_id": user_id,
            "phone": account['phone'],
            "session_string": account.get('session_string', ''),
            "status": "active",
            "created_at": datetime.utcnow(),
            "account_id": str(account['_id']),
            "has_otp": False,
            "last_otp": None,
            "last_otp_time": None
        }
        otp_sessions_col.insert_one(otp_session)
        
        order = {
            "user_id": user_id,
            "account_id": str(account.get('_id')),
            "country": account['country'],
            "price": price,
            "phone_number": account.get('phone', 'N/A'),
            "session_id": session_id,
            "status": "waiting_otp",
            "created_at": datetime.utcnow(),
            "monitoring_duration": 1800
        }
        order_id = orders_col.insert_one(order).inserted_id
        
        try:
            accounts_col.update_one(
                {"_id": account.get('_id')},
                {"$set": {"used": True, "used_at": datetime.utcnow()}}
            )
        except Exception:
            accounts_col.update_one(
                {"_id": ObjectId(account_id)},
                {"$set": {"used": True, "used_at": datetime.utcnow()}}
            )
        
        def start_simple_monitoring():
            try:
                account_manager.start_simple_monitoring_sync(
                    account.get('session_string', ''),
                    session_id,
                    1800
                )
            except Exception as e:
                logger.error(f"Simple monitoring error: {e}")
        
        thread = threading.Thread(target=start_simple_monitoring, daemon=True)
        thread.start()
        
        phone = account.get('phone', 'N/A')
        fa_pass = account.get('two_step_password', '')
        fa_line = f"\n🔐 <b>2FA Password:</b> <code>{fa_pass}</code>" if fa_pass else ""
        remaining_bal = get_balance(user_id)

        account_details = (
            "✅ <b>Purchase Successful!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>"
            f"🌍 <b>Country:</b> {account['country']}\n"
            f"💸 <b>Price:</b> {format_currency(price)}\n"
            f"📱 <b>Phone:</b> <code>{phone}</code>{fa_line}\n"
            f"💰 <b>Balance Left:</b> {format_currency(remaining_bal)}"
            f"</blockquote>\n\n"
            "📲 <b>Instructions:</b>\n"
            "1️⃣ Open <b>Telegram X</b> app\n"
            f"2️⃣ Enter phone: <code>{phone}</code>\n"
            "3️⃣ Click <b>Next</b> → then click <b>Get OTP</b> below\n\n"
            "⏳ OTP valid for <b>30 minutes</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "💬 Join our community for updates:\n"
            "<a href='https://t.me/+IV9iBTi_CSBlODU8'>👥 Legend OTP Community</a>"
        )

        get_otp_markup = InlineKeyboardMarkup(row_width=2)
        get_otp_markup.add(
            InlineKeyboardButton("🔢 Get OTP", callback_data=f"get_otp_{session_id}"),
            InlineKeyboardButton("🏠 Home", callback_data="back_to_menu")
        )
        get_otp_markup.add(
            InlineKeyboardButton("👥 Join Community", url="https://t.me/+IV9iBTi_CSBlODU8")
        )

        # Personal log — full detail
        try:
            udata = users_col.find_one({"user_id": user_id}) or {}
            log_personal_purchase_async(
                user_id=user_id,
                username=udata.get("username", ""),
                country=account['country'],
                price=price,
                phone=phone
            )
        except:
            pass

        sent_msg = edit_or_resend(
            chat_id,
            message_id,
            account_details,
            markup=get_otp_markup,
            parse_mode="HTML"
        )
        
        if sent_msg:
            user_last_message[user_id] = sent_msg.message_id
        
        bot.answer_callback_query(callback_id, "✅ Purchase successful! Click Get OTP when needed.", show_alert=True)
    
    except Exception as e:
        logger.error(f"Purchase error: {e}")
        try:
            bot.answer_callback_query(callback_id, "❌ Purchase failed", show_alert=True)
        except:
            pass

# =============================================================
# RESTART COMMAND (VPS + HEROKU SAFE)
# =============================================================
# /stats COMMAND — Admin dashboard
# =============================================================

@bot.message_handler(commands=['stats'])
def cmd_stats(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Sirf admin use kar sakta hai!")
        return
    try:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        total_users   = users_col.count_documents({})
        new_today     = users_col.count_documents({"created_at": {"$gte": today_start}})
        banned_count  = banned_users_col.count_documents({"status": "banned"})

        total_orders  = orders_col.count_documents({})
        today_orders  = orders_col.count_documents({"created_at": {"$gte": today_start}})

        revenue_pipe  = [{"$group": {"_id": None, "total": {"$sum": "$price"}}}]
        rev_all       = list(orders_col.aggregate(revenue_pipe))
        total_revenue = rev_all[0]["total"] if rev_all else 0

        rev_today_pipe = [
            {"$match": {"created_at": {"$gte": today_start}}},
            {"$group": {"_id": None, "total": {"$sum": "$price"}}}
        ]
        rev_today_res  = list(orders_col.aggregate(rev_today_pipe))
        today_revenue  = rev_today_res[0]["total"] if rev_today_res else 0

        pending_rc    = recharges_col.count_documents({"status": "pending"})
        approved_rc   = recharges_col.count_documents({"status": "approved"})

        total_accounts  = accounts_col.count_documents({})
        active_accounts = accounts_col.count_documents({"status": "active", "used": False})
        sold_accounts   = accounts_col.count_documents({"used": True})

        total_admins = admins_col.count_documents({})

        t = now.strftime("%d-%m-%Y %H:%M UTC")

        text = (
            f"📊 <b>BOT STATS DASHBOARD</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
            f"<b>👥 USERS</b>\n"
            f"  • Total: <b>{total_users}</b>\n"
            f"  • Aaj Naye: <b>{new_today}</b>\n"
            f"  • Banned: <b>{banned_count}</b>\n"
            f"  • Admins: <b>{total_admins}</b>\n\n"
            f"<b>🛒 ORDERS</b>\n"
            f"  • Total: <b>{total_orders}</b>\n"
            f"  • Aaj: <b>{today_orders}</b>\n\n"
            f"<b>💰 REVENUE</b>\n"
            f"  • Total: <b>₹{total_revenue:,.2f}</b>\n"
            f"  • Aaj: <b>₹{today_revenue:,.2f}</b>\n\n"
            f"<b>💳 RECHARGES</b>\n"
            f"  • Pending: <b>{pending_rc}</b>\n"
            f"  • Approved: <b>{approved_rc}</b>\n\n"
            f"<b>📱 ACCOUNTS (Stock)</b>\n"
            f"  • Total: <b>{total_accounts}</b>\n"
            f"  • Active: <b>{active_accounts}</b>\n"
            f"  • Sold: <b>{sold_accounts}</b>\n\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"⏰ <i>{t}</i>\n"
            f"🤖 @LEGENDARY_OTP_SELLER_Bot"
        )
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"/stats error: {e}")
        bot.send_message(message.chat.id, f"❌ Stats load karne mein error: {e}")


# =============================================================
# /loadallcountries — Admin: load all 195+ world countries into DB
# =============================================================

@bot.message_handler(commands=['loadallcountries'])
def cmd_load_all_countries(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Sirf admin use kar sakta hai!")
        return

    # Parse optional default price from command: /loadallcountries 5
    parts = message.text.strip().split()
    try:
        default_price = float(parts[1]) if len(parts) > 1 else 5.0
    except ValueError:
        default_price = 5.0

    bot.send_message(message.chat.id, "⏳ Loading all world countries... please wait.")

    added = 0
    skipped = 0
    try:
        for name, dial_code, flag in WORLD_COUNTRIES_LIST:
            display_name = f"{flag} {name}"
            existing = countries_col.find_one({"name": {"$regex": f"^{re.escape(display_name)}$", "$options": "i"}})
            if existing:
                skipped += 1
                continue
            # Also check without flag
            existing2 = countries_col.find_one({"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}})
            if existing2:
                skipped += 1
                continue
            countries_col.insert_one({
                "name": display_name,
                "price": default_price,
                "status": "active",
                "dial_code": dial_code,
                "flag": flag,
                "created_at": datetime.utcnow(),
                "created_by": user_id,
                "global": True,
            })
            added += 1

        total_now = countries_col.count_documents({"status": "active"})
        bot.send_message(
            message.chat.id,
            f"✅ <b>All World Countries Loaded!</b>\n\n"
            f"🌍 Added: <b>{added}</b> new countries\n"
            f"⏭️ Already existed (skipped): <b>{skipped}</b>\n"
            f"📊 Total active countries: <b>{total_now}</b>\n\n"
            f"💰 Default price set: <b>₹{default_price}</b>\n"
            f"✏️ Use /editprice to change any country's price\n\n"
            f"<i>Tip: /loadallcountries 10 — 10 rupees default price</i>",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"/loadallcountries error: {e}")
        bot.send_message(message.chat.id, f"❌ Error: {e}")


# =============================================================
# /clearaccounts COMMAND — Admin: clear stock accounts
# =============================================================

@bot.message_handler(commands=['clearaccounts'])
def cmd_clearaccounts(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Sirf admin use kar sakta hai!")
        return
    try:
        total  = accounts_col.count_documents({})
        active = accounts_col.count_documents({"status": "active", "used": False})
        sold   = accounts_col.count_documents({"used": True})
    except:
        total = active = sold = 0

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(f"🗑️ Sirf Sold accounts clear karo ({sold})", callback_data="clearacc_sold"),
        InlineKeyboardButton(f"🗑️ Sirf Active accounts clear karo ({active})", callback_data="clearacc_active"),
        InlineKeyboardButton(f"⚠️ Sab clear karo ({total} total)", callback_data="clearacc_all"),
        InlineKeyboardButton("❌ Cancel", callback_data="admin_panel"),
    )
    bot.send_message(
        message.chat.id,
        f"🗑️ <b>Clear Accounts</b>\n\n"
        f"📱 Total Stock: <b>{total}</b>\n"
        f"✅ Active: <b>{active}</b>\n"
        f"💰 Sold: <b>{sold}</b>\n\n"
        f"<b>Kya clear karna hai?</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )


# =============================================================

@bot.message_handler(commands=['dbstats'])
def cmd_dbstats(message):
    user_id = message.from_user.id
    if not is_super_admin(user_id):
        bot.reply_to(message, "❌ Only owner can run this command.")
        return
    try:
        stats = db.command("dbStats")
        data_mb    = stats.get("dataSize", 0)    / (1024 * 1024)
        storage_mb = stats.get("storageSize", 0) / (1024 * 1024)
        index_mb   = stats.get("indexSize", 0)   / (1024 * 1024)
        total_docs = stats.get("objects", 0)
        num_cols   = stats.get("collections", 0)

        # Per-collection breakdown
        col_lines = []
        col_names = [
            ("users",        users_col),
            ("accounts",     accounts_col),
            ("orders",       orders_col),
            ("wallets",      wallets_col),
            ("recharges",    recharges_col),
            ("otp_sessions", otp_sessions_col),
            ("transactions", transactions_col),
            ("referrals",    referrals_col),
            ("coupons",      coupons_col),
            ("banned_users", banned_users_col),
            ("admins",       admins_col),
        ]
        for name, col in col_names:
            try:
                cs = db.command("collStats", name)
                c_size = cs.get("size", 0) / 1024
                c_docs = cs.get("count", 0)
                col_lines.append(f"  <code>{name:<14}</code> {c_docs:>6} docs  {c_size:>7.1f} KB")
            except:
                col_lines.append(f"  <code>{name:<14}</code>  —")

        # Warning logic
        WARNING_MB = 400
        DANGER_MB  = 450
        if data_mb >= DANGER_MB:
            status = "🔴 <b>DANGER — DB almost full! Run /clean now!</b>"
        elif data_mb >= WARNING_MB:
            status = "🟡 <b>WARNING — DB getting full. Consider /clean.</b>"
        else:
            status = "🟢 <b>DB healthy</b>"

        col_text = "\n".join(col_lines)
        text = (
            f"📦 <b>MongoDB Stats</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
            f"{status}\n\n"
            f"<b>💾 Storage</b>\n"
            f"  Data:     <b>{data_mb:.2f} MB</b>\n"
            f"  Storage:  <b>{storage_mb:.2f} MB</b>\n"
            f"  Indexes:  <b>{index_mb:.2f} MB</b>\n"
            f"  Docs:     <b>{total_docs:,}</b>\n"
            f"  Cols:     <b>{num_cols}</b>\n\n"
            f"<b>📋 Collections</b>\n"
            f"{col_text}\n\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"💡 <i>Run /clean to free up space</i>"
        )
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"/dbstats error: {e}")
        bot.send_message(message.chat.id, f"❌ Error fetching DB stats: {e}")


@bot.message_handler(commands=['emptycountries'])
def cmd_empty_countries(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Sirf admins ke liye.")
        return
    all_countries = get_all_countries()
    empty = [c for c in all_countries if get_available_accounts_count(c['name']) == 0]
    if not empty:
        bot.reply_to(message, "✅ <b>Sabhi countries mein stock available hai!</b>\nKoi bhi country 0-stock nahi hai.", parse_mode="HTML")
        return
    lines = "\n".join([f"• {c['name']} — {format_currency(c['price'])}" for c in empty])
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📭 Manage Empty Countries", callback_data="mgmt_show_empty"))
    bot.send_message(
        message.chat.id,
        f"📭 <b>0-Stock Countries ({len(empty)} total):</b>\n\n{lines}",
        reply_markup=markup, parse_mode="HTML"
    )

@bot.message_handler(commands=['cleanempty'])
def cmd_clean_empty_countries(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Sirf admins ke liye.")
        return
    all_countries = get_all_countries()
    empty = [c for c in all_countries if get_available_accounts_count(c['name']) == 0]
    if not empty:
        bot.reply_to(message,
            "✅ <b>Kuch bhi remove nahi karna!</b>\nSabhi countries mein stock available hai.",
            parse_mode="HTML")
        return
    lines = "\n".join([f"• {c['name']} — {format_currency(c['price'])}" for c in empty])
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(
            f"🗑️ Haan, {len(empty)} empty countries remove karo",
            callback_data="cleanempty_confirm"
        ),
        InlineKeyboardButton("❌ Cancel", callback_data="admin_panel")
    )
    bot.send_message(
        message.chat.id,
        f"⚠️ <b>Yeh {len(empty)} 0-stock countries permanently delete ho jaayengi:</b>\n\n"
        f"{lines}\n\n"
        f"<b>Confirm karo?</b>",
        reply_markup=markup, parse_mode="HTML"
    )

@bot.message_handler(commands=['cleanmongo', 'clean'])
def cmd_cleanmongo(message):
    user_id = message.from_user.id
    if not is_super_admin(user_id):
        bot.reply_to(message, "❌ Only owner can run this command.")
        return
    db_info = _get_db_stats()
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Yes, Clean Now", callback_data="cleanmongo_run"),
        InlineKeyboardButton("❌ Cancel", callback_data="admin_panel")
    )
    bot.send_message(
        message.chat.id,
        "🧹 <b>MongoDB Cleanup</b>\n\n"
        f"💾 <b>Current DB:</b> <code>{db_info}</code>\n\n"
        "Yeh delete hoga:\n"
        "• OTP sessions &gt; 2 ghante purane\n"
        "• Used accounts &gt; 30 din purane\n"
        "• Old recharges &gt; 60 din purane\n"
        "• Old orders &gt; 60 din purane\n"
        "• Old transactions &gt; 90 din purane\n"
        "• Old referrals &gt; 90 din purane\n"
        "• Used/expired coupons &gt; 30 din purane\n\n"
        "<b>Confirm karo?</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )


@bot.message_handler(commands=['cancel'])
def cancel_command(msg):
    """Clear ALL pending states and return to main menu with animation"""
    user_id = msg.from_user.id
    chat_id = msg.chat.id

    # ── Animation frames ──────────────────────────────────────────────
    frames = [
        "⏳ <b>Cancelling...</b>",
        "🔄 <b>Clearing all pending tasks...</b>",
        "🗑️ <b>Removing active sessions...</b>",
        "✅ <b>All tasks cancelled!</b>\n\n↩️ Returning to main menu...",
    ]
    _anim(chat_id, frames, delay=0.55)

    # ── Stop FamPay background poll thread ───────────────────────────
    fampay_cancelled_users.add(user_id)

    # ── Cancel any pending DB recharge requests ───────────────────────
    try:
        recharges_col.update_many(
            {"user_id": user_id, "status": "pending"},
            {"$set": {"status": "cancelled_by_user"}}
        )
    except Exception:
        pass

    # ── Clear ALL in-memory state dicts ──────────────────────────────
    for _d in (
        upi_payment_states, fampay_auto_states, recharge_method_state,
        login_states, edit_price_state, coupon_state, admin_deduct_state,
        cancellation_trackers, admin_add_state, admin_remove_state,
        broadcast_data, user_states, pending_messages, active_chats,
        user_last_message, user_orders, order_messages, order_timers,
        change_number_requests, whatsapp_number_timers, payment_orders,
        referral_data, bulk_add_states, recharge_approvals,
    ):
        try:
            _d.pop(user_id, None)
        except Exception:
            pass

    # user_stage uses both user_id AND chat_id as keys
    user_stage.pop(user_id, None)
    user_stage.pop(chat_id, None)

    # ── Clear telebot next-step handlers ─────────────────────────────
    try:
        bot.clear_step_handler_by_chat_id(chat_id)
    except Exception:
        pass

    # ── Back to main menu ─────────────────────────────────────────────
    clean_ui_and_send_menu(chat_id, user_id)

@bot.message_handler(commands=['restart'])
def restart_bot(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        bot.reply_to(message, "❌ Sirf admin use kar sakta hai!")
        return

    bot.reply_to(message, "♻️ Restarting bot...")

    logger.info(f"Admin {user_id} triggered restart")

    time.sleep(1)

    # Clean restart
    os.execv(sys.executable, ['python'] + sys.argv)

# ---------------------------------------------------------------------
# ANIMATED HELPER
# ---------------------------------------------------------------------

def _anim(chat_id, frames, delay=0.7):
    """Send animated message — shows each frame with delay"""
    try:
        m = bot.send_message(chat_id, frames[0], parse_mode="HTML")
        for f in frames[1:]:
            time.sleep(delay)
            try:
                bot.edit_message_text(f, chat_id, m.message_id, parse_mode="HTML")
            except: pass
        return m
    except Exception as e:
        logger.error(f"_anim error: {e}")

# ---------------------------------------------------------------------
# 40 USER & ADMIN COMMANDS WITH ANIMATIONS
# ---------------------------------------------------------------------

@bot.message_handler(commands=['help'])
def cmd_help(msg):
    user_id = msg.from_user.id
    frames = [
        "⏳ <b>Loading Help...</b>",
        "📖 <b>Loading Guide...</b>\n━━━━━━━━━━━━━━━━━━━━━",
        (
            "📖 <b>LEGENDARY OTP BOT — HELP</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🛒 /buy — Account kharido\n"
            "💰 /balance — Wallet balance\n"
            "💳 /recharge — Paisa add karo\n"
            "👥 /refer — Referral link lo\n"
            "🎁 /redeem — Coupon lagao\n"
            "👤 /profile — Apna profile\n"
            "📋 /history — Transactions\n"
            "🌍 /countries — Available countries\n"
            "💡 /prices — Price list\n"
            "❓ /faq — Common questions\n"
            "📜 /rules — Bot rules\n"
            "🛠️ /support — Admin se baat\n"
            "❌ /cancel — Koi bhi kaam band karo\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "💎 <i>Legendary OTP Bot — Always #1</i>"
        )
    ]
    _anim(msg.chat.id, frames)

@bot.message_handler(commands=['id'])
def cmd_id(msg):
    uid = msg.from_user.id
    uname = msg.from_user.username or "N/A"
    fname = msg.from_user.first_name or "User"
    frames = [
        "🔍 <b>Fetching your ID...</b>",
        (
            "🪪 <b>YOUR TELEGRAM INFO</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Name:</b> {fname}\n"
            f"🆔 <b>User ID:</b> <code>{uid}</code>\n"
            f"📛 <b>Username:</b> @{uname}\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 <i>Apna ID copy karne ke liye upar tap karein</i>"
        )
    ]
    _anim(msg.chat.id, frames, delay=0.6)

@bot.message_handler(commands=['ping'])
def cmd_ping(msg):
    import time as _t
    t0 = _t.time()
    frames = [
        "📡 <b>Pinging...</b> 🏓",
        "📡 <b>Ping Pong!</b> 🏓\n⚡ Calculating...",
    ]
    m = bot.send_message(msg.chat.id, frames[0], parse_mode="HTML")
    time.sleep(0.5)
    ms = int((_t.time() - t0) * 1000)
    emoji = "🟢" if ms < 300 else ("🟡" if ms < 700 else "🔴")
    try:
        bot.edit_message_text(
            f"🏓 <b>PONG!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{emoji} <b>Response Time:</b> <code>{ms}ms</code>\n"
            f"✅ <b>Bot Status:</b> Online & Active\n"
            f"🚀 <b>Server:</b> Replit Cloud\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>⚡ Legendary OTP Bot — Always Fast!</i>",
            msg.chat.id, m.message_id, parse_mode="HTML"
        )
    except: pass

@bot.message_handler(commands=['status'])
def cmd_status(msg):
    frames = [
        "⚙️ <b>System Check...</b>",
        "⚙️ <b>Checking MongoDB...</b> 🔄",
        "⚙️ <b>Checking Accounts...</b> 🔄",
    ]
    m = bot.send_message(msg.chat.id, frames[0], parse_mode="HTML")
    time.sleep(0.6)
    try:
        bot.edit_message_text(frames[1], msg.chat.id, m.message_id, parse_mode="HTML")
    except: pass
    time.sleep(0.6)
    try:
        bot.edit_message_text(frames[2], msg.chat.id, m.message_id, parse_mode="HTML")
    except: pass
    time.sleep(0.6)
    try:
        total_users = users_col.count_documents({})
        total_accounts = accounts_col.count_documents({"status": "active", "used": False})
        total_countries = countries_col.count_documents({"status": "active"})
        db_ok = "🟢 Online"
    except:
        db_ok = "🔴 Error"
        total_users = total_accounts = total_countries = "?"
    try:
        bot.edit_message_text(
            f"📊 <b>BOT LIVE STATUS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <b>Bot:</b> 🟢 Online\n"
            f"🗄️ <b>Database:</b> {db_ok}\n"
            f"👥 <b>Total Users:</b> {total_users}\n"
            f"📱 <b>Available Accounts:</b> {total_accounts}\n"
            f"🌍 <b>Active Countries:</b> {total_countries}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>⚡ Everything running smooth!</i>",
            msg.chat.id, m.message_id, parse_mode="HTML"
        )
    except: pass

@bot.message_handler(commands=['profile'])
def cmd_profile(msg):
    user_id = msg.from_user.id
    fname = msg.from_user.first_name or "User"
    frames = [
        "👤 <b>Loading Profile...</b>",
        "👤 <b>Fetching your data...</b> ⏳",
    ]
    m = bot.send_message(msg.chat.id, frames[0], parse_mode="HTML")
    time.sleep(0.7)
    try:
        bot.edit_message_text(frames[1], msg.chat.id, m.message_id, parse_mode="HTML")
    except: pass
    time.sleep(0.6)
    try:
        bal = get_balance(user_id)
        user_data = users_col.find_one({"user_id": user_id}) or {}
        uname = user_data.get("username") or msg.from_user.username or "N/A"
        joined = user_data.get("created_at")
        joined_str = joined.strftime("%d %b %Y") if joined else "N/A"
        referrals = user_data.get("referral_count", 0)
        bot.edit_message_text(
            f"👤 <b>MY PROFILE</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📛 <b>Name:</b> {fname}\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            f"📛 <b>Username:</b> @{uname}\n"
            f"💰 <b>Wallet:</b> {format_currency(bal)}\n"
            f"👥 <b>Referrals:</b> {referrals}\n"
            f"📅 <b>Joined:</b> {joined_str}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>🌟 Legendary OTP Bot Member</i>",
            msg.chat.id, m.message_id, parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Profile cmd error: {e}")

@bot.message_handler(commands=['history'])
def cmd_history(msg):
    user_id = msg.from_user.id
    frames = ["📋 <b>Loading History...</b>", "📋 <b>Fetching transactions...</b> ⏳"]
    m = bot.send_message(msg.chat.id, frames[0], parse_mode="HTML")
    time.sleep(0.7)
    try: bot.edit_message_text(frames[1], msg.chat.id, m.message_id, parse_mode="HTML")
    except: pass
    time.sleep(0.6)
    try:
        recharges = list(db['recharges'].find({"user_id": user_id, "status": "approved"}).sort("timestamp", -1).limit(5))
        if recharges:
            lines = "\n".join([
                f"✅ +{format_currency(r.get('amount',0))} — {r.get('method','UPI')} ({r.get('timestamp', datetime.utcnow()).strftime('%d %b')})"
                for r in recharges
            ])
        else:
            lines = "<i>Koi transaction nahi mila abhi tak.</i>"
        bot.edit_message_text(
            f"📋 <b>RECENT TRANSACTIONS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{lines}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Last 5 approved recharges shown</i>",
            msg.chat.id, m.message_id, parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"History cmd error: {e}")

@bot.message_handler(commands=['countries'])
def cmd_countries(msg):
    frames = ["🌍 <b>Loading Countries...</b>", "🌍 <b>Fetching stock list...</b> ⏳"]
    m = bot.send_message(msg.chat.id, frames[0], parse_mode="HTML")
    time.sleep(0.7)
    try: bot.edit_message_text(frames[1], msg.chat.id, m.message_id, parse_mode="HTML")
    except: pass
    time.sleep(0.6)
    try:
        countries = list(countries_col.find({"status": "active"}).sort("name", 1).limit(30))
        if countries:
            lines = ""
            for c in countries:
                name = c.get("name", "")
                flag = COUNTRY_FLAGS.get(name.lower(), "🌐")
                price = c.get("price", 0)
                stock = get_available_accounts_count(name)
                lines += f"{flag} <b>{name}</b> — ₹{price} | Stock: {stock}\n"
        else:
            lines = "<i>Koi country available nahi hai abhi.</i>"
        bot.edit_message_text(
            f"🌍 <b>AVAILABLE COUNTRIES</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{lines}"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Use /buy to purchase</i>",
            msg.chat.id, m.message_id, parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Countries cmd error: {e}")

@bot.message_handler(commands=['prices'])
def cmd_prices(msg):
    frames = ["💡 <b>Loading Prices...</b>", "💡 <b>Fetching price list...</b> ⏳"]
    m = bot.send_message(msg.chat.id, frames[0], parse_mode="HTML")
    time.sleep(0.6)
    try: bot.edit_message_text(frames[1], msg.chat.id, m.message_id, parse_mode="HTML")
    except: pass
    time.sleep(0.5)
    try:
        countries = list(countries_col.find({"status": "active"}).sort("price", 1).limit(20))
        if countries:
            lines = ""
            for c in countries:
                name = c.get("name", "")
                flag = COUNTRY_FLAGS.get(name.lower(), "🌐")
                price = c.get("price", 0)
                lines += f"{flag} {name} — <b>₹{price}</b>\n"
        else:
            lines = "<i>Price list available nahi hai.</i>"
        bot.edit_message_text(
            f"💡 <b>PRICE LIST</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{lines}"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Sorted by cheapest first</i>",
            msg.chat.id, m.message_id, parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Prices cmd error: {e}")

@bot.message_handler(commands=['faq'])
def cmd_faq(msg):
    frames = ["❓ <b>Loading FAQ...</b>", "❓ <b>Preparing answers...</b> ⏳"]
    m = bot.send_message(msg.chat.id, frames[0], parse_mode="HTML")
    time.sleep(0.6)
    try: bot.edit_message_text(frames[1], msg.chat.id, m.message_id, parse_mode="HTML")
    except: pass
    time.sleep(0.5)
    try:
        bot.edit_message_text(
            "❓ <b>FREQUENTLY ASKED QUESTIONS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>Q: Account kaise kharidu?</b>\n"
            "→ Recharge karo → /buy → Country select karo\n\n"
            "<b>Q: OTP kab aayega?</b>\n"
            "→ Account se Telegram login karo, OTP 1-2 min mein aayega\n\n"
            "<b>Q: Paisa kaise add karu?</b>\n"
            "→ /recharge → UPI/Crypto method select karo\n\n"
            "<b>Q: Referral kya hai?</b>\n"
            "→ Dost ko invite karo, unke recharge par 1.7% commission milega\n\n"
            "<b>Q: Account kaam nahi kiya toh?</b>\n"
            "→ /support pe contact karo, admin help karega\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "<i>Aur sawaal? /support type karo!</i>",
            msg.chat.id, m.message_id, parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"FAQ cmd error: {e}")

@bot.message_handler(commands=['rules'])
def cmd_rules(msg):
    frames = ["📜 <b>Loading Rules...</b>", "📜 <b>Bot ke niyam...</b> ⏳"]
    m = bot.send_message(msg.chat.id, frames[0], parse_mode="HTML")
    time.sleep(0.6)
    try: bot.edit_message_text(frames[1], msg.chat.id, m.message_id, parse_mode="HTML")
    except: pass
    time.sleep(0.5)
    try:
        bot.edit_message_text(
            "📜 <b>BOT RULES</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ <b>Allowed:</b>\n"
            "• Apne kaam ke liye accounts khareedna\n"
            "• Referral se doston ko invite karna\n"
            "• Support se madad maangna\n\n"
            "❌ <b>Not Allowed:</b>\n"
            "• Spam ya abuse karna\n"
            "• Bot hack karne ki koshish\n"
            "• Fake payment karna\n"
            "• Multiple accounts banana\n\n"
            "⚠️ <b>Rules todne par:</b>\n"
            "• Permanent ban + balance freeze\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "<i>Fair use se sab ka fayda hoga! 🙏</i>",
            msg.chat.id, m.message_id, parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Rules cmd error: {e}")

@bot.message_handler(commands=['time'])
def cmd_time(msg):
    now = datetime.now(timezone.utc)
    ist = now + timedelta(hours=5, minutes=30)
    frames = ["🕐 <b>Fetching time...</b>"]
    m = bot.send_message(msg.chat.id, frames[0], parse_mode="HTML")
    time.sleep(0.5)
    try:
        bot.edit_message_text(
            f"🕐 <b>CURRENT TIME</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🇮🇳 <b>IST:</b> {ist.strftime('%d %b %Y | %I:%M:%S %p')}\n"
            f"🌐 <b>UTC:</b> {now.strftime('%d %b %Y | %H:%M:%S')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>⚡ Bot always online — 24/7!</i>",
            msg.chat.id, m.message_id, parse_mode="HTML"
        )
    except: pass

@bot.message_handler(commands=['contact'])
def cmd_contact(msg):
    frames = ["📞 <b>Loading Contact...</b>"]
    m = bot.send_message(msg.chat.id, frames[0], parse_mode="HTML")
    time.sleep(0.5)
    try:
        bot.edit_message_text(
            "📞 <b>CONTACT US</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "👑 <b>Owner:</b> @MR_DARK_OP\n"
            "🛠️ <b>Support:</b> @rchiex\n"
            "📢 <b>Updates:</b> @II_LEGEND_OTP_SELLER_UPDATES_II\n"
            "🎉 <b>Events:</b> @Legendaryevent\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "<i>24/7 Support Available!</i>",
            msg.chat.id, m.message_id, parse_mode="HTML"
        )
    except: pass

@bot.message_handler(commands=['daily'])
def cmd_daily(msg):
    user_id = msg.from_user.id
    frames = ["🎁 <b>Checking Daily Bonus...</b>", "🎁 <b>Loading reward...</b> ⏳"]
    m = bot.send_message(msg.chat.id, frames[0], parse_mode="HTML")
    time.sleep(0.6)
    try: bot.edit_message_text(frames[1], msg.chat.id, m.message_id, parse_mode="HTML")
    except: pass
    time.sleep(0.5)
    try:
        last = db['daily_bonus'].find_one({"user_id": user_id})
        now = datetime.utcnow()
        if last:
            diff = now - last.get("last_claim", now - timedelta(days=2))
            if diff.total_seconds() < 86400:
                remaining = 86400 - diff.total_seconds()
                h, rem = divmod(int(remaining), 3600)
                mn = rem // 60
                bot.edit_message_text(
                    f"⏳ <b>Daily Bonus Already Claimed!</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🕐 Agli baar: <b>{h}h {mn}m</b> mein\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"<i>Kal wapas aana! 😊</i>",
                    msg.chat.id, m.message_id, parse_mode="HTML"
                )
                return
        # Give bonus
        bonus = 2.0
        add_balance(user_id, bonus)
        db['daily_bonus'].update_one(
            {"user_id": user_id},
            {"$set": {"last_claim": now, "user_id": user_id}},
            upsert=True
        )
        bot.edit_message_text(
            f"🎁 <b>DAILY BONUS CLAIMED!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>+{format_currency(bonus)}</b> added to your wallet!\n"
            f"💳 <b>New Balance:</b> {format_currency(get_balance(user_id))}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Kal bhi aana for more! 🎉</i>",
            msg.chat.id, m.message_id, parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Daily cmd error: {e}")

@bot.message_handler(commands=['leaderboard'])
def cmd_leaderboard(msg):
    frames = ["🏆 <b>Loading Leaderboard...</b>", "🏆 <b>Ranking users...</b> ⏳"]
    m = bot.send_message(msg.chat.id, frames[0], parse_mode="HTML")
    time.sleep(0.7)
    try: bot.edit_message_text(frames[1], msg.chat.id, m.message_id, parse_mode="HTML")
    except: pass
    time.sleep(0.6)
    try:
        top = list(wallets_col.find().sort("balance", -1).limit(10))
        medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        lines = ""
        for i, w in enumerate(top):
            uid = w.get("user_id", 0)
            u = users_col.find_one({"user_id": uid}) or {}
            name = u.get("name") or u.get("username") or f"User{uid}"
            bal = w.get("balance", 0)
            lines += f"{medals[i]} <b>{name[:15]}</b> — {format_currency(bal)}\n"
        if not lines:
            lines = "<i>Koi data nahi abhi.</i>"
        bot.edit_message_text(
            f"🏆 <b>TOP WALLETS LEADERBOARD</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{lines}"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Recharge karo aur top pe aao! 💪</i>",
            msg.chat.id, m.message_id, parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Leaderboard cmd error: {e}")

@bot.message_handler(commands=['invite'])
def cmd_invite(msg):
    user_id = msg.from_user.id
    bot_info = bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
    frames = ["🔗 <b>Generating Invite Link...</b>"]
    m = bot.send_message(msg.chat.id, frames[0], parse_mode="HTML")
    time.sleep(0.5)
    try:
        bot.edit_message_text(
            f"🔗 <b>YOUR INVITE LINK</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<code>{ref_link}</code>\n\n"
            f"💰 <b>Earn {REFERRAL_COMMISSION}%</b> commission on every recharge!\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Share karo aur kamao! 🎉</i>",
            msg.chat.id, m.message_id, parse_mode="HTML",
            disable_web_page_preview=True
        )
    except: pass

@bot.message_handler(commands=['wallet'])
def cmd_wallet(msg):
    user_id = msg.from_user.id
    frames = ["💳 <b>Loading Wallet...</b>", "💳 <b>Fetching balance...</b> ⏳"]
    m = bot.send_message(msg.chat.id, frames[0], parse_mode="HTML")
    time.sleep(0.6)
    try: bot.edit_message_text(frames[1], msg.chat.id, m.message_id, parse_mode="HTML")
    except: pass
    time.sleep(0.5)
    try:
        bal = get_balance(user_id)
        bot.edit_message_text(
            f"💳 <b>MY WALLET</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>Balance:</b> {format_currency(bal)}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Recharge ke liye /recharge karo</i>",
            msg.chat.id, m.message_id, parse_mode="HTML"
        )
    except: pass

@bot.message_handler(commands=['checkpayment'])
def cmd_checkpayment(msg):
    """
    /checkpayment <order_id>
    User manually triggers payment status check. If paid → instant credit.
    Useful when auto-poll missed or bot restarted.
    """
    user_id = msg.from_user.id
    parts = msg.text.strip().split(maxsplit=1)

    if len(parts) < 2 or not parts[1].strip():
        # No order_id given — check if user has a recent pending order in DB or memory
        pending = None
        # Check in-memory state first
        if user_id in fampay_auto_states:
            st = fampay_auto_states[user_id]
            pending = {"order_id": st["order_id"], "amount": st["amount"],
                       "chat_id": st["chat_id"]}
        else:
            # Check MongoDB for latest pending order
            try:
                rec = recharges_col.find_one(
                    {"user_id": user_id, "status": "pending", "method": "UPI Auto"},
                    sort=[("created_at", -1)]
                )
                if rec:
                    pending = {"order_id": rec["order_id"], "amount": rec["amount"],
                               "chat_id": rec.get("chat_id", user_id)}
            except Exception:
                pass

        if not pending:
            bot.send_message(
                msg.chat.id,
                "🔍 <b>Payment Check</b>\n\n"
                "Order ID provide karein:\n"
                "<code>/checkpayment ORDER_ID</code>\n\n"
                "Order ID aapko QR message mein mila tha.\n"
                "<i>Example: /checkpayment FAMPAY1234567890</i>",
                parse_mode="HTML"
            )
            return
        order_id = pending["order_id"]
        amount   = pending["amount"]
        chat_id  = pending["chat_id"]
    else:
        order_id = parts[1].strip()
        # Look up amount from DB or memory
        amount  = 0
        chat_id = msg.chat.id
        if user_id in fampay_auto_states and \
                fampay_auto_states[user_id].get("order_id") == order_id:
            amount  = fampay_auto_states[user_id]["amount"]
            chat_id = fampay_auto_states[user_id]["chat_id"]
        else:
            try:
                rec = recharges_col.find_one({"order_id": order_id})
                if rec:
                    # Security: only allow owner or admin
                    if rec.get("user_id") != user_id and user_id != ADMIN_ID:
                        bot.send_message(msg.chat.id,
                                         "❌ Ye order aapka nahi hai.",
                                         parse_mode="HTML")
                        return
                    amount  = rec.get("amount", 0)
                    chat_id = rec.get("chat_id", msg.chat.id)
                    user_id = rec.get("user_id", user_id)  # credit to order owner
            except Exception:
                pass

    # Already credited?
    if order_id in fampay_approved_orders:
        bot.send_message(msg.chat.id,
                         f"✅ Order <code>{order_id}</code> pehle se credit ho chuka hai!",
                         parse_mode="HTML")
        return

    # Inform user we're checking
    wait_msg = bot.send_message(
        msg.chat.id,
        f"🔍 <b>Payment Check Ho Raha Hai...</b>\n"
        f"🆔 <code>{order_id}</code>",
        parse_mode="HTML"
    )

    status = fp_check_status(order_id)

    try:
        bot.delete_message(msg.chat.id, wait_msg.message_id)
    except Exception:
        pass

    if status == "success":
        if amount > 0:
            fp_credit_wallet(chat_id, user_id, order_id, amount)
        else:
            bot.send_message(
                msg.chat.id,
                f"✅ Payment verified!\n"
                f"🆔 Order: <code>{order_id}</code>\n\n"
                f"⚠️ Amount detect nahi hua. Admin se contact karein:\n"
                f"Order ID share karein aur credit karwa lein.",
                parse_mode="HTML"
            )
    elif status == "expired":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔄 New Payment", callback_data="recharge_fampay_auto"))
        markup.add(InlineKeyboardButton("📞 Contact Admin", url="https://t.me/ID_GMS_SELLER_bot"))
        bot.send_message(
            msg.chat.id,
            f"❌ <b>Order Expired</b>\n\n"
            f"🆔 <code>{order_id}</code>\n\n"
            f"Agar aapne pay kiya hai toh admin se contact karein.",
            parse_mode="HTML",
            reply_markup=markup
        )
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔄 Check Again", callback_data="check_again_" + order_id[:20]))
        bot.send_message(
            msg.chat.id,
            f"⏳ <b>Payment Abhi Pending Hai</b>\n\n"
            f"🆔 <code>{order_id}</code>\n\n"
            f"Pay karne ke baad thodi der mein automatic credit ho jayega.\n"
            f"Ya 2-3 min baad dobara /checkpayment karein.",
            parse_mode="HTML"
        )


@bot.message_handler(commands=['menu'])
def cmd_menu(msg):
    user_id = msg.from_user.id
    try:
        bot.delete_message(msg.chat.id, msg.message_id)
    except: pass
    clean_ui_and_send_menu(msg.chat.id, user_id)

@bot.message_handler(commands=['rank'])
def cmd_rank(msg):
    user_id = msg.from_user.id
    frames = ["🎖️ <b>Checking Rank...</b>"]
    m = bot.send_message(msg.chat.id, frames[0], parse_mode="HTML")
    time.sleep(0.6)
    try:
        bal = get_balance(user_id)
        above = wallets_col.count_documents({"balance": {"$gt": bal}})
        rank = above + 1
        total = wallets_col.count_documents({})
        percentile = int((1 - above / max(total, 1)) * 100)
        bot.edit_message_text(
            f"🎖️ <b>YOUR RANK</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏅 <b>Rank:</b> #{rank} out of {total}\n"
            f"💰 <b>Balance:</b> {format_currency(bal)}\n"
            f"📊 <b>Top:</b> {percentile}% users\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Recharge karo rank improve karo! 💪</i>",
            msg.chat.id, m.message_id, parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Rank cmd error: {e}")

# ── ADMIN COMMANDS ─────────────────────────────────────────────────────

@bot.message_handler(commands=['ban'])
def cmd_ban(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        bot.reply_to(msg, "❌ Sirf admin use kar sakta hai!")
        return
    args = msg.text.split()
    if len(args) < 2:
        bot.reply_to(msg, "⚠️ Usage: /ban <user_id> [reason]")
        return
    try:
        target = int(args[1])
        reason = " ".join(args[2:]) if len(args) > 2 else "Admin ban"
        banned_users_col.update_one(
            {"user_id": target},
            {"$set": {"user_id": target, "status": "active", "reason": reason,
                      "banned_by": user_id, "banned_at": datetime.utcnow()}},
            upsert=True
        )
        bot.reply_to(msg, f"🚫 User <code>{target}</code> banned!\n📝 Reason: {reason}", parse_mode="HTML")
        try:
            bot.send_message(target, f"🚫 <b>You have been banned!</b>\n📝 Reason: {reason}", parse_mode="HTML")
        except: pass
    except (ValueError, IndexError):
        bot.reply_to(msg, "❌ Invalid user ID!")

@bot.message_handler(commands=['unban'])
def cmd_unban(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        bot.reply_to(msg, "❌ Sirf admin use kar sakta hai!")
        return
    args = msg.text.split()
    if len(args) < 2:
        bot.reply_to(msg, "⚠️ Usage: /unban <user_id>")
        return
    try:
        target = int(args[1])
        banned_users_col.update_one({"user_id": target}, {"$set": {"status": "inactive"}})
        bot.reply_to(msg, f"✅ User <code>{target}</code> unbanned!", parse_mode="HTML")
        try:
            bot.send_message(target, "✅ <b>Aapka ban hata diya gaya hai!</b> Bot use kar sakte ho.", parse_mode="HTML")
        except: pass
    except (ValueError, IndexError):
        bot.reply_to(msg, "❌ Invalid user ID!")

@bot.message_handler(commands=['addbalance'])
def cmd_addbalance(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        bot.reply_to(msg, "❌ Sirf admin use kar sakta hai!")
        return
    args = msg.text.split()
    if len(args) < 3:
        bot.reply_to(msg, "⚠️ Usage: /addbalance <user_id> <amount>")
        return
    try:
        target = int(args[1])
        amount = float(args[2])
        add_balance(target, amount)
        new_bal = get_balance(target)
        bot.reply_to(msg, f"✅ <code>{target}</code> ko <b>+{format_currency(amount)}</b> diya!\n💳 Naya balance: {format_currency(new_bal)}", parse_mode="HTML")
        try:
            bot.send_message(target, f"💰 <b>Balance Added!</b>\n+{format_currency(amount)} added by admin.\n💳 New Balance: {format_currency(new_bal)}", parse_mode="HTML")
        except: pass
    except (ValueError, IndexError):
        bot.reply_to(msg, "❌ Invalid user ID or amount!")

@bot.message_handler(commands=['userinfo'])
def cmd_userinfo(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        bot.reply_to(msg, "❌ Sirf admin use kar sakta hai!")
        return
    args = msg.text.split()
    if len(args) < 2:
        bot.reply_to(msg, "⚠️ Usage: /userinfo <user_id>")
        return
    try:
        target = int(args[1])
        u = users_col.find_one({"user_id": target}) or {}
        bal = get_balance(target)
        banned = is_user_banned(target)
        purchases = db['orders'].count_documents({"user_id": target}) if 'orders' in db.list_collection_names() else 0
        bot.reply_to(
            msg,
            f"👤 <b>USER INFO</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 ID: <code>{target}</code>\n"
            f"📛 Name: {u.get('name','N/A')}\n"
            f"👤 Username: @{u.get('username','N/A')}\n"
            f"💰 Balance: {format_currency(bal)}\n"
            f"🛒 Purchases: {purchases}\n"
            f"🚫 Banned: {'Yes' if banned else 'No'}\n"
            f"📅 Joined: {u.get('created_at', datetime.utcnow()).strftime('%d %b %Y') if u.get('created_at') else 'N/A'}",
            parse_mode="HTML"
        )
    except (ValueError, IndexError):
        bot.reply_to(msg, "❌ Invalid user ID!")

@bot.message_handler(commands=['listcoupons'])
def cmd_listcoupons(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        bot.reply_to(msg, "❌ Sirf admin use kar sakta hai!")
        return
    try:
        coupons = list(db['coupons'].find({"status": "active"}).limit(20))
        if not coupons:
            bot.reply_to(msg, "📋 Koi active coupon nahi hai.")
            return
        lines = "\n".join([
            f"🎁 <code>{c.get('code','?')}</code> — ₹{c.get('amount',0)} | Used: {c.get('used_count',0)}/{c.get('max_uses','∞')}"
            for c in coupons
        ])
        bot.reply_to(msg, f"🎟️ <b>ACTIVE COUPONS</b>\n━━━━━━━━━━━━━━━━━━━━━\n{lines}", parse_mode="HTML")
    except Exception as e:
        bot.reply_to(msg, f"❌ Error: {e}")

@bot.message_handler(commands=['maintenance'])
def cmd_maintenance(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        bot.reply_to(msg, "❌ Sirf admin use kar sakta hai!")
        return
    try:
        current = db['settings'].find_one({"key": "maintenance"})
        new_status = not (current.get("value", False) if current else False)
        db['settings'].update_one(
            {"key": "maintenance"},
            {"$set": {"key": "maintenance", "value": new_status, "set_by": user_id, "set_at": datetime.utcnow()}},
            upsert=True
        )
        status_text = "🔴 ON" if new_status else "🟢 OFF"
        bot.reply_to(msg, f"⚙️ <b>Maintenance Mode: {status_text}</b>", parse_mode="HTML")
    except Exception as e:
        bot.reply_to(msg, f"❌ Error: {e}")

@bot.message_handler(commands=['broadcast'])
def cmd_broadcast_shortcut(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        bot.reply_to(msg, "❌ Sirf admin use kar sakta hai!")
        return
    bot.reply_to(msg, "📢 Broadcast ke liye /sendbroadcast use karo (reply karke kisi message ko)")

@bot.message_handler(commands=['deduct'])
def cmd_deduct(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        bot.reply_to(msg, "❌ Sirf admin use kar sakta hai!")
        return
    args = msg.text.split()
    if len(args) < 3:
        bot.reply_to(msg, "⚠️ Usage: /deduct <user_id> <amount>")
        return
    try:
        target = int(args[1])
        amount = float(args[2])
        cur_bal = get_balance(target)
        if amount > cur_bal:
            bot.reply_to(msg, f"❌ Insufficient balance! User has {format_currency(cur_bal)}")
            return
        deduct_balance(target, amount)
        new_bal = get_balance(target)
        bot.reply_to(msg, f"✅ <code>{target}</code> se <b>-{format_currency(amount)}</b> deduct kiya!\n💳 Naya balance: {format_currency(new_bal)}", parse_mode="HTML")
        try:
            bot.send_message(target, f"⚠️ <b>Balance Deducted!</b>\n-{format_currency(amount)} by admin.\n💳 New Balance: {format_currency(new_bal)}", parse_mode="HTML")
        except: pass
    except (ValueError, IndexError):
        bot.reply_to(msg, "❌ Invalid user ID or amount!")

@bot.message_handler(commands=['totalusers'])
def cmd_totalusers(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ Sirf admin use kar sakta hai!")
        return
    count = users_col.count_documents({})
    banned = banned_users_col.count_documents({"status": "active"})
    bot.reply_to(msg, f"👥 <b>Total Users:</b> {count}\n🚫 <b>Banned:</b> {banned}", parse_mode="HTML")

@bot.message_handler(commands=['totalaccounts'])
def cmd_totalaccounts(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ Sirf admin use kar sakta hai!")
        return
    total = accounts_col.count_documents({"status": "active"})
    used = accounts_col.count_documents({"used": True})
    available = accounts_col.count_documents({"status": "active", "used": False})
    bot.reply_to(msg,
        f"📱 <b>ACCOUNT STATS</b>\n"
        f"Total: {total}\nUsed: {used}\nAvailable: {available}",
        parse_mode="HTML"
    )



# ---------------------------------------------------------------------
# MESSAGE HANDLER FOR ADMIN DEDUCT
# ---------------------------------------------------------------------

@bot.message_handler(func=lambda m: True, content_types=['text','photo','video','document'])
def chat_handler(msg):
    user_id = msg.from_user.id

    # ── Security gate ──────────────────────────────────────────────
    if _is_security_blocked(user_id):
        return
    if not is_admin(user_id):
        if _check_honeypot(user_id, msg.text or ""):
            bot.send_message(msg.chat.id, "⚠️ Invalid command.", parse_mode=None)
            return
        if _is_rate_limited(user_id):
            bot.send_message(msg.chat.id, "🚦 Too many messages. Please slow down.")
            return
    # ───────────────────────────────────────────────────────────────

    # Check if user is in admin add flow
    if user_id in admin_add_state:
        handle_add_admin_userid(msg)
        return

    # Check if user is in admin remove flow
    if user_id in admin_remove_state:
        handle_remove_admin_userid(msg)
        return

    if is_admin(user_id) and user_id in admin_deduct_state:
        pass

    if is_user_banned(user_id):
        return
    
    ensure_user_exists(
        user_id,
        msg.from_user.first_name or "Unknown",
        msg.from_user.username
    )
    
    if (
        msg.text and msg.text.startswith('/') and
        not (is_admin(user_id) and user_id in admin_deduct_state)
    ):
        return
    
    if is_admin(user_id) and user_id in admin_deduct_state:
        state = admin_deduct_state[user_id]
        
        if state["step"] == "ask_user_id":
            try:
                target_user_id = int(msg.text.strip())
                user_exists = users_col.find_one({"user_id": target_user_id})
                if not user_exists:
                    bot.send_message(user_id, "❌ User not found. Enter valid User ID:")
                    return
                
                current_balance = get_balance(target_user_id)
                admin_deduct_state[user_id] = {
                    "step": "ask_amount",
                    "target_user_id": target_user_id,
                    "current_balance": current_balance
                }
                bot.send_message(
                    user_id,
                    f"👤 User ID: {target_user_id}\n"
                    f"💰 Current Balance: {format_currency(current_balance)}\n\n"
                    f"💸 Enter amount to deduct:"
                )
                return
            except ValueError:
                bot.send_message(user_id, "❌ Invalid User ID. Enter numeric ID:")
                return
        
        elif state["step"] == "ask_amount":
            try:
                amount = float(msg.text.strip())
                current_balance = state["current_balance"]
                if amount <= 0:
                    bot.send_message(user_id, "❌ Amount must be greater than 0:")
                    return
                if amount > current_balance:
                    bot.send_message(
                        user_id,
                        f"❌ Amount exceeds balance ({format_currency(current_balance)}):"
                    )
                    return
                
                admin_deduct_state[user_id] = {
                    "step": "ask_reason",
                    "target_user_id": state["target_user_id"],
                    "amount": amount,
                    "current_balance": current_balance
                }
                bot.send_message(user_id, "📝 Enter reason for deduction:")
                return
            except ValueError:
                bot.send_message(user_id, "❌ Invalid amount. Enter number:")
                return
        
        elif state["step"] == "ask_reason":
            reason = msg.text.strip()
            if not reason:
                bot.send_message(user_id, "❌ Reason cannot be empty:")
                return
            
            target_user_id = state["target_user_id"]
            amount = state["amount"]
            old_balance = state["current_balance"]
            
            deduct_balance(target_user_id, amount)
            new_balance = get_balance(target_user_id)
            
            transaction_id = f"DEDUCT{target_user_id}{int(time.time())}"
            if 'deductions' not in db.list_collection_names():
                db.create_collection('deductions')
            db['deductions'].insert_one({
                "transaction_id": transaction_id,
                "user_id": target_user_id,
                "amount": amount,
                "reason": reason,
                "admin_id": user_id,
                "old_balance": old_balance,
                "new_balance": new_balance,
                "timestamp": datetime.utcnow()
            })
            
            bot.send_message(
                user_id,
                f"✅ Balance Deducted Successfully\n\n"
                f"👤 User: {target_user_id}\n"
                f"💰 Amount: {format_currency(amount)}\n"
                f"📝 Reason: {reason}\n"
                f"📉 Old Balance: {format_currency(old_balance)}\n"
                f"📈 New Balance: {format_currency(new_balance)}\n"
                f"🆔 Txn ID: {transaction_id}"
            )
            
            try:
                bot.send_message(
                    target_user_id,
                    f"⚠️ Balance Deducted by Admin\n\n"
                    f"💰 Amount: {format_currency(amount)}\n"
                    f"📝 Reason: {reason}\n"
                    f"📈 New Balance: {format_currency(new_balance)}\n"
                    f"🆔 Txn ID: {transaction_id}"
                )
            except:
                bot.send_message(ADMIN_ID, "⚠️ User notification failed (maybe blocked)")
            
            del admin_deduct_state[user_id]
            return
    
    if msg.chat.type == "private":
        text = msg.text or ""
        user_name = msg.from_user.first_name or "User"
        username = msg.from_user.username or ""

        # ── Security probe check ────────────────────────────────────────
        if _is_secret_probe(text):
            bot.send_message(
                user_id,
                "🚨 <b>SECURITY WARNING!</b>\n\n"
                "⚠️ Bot ki confidential information share nahi ki ja sakti.\n"
                "✅ Koi aur help chahiye toh /start press karein.",
                parse_mode="HTML"
            )
            try:
                bot.send_message(
                    ADMIN_ID,
                    f"🚨 <b>Secret Probe Alert</b>\n\n"
                    f"👤 <code>{user_id}</code> | @{username or 'N/A'} | {user_name}\n"
                    f"💬 <code>{text[:300]}</code>",
                    parse_mode="HTML"
                )
            except Exception:
                pass
            threading.Thread(
                target=log_personal_security_alert_async,
                args=(user_id, username, user_name, text),
                daemon=True
            ).start()
            return

        # ── Unknown text — redirect to menu ────────────────────────────
        if text and not text.startswith('/'):
            bot.send_message(
                user_id,
                f"Namaste {user_name}! 👋\n"
                f"Menu se apna kaam select karein ya /start press karein.",
                parse_mode="HTML"
            )
        else:
            bot.send_message(user_id, "⚠️ /start press karein ya menu se option chunein.")

# ---------------------------------------------------------------------
# FLASK WEBHOOK SERVER — exclusive control, no polling conflicts
# ---------------------------------------------------------------------
from flask import Flask, request as flask_request, abort

flask_app = Flask(__name__)

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_PORT = int(os.getenv("PORT", 5000))
REPLIT_DOMAIN = os.getenv("REPLIT_DEV_DOMAIN", "")

@flask_app.route(WEBHOOK_PATH, methods=["POST"])
def telegram_webhook():
    if flask_request.headers.get("content-type") == "application/json":
        json_str = flask_request.get_data(as_text=True)
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "OK", 200
    abort(403)

@flask_app.route("/", methods=["GET"])
def health():
    return "GMS Bot is running via webhook ✅", 200

@flask_app.route("/fampay/webhook", methods=["GET", "POST"])
def fampay_payment_webhook():
    """FamPay server-push webhook — instant payment confirmation"""
    if flask_request.method == "GET":
        return "✅ FamPay Webhook Active | POST only", 200
    return _fp_webhook_handler()

# Also accept old path for backwards compatibility
@flask_app.route("/webhook/payment", methods=["GET", "POST"])
def fampay_payment_webhook_legacy():
    if flask_request.method == "GET":
        return "✅ FamPay Webhook Active | POST only", 200
    return _fp_webhook_handler()

# ---------------------------------------------------------------------
# RUN BOT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    logger.info(f"🤖 Legendary OTP Bot Starting (Webhook Mode)...")
    logger.info(f"Admin ID: {ADMIN_ID}")
    logger.info(f"Bot Token: {(BOT_TOKEN or '')[:10]}...")
    logger.info(f"Must Join Channel 1: {MUST_JOIN_CHANNEL_1}")
    logger.info(f"Must Join Channel 2: {MUST_JOIN_CHANNEL_2}")
    logger.info(f"Log Channel ID: {LOG_CHANNEL_ID}")
    logger.info(f"UPI ID: {UPI_ID}")

    IS_BROADCASTING = False

    try:
        coupons_col.create_index([("coupon_code", 1)], unique=True)
        coupons_col.create_index([("status", 1)])
        coupons_col.create_index([("created_at", -1)])
        logger.info("✅ Coupon indexes created")
    except Exception as e:
        logger.error(f"❌ Failed to create coupon indexes: {e}")

    try:
        admins_col.create_index([("user_id", 1)], unique=True)
        logger.info("✅ Admin indexes created")
    except Exception as e:
        logger.error(f"❌ Failed to create admin indexes: {e}")

    # TTL Indexes — MongoDB auto-expires old documents
    try:
        otp_sessions_col.create_index([("created_at", 1)], expireAfterSeconds=7200)        # 2 hrs
        recharges_col.create_index([("processed_at", 1)], expireAfterSeconds=5184000)       # 60 days
        transactions_col.create_index([("created_at", 1)], expireAfterSeconds=7776000)      # 90 days
        referrals_col.create_index([("created_at", 1)], expireAfterSeconds=7776000)         # 90 days
        logger.info("✅ TTL indexes created — MongoDB will auto-expire old data")
    except Exception as e:
        logger.error(f"❌ TTL indexes error: {e}")

    # Start auto-cleanup background thread (runs every 24 hours)
    threading.Thread(target=_auto_cleanup_scheduler, daemon=True, name="AutoCleanup").start()
    logger.info("✅ Auto-cleanup scheduler started (runs every 24h)")

    # Register commands with BotFather — 40 commands total
    try:
        from telebot.types import BotCommand
        user_cmds = [
            BotCommand("start",          "🏠 Main menu"),
            BotCommand("help",           "📖 Help & guide dekhein"),
            BotCommand("menu",           "📋 Menu wapas lao"),
            BotCommand("balance",        "💰 Wallet balance check karo"),
            BotCommand("wallet",         "💳 Wallet details dekhein"),
            BotCommand("recharge",       "💳 Paisa add karo wallet mein"),
            BotCommand("buy",            "🛒 Telegram account kharido"),
            BotCommand("refer",          "👥 Referral link lo aur kamao"),
            BotCommand("invite",         "🔗 Invite link share karo"),
            BotCommand("redeem",         "🎁 Coupon code lagao"),
            BotCommand("daily",          "🎁 Daily bonus claim karo"),
            BotCommand("profile",        "👤 Apna profile dekhein"),
            BotCommand("history",        "📋 Transaction history"),
            BotCommand("rank",           "🎖️ Apni rank dekhein"),
            BotCommand("leaderboard",    "🏆 Top users ki list"),
            BotCommand("countries",      "🌍 Available countries & stock"),
            BotCommand("prices",         "💡 Price list dekhein"),
            BotCommand("status",         "📊 Bot live status check karo"),
            BotCommand("ping",           "🏓 Bot ping test"),
            BotCommand("id",             "🆔 Apna Telegram ID dekhein"),
            BotCommand("time",           "🕐 Server time dekhein"),
            BotCommand("faq",            "❓ Common sawaalon ke jawab"),
            BotCommand("rules",          "📜 Bot rules padhein"),
            BotCommand("contact",        "📞 Owner/support contact"),
            BotCommand("support",        "🛠️ Admin se madad lo"),
            BotCommand("cancel",         "❌ Sab kuch cancel karo"),
            BotCommand("checkpayment",   "🔍 UPI payment status check karo"),
        ]
        admin_cmds = user_cmds + [
            BotCommand("stats",            "📊 Full bot statistics"),
            BotCommand("dbstats",          "📦 MongoDB storage sizes"),
            BotCommand("userinfo",         "👤 Kisi bhi user ki info"),
            BotCommand("totalusers",       "👥 Total user count"),
            BotCommand("totalaccounts",    "📱 Account stock stats"),
            BotCommand("addbalance",       "➕ User ko balance do"),
            BotCommand("deduct",           "➖ User se balance kaato"),
            BotCommand("ban",              "🚫 User ban karo"),
            BotCommand("unban",            "✅ User unban karo"),
            BotCommand("listcoupons",      "🎟️ All active coupons"),
            BotCommand("addadmin",         "👑 Naya admin add karo"),
            BotCommand("removeadmin",      "🗑️ Admin remove karo"),
            BotCommand("maintenance",      "⚙️ Maintenance mode toggle"),
            BotCommand("broadcast",        "📢 Broadcast shortcut"),
            BotCommand("sendbroadcast",    "📢 Broadcast message bhejo"),
            BotCommand("resetbroadcast",   "🔄 Broadcast reset karo"),
            BotCommand("loadallcountries", "🌍 Sab countries load karo"),
            BotCommand("clearaccounts",    "🗑️ Accounts clear karo"),
            BotCommand("emptycountries",   "📭 0-stock countries ki list"),
            BotCommand("cleanempty",       "🗑️ 0-stock countries remove karo"),
            BotCommand("clean",            "🧹 MongoDB junk clean karo"),
            BotCommand("cleanmongo",       "🧹 MongoDB cleanup"),
            BotCommand("restart",          "♻️ Bot restart karo"),
        ]
        bot.set_my_commands(user_cmds)
        bot.set_my_commands(admin_cmds, scope=telebot.types.BotCommandScopeChat(ADMIN_ID))
        logger.info(f"✅ BotFather commands registered — {len(user_cmds)} user + {len(admin_cmds)} admin")
    except Exception as e:
        logger.error(f"❌ BotFather commands error: {e}")

    # Set webhook — clears any other polling/webhook session automatically
    if REPLIT_DOMAIN:
        WEBHOOK_URL = f"https://{REPLIT_DOMAIN}{WEBHOOK_PATH}"
        try:
            bot.remove_webhook()
            time.sleep(1)
            bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
            logger.info(f"✅ Webhook set: {WEBHOOK_URL}")
        except Exception as e:
            logger.error(f"❌ Failed to set webhook: {e}")
    else:
        logger.warning("⚠️ REPLIT_DEV_DOMAIN not set, falling back to polling")
        while True:
            try:
                bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
            except Exception as e:
                logger.error(f"Polling error: {e}")
                time.sleep(15)

    logger.info(f"🚀 Starting Flask webhook server on port {WEBHOOK_PORT}...")
    import socket as _sock
    import socketserver as _ss

    # Force SO_REUSEADDR so port is freed immediately on restart
    _ss.TCPServer.allow_reuse_address = True

    try:
        flask_app.run(host="0.0.0.0", port=WEBHOOK_PORT, debug=False,
                      use_reloader=False, threaded=True)
    except OSError:
        import os as _os
        _os.system(f"fuser -k {WEBHOOK_PORT}/tcp 2>/dev/null || true; sleep 2")
        flask_app.run(host="0.0.0.0", port=WEBHOOK_PORT, debug=False,
                      use_reloader=False, threaded=True)

