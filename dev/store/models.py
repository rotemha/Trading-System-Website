from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

CategoryChoice = (
	("1", "ALL"),
	("2", "HOME"),
	("3", "WORK"),
)


# class MaxMinCondition(models.Model):
# 	max_amount = models.PositiveIntegerField(default=2147483647)
# 	min_amount = models.PositiveIntegerField(default=0)


# class Discount(models.Model):
# 	start_date = models.DateField(auto_now_add=True)
# 	end_date = models.DateField(help_text='format: mm/dd/yyyy')
# 	percentage = models.PositiveSmallIntegerField()
# 	conditions = models.ManyToManyField(MaxMinCondition)


class Item(models.Model):
	price = models.DecimalField(max_digits=6, decimal_places=2, default=0,
	                            validators=[MinValueValidator(Decimal('0.01'))])
	name = models.CharField(max_length=30, default=None)
	description = models.CharField(max_length=64, default=None)
	category = models.CharField(max_length=30, choices=CategoryChoice, default=1)
	quantity = models.PositiveIntegerField(default=1)

	# discounts = models.ManyToManyField(Discount)

	def get_absolute_url(self):
		return reverse('item-detail', kwargs={'id': self.pk})

	def __str__(self):
		return "Name: " + self.name + ", Category: " + self.get_category_display() + ", Description: " + self.description + ", Price: " + str(
			self.price) + ", Quantity: " + str(self.quantity)


class Store(models.Model):
	name = models.CharField(max_length=30)
	owners = models.ManyToManyField(User)
	managers = models.ManyToManyField(User, related_name="store_managers")
	partners = models.ManyToManyField(User, related_name="store_partners")
	items = models.ManyToManyField(Item)
	description = models.CharField(max_length=64)

	# discounts = models.ManyToManyField(Discount)

	# max_quantity = models.PositiveIntegerField(null=True, blank=True)
	# max_op = models.CharField(max_length=3, null=True, blank=True)
	# min_quantity = models.PositiveIntegerField(null=True, blank=True)
	# min_op = models.CharField(max_length=3, null=True, blank=True)
	# registered_only = models.BooleanField(default=False)
	# registered_op = models.CharField(max_length=3, null=True, blank=True)

	class Meta:
		permissions = (
			('ADD_ITEM', 'add item'),  # V
			('REMOVE_ITEM', 'delete item'),  # V
			('EDIT_ITEM', 'update item'),  # V
			('ADD_MANAGER', 'add manager'),  # V
			('REMOVE_STORE', 'delete store'),  # V
			('ADD_DISCOUNT', 'add discount'),  # V
			('ADD_RULE', 'add rule')  # V
		)


class BaseRule(models.Model):
	MAX_QUANTITY = 'MXQ'
	MIN_QUANTITY = 'MNQ'
	REGISTERED_ONLY = 'RGO'
	FORBIDDEN_COUNTRIES = 'FBC'
	RULE_TYPES = (
		(MAX_QUANTITY, 'max_quantity'),
		(MIN_QUANTITY, 'min_quantity'),
		(REGISTERED_ONLY, 'registered_only'),
		(FORBIDDEN_COUNTRIES, 'forbidden_countries')
	)
	store = models.ForeignKey(Store, on_delete=models.CASCADE)
	type = models.CharField(max_length=3, choices=RULE_TYPES)
	parameter = models.CharField(max_length=120)


class ComplexStoreRule(models.Model):
	LOGICS = (('OR', 'or'),
	          ('AND', 'and'),
	          ('XOR', 'xor'))
	# if rule begins with # it means it is basic, otherwise begins with * - complex
	left = models.CharField(max_length=4)
	right = models.CharField(max_length=4)
	operator = models.CharField(max_length=3, choices=LOGICS)
	store = models.ForeignKey(Store, on_delete=models.CASCADE)


class BaseItemRule(models.Model):
	MAX_QUANTITY = 'MXQ'
	MIN_QUANTITY = 'MNQ'
	RULE_TYPES = (
		(MAX_QUANTITY, 'max_quantity'),
		(MIN_QUANTITY, 'min_quantity'),
	)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	type = models.CharField(max_length=3, choices=RULE_TYPES)
	parameter = models.CharField(max_length=120)


class ComplexItemRule(models.Model):
	LOGICS = (('OR', 'or'),
	          ('AND', 'and'),
	          ('XOR', 'xor'))
	left = models.CharField(max_length=4)
	right = models.CharField(max_length=4)
	operator = models.CharField(max_length=3, choices=LOGICS)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)


class Discount(models.Model):
	MAX_QUANTITY = 'MXQ'
	MIN_QUANTITY = 'MNQ'
	RULE_TYPES = (
		(MAX_QUANTITY, 'max_quantity'),
		(MIN_QUANTITY, 'min_quantity'),
	)
	store = models.ForeignKey(Store, on_delete=models.CASCADE)
	item = models.ForeignKey(Item, null=True, on_delete=models.CASCADE)
	type = models.CharField(max_length=3, choices=RULE_TYPES)
	amount = models.IntegerField(default=0, null=True)
	end_date = models.DateField(help_text='format: mm/dd/yyyy')
	percentage = models.PositiveSmallIntegerField()


class ComplexDiscount(models.Model):
	LOGICS = (('OR', 'or'),
	          ('AND', 'and'),
	          ('XOR', 'xor'))
	left = models.CharField(max_length=4)
	right = models.CharField(max_length=4)
	operator = models.CharField(max_length=3, choices=LOGICS)
	store = models.ForeignKey(Store, on_delete=models.CASCADE)


class ManagersWhoWait(models.Model):
	user_who_wait = models.ForeignKey(User, on_delete=None)
	is_approve = models.BooleanField(default=False)


class WaitToAgreement(models.Model):
	user_to_wait = models.ForeignKey(User, on_delete=None)
	store = models.ForeignKey(Store, on_delete=None)
	managers_who_wait = models.ManyToManyField(ManagersWhoWait, related_name="store_managers_to_wait")
