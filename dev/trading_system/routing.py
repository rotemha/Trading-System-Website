from django.conf.urls import url

from . import consumers

AUCTION_PARTICIPANT_URL = 'auction_participant'

websocket_urlpatterns = [
	# url(r'^ws/auction_participant/(?P<participant_id>[^/]+)/(?P<item_id>[^/]+)/$', consumers.AuctionParticipantConsumer),
	url(r'^ws/auction_participant/(?P<item_id>[^/]+)/(?P<participant_id>[^/]+)/$', consumers.ParticipantConsumer),
]
