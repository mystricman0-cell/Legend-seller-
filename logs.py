"""
Logging Module for OTP Bot — Dual Channel
Channel 1 (MASKED  — public log):  -1003912691513
Channel 2 (FULL detail — personal): same as channel 1 unless PERSONAL_LOG_CHANNEL_ID is set
"""

import logging
import time
from datetime import datetime
from typing import Optional
import threading

logger = logging.getLogger(__name__)

# ─── Masking helpers ───────────────────────────────────────────────────────────

def _mask_otp(otp_code: str) -> str:
    if not otp_code:
        return "****"
    s = str(otp_code).strip()
    return (s[:2] + "****") if len(s) > 2 else (s + "****")

def _mask_2fa(password: str) -> str:
    if not password:
        return "****"
    p = str(password)
    return (p[:2] + "****") if len(p) > 2 else (p + "****")

def _mask_phone(phone: str) -> str:
    if not phone:
        return "N/A"
    try:
        d = ''.join(filter(str.isdigit, phone))
        if len(d) >= 8:
            return d[:4] + "****" + d[-2:]
        elif d:
            return d[:3] + "****"
        return "N/A"
    except:
        return "****"

def _mask_user(user_id) -> str:
    try:
        s = str(user_id)
        return (s[:3] + "***" + s[-2:]) if len(s) > 4 else (s[:2] + "***")
    except:
        return str(user_id)[:3] + "***"

def _mask_utr(utr: str) -> str:
    if not utr:
        return "N/A"
    try:
        return (utr[:4] + "****" + utr[-2:]) if len(utr) >= 8 else (utr[:3] + "***")
    except:
        return utr

# ─── Logger class ──────────────────────────────────────────────────────────────

