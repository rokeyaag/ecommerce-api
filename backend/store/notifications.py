import requests
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


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
        msg.encoding = 'utf-8'
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
# 3. WHATSAPP — Twilio
# ─────────────────────────────────────────────────────────────────────
def send_whatsapp(phone: str, message: str) -> bool:
    account_sid = _cfg('TWILIO_ACCOUNT_SID')
    auth_token  = _cfg('TWILIO_AUTH_TOKEN')
    from_number = _cfg('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')

    if not account_sid or not auth_token:
        logger.warning('WhatsApp skipped — Twilio credentials not set')
        return False

    try:
        if phone.startswith('0'):
            to_number = 'whatsapp:+880' + phone[1:]
        elif phone.startswith('880'):
            to_number = 'whatsapp:+' + phone
        else:
            to_number = 'whatsapp:' + phone

        res = requests.post(
            f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json',
            data={'From': from_number, 'To': to_number, 'Body': message},
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
def send_telegram(message: str, chat_id: str = None) -> bool:
    bot_token = _cfg('TELEGRAM_BOT_TOKEN')
    cid       = chat_id or _cfg('TELEGRAM_CHAT_ID')

    if not bot_token or not cid:
        logger.warning('Telegram skipped — credentials not set')
        return False

    try:
        res = requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            json={'chat_id': cid, 'text': message, 'parse_mode': 'HTML'},
            timeout=10,
        )
        data = res.json()
        if data.get('ok'):
            logger.info(f'✅ Telegram sent → {cid}')
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


# ── Admin Templates ──────────────────────────────────────────────────

def _admin_sms_text(order) -> str:
    return (
        f"[ShopBD] New Order #{order.id}!\n"
        f"Product: {order.product.name} x{order.quantity}\n"
        f"Customer: {order.phone}\n"
        f"Total: {order.total_amount} BDT\n"
        f"Payment: {_pay_label(order.payment_method)}\n"
        f"Address: {str(order.address)[:60]}"
    )


def _admin_telegram_text(order) -> str:
    return (
        f"<b>New Order #{order.id}!</b>\n\n"
        f"<b>Product:</b> {order.product.name}\n"
        f"<b>Quantity:</b> {order.quantity}\n"
        f"<b>Customer:</b> <code>{order.phone}</code>\n"
        f"<b>Address:</b> {str(order.address)[:100]}\n"
        f"<b>Payment:</b> {_pay_label(order.payment_method)}\n"
        f"<b>Total:</b> {order.total_amount} BDT\n"
        f"<b>Status:</b> {order.order_status}"
    )


