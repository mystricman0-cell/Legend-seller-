"""
Logging Module for OTP Bot
Sends purchase logs, OTP receipts, and recharge approvals to Telegram channel
Channel: -1003912691513
"""

import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any
import threading

logger = logging.getLogger(__name__)

def _mask_otp(otp_code: str) -> str:
    """Mask OTP - show first 2 digits then ****"""
    if not otp_code:
        return "****"
    otp_str = str(otp_code).strip()
    if len(otp_str) <= 2:
        return otp_str + "****"
    return otp_str[:2] + "****"

def _mask_2fa(password: str) -> str:
    """Mask 2FA password - show first 2 chars then ****"""
    if not password:
        return "****"
    pwd = str(password)
    if len(pwd) <= 2:
        return pwd + "****"
    return pwd[:2] + "****"

def _mask_phone(phone: str) -> str:
    """Mask phone number - show first 4 digits and last 2"""
    if not phone:
        return "N/A"
    try:
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) >= 8:
            return digits[:4] + "****" + digits[-2:]
        elif len(digits) > 0:
            return digits[:3] + "****"
        return "N/A"
    except:
        return "****"

def _mask_user(user_id) -> str:
    """Mask user ID"""
    try:
        user_str = str(user_id)
        if len(user_str) > 4:
            return user_str[:3] + "***" + user_str[-2:]
        return user_str[:2] + "***"
    except:
        return str(user_id)[:3] + "***"

def _mask_utr(utr: str) -> str:
    """Mask UTR number"""
    if not utr:
        return "N/A"
    try:
        if len(utr) >= 8:
            return utr[:4] + "****" + utr[-2:]
        return utr[:3] + "***"
    except:
        return utr


