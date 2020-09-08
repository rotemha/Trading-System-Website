from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
	url(r'^ws/store_owner/(?P<owner_id>[^/]+)/$', consumers.StoreOwnerConsumer),
]
