from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from .models import Item, Store  # , Discount, MaxMinCondition


class StoreForm(forms.ModelForm):
	class Meta:
		model = Store
		# fields = ['name', 'owners', 'description', 'discounts']

		fields = ['name', 'description']


# widgets = {
# 	'owners': forms.CheckboxSelectMultiple,
# 	# 'items': forms.CheckboxSelectMultiple,
# }


# 		def __init__(self, user, list_for_guest, *args, **kwargs):
# 			super(StoreForm, self).__init__(*args, **kwargs)
# 			self.fields['items'] = forms.MultipleChoiceField(
# 				choices=[(o.id,
# 				          mark_safe(' <a id="buy_href" href=' + '/' + 'store/view_item/' + str(
# 					          o.id) + '>' + o.name + '  :  ' + o.description + '</a>')) for o in
# 				         ]
#

class DeleteOwners(forms.Form):
	def __init__(self, owners, store_id, *args, **kwargs):
		super(DeleteOwners, self).__init__(*args, **kwargs)
		list_ = owners
		self.fields['owners_to_delete'] = forms.MultipleChoiceField(
			choices=[(o['id'],
			          mark_safe('owner name : ' + str(o[
				                                          'username']) + '  <a id="delete_owners" href=' +
			                    '/' + 'store/delete_owner/' + str(
				          o['id']) + '/' + str(store_id) + '>' + 'remove this owner' + '</a>')) for o in
			         list_]
			, widget=forms.CheckboxSelectMultiple(),

		)


class ApproveForm(forms.Form):
	def __init__(self, wait_to_approve_list, *args, **kwargs):
		super(ApproveForm, self).__init__(*args, **kwargs)
		list_ = wait_to_approve_list
		self.fields['approve_list'] = forms.MultipleChoiceField(
			choices=[(key,
			          mark_safe(
				          ' <a id="approve_href" href=' + '/' + 'agreement_by_partner/' + str(value) + '/' + str(key
				                                                                                                 ) + '>' + ' approve: ' + str(
					          User.objects.get(id=key)) + ' </a>')) for key, value in list_.items()
			         ]
			, widget=forms.CheckboxSelectMultiple(),
			label='',

		)


class UpdateItems(forms.Form):
	def __init__(self, items, *args, **kwargs):
		super(UpdateItems, self).__init__(*args, **kwargs)
		list_ = items
		self.fields['items'] = forms.MultipleChoiceField(
			choices=[(o['id'],
			          mark_safe(' <a id="update_href" href=' + '/' + 'store/update_item/' + str(
				          o['id']) + '>' + o['name'] + '  :  ' + o['description'] + '</a>')) for o in
			         list_]
			, widget=forms.CheckboxSelectMultiple(),
			label='',

		)


# class AddRuleToStore(forms.Form):
# 	CHOICES = (('MAX_QUANTITY', 'Max quantity - restrict max amount of items per order'),
# 	           ('MIN_QUANTITY', 'Min quantity - restrict min amount of items per order'),
# 	           ('FORBIDDEN_COUNTRY', 'Forbidden Country - restrict orderes for specific country'),
# 	           ('REGISTERED_ONLY', 'Registered only - only members will be able to buy from your store'),)
# 	rules = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, required=False)
# 	#parameter_number = forms.IntegerField(min_value=0, required=False)
# 	parameter = forms.CharField(max_length=100, required=False)


class AddRuleToStore_base(forms.Form):
	CHOICES = (('MAX_QUANTITY', 'Max quantity - restrict max amount of items per order'),
	           ('MIN_QUANTITY', 'Min quantity - restrict min amount of items per order'),
	           ('FORBIDDEN_COUNTRY', 'Forbidden Country - restrict orderes for specific country'),
	           ('REGISTERED_ONLY', 'Registered only - only members will be able to buy from your store'),)
	rule = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, required=False)
	# parameter_number = forms.IntegerField(min_value=0, required=False)
	parameter = forms.CharField(max_length=100, required=False)


class AddRuleToStore_withop(forms.Form):
	CHOICES = (('MAX_QUANTITY', 'Max quantity - restrict max amount of items per order'),
	           ('MIN_QUANTITY', 'Min quantity - restrict min amount of items per order'),
	           ('FORBIDDEN_COUNTRY', 'Forbidden Country - restrict orderes for specific country'),
	           ('REGISTERED_ONLY', 'Registered only - only members will be able to buy from your store'),)
	LOGICS = (('OR', 'or'),
	          ('AND', 'and'),
	          ('XOR', 'xor'))
	operator = forms.ChoiceField(choices=LOGICS, widget=forms.RadioSelect)
	rule = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, required=False)
	# parameter_number = forms.IntegerField(min_value=0, required=False)
	parameter = forms.CharField(max_length=100, required=False)


class AddRuleToStore_two(forms.Form):
	CHOICES = (('MAX_QUANTITY', 'Max quantity - restrict max amount of items per order'),
	           ('MIN_QUANTITY', 'Min quantity - restrict min amount of items per order'),
	           ('FORBIDDEN_COUNTRY', 'Forbidden Country - restrict orderes for specific country'),
	           ('REGISTERED_ONLY', 'Registered only - only members will be able to buy from your store'),)
	LOGICS = (('OR', 'or'),
	          ('AND', 'and'),
	          ('XOR', 'xor'))
	operator2 = forms.ChoiceField(choices=LOGICS, widget=forms.RadioSelect)
	rule1 = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, required=False)
	parameter1 = forms.CharField(max_length=100, required=False)
	operator1 = forms.ChoiceField(choices=LOGICS, widget=forms.RadioSelect)
	rule2 = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, required=False)
	# parameter_number = forms.IntegerField(min_value=0, required=False)
	parameter2 = forms.CharField(max_length=100, required=False)