class TelegramLogger:
    """Sends logs to Telegram channel -1003912691513"""

    def __init__(self, bot_token: str, log_channel_id: str,
                 support_link: str = "https://t.me/rchiex",
                 buy_link: str = "http://t.me/LEGENDARY_OTP_SELLER_Bot"):
        self.bot_token = bot_token
        self.log_channel_id = log_channel_id
        self.support_link = support_link
        self.buy_link = buy_link
        self._bot = None
        self._init_bot()

    def _init_bot(self):
        try:
            import telebot
            from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
            self._bot = telebot.TeleBot(self.bot_token)
            self.InlineKeyboardMarkup = InlineKeyboardMarkup
            self.InlineKeyboardButton = InlineKeyboardButton
            logger.info(f"✅ Telegram logger initialized for channel: {self.log_channel_id}")
        except ImportError:
            logger.error("❌ Failed to import telebot.")
            self._bot = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize Telegram logger: {e}")
            self._bot = None

    def _get_inline_buttons(self):
        markup = self.InlineKeyboardMarkup(row_width=2)
        support_btn = self.InlineKeyboardButton("🆘 Support", url=self.support_link)
        buy_btn = self.InlineKeyboardButton("🛒 Buy", url=self.buy_link)
        markup.add(support_btn, buy_btn)
        return markup

    def send_log(self, message: str, parse_mode: str = "HTML") -> bool:
        if not self._bot:
            logger.error("Telegram bot not initialized")
            return False
        try:
            quoted_message = f"<blockquote>{message}</blockquote>"
            markup = self._get_inline_buttons()
            self._bot.send_message(
                self.log_channel_id,
                quoted_message,
                parse_mode=parse_mode,
                disable_web_page_preview=True,
                reply_markup=markup
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send log to Telegram: {e}")
            return False

    def log_purchase(self, user_id: int, country: str, price: float, phone: str) -> bool:
        """Log new number purchase — MASKED"""
        formatted_phone = _mask_phone(phone)
        formatted_user = _mask_user(user_id)
        current_time = datetime.now().strftime("%I:%M %p")

        message = (
            f"<b>🔥 NEW ACCOUNT SOLD! 🔥</b>\n\n"
            f"<b>✚ Category:</b> {country}\n"
            f"<b>✚ Region:</b> {country}\n"
            f"<b>✚ Number:</b> {formatted_phone} 📞\n"
            f"<b>✚ User:</b> {formatted_user} 👤\n"
            f"<b>✚ Price:</b> ₹{price:.0f}\n"
            f"<b>✚ Status:</b> Verified & Delivered ✅\n"
            f"<b>✚ Time:</b> {current_time}\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self.send_log(message)

    def log_otp_received(self, user_id: int, phone: str, otp_code: str,
                         country: str, price: float) -> bool:
        """Log OTP received — OTP MASKED"""
        formatted_phone = _mask_phone(phone)
        formatted_user = _mask_user(user_id)
        masked_otp = _mask_otp(otp_code)
        current_time = datetime.now().strftime("%I:%M %p")

        message = (
            f"<b>🔐 OTP RECEIVED! 🔐</b>\n\n"
            f"<b>━ Category:</b> {country}\n"
            f"<b>━ Number:</b> {formatted_phone} 📞\n"
            f"<b>━ OTP:</b> <code>{masked_otp}</code> 💬\n"
            f"<b>━ User:</b> {formatted_user} 👤\n"
            f"<b>━ Time:</b> {current_time}\n"
            f"<b>━ Status:</b> OTP Delivered ✅\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self.send_log(message)

    def log_recharge_approved(self, user_id: int, amount: float,
                              method: str = "UPI", utr: str = None) -> bool:
        """Log deposit approved"""
        formatted_user = _mask_user(user_id)
        formatted_utr = _mask_utr(utr) if utr else "N/A"
        current_time = datetime.now().strftime("%I:%M %p")

        message = (
            f"<b>💰 DEPOSIT APPROVED! 💰</b>\n\n"
            f"<b>User:</b> {formatted_user}\n"
            f"<b>Amount:</b> ₹{amount:,.0f}\n"
            f"<b>Method:</b> {method}\n"
            f"<b>UTR:</b> {formatted_utr}\n"
            f"<b>Time:</b> {current_time}\n"
            f"<b>Status:</b> Balance Updated ✅\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self.send_log(message)

    def log_recharge_rejected(self, user_id: int, amount: float,
                              method: str = "UPI", utr: str = None) -> bool:
        """Log deposit rejected"""
        formatted_user = _mask_user(user_id)
        formatted_utr = _mask_utr(utr) if utr else "N/A"
        current_time = datetime.now().strftime("%I:%M %p")

        message = (
            f"<b>❌ DEPOSIT REJECTED! ❌</b>\n\n"
            f"<b>User:</b> {formatted_user}\n"
            f"<b>Amount:</b> ₹{amount:,.0f}\n"
            f"<b>Method:</b> {method}\n"
            f"<b>UTR:</b> {formatted_utr}\n"
            f"<b>Time:</b> {current_time}\n"
            f"<b>Status:</b> Request Rejected ❌\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self.send_log(message)

    def log_custom(self, title: str, **kwargs) -> bool:
        formatted_data = []
        for key, value in kwargs.items():
            if key.lower() == "user_id" and value:
                value = _mask_user(value)
            elif key.lower() == "phone" and value:
                value = _mask_phone(str(value))
            elif key.lower() in ("otp", "otp_code") and value:
                value = _mask_otp(str(value))
            elif key.lower() in ("password", "2fa", "two_fa") and value:
                value = _mask_2fa(str(value))
            formatted_data.append(f"<b>{key}:</b> {value}")

        current_time = datetime.now().strftime("%I:%M %p")
        message = (
            f"<b>{title}</b>\n\n"
            f"{chr(10).join(formatted_data)}\n\n"
            f"⏰ {current_time}"
        )
        return self.send_log(message)


# ─── Global instance ───────────────────────────────────────────────────────────

telegram_logger = None


def init_logger(bot_token: str, log_channel_id: str,
                support_link: str = "https://t.me/rchiex",
                buy_link: str = "https://t.me/LEGENDARY_OTP_SELLER_Bot"):
    global telegram_logger
    telegram_logger = TelegramLogger(bot_token, log_channel_id, support_link, buy_link)
    return telegram_logger


def get_logger() -> TelegramLogger:
    global telegram_logger
    if telegram_logger is None:
        raise ValueError("Telegram logger not initialized. Call init_logger() first.")
    return telegram_logger


# ─── Async helper functions ────────────────────────────────────────────────────

def log_purchase_async(user_id: int, country: str, price: float, phone: str):
    def _log():
        try:
            get_logger().log_purchase(user_id, country, price, phone)
        except Exception as e:
            logging.error(f"Failed to log purchase: {e}")
    threading.Thread(target=_log, daemon=True).start()


def log_otp_received_async(user_id: int, phone: str, otp_code: str,
                           country: str, price: float):
    def _log():
        try:
            get_logger().log_otp_received(user_id, phone, otp_code, country, price)
        except Exception as e:
            logging.error(f"Failed to log OTP: {e}")
    threading.Thread(target=_log, daemon=True).start()


def log_recharge_approved_async(user_id: int, amount: float,
                                method: str = "UPI", utr: str = None):
    def _log():
        try:
            get_logger().log_recharge_approved(user_id, amount, method, utr)
        except Exception as e:
            logging.error(f"Failed to log recharge approval: {e}")
    threading.Thread(target=_log, daemon=True).start()


def log_recharge_rejected_async(user_id: int, amount: float,
                                method: str = "UPI", utr: str = None):
    def _log():
        try:
            get_logger().log_recharge_rejected(user_id, amount, method, utr)
        except Exception as e:
            logging.error(f"Failed to log recharge rejection: {e}")
    threading.Thread(target=_log, daemon=True).start()


def log_custom_async(title: str, **kwargs):
    def _log():
        try:
            get_logger().log_custom(title, **kwargs)
        except Exception as e:
            logging.error(f"Failed to send custom log: {e}")
    threading.Thread(target=_log, daemon=True).start()


__all__ = [
    'TelegramLogger',
    'init_logger',
    'get_logger',
    'log_purchase_async',
    'log_otp_received_async',
    'log_recharge_approved_async',
    'log_recharge_rejected_async',
    'log_custom_async',
    'telegram_logger',
]