class TelegramLogger:
    """
    Sends logs to TWO Telegram channels:
      • log_channel_id       — masked (public/shared)
      • personal_channel_id  — full unmasked detail (owner only)
    """

    def __init__(self, bot_token: str, log_channel_id: str,
                 personal_channel_id: str = None,
                 support_link: str = "https://t.me/rchiex",
                 buy_link: str = "https://t.me/LEGENDARY_OTP_SELLER_Bot"):
        self.bot_token = bot_token
        self.log_channel_id = str(log_channel_id)
        # If no personal channel given, fall back to same channel
        self.personal_channel_id = str(personal_channel_id) if personal_channel_id else str(log_channel_id)
        self.support_link = support_link
        self.buy_link = buy_link
        self._bot = None
        self._init_bot()

    def _init_bot(self):
        try:
            import telebot
            from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
            self._bot = telebot.TeleBot(self.bot_token)
            self.IKM = InlineKeyboardMarkup
            self.IKB = InlineKeyboardButton
            logger.info(f"✅ Telegram logger ready | masked={self.log_channel_id} | full={self.personal_channel_id}")
        except Exception as e:
            logger.error(f"❌ Logger init failed: {e}")
            self._bot = None

    def _inline_btns(self):
        m = self.IKM(row_width=2)
        m.add(
            self.IKB("🆘 Support", url=self.support_link),
            self.IKB("🛒 Buy", url=self.buy_link)
        )
        return m

    def _send(self, channel_id: str, message: str, markup=None) -> bool:
        if not self._bot:
            return False
        try:
            self._bot.send_message(
                channel_id,
                f"<blockquote>{message}</blockquote>",
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=markup or self._inline_btns()
            )
            return True
        except Exception as e:
            logger.error(f"Log send failed to {channel_id}: {e}")
            return False

    # ── PUBLIC (masked) channel helpers ─────────────────────────────────────────

    def log_purchase(self, user_id: int, country: str, price: float, phone: str) -> bool:
        """Masked purchase log → public channel"""
        t = datetime.now().strftime("%I:%M %p")
        msg = (
            f"<b>🔥 NEW ACCOUNT SOLD! 🔥</b>\n\n"
            f"<b>✚ Category:</b> {country}\n"
            f"<b>✚ Number:</b> {_mask_phone(phone)} 📞\n"
            f"<b>✚ User:</b> {_mask_user(user_id)} 👤\n"
            f"<b>✚ Price:</b> ₹{price:.0f}\n"
            f"<b>✚ Status:</b> Verified &amp; Delivered ✅\n"
            f"<b>✚ Time:</b> {t}\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self._send(self.log_channel_id, msg)

    def log_otp_received(self, user_id: int, phone: str, otp_code: str,
                         country: str, price: float) -> bool:
        """Masked OTP log → public channel"""
        t = datetime.now().strftime("%I:%M %p")
        msg = (
            f"<b>🔐 OTP RECEIVED! 🔐</b>\n\n"
            f"<b>━ Category:</b> {country}\n"
            f"<b>━ Number:</b> {_mask_phone(phone)} 📞\n"
            f"<b>━ OTP:</b> ||<code>{_mask_otp(otp_code)}</code>|| 💬\n"
            f"<b>━ User:</b> {_mask_user(user_id)} 👤\n"
            f"<b>━ Time:</b> {t}\n"
            f"<b>━ Status:</b> OTP Delivered ✅\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self._send(self.log_channel_id, msg)

    def log_recharge_approved(self, user_id: int, amount: float,
                              method: str = "UPI", utr: str = None) -> bool:
        """Masked deposit approved → public channel"""
        t = datetime.now().strftime("%I:%M %p")
        msg = (
            f"<b>💰 DEPOSIT APPROVED! 💰</b>\n\n"
            f"<b>User:</b> {_mask_user(user_id)}\n"
            f"<b>Amount:</b> ₹{amount:,.0f}\n"
            f"<b>Method:</b> {method}\n"
            f"<b>UTR:</b> {_mask_utr(utr) if utr else 'N/A'}\n"
            f"<b>Time:</b> {t}\n"
            f"<b>Status:</b> Balance Updated ✅\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self._send(self.log_channel_id, msg)

    def log_recharge_rejected(self, user_id: int, amount: float,
                              method: str = "UPI", utr: str = None) -> bool:
        """Masked deposit rejected → public channel"""
        t = datetime.now().strftime("%I:%M %p")
        msg = (
            f"<b>❌ DEPOSIT REJECTED! ❌</b>\n\n"
            f"<b>User:</b> {_mask_user(user_id)}\n"
            f"<b>Amount:</b> ₹{amount:,.0f}\n"
            f"<b>Method:</b> {method}\n"
            f"<b>UTR:</b> {_mask_utr(utr) if utr else 'N/A'}\n"
            f"<b>Time:</b> {t}\n"
            f"<b>Status:</b> Rejected ❌\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self._send(self.log_channel_id, msg)

    # ── PERSONAL (full detail) channel helpers ──────────────────────────────────

    def log_personal_purchase(self, user_id: int, username: str, country: str,
                               price: float, phone: str) -> bool:
        """Full unmasked purchase log → personal channel"""
        t = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
        msg = (
            f"<b>📦 PURCHASE — FULL DETAIL</b>\n\n"
            f"<b>🆔 User ID:</b> <code>{user_id}</code>\n"
            f"<b>👤 Username:</b> @{username or 'N/A'}\n"
            f"<b>🌍 Country:</b> {country}\n"
            f"<b>📱 Phone:</b> <code>{phone}</code>\n"
            f"<b>💰 Price:</b> ₹{price:.2f}\n"
            f"<b>⏰ Time:</b> {t}\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self._send(self.personal_channel_id, msg)

    def log_personal_otp(self, user_id: int, username: str, phone: str,
                          otp_code: str, two_fa: str, country: str) -> bool:
        """Full OTP + 2FA → personal channel"""
        t = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
        fa_line = f"\n<b>🔐 2FA:</b> <code>{two_fa}</code>" if two_fa else ""
        msg = (
            f"<b>🔑 OTP RECEIVED — FULL DETAIL</b>\n\n"
            f"<b>🆔 User ID:</b> <code>{user_id}</code>\n"
            f"<b>👤 Username:</b> @{username or 'N/A'}\n"
            f"<b>🌍 Country:</b> {country}\n"
            f"<b>📱 Phone:</b> <code>{phone}</code>\n"
            f"<b>🔢 OTP:</b> <code>{otp_code}</code>{fa_line}\n"
            f"<b>⏰ Time:</b> {t}\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self._send(self.personal_channel_id, msg)

    def log_personal_deposit_approved(self, user_id: int, username: str,
                                       amount: float, method: str,
                                       utr: str, admin_name: str) -> bool:
        """Full deposit approved → personal channel"""
        t = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
        msg = (
            f"<b>✅ DEPOSIT APPROVED — FULL DETAIL</b>\n\n"
            f"<b>🆔 User ID:</b> <code>{user_id}</code>\n"
            f"<b>👤 Username:</b> @{username or 'N/A'}\n"
            f"<b>💰 Amount:</b> ₹{amount:,.2f}\n"
            f"<b>💳 Method:</b> {method}\n"
            f"<b>🔢 UTR:</b> <code>{utr or 'N/A'}</code>\n"
            f"<b>👮 Approved By:</b> {admin_name}\n"
            f"<b>⏰ Time:</b> {t}\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self._send(self.personal_channel_id, msg)

    def log_personal_deposit_rejected(self, user_id: int, username: str,
                                       amount: float, method: str,
                                       utr: str, admin_name: str) -> bool:
        """Full deposit rejected → personal channel"""
        t = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
        msg = (
            f"<b>❌ DEPOSIT REJECTED — FULL DETAIL</b>\n\n"
            f"<b>🆔 User ID:</b> <code>{user_id}</code>\n"
            f"<b>👤 Username:</b> @{username or 'N/A'}\n"
            f"<b>💰 Amount:</b> ₹{amount:,.2f}\n"
            f"<b>💳 Method:</b> {method}\n"
            f"<b>🔢 UTR:</b> <code>{utr or 'N/A'}</code>\n"
            f"<b>👮 Rejected By:</b> {admin_name}\n"
            f"<b>⏰ Time:</b> {t}\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self._send(self.personal_channel_id, msg)

    def log_personal_new_user(self, user_id: int, username: str, first_name: str,
                               referred_by: int = None) -> bool:
        """New user joined → personal channel"""
        t = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
        ref_line = f"\n<b>🔗 Referred By:</b> <code>{referred_by}</code>" if referred_by else ""
        msg = (
            f"<b>👤 NEW USER JOINED</b>\n\n"
            f"<b>🆔 User ID:</b> <code>{user_id}</code>\n"
            f"<b>👤 Username:</b> @{username or 'N/A'}\n"
            f"<b>📛 Name:</b> {first_name or 'N/A'}{ref_line}\n"
            f"<b>⏰ Time:</b> {t}\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self._send(self.personal_channel_id, msg)

    def log_personal_recharge_request(self, user_id: int, username: str,
                                       amount: float, utr: str, method: str) -> bool:
        """New recharge request → personal channel"""
        t = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
        msg = (
            f"<b>🔔 NEW RECHARGE REQUEST</b>\n\n"
            f"<b>🆔 User ID:</b> <code>{user_id}</code>\n"
            f"<b>👤 Username:</b> @{username or 'N/A'}\n"
            f"<b>💰 Amount:</b> ₹{amount:,.2f}\n"
            f"<b>💳 Method:</b> {method}\n"
            f"<b>🔢 UTR:</b> <code>{utr or 'N/A'}</code>\n"
            f"<b>⏰ Time:</b> {t}\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self._send(self.personal_channel_id, msg)

    def log_personal_balance_deduct(self, user_id: int, username: str,
                                     amount: float, reason: str, admin_name: str) -> bool:
        """Balance deduction → personal channel"""
        t = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
        msg = (
            f"<b>💸 BALANCE DEDUCTED</b>\n\n"
            f"<b>🆔 User ID:</b> <code>{user_id}</code>\n"
            f"<b>👤 Username:</b> @{username or 'N/A'}\n"
            f"<b>💰 Amount:</b> ₹{amount:,.2f}\n"
            f"<b>📝 Reason:</b> {reason}\n"
            f"<b>👮 By Admin:</b> {admin_name}\n"
            f"<b>⏰ Time:</b> {t}\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self._send(self.personal_channel_id, msg)

    def log_personal_ban(self, user_id: int, username: str, action: str,
                          admin_name: str) -> bool:
        """User ban/unban → personal channel"""
        t = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
        icon = "🚫" if action == "banned" else "✅"
        msg = (
            f"<b>{icon} USER {action.upper()}</b>\n\n"
            f"<b>🆔 User ID:</b> <code>{user_id}</code>\n"
            f"<b>👤 Username:</b> @{username or 'N/A'}\n"
            f"<b>👮 By Admin:</b> {admin_name}\n"
            f"<b>⏰ Time:</b> {t}\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self._send(self.personal_channel_id, msg)

    def log_heartbeat(self, uptime_str: str, stats: dict) -> bool:
        """Heartbeat report → personal channel"""
        t = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
        msg = (
            f"<b>💓 BOT HEARTBEAT REPORT</b>\n\n"
            f"<b>⏰ Time:</b> {t}\n"
            f"<b>🕐 Uptime:</b> {uptime_str}\n"
            f"<b>👥 Total Users:</b> {stats.get('users', 0)}\n"
            f"<b>📦 Active Accounts:</b> {stats.get('active_accounts', 0)}\n"
            f"<b>🛒 Total Orders:</b> {stats.get('orders', 0)}\n"
            f"<b>💰 Pending Recharges:</b> {stats.get('pending_recharges', 0)}\n"
            f"<b>✅ Status:</b> Running normally 🟢\n\n"
            f"<b>🤖 @LEGENDARY_OTP_SELLER_Bot</b>"
        )
        return self._send(self.personal_channel_id, msg)

    def log_custom(self, title: str, **kwargs) -> bool:
        formatted = []
        for k, v in kwargs.items():
            if k.lower() == "user_id" and v:
                v = _mask_user(v)
            elif k.lower() == "phone" and v:
                v = _mask_phone(str(v))
            elif k.lower() in ("otp", "otp_code") and v:
                v = _mask_otp(str(v))
            elif k.lower() in ("password", "2fa", "two_fa") and v:
                v = _mask_2fa(str(v))
            formatted.append(f"<b>{k}:</b> {v}")
        t = datetime.now().strftime("%I:%M %p")
        msg = f"<b>{title}</b>\n\n{chr(10).join(formatted)}\n\n⏰ {t}"
        return self._send(self.log_channel_id, msg)


# ─── Global instance ───────────────────────────────────────────────────────────

telegram_logger = None


def init_logger(bot_token: str, log_channel_id: str,
                personal_channel_id: str = None,
                support_link: str = "https://t.me/rchiex",
                buy_link: str = "https://t.me/LEGENDARY_OTP_SELLER_Bot"):
    global telegram_logger
    telegram_logger = TelegramLogger(
        bot_token, log_channel_id,
        personal_channel_id=personal_channel_id,
        support_link=support_link,
        buy_link=buy_link
    )
    return telegram_logger


def get_logger() -> TelegramLogger:
    global telegram_logger
    if telegram_logger is None:
        raise ValueError("Logger not initialized. Call init_logger() first.")
    return telegram_logger


# ─── Async wrapper helpers ─────────────────────────────────────────────────────

def _run_async(fn, *args, **kwargs):
    threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()


def log_purchase_async(user_id: int, country: str, price: float, phone: str):
    def _log():
        try:
            get_logger().log_purchase(user_id, country, price, phone)
        except Exception as e:
            logging.error(f"log_purchase_async: {e}")
    _run_async(_log)


def log_otp_received_async(user_id: int, phone: str, otp_code: str,
                           country: str, price: float):
    def _log():
        try:
            get_logger().log_otp_received(user_id, phone, otp_code, country, price)
        except Exception as e:
            logging.error(f"log_otp_received_async: {e}")
    _run_async(_log)


def log_recharge_approved_async(user_id: int, amount: float,
                                method: str = "UPI", utr: str = None):
    def _log():
        try:
            get_logger().log_recharge_approved(user_id, amount, method, utr)
        except Exception as e:
            logging.error(f"log_recharge_approved_async: {e}")
    _run_async(_log)


def log_recharge_rejected_async(user_id: int, amount: float,
                                method: str = "UPI", utr: str = None):
    def _log():
        try:
            get_logger().log_recharge_rejected(user_id, amount, method, utr)
        except Exception as e:
            logging.error(f"log_recharge_rejected_async: {e}")
    _run_async(_log)


def log_personal_purchase_async(user_id: int, username: str, country: str,
                                 price: float, phone: str):
    def _log():
        try:
            get_logger().log_personal_purchase(user_id, username, country, price, phone)
        except Exception as e:
            logging.error(f"log_personal_purchase_async: {e}")
    _run_async(_log)


def log_personal_otp_async(user_id: int, username: str, phone: str,
                            otp_code: str, two_fa: str, country: str):
    def _log():
        try:
            get_logger().log_personal_otp(user_id, username, phone, otp_code, two_fa, country)
        except Exception as e:
            logging.error(f"log_personal_otp_async: {e}")
    _run_async(_log)


def log_personal_deposit_approved_async(user_id: int, username: str, amount: float,
                                        method: str, utr: str, admin_name: str):
    def _log():
        try:
            get_logger().log_personal_deposit_approved(user_id, username, amount, method, utr, admin_name)
        except Exception as e:
            logging.error(f"log_personal_deposit_approved_async: {e}")
    _run_async(_log)


def log_personal_deposit_rejected_async(user_id: int, username: str, amount: float,
                                        method: str, utr: str, admin_name: str):
    def _log():
        try:
            get_logger().log_personal_deposit_rejected(user_id, username, amount, method, utr, admin_name)
        except Exception as e:
            logging.error(f"log_personal_deposit_rejected_async: {e}")
    _run_async(_log)


def log_personal_new_user_async(user_id: int, username: str, first_name: str,
                                 referred_by: int = None):
    def _log():
        try:
            get_logger().log_personal_new_user(user_id, username, first_name, referred_by)
        except Exception as e:
            logging.error(f"log_personal_new_user_async: {e}")
    _run_async(_log)


def log_personal_recharge_request_async(user_id: int, username: str,
                                         amount: float, utr: str, method: str):
    def _log():
        try:
            get_logger().log_personal_recharge_request(user_id, username, amount, utr, method)
        except Exception as e:
            logging.error(f"log_personal_recharge_request_async: {e}")
    _run_async(_log)


def log_personal_balance_deduct_async(user_id: int, username: str,
                                       amount: float, reason: str, admin_name: str):
    def _log():
        try:
            get_logger().log_personal_balance_deduct(user_id, username, amount, reason, admin_name)
        except Exception as e:
            logging.error(f"log_personal_balance_deduct_async: {e}")
    _run_async(_log)


def log_personal_ban_async(user_id: int, username: str, action: str, admin_name: str):
    def _log():
        try:
            get_logger().log_personal_ban(user_id, username, action, admin_name)
        except Exception as e:
            logging.error(f"log_personal_ban_async: {e}")
    _run_async(_log)


def log_custom_async(title: str, **kwargs):
    def _log():
        try:
            get_logger().log_custom(title, **kwargs)
        except Exception as e:
            logging.error(f"log_custom_async: {e}")
    _run_async(_log)


__all__ = [
    'TelegramLogger', 'init_logger', 'get_logger',
    'log_purchase_async', 'log_otp_received_async',
    'log_recharge_approved_async', 'log_recharge_rejected_async',
    'log_personal_purchase_async', 'log_personal_otp_async',
    'log_personal_deposit_approved_async', 'log_personal_deposit_rejected_async',
    'log_personal_new_user_async', 'log_personal_recharge_request_async',
    'log_personal_balance_deduct_async', 'log_personal_ban_async',
    'log_custom_async', 'telegram_logger',
]
