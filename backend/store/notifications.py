# ═══════════════════════════════════════════════════════════════════════
# store/notifications.py
# ───────────────────────────────────────────────────────────────────────
# নতুন Order হলে Admin/Seller কে পাঠায়:
#   ✅ Email     — Gmail SMTP
#   ✅ SMS       — SSL Wireless (Bangladesh)
#   ✅ WhatsApp  — Twilio WhatsApp API
#   ✅ Telegram  — Telegram Bot API
#
# .env তে যা লাগবে:
#   ADMIN_PHONE         = 01XXXXXXXXX
#   ADMIN_EMAIL         = admin@shopbd.com
#   EMAIL_HOST_USER     = yourshop@gmail.com
#   EMAIL_HOST_PASSWORD = xxxx xxxx xxxx xxxx   ← Gmail App Password
#   SSL_WIRELESS_API_TOKEN = your_token
#   SSL_WIRELESS_SID       = your_sid
#   TWILIO_ACCOUNT_SID  = ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#   TWILIO_AUTH_TOKEN   = your_auth_token
#   TWILIO_WHATSAPP_FROM= whatsapp:+14155238886
#   TELEGRAM_BOT_TOKEN  = 123456789:AAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#   TELEGRAM_CHAT_ID    = -100xxxxxxxxxx   ← আপনার channel/group ID
# ═══════════════════════════════════════════════════════════════════════

import requests
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────
# Helper — settings থেকে value নিরাপদে পড়া
# ─────────────────────────────────────────────────────────────────────
def _cfg(key, default=''):
    return getattr(settings, key, default) or default


# ─────────────────────────────────────────────────────────────────────
# 1. EMAIL — Gmail SMTP
# ─────────────────────────────────────────────────────────────────────
def send_order_email(to: str, subject: str, html_body: str) -> bool:
    try:
        plain = strip_tags(html_body)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain,
            from_email=_cfg('DEFAULT_FROM_EMAIL', 'ShopBD <noreply@shopbd.com>'),
            to=[to],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send()
        logger.info(f'✅ Email sent → {to}')
        return True
    except Exception as e:
        logger.error(f'❌ Email error → {to}: {e}')
        return False


# ─────────────────────────────────────────────────────────────────────
# 2. SMS — SSL Wireless (Bangladesh)
# ─────────────────────────────────────────────────────────────────────
def send_sms(phone: str, message: str) -> bool:
    token = _cfg('SSL_WIRELESS_API_TOKEN')
    sid   = _cfg('SSL_WIRELESS_SID')
    if not token or not sid:
        logger.warning('SMS skipped — SSL_WIRELESS credentials not set')
        return False
    try:
        if phone.startswith('0'):
            phone = '880' + phone[1:]
        res = requests.post(
            'https://sms.sslwireless.com/pushapi/dynamic/server.php',
            data={
                'api_token': token,
                'sid':       sid,
                'msisdn':    phone,
                'sms':       message,
                'csmsid':    f'SBD_{phone[-6:]}',
            },
            timeout=10,
        )
        data = res.json()
        if data.get('status') in ('ACCEPTED', 'Success'):
            logger.info(f'✅ SMS sent → {phone}')
            return True
        logger.warning(f'❌ SMS failed → {data}')
        return False
    except Exception as e:
        logger.error(f'❌ SMS error: {e}')
        return False


# ─────────────────────────────────────────────────────────────────────
# 3. WHATSAPP — Twilio WhatsApp API
# ─────────────────────────────────────────────────────────────────────
def send_whatsapp(phone: str, message: str) -> bool:
    """
    Twilio WhatsApp Sandbox বা Business Account দিয়ে message পাঠায়।

    Sandbox test করতে:
      1. https://console.twilio.com → Messaging → Try it out → WhatsApp
      2. আপনার phone থেকে "join <sandbox_code>" পাঠান
      3. তারপর message পাবেন

    .env তে লাগবে:
      TWILIO_ACCOUNT_SID   = ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
      TWILIO_AUTH_TOKEN    = your_auth_token
      TWILIO_WHATSAPP_FROM = whatsapp:+14155238886
    """
    account_sid = _cfg('TWILIO_ACCOUNT_SID')
    auth_token  = _cfg('TWILIO_AUTH_TOKEN')
    from_number = _cfg('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')

    if not account_sid or not auth_token:
        logger.warning('WhatsApp skipped — Twilio credentials not set')
        return False

    try:
        # phone format: 01XXXXXXXXX → whatsapp:+880XXXXXXXXX
        if phone.startswith('0'):
            to_number = 'whatsapp:+880' + phone[1:]
        elif phone.startswith('880'):
            to_number = 'whatsapp:+' + phone
        else:
            to_number = 'whatsapp:' + phone

        res = requests.post(
            f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json',
            data={
                'From': from_number,
                'To':   to_number,
                'Body': message,
            },
            auth=(account_sid, auth_token),
            timeout=15,
        )
        data = res.json()
        if res.status_code in (200, 201):
            logger.info(f'✅ WhatsApp sent → {to_number}')
            return True
        logger.warning(f'❌ WhatsApp failed → {data.get("message", data)}')
        return False
    except Exception as e:
        logger.error(f'❌ WhatsApp error: {e}')
        return False