class AddRuleToItem(forms.Form):
	CHOICES = (('MAX_QUANTITY', 'Max quantity - restrict max amount of items per order'),
	           ('MIN_QUANTITY', 'Min quantity - restrict min amount of items per order'),)
	rule = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, required=False)
	# parameter_number = forms.IntegerField(min_value=0, required=False)
	parameter = forms.IntegerField(min_value=1)


class AddRuleToItem_withop(forms.Form):
	CHOICES = (('MAX_QUANTITY', 'Max quantity - restrict max amount of items per order'),
	           ('MIN_QUANTITY', 'Min quantity - restrict min amount of items per order'),)
	LOGICS = (('OR', 'or'),
	          ('AND', 'and'),
	          ('XOR', 'xor'))
	operator = forms.ChoiceField(choices=LOGICS, widget=forms.RadioSelect)
	rule = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, required=False)
	parameter = forms.IntegerField(min_value=0)


class AddDiscountForm(forms.Form):
	def __init__(self, store_id, *args, **kwargs):
		super(AddDiscountForm, self).__init__(*args, **kwargs)
		self.store_id = store_id
		CHOICES = (('MAX_QUANTITY', 'Max quantity - restrict max amount of items per order'),
		           ('MIN_QUANTITY', 'Min quantity - restrict min amount of items per order'),)
		self.fields['percentage'] = forms.IntegerField(min_value=0, max_value=100)
		self.fields['end_date'] = forms.DateField(help_text='format: mm/dd/yyyy')
		self.fields['type'] = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, required=False)
		self.fields['amount'] = forms.IntegerField(min_value=0, required=False)
		self.fields['item'] = forms.ModelChoiceField(queryset=Item.objects.filter(store=self.store_id), required=False)


class AddComplexDiscountForm(forms.Form):
	def __init__(self, store_id, *args, **kwargs):
		super(AddComplexDiscountForm, self).__init__(*args, **kwargs)
		self.store_id = store_id
		CHOICES = (('MAX_QUANTITY', 'Max quantity - restrict max amount of items per order'),
		           ('MIN_QUANTITY', 'Min quantity - restrict min amount of items per order'),)
		LOGICS = (('OR', 'or'),
		          ('AND', 'and'),
		          ('XOR', 'xor'))
		self.fields['operator'] = forms.ChoiceField(choices=LOGICS, widget=forms.RadioSelect)
		self.fields['percentage'] = forms.IntegerField(min_value=0, max_value=100)
		self.fields['end_date'] = forms.DateField(help_text='format: mm/dd/yyyy')
		self.fields['type'] = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, required=False)
		self.fields['amount'] = forms.IntegerField(min_value=0, required=False)
		self.fields['item'] = forms.ModelChoiceField(queryset=Item.objects.filter(store=self.store_id), required=False)


class AddRuleToItem_two(forms.Form):
	CHOICES = (('MAX_QUANTITY', 'Max quantity - restrict max amount of items per order'),
	           ('MIN_QUANTITY', 'Min quantity - restrict min amount of items per order'),)
	LOGICS = (('OR', 'or'),
	          ('AND', 'and'),
	          ('XOR', 'xor'))
	operator2 = forms.ChoiceField(choices=LOGICS, widget=forms.RadioSelect)
	rule1 = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, required=False)
	parameter1 = forms.CharField(max_length=100, required=False)
	operator1 = forms.ChoiceField(choices=LOGICS, widget=forms.RadioSelect)
	rule2 = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, required=False)
	parameter2 = forms.CharField(max_length=100, required=False)


# class MaxMinConditionForm(forms.ModelForm):
#    cond_min_max = forms.BooleanField(required=False)
#    class Meta:
#       model = MaxMinCondition
#       fields = ['min_amount', 'max_amount']


class AddManagerForm(forms.Form):
	user_name = forms.CharField()
	is_owner = forms.BooleanField(required=False)
	is_partner = forms.BooleanField(required=False)
	CHOICES = (('ADD_ITEM', 'add item'),
	           ('REMOVE_ITEM', 'delete item'),
	           ('EDIT_ITEM', 'update item'),
	           ('ADD_MANAGER', 'add manager'),
	           ('REMOVE_STORE', 'delete store'),
	           ('ADD_DISCOUNT', 'add discount'),
	           ('ADD_RULE', 'add rule'))

	permissions = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple())


class OpenStoreForm(forms.Form):
	name = forms.CharField()
	description = forms.CharField(max_length=128)


class ItemForm(forms.ModelForm):
	class Meta:
		model = Item
		fields = ['name', 'description', 'category', 'price', 'quantity']


class BuyForm(forms.Form):
	amount = forms.IntegerField()


class PayForm(forms.Form):
	holder = forms.CharField(max_length=50, required=True)
	id = forms.IntegerField()
	card_number = forms.IntegerField(required=True)
	month = forms.IntegerField(required=True)
	year = forms.IntegerField(required=True)
	cvc = forms.CharField(required=True, label='CVV / CVC',
	                      widget=forms.TextInput(attrs={'size': '3',
	                                                    'maxlength': '3',
	                                                    'placeholder': ''}))


class ShippingForm(forms.Form):
	name = forms.CharField(label='Customer', max_length=25, required=True)
	address = forms.CharField(label='Street', max_length=30)
	city = forms.CharField(label='City', max_length=25)
	country = forms.CharField(max_length=25)
	zip = forms.IntegerField(label='Zip Code')
