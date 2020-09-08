from django import forms
from django.utils.safestring import mark_safe

from .models import Cart


class SomeForm(forms.Form):
	CHOICES = (('a', 'add item'),
	           ('b', 'delete item'),
	           ('c', 'update item'),
	           ('d', 'add manager'),)
	picked = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple())


class SearchForm(forms.Form):
	search = forms.CharField()


class QForm(forms.Form):
	def __init__(self, user, list_for_guest, *args, **kwargs, ):
		# quantity = kwargs.pop('quantity')
		super(QForm, self).__init__(*args, **kwargs)

		if user.is_anonymous:
			list_ = list_for_guest
			for x in list_:
				self.fields['quantity' + str(x.id)] = forms.IntegerField(required=False, label='quantity ')
		else:
			list_ = []
			carts = Cart.objects.filter(customer=user)
			for cart in carts:
				list_ += list(cart.items.all())
			for x in list_:
				self.fields['quantity' + str(x.id)] = forms.IntegerField(required=False, label='quantity: ')


class CartForm(forms.Form):

	def __init__(self, user, list_for_guest, *args, **kwargs):
		super(CartForm, self).__init__(*args, **kwargs)
		print('\n an ', user.is_anonymous)
		if user.is_anonymous:

			list_ = list_for_guest
			self.fields['items'] = forms.MultipleChoiceField(
				choices=[(o.id,
				          mark_safe(' <a id="buy_href" href=' + '/' + 'store/view_item/' + str(
					          o.id) + '>' + o.name + '  :  ' + o.description + '</a>' +
				                    '<a href= "/delete_item_from_cart/' + str(o.id) + '"> delete </a>    '
				                    # +
				                    # ' <form action="/delete_item_from_cart/' + str(o.id) + '" method="post">  '
				                    #                                                        '{% csrf_token %} {{pk}}	<input type="submit" value="Remove"> </form>'
				                    )) for o in
				         list_]
				, widget=forms.CheckboxSelectMultiple(),

			)


		else:
			carts = Cart.objects.filter(customer=user)
			list_ = []
			for cart in carts:
				list_ += list(cart.items.all())
			self.fields['items'] = forms.MultipleChoiceField(
				choices=[(o.id,
				          mark_safe(' <a id="buy_href" href=' + '/' + 'store/view_item/' + str(
					          o.id) + '>' + o.name + '  :  ' + o.description + '</a>' +
				                    '<a href= "/delete_item_from_cart/' + str(o.id) + '"> delete </a>    '
				                    # +
				                    # ' <form action="/delete_item_from_cart/' +  str(o.id) + ' " method="post"> '
				                    #                                                         ' {% csrf_token %} {{pk}}	<input type="submit" value="Remove"> </form>'
				                    )) for o in
				         list_]
				, widget=forms.CheckboxSelectMultiple(),

			)


class BidForm(forms.Form):
	offer = forms.DecimalField(max_digits=6, decimal_places=2)


class AddSuperUser(forms.Form):
	name = forms.CharField()
	password = forms.CharField()