# ─────────────────────────────────────────────────────────────────────
# 4. TELEGRAM — Bot API
# ─────────────────────────────────────────────────────────────────────
def send_telegram(message: str) -> bool:
    """
    Telegram Bot দিয়ে channel/group/personal chat এ message পাঠায়.

    Bot বানাতে:
      1. Telegram এ @BotFather → /newbot
      2. Bot Token কপি করুন → TELEGRAM_BOT_TOKEN
      3. Channel বানান → Bot কে admin করুন
      4. Channel ID পেতে: https://api.telegram.org/bot<TOKEN>/getUpdates

    .env তে লাগবে:
      TELEGRAM_BOT_TOKEN = 123456789:AAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
      TELEGRAM_CHAT_ID   = -100xxxxxxxxxx
    """
    bot_token = _cfg('TELEGRAM_BOT_TOKEN')
    chat_id   = _cfg('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        logger.warning('Telegram skipped — credentials not set')
        return False

    try:
        res = requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            json={
                'chat_id':    chat_id,
                'text':       message,
                'parse_mode': 'HTML',
            },
            timeout=10,
        )
        data = res.json()
        if data.get('ok'):
            logger.info('✅ Telegram sent')
            return True
        logger.warning(f'❌ Telegram failed → {data.get("description")}')
        return False
    except Exception as e:
        logger.error(f'❌ Telegram error: {e}')
        return False


# ─────────────────────────────────────────────────────────────────────
# Message Templates
# ─────────────────────────────────────────────────────────────────────

def _pay_label(method):
    return {
        'cod': 'Cash on Delivery', 'bkash': 'bKash',
        'nagad': 'Nagad', 'rocket': 'Rocket', 'upay': 'Upay',
        'ssl': 'SSL Commerz', 'shurjopay': 'Shurjopay',
    }.get(method, method.upper())


def _admin_sms_text(order) -> str:
    return (
        f"[ShopBD] নতুন Order #{order.id}!\n"
        f"Product: {order.product.name} x{order.quantity}\n"
        f"Customer: {order.phone}\n"
        f"Total: {order.total_amount} BDT\n"
        f"Payment: {_pay_label(order.payment_method)}\n"
        f"Address: {str(order.address)[:60]}"
    )


def _admin_whatsapp_text(order) -> str:
    return (
        f"🛒 *নতুন Order #{order.id}!* — ShopBD\n\n"
        f"📦 *Product:* {order.product.name}\n"
        f"🔢 *Quantity:* {order.quantity}\n"
        f"📞 *Customer:* {order.phone}\n"
        f"📍 *Address:* {str(order.address)[:80]}\n"
        f"💳 *Payment:* {_pay_label(order.payment_method)}\n"
        f"💰 *Total:* ৳{order.total_amount}\n\n"
        f"⏰ এখনই process করুন!"
    )


def _admin_telegram_text(order) -> str:
    return (
        f"🔔 <b>নতুন Order #{order.id}!</b>\n\n"
        f"📦 <b>Product:</b> {order.product.name}\n"
        f"🔢 <b>Quantity:</b> {order.quantity}\n"
        f"📞 <b>Customer:</b> <code>{order.phone}</code>\n"
        f"📍 <b>Address:</b> {str(order.address)[:100]}\n"
        f"💳 <b>Payment:</b> {_pay_label(order.payment_method)}\n"
        f"💰 <b>Total:</b> ৳{order.total_amount}\n"
        f"📊 <b>Status:</b> {order.order_status}\n\n"
        f"🔗 <a href='{_cfg('BASE_URL', 'http://127.0.0.1:8000')}"
        f"/admin/store/order/{order.id}/change/'>Admin Panel এ দেখুন →</a>"
    )