def _admin_email_html(order) -> str:
    pay = _pay_label(order.payment_method)
    base_url  = _cfg('BASE_URL', 'http://127.0.0.1:8000')
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
  .alert {{ background: #fff7ed; border: 1px solid #fed7aa; border-radius: 10px; padding: 14px 18px; margin-bottom: 20px; }}
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
    <h1>ShopBD - New Order!</h1>
    <p>Order #{order.id} received - Please process now</p>
  </div>
  <div class="body">
    <div class="alert">
      <span class="alert-text">New Order #{order.id} - {order.product.name}</span>
    </div>
    <table class="table">
      <tr><td>Product</td><td>{order.product.name}</td></tr>
      <tr><td>Quantity</td><td>{order.quantity}</td></tr>
      <tr><td>Customer Phone</td><td>{order.phone}</td></tr>
      <tr><td>Delivery Address</td><td>{order.address}</td></tr>
      <tr><td>Payment Method</td><td>{pay}</td></tr>
      <tr><td>Payment Status</td><td>{order.payment_status}</td></tr>
      <tr><td>Delivery Charge</td><td>{order.delivery_charge} BDT</td></tr>
      <tr><td>Transaction ID</td><td>{order.transaction_id or 'N/A'}</td></tr>
    </table>
    <div class="total-box">
      <span>Grand Total</span>
      <strong>{order.total_amount} BDT</strong>
    </div>
    <a href="{admin_url}" class="btn">View in Admin Panel</a>
    <div class="footer" style="margin-top:16px;">ShopBD Admin Notification System</div>
  </div>
</div>
</body>
</html>"""


# ── Customer Templates ───────────────────────────────────────────────

def _customer_telegram_text(order) -> str:
    return (
        f"<b>Order Confirmed!</b>\n\n"
        f"Thank you for your order!\n\n"
        f"<b>Order ID:</b> #{order.id}\n"
        f"<b>Product:</b> {order.product.name}\n"
        f"<b>Quantity:</b> {order.quantity}\n"
        f"<b>Payment:</b> {_pay_label(order.payment_method)}\n"
        f"<b>Total:</b> {order.total_amount} BDT\n"
        f"<b>Status:</b> Confirmed\n\n"
        f"We will contact you soon!"
    )


def _customer_email_html(order) -> str:
    pay = _pay_label(order.payment_method)
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
  .success {{ background: #f0fdf4; border: 1px solid #86efac; border-radius: 10px; padding: 20px; margin-bottom: 20px; text-align: center; }}
  .success-icon {{ font-size: 48px; margin-bottom: 8px; }}
  .success-text {{ color: #16a34a; font-weight: 700; font-size: 18px; }}
  .table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
  .table tr td {{ padding: 10px 12px; font-size: 14px; border-bottom: 1px solid #f1f5f9; }}
  .table tr td:first-child {{ color: #94a3b8; width: 40%; }}
  .table tr td:last-child {{ color: #1e293b; font-weight: 600; }}
  .total-box {{ background: linear-gradient(135deg, #f97316, #ea580c); border-radius: 12px; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
  .total-box span {{ color: #fff; font-size: 15px; font-weight: 700; }}
  .total-box strong {{ color: #fff; font-size: 24px; font-weight: 900; }}
  .footer {{ text-align: center; margin-top: 20px; color: #94a3b8; font-size: 12px; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <h1>ShopBD</h1>
    <p>Order Confirmation</p>
  </div>
  <div class="body">
    <div class="success">
      <div class="success-icon">✅</div>
      <div class="success-text">Order Confirmed!</div>
      <p style="color:#64748b; font-size:13px; margin-top:6px;">Thank you for shopping with ShopBD</p>
    </div>
    <table class="table">
      <tr><td>Order ID</td><td>#{order.id}</td></tr>
      <tr><td>Product</td><td>{order.product.name}</td></tr>
      <tr><td>Quantity</td><td>{order.quantity}</td></tr>
      <tr><td>Delivery Address</td><td>{order.address}</td></tr>
      <tr><td>Phone</td><td>{order.phone}</td></tr>
      <tr><td>Payment Method</td><td>{pay}</td></tr>
      <tr><td>Delivery Charge</td><td>{order.delivery_charge} BDT</td></tr>
    </table>
    <div class="total-box">
      <span>Grand Total</span>
      <strong>{order.total_amount} BDT</strong>
    </div>
    <p style="color:#64748b; font-size:13px; text-align:center; line-height:1.6;">
      We will contact you soon to confirm delivery.<br/>
      Thank you for trusting ShopBD!
    </p>
    <div class="footer" style="margin-top:16px;">ShopBD — Bangladesh's trusted online shop</div>
  </div>
</div>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────
# MAIN FUNCTION — views.py থেকে এটাই call করুন
# ─────────────────────────────────────────────────────────────────────

def send_order_notifications(order) -> dict:
    results = {}

    admin_phone = _cfg('ADMIN_PHONE')
    admin_email = _cfg('ADMIN_EMAIL')

    # ── Admin Notifications ──────────────────────────────────────────

    # 1. Admin Email
    if admin_email:
        results['admin_email'] = send_order_email(
            to=admin_email,
            subject=f'New Order #{order.id} - {order.product.name} | ShopBD',
            html_body=_admin_email_html(order),
        )
    else:
        results['admin_email'] = False
        logger.warning('Admin email not configured')

    # 2. Admin SMS
    if admin_phone:
        results['admin_sms'] = send_sms(admin_phone, _admin_sms_text(order))
    else:
        results['admin_sms'] = False

    # 3. Admin WhatsApp
    if admin_phone:
        results['admin_whatsapp'] = send_whatsapp(admin_phone, _admin_sms_text(order))
    else:
        results['admin_whatsapp'] = False

    # 4. Admin Telegram
    results['admin_telegram'] = send_telegram(_admin_telegram_text(order))

    # ── Customer Notifications ───────────────────────────────────────

    # 5. Customer Email
    customer_email = getattr(order.user, 'email', None) if order.user else None
    if customer_email:
        results['customer_email'] = send_order_email(
            to=customer_email,
            subject=f'Order Confirmed #{order.id} - {order.product.name} | ShopBD',
            html_body=_customer_email_html(order),
        )
    else:
        results['customer_email'] = False
        logger.warning(f'Customer email not found for order #{order.id}')

    # 6. Customer Telegram (customer এর chat_id থাকলে)
    customer_telegram_id = _cfg('CUSTOMER_TELEGRAM_CHAT_ID')
    if customer_telegram_id:
        results['customer_telegram'] = send_telegram(
            _customer_telegram_text(order),
            chat_id=customer_telegram_id,
        )
    else:
        results['customer_telegram'] = False

    logger.info(f'Order #{order.id} notifications: {results}')
    return results