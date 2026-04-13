# ShopBD — সম্পূর্ণ Setup Guide
## সব কিছু এক জায়গায়

---

## 📁 আপনার Project Structure

```
ecommerce-frontend/          ← React project
└── src/
    └── App.jsx              ← ✅ এই file replace করুন

myproject/                   ← Django project
├── myproject/
│   ├── settings.py          ← ✅ নিচের Settings section ADD করুন
│   └── urls.py              ← ✅ এই file replace করুন
└── store/
    ├── models.py            ← ✅ এই file replace করুন
    ├── views.py             ← ✅ এই file replace করুন
    └── notifications.py     ← ✅ নতুন file তৈরি করুন
```

---

## ⚡ ধাপ ১ — Install করুন

```bash
pip install sslcommerz-lib requests djangorestframework
```

---

## ⚡ ধাপ ২ — settings.py-র একদম নিচে ADD করুন

```python
import os

# Site URLs
BASE_URL     = 'http://127.0.0.1:8000'    # production-এ আপনার domain
FRONTEND_URL = 'http://localhost:3000'     # production-এ আপনার domain

# Admin contact — আপনি notification পাবেন
ADMIN_PHONE = '01XXXXXXXXX'               # ← আপনার নম্বর
ADMIN_EMAIL = 'admin@shopbd.com'          # ← আপনার email

# Gmail SMTP — Email notification
# Gmail → Google Account → Security → App Passwords → Generate
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = 'yourshop@gmail.com'     # ← আপনার Gmail
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'    # ← 16-digit App Password
DEFAULT_FROM_EMAIL  = 'ShopBD <yourshop@gmail.com>'

# SSL Wireless — SMS notification (Bangladesh)
# পাবেন: https://sms.sslwireless.com
SSL_WIRELESS_API_TOKEN = 'your_token'     # ← এখানে বসান
SSL_WIRELESS_SID       = 'your_sid'       # ← এখানে বসান

# bKash — https://developer.bka.sh
BKASH_USERNAME   = 'your_username'
BKASH_PASSWORD   = 'your_password'
BKASH_APP_KEY    = 'your_app_key'
BKASH_APP_SECRET = 'your_app_secret'

# SSL Commerz — https://manage.sslcommerz.com
SSL_STORE_ID   = 'your_store_id'
SSL_STORE_PASS = 'your_store_password'

# Shurjopay — https://shurjopay.com.bd
SHURJOPAY_USERNAME = 'your_username'
SHURJOPAY_PASSWORD = 'your_password'

# Anthropic AI
ANTHROPIC_API_KEY = 'sk-ant-...'

# Media files
MEDIA_URL  = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## ⚡ ধাপ ৩ — Migration চালান

```bash
cd myproject
python manage.py makemigrations store
python manage.py migrate
python manage.py runserver
```

---

## ✅ কাজ শেষে কী হবে

| কে | কখন | কী পাবেন |
|---|---|---|
| Customer | Order করলে | 📱 SMS + 📧 Email (receipt) |
| Admin (আপনি) | Order আসলে | 📱 SMS + 📧 Email (details) |

### Payment flow:
```
COD order    → সাথে সাথে notify
bKash order  → payment complete হলে notify
SSL Commerz  → payment complete হলে notify
Shurjopay    → payment complete হলে notify
```

---

## 🔑 Gmail App Password কীভাবে পাবেন

১. Gmail খুলুন → ডান দিকে profile picture → **Manage Google Account**
২. **Security** tab
৩. **2-Step Verification** চালু করুন (যদি না থাকে)
৪. Search করুন **"App Passwords"**
৫. App: **Mail**, Device: **Windows Computer** → **Generate**
৬. ১৬ digit password পাবেন → `EMAIL_HOST_PASSWORD` তে বসান

---

## ❓ সাধারণ সমস্যা

**`ModuleNotFoundError: sslcommerz_lib`**
```bash
pip install sslcommerz-lib
```

**`No module named 'rest_framework'`**
```bash
pip install djangorestframework
# settings.py INSTALLED_APPS-এ যোগ করুন:
# 'rest_framework',
```

**`relation "store_order" does not exist`**
```bash
python manage.py makemigrations store
python manage.py migrate
```

**`SMTPAuthenticationError`**
→ Gmail App Password ঠিকমতো বসানো হয়নি। App Password হবে ১৬ digit, space ছাড়া।

**`Given token not valid`**
→ Logout করে আবার Login করুন।