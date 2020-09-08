import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User

from trading_system.models import Notification


class StoreOwnerConsumer(WebsocketConsumer):
	def connect(self):
		self.owner_id = self.scope['url_route']['kwargs']['owner_id']
		self.owner_group_name = 'owner_%s' % self.owner_id

		# Join room group
		async_to_sync(self.channel_layer.group_add)(
			self.owner_group_name,
			self.channel_name
		)

		self.accept()

	def disconnect(self, close_code):
		# Leave room group
		async_to_sync(self.channel_layer.group_discard)(
			self.owner_group_name,
			self.channel_name
		)

	# Receive message from WebSocket
	def receive(self, text_data=None, bytes_data=None):
		text_data_json = json.loads(text_data)
		ntfcs_ids = extract_ntfcs_ids(text_data_json['message'])
		for ntfc_id in ntfcs_ids:
			ntfc = Notification.objects.get(pk=ntfc_id)
			ntfc.users.add(User.objects.get(pk=self.owner_id))
		# Send message to WebSocket
		async_to_sync(self.channel_layer.group_send)(
			self.owner_group_name,
			{
				'type': 'chat_message',
				'message': '{}'
			}
		)

	# Receive message from room group
	def chat_message(self, event):
		self.send(text_data=json.dumps({
			'message': '{}'
		}))


def extract_ntfcs_ids(param):
	return param
