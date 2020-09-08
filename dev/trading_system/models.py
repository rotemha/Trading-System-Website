from django.contrib.auth.models import User
from django.db import models

from store.models import Store, Item


# Create your models here.
# Create your models here.


class CartGuest(object):
	def __init__(self, items_id):
		self.items_id = items_id

	def serialize(self):
		return self.__dict__


class Cart(models.Model):
	customer = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
	store = models.ForeignKey(Store, on_delete=models.CASCADE, default=None)
	items = models.ManyToManyField(Item)

	class Meta:
		unique_together = (("customer", "store"),)


class Auction(models.Model):
	item = models.ForeignKey(Item, on_delete=models.CASCADE, default=None)
	customers = models.ManyToManyField(User, through='AuctionParticipant')


class AuctionParticipant(models.Model):
	auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
	customer = models.ForeignKey(User, on_delete=models.CASCADE)
	offer = models.DecimalField(max_digits=6, decimal_places=2)
	address = models.URLField(max_length=250)

	class Meta:
		unique_together = (("auction", "customer"),)


class Notification(models.Model):
	date = models.DateTimeField(auto_now_add=True, blank=True)
	msg = models.CharField(max_length=250)
	users = models.ManyToManyField(User, through='NotificationUser')


class NotificationUser(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
	been_read = models.BooleanField(default=False)

	class Meta:
		unique_together = (("user", "notification"),)


class ObserverUser(models.Model):
	address = models.URLField(max_length=250)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
