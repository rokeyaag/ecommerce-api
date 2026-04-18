import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from store.models import Order
from store.notifications import send_order_notifications
order = Order.objects.last()
print(send_order_notifications(order))