def _admin_email_html(order) -> str:
    pay = _pay_label(order.payment_method)
    base_url = _cfg('BASE_URL', 'http://127.0.0.1:8000')
    admin_url = f"{base_url}/admin/store/order/{order.id}/change/"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f4f8; padding: 24px; }}
  .wrap {{ max-width: 540px; margin: 0 auto; }}
  .header {{ background: linear-gradient(135deg, #f97316, #ea580c); border-radius: 16px 16px 0 0; padding: 24px; text-align: center; }}
  .header h1 {{ color: #fff; font-size: 22px; font-weight: 900; }}
  .header p  {{ color: rgba(255,255,255,0.85); font-size: 13px; margin-top: 4px; }}
  .body {{ background: #fff; padding: 28px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
  .alert {{ background: #fff7ed; border: 1px solid #fed7aa; border-radius: 10px; padding: 14px 18px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }}
  .alert-icon {{ font-size: 24px; }}
  .alert-text {{ color: #c2410c; font-weight: 700; font-size: 15px; }}
  .table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
  .table tr td {{ padding: 10px 12px; font-size: 14px; border-bottom: 1px solid #f1f5f9; }}
  .table tr td:first-child {{ color: #94a3b8; width: 40%; }}
  .table tr td:last-child {{ color: #1e293b; font-weight: 600; }}
  .total-box {{ background: linear-gradient(135deg, #f97316, #ea580c); border-radius: 12px; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
  .total-box span {{ color: #fff; font-size: 15px; font-weight: 700; }}
  .total-box strong {{ color: #fff; font-size: 24px; font-weight: 900; }}
  .btn {{ display: block; text-align: center; background: #1e293b; color: #fff; border-radius: 10px; padding: 14px; font-weight: 700; text-decoration: none; font-size: 14px; }}
  .footer {{ text-align: center; margin-top: 20px; color: #94a3b8; font-size: 12px; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <h1>🛒 ShopBD — নতুন Order!</h1>
    <p>Order #{order.id} এসেছে, এখনই process করুন</p>
  </div>
  <div class="body">
    <div class="alert">
      <span class="alert-icon">🔔</span>
      <span class="alert-text">নতুন Order #{order.id} — {order.product.name}</span>
    </div>

    <table class="table">
      <tr><td>📦 Product</td><td>{order.product.name}</td></tr>
      <tr><td>🔢 Quantity</td><td>{order.quantity}</td></tr>
      <tr><td>📞 Customer Phone</td><td>{order.phone}</td></tr>
      <tr><td>📍 Delivery Address</td><td>{order.address}</td></tr>
      <tr><td>💳 Payment Method</td><td>{pay}</td></tr>
      <tr><td>📊 Payment Status</td><td>{order.payment_status}</td></tr>
      <tr><td>🚚 Delivery Charge</td><td>৳{order.delivery_charge}</td></tr>
      <tr><td>🆔 Transaction ID</td><td>{order.transaction_id or 'N/A'}</td></tr>
    </table>

    <div class="total-box">
      <span>Grand Total</span>
      <strong>৳{order.total_amount}</strong>
    </div>

    <a href="{admin_url}" class="btn">
      🔗 Admin Panel এ দেখুন →
    </a>

    <div class="footer" style="margin-top:16px;">
      ShopBD Admin Notification System · {_cfg('ADMIN_PHONE', '01700-000000')}
    </div>
  </div>
</div>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────
# MAIN FUNCTION — views.py থেকে এটাই call করুন
# ─────────────────────────────────────────────────────────────────────

def send_order_notifications(order) -> dict:
    """
    একটা function call এ সব notification পাঠায়।

    Usage in views.py:
        from .notifications import send_order_notifications
        send_order_notifications(order)

    Returns dict of results:
        { 'email': True, 'sms': True, 'whatsapp': True, 'telegram': True }
    """
    results = {}

    admin_phone = _cfg('ADMIN_PHONE')
    admin_email = _cfg('ADMIN_EMAIL')

    # ── 1. Email ─────────────────────────────────────────────────────
    if admin_email:
        results['email'] = send_order_email(
            to=admin_email,
            subject=f'🔔 নতুন Order #{order.id} — {order.product.name} | ShopBD',
            html_body=_admin_email_html(order),
        )
    else:
        results['email'] = False
        logger.warning('Admin email not configured')

    # ── 2. SMS ───────────────────────────────────────────────────────
    if admin_phone:
        results['sms'] = send_sms(admin_phone, _admin_sms_text(order))
    else:
        results['sms'] = False
        logger.warning('Admin phone not configured')

    # ── 3. WhatsApp ──────────────────────────────────────────────────
    if admin_phone:
        results['whatsapp'] = send_whatsapp(admin_phone, _admin_whatsapp_text(order))
    else:
        results['whatsapp'] = False

    # ── 4. Telegram ──────────────────────────────────────────────────
    results['telegram'] = send_telegram(_admin_telegram_text(order))

    logger.info(f'Order #{order.id} notifications: {results}')
    return results