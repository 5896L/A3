"""
ASGI config for dm_django project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from . import routings
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dm_django.settings')

# application = get_asgi_application()

# 修改成既支持http协议，又支持websocket协议
application = ProtocolTypeRouter({
    # 告诉 Channels 当 Channels 服务器接收到 HTTP 请求时要运行什么代码
    "http": get_asgi_application(),   # 自动去找urls.py
    "websocket": URLRouter(routings.websocket_urlpatterns),
})
