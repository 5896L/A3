from django.urls import re_path
from dm import consumers

websocket_urlpatterns = [
    # 只要和dm_django/xxx匹配上，就走ChatConsumer这个函数，原理和视图函数差不多
    re_path(r'room/(?P<group>\w+)/$', consumers.ChatConsumer.as_asgi()),
]