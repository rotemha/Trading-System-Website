import json
from typing import Any, List, Union

import django
from django.contrib import messages
# from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, QuerySet
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
# from external_systems.spellChecker import checker
from django.views.generic import DetailView
from django.views.generic.list import ListView

from dev.settings import PROJ_IP, PROJ_PORT
from store.forms import ShippingForm, PayForm
from store.models import Item, Store
from store.views import loger, logev
from trading_system import service
from trading_system.forms import SearchForm, SomeForm, CartForm
# Create your views here.
from trading_system.models import Cart, Auction, CartGuest
from trading_system.observer import AuctionSubject
from trading_system.service import DBFailedExceptionServiceToViews
from .models import AuctionParticipant
from .routing import AUCTION_PARTICIPANT_URL

django.setup()

from django.contrib.auth.forms import UserCreationForm


def def_super_user(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			u = form.save()
			u.is_superuser = True
			u.is_staff = True
			u.save()
			messages.success(request, 'add super-user ' + str(u.username))
			logev.info('add superuser successfully')
			return render(request, 'homepage_guest.html', {'text': SearchForm()})

		else:
			return redirect('/super_user')

	else:
		return render(request, 'trading_system/add_super_user.html', {'form': UserCreationForm()})


# ---------------------new
from store.models import WaitToAgreement
from django.contrib.auth.models import User


def approve_user(pk_manager, pk_user):
	try:
		manager_obj = User.objects.get(id=pk_manager)
		user_obj = User.objects.get(id=pk_user)
		wait_to_agg_obj = WaitToAgreement.objects.get(user_to_wait=user_obj)
		managersWhoWait_obj = wait_to_agg_obj.managers_who_wait.get(user_who_wait=manager_obj)
		managersWhoWait_obj.is_approve = True
		managersWhoWait_obj.save()
		return True
	except:
		return False


# def check_if_this_partner_need_to_approve(manager):
# 	return len(WaitToAgreement.objects.filter(managers_who_wait__user_who_wait__in=[manager])) == 1


def get_all_wait_agreement_t_need_to_approve(manager):
	return service.get_all_wait_agreement_t_need_to_approve(manager.id)


# def check_if_user_is_in_waiting_list(user_):
# 	return len(WaitToAgreement.objects.filter(user_to_wait=user_)) == 1
#

def check_if_user_is_approved(user_, store):
	# wait_to_agg_obj = WaitToAgreement.objects.get(user_to_wait=user_, store=store)
	# managers_list = wait_to_agg_obj.managers_who_wait.all()
	# for obj in managers_list:
	# 	if not obj.is_approve:
	# 		return False
	# return True
	return service.check_if_user_is_approved(user_.id, store.id)


def agreement_by_partner(request, store_pk, user_pk):
	partner = User.objects.get(id=request.user.id)

	if (service.agreement_by_partner(partner.id, store_pk, user_pk)):
		messages.success(request, ' you approve! ')
	else:
		messages.warning(request, ' try again ')
	return redirect('/login_redirect')


def approved_user_to_store_manager(user_pk, store_pk):
	user = User.objects.get(id=user_pk)
	store = Store.objects.get(id=store_pk)
	if (service.approved_user_to_store_manager(user.username, store_pk)):
		wait_to_agg_obj = WaitToAgreement.objects.get(user_to_wait=user, store=store)
		wait_to_agg_obj.delete()
		return True
	return False


def login_redirect(request: Any) -> Union[HttpResponseRedirect, HttpResponse]:
	if request.user.is_authenticated:
		if "store_owners" in request.user.groups.values_list('name',
		                                                     flat=True) or "store_managers" in request.user.groups.values_list(
			'name', flat=True):

			return redirect('/store/home_page_owner/',
			                {'text': SearchForm(), 'user_name': request.user.username, 'owner_id': request.user.pk, })
		else:

			return render(request, 'homepage_member.html', {'text': SearchForm(), 'user_name': request.user.username})

	# return render(request, 'homepage_member.html',
	#               {'text': text, 'user_name': user_name})

	return render(request, 'homepage_guest.html', {'text': SearchForm()})


def item(request: Any, id1: int) -> HttpResponse:
	return render(request, 'trading_system/item_page.html', {
		'item': Item.objects.get(name=id1)
	})


class CartsListView(ListView):
	model = Cart
	template_name = 'trading_system/user_carts.html'

	def get_queryset(self) -> List[Cart]:
		return Cart.objects.filter(customer_id=self.request.user.pk)


# ELHANANA - note that search returns the filtered items list
def search(request: Any) -> QuerySet:
	text = SearchForm(request.GET)
	if text.is_valid():
		# spell checker
		# correct_word = checker.Spellchecker(text)
		# items = Item.objects.filter(name=correct_word)
		return Item.objects.filter(Q(name__contains=text.cleaned_data.get('search')) | Q(
			description__contains=text.cleaned_data.get('search')) | Q(
			category__contains=text.cleaned_data.get('search')))


########## Need to check with elhanan
class CartDetail(DetailView):
	model = Cart

	# def get_context_data(self, **kwargs):
	# 	print('!!!!!!!!!!!!!!!!!!!!!!!!!\n')
	# 	cart = Cart.objects.get(pk=kwargs['object'].pk)
	# 	item_ids = list(map(lambda i: i.pk, cart.items.all()))
	# 	context = super().get_context_data(**kwargs)  # get the default context data
	# 	context['items'] = list(map(lambda i_pk: Item.objects.get(pk=i_pk), item_ids))

	def get_context_data(self, **kwargs):
		print('???????????????????????????\n')
		cart = Cart.objects.get(pk=kwargs['object'].pk)
		item_ids = list(map(lambda i: i.pk, cart.items.all()))
		items = list(map(lambda i_pk: Item.objects.get(pk=i_pk), item_ids))
		context = super(CartDetail, self).get_context_data(**kwargs)  # get the default context data
		context['items'] = items

		context['store_name'] = Store.objects.get(pk=cart.store_id).name
		return context


########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################

def index(request: Any) -> HttpResponse:
	try:
		if service.len_of_super() == 0:
			return redirect('/super_user')
		return render(request, 'homepage_guest.html', {'text': SearchForm()})
	except DBFailedExceptionServiceToViews as e:
		messages.warning(request, e.msg)
		loger.warning(e.msg)
		return redirect('/login_redirect')


def show_cart(request: Any) -> HttpResponse:
	if request.user.is_authenticated:
		if "store_owners" in request.user.groups.values_list('name',
		                                                     flat=True) or "store_managers" in request.user.groups.values_list(
			'name', flat=True):
			base_template_name = 'store/homepage_store_owner.html'
		else:
			base_template_name = 'homepage_member.html'
		return render(request, 'cart.html', {
			'user_name': request.user.username,
			'text': SearchForm(),
			'base_template_name': base_template_name
		})


# else:
# 	base_template_name = 'homepage_guest.html'


cart_index = 0


class SearchListView(ListView):
	model = Item
	template_name = 'trading_system/search_results.html'

	def get_context_data(self, **kwargs):
		try:
			text = SearchForm()
			# context = super(SearchListView, self).get_context_data(**kwargs)  # get the default context data
			text = SearchForm(self.request.GET)
			if text.is_valid():
				items = service.search(text.cleaned_data.get('search'))
			context = {}
			context['text'] = text
			context['object_list'] = items

			return context
		except DBFailedExceptionServiceToViews as e:
			messages.warning(self.request, e.msg)
			loger.warning(e.msg)
			return redirect('/login_redirect')


def register(request: Any) -> HttpResponse:
	return render(request, 'trading_system/register.html')


def home_button(request: Any) -> HttpResponseRedirect:
	return redirect('/login_redirect')


def approve_event(request: Any) -> HttpResponse:
	if request.method == 'POST':
		form = SomeForm(request.POST)
		if form.is_valid():
			# ('\n', form.cleaned_data.get('picked'))
			render(request, 'check_box_items.html', {'form': form})
		render(request, 'check_box_items.html', {'form': form})
	# do something with your results
	else:
		form = SomeForm
	return render(request, 'check_box_items.html', {'form': form})


from decimal import Decimal

from .forms import QForm


def get_queryset(self):
	return Cart.objects.filter(customer_id=self.request.user.pk)


class AuctionsListView(ListView):
	model = Auction
	template_name = 'trading_system/user_auctions.html'

	def get_queryset(self):
		return Auction.objects.filter(
			auctionparticipant__customer=self.request.user.pk
		)


def join_auction(request, item_pk):
	try:
		auction = Auction.objects.get(item_id=item_pk)
	except ObjectDoesNotExist:
		auction = Auction.objects.create(item_id=item_pk)
	ap = AuctionParticipant(auction_id=auction.pk, customer_id=request.user.pk, offer=3,
	                        address="ws://{}:{}/ws/{}/{}/{}/".format(PROJ_IP, PROJ_PORT, AUCTION_PARTICIPANT_URL,
	                                                                 item_pk, request.user.pk))
	context = {'action_desc': ''}
	try:
		ap.save()
		context['action_desc'] = 'You joined the auction'
	except django.db.IntegrityError as e:
		context['action_desc'] = 'You have already joined this auction'
	auction_subject = AuctionSubject(auction_id=auction.pk)
	auction_subject._notify()
	return render(request, 'trading_system/action_happend_succefully.html', context)


def view_auction(request, auction_pk):
	auction = Auction.objects.get(id=auction_pk)
	context = {
		'participant_id_json': mark_safe(json.dumps(request.user.pk)),
		'participant_id': request.user.pk,
		'item_id': auction.item_id,
		'url': AUCTION_PARTICIPANT_URL
	}
	return render(request, 'trading_system/auction_feed.html', context)


# def get_item_store(item_pk):
# 	stores = list(filter(lambda s: item_pk in map(lambda i: i.pk, s.items.all()), Store.objects.all()))
# 	# Might cause bug. Need to apply the item-in-one-store condition
# 	return stores[0]


def add_item_to_cart(request, item_pk):
	try:
		if not (request.user.is_authenticated):
			if 'cart' in request.session:
				items_in = request.session['cart']['items_id']

				cart_g = request.session['cart']
				if (item_pk not in items_in):
					cart_g['items_id'].append(item_pk)
			else:
				cart_g = CartGuest([item_pk]).serialize()

			request.session['cart'] = cart_g
			messages.success(request, 'add to cart successfully')
			logev.info('add item to cart successfully')
			return redirect('/login_redirect')
		else:
			ans = service.add_item_to_cart(request.user.pk, item_pk)
			if ans is True:
				messages.success(request, 'add to cart successfully')
				logev.info('add item to cart successfully')
				return redirect('/login_redirect')
			else:
				messages.warning(request, 'can`t add to cart ')
				loger.warning('add item to cart failed')
				return redirect('/login_redirect')
	except DBFailedExceptionServiceToViews as e:
		messages.warning(request, e.msg)
		loger.warning(e.msg)
		return redirect('/login_redirect')


def make_guest_cart(request):
	try:
		if request.user.is_authenticated:
			return []
		else:
			items_ = []
			# for id1 in request.session['cart']['items_id']:
			# 	items_ += list([service.get_item(id1)])
			# return items_
			if 'cart' in request.session:
				cartG = request.session['cart']
				id_list = cartG['items_id']
				for id in id_list:
					items_ += list([service.get_item(id)])

			return items_
	except DBFailedExceptionServiceToViews as e:
		messages.warning(request, e.msg)
		loger.warning(e.msg)
		return redirect('/login_redirect')


def delete_item_from_cart(request, item_pk):
	if request.user.is_authenticated:
		get_cart(get_item_store(item_pk), request.user.pk).items.remove(item_pk)
		messages.success(request, 'remove to cart successfully')
		logev.info('remove item from cart successfully')
		return redirect('/login_redirect')
	else:

		cart_g = request.session['cart']
		cart_g['items_id'].remove(item_pk)

		request.session['cart'] = cart_g

		messages.success(request, 'remove to cart successfully')
		logev.info('remove item from cart successfully')
		return redirect('/login_redirect')


# TODO move to domain
def get_item_store(item_pk):
	# stores = list(filter(lambda s: item_pk in map(lambda i: i.pk, s.items.all()), Store.objects.all()))
	# Might cause bug. Need to apply the item-in-one-store condition
	return list(filter(lambda s: item_pk in map(lambda i: i.pk, s.items.all()), Store.objects.all()))[0]


# TODO move to domain
def get_cart(store_pk, user_pk):
	carts = Cart.objects.all().filter(customer_id=user_pk)
	print(carts)
	carts = carts.filter(store_id=store_pk.id)
	print(carts)
	if len(carts) == 0:
		return None
	else:
		return carts[0]


def make_cart_list(request: Any) -> Union[HttpResponseRedirect, HttpResponse]:
	try:
		# if not (request.user.is_authenticated):
		# 	return makeGuestCart(request)
		items_bought = []
		if request.method == 'POST':
			form = CartForm(request.user, make_guest_cart(request), request.POST)
			shipping_form = ShippingForm(request.POST)
			supply_form = PayForm(request.POST)

			if shipping_form.is_valid() and supply_form.is_valid():
				# shipping
				country = shipping_form.cleaned_data.get('country')
				city = shipping_form.cleaned_data.get('city')
				zip1 = shipping_form.cleaned_data.get('zip')
				address = shipping_form.cleaned_data.get('address')
				name = shipping_form.cleaned_data.get('name')

				shipping_details = {'country': country, 'city': city, 'zip': zip1, 'address': address, 'name': name}

				# card

				card_number = supply_form.cleaned_data.get('card_number')
				month = supply_form.cleaned_data.get('month')
				year = supply_form.cleaned_data.get('year')
				holder = supply_form.cleaned_data.get('holder')
				cvc = supply_form.cleaned_data.get('cvc')
				id1 = supply_form.cleaned_data.get('id')

				card_details = {'card_number': card_number, 'month': month, 'year': year, 'holder': holder, 'cvc': cvc,
				                'id': id1}
			else:
				err = '' + str(shipping_form.errors) + str(supply_form.errors)
				messages.warning(request, 'error in :  ' + err)
				loger.warning('buy from cart failed')
				return redirect('/login_redirect')

			if form.is_valid():
				list_of_items = []
				total_amount=0
				items = form.cleaned_data.get('items')
				for item_id in items:
					quantity_to_buy = 1
					try:
						quantity_to_buy = request.POST.get('quantity' + item_id)
						total_amount += int(quantity_to_buy)
					# print('q----------------id:----' + str(item.id) + '------------' + quantity_to_buy)
					except:
						messages.warning(request, 'problem with quantity ')
						loger.warning('buy from cart failed')

					list_of_items.append({'item_id': int(item_id), 'amount': int(quantity_to_buy)})
				res, res_before = service.apply_discounts_for_cart(list_of_items)
				for item_id in form.cleaned_data.get('items'):
					amount_in_db = service.get_quantity(item_id)
					if amount_in_db > 0:
						item1 = Item.objects.get(id=item_id)
						# quantity_to_buy = 1
						# try:
						# 	quantity_to_buy = request.POST.get('quantity' + str(item1.id))
						# # print('q----------------id:----' + str(item.id) + '------------' + quantity_to_buy)
						# except:
						# 	messages.warning(request, 'problem with quantity ')
						# 	loger.warning('buy from cart failed')

						valid, total, total_after_discount, messages_ = service.buy_logic(int(item_id), int(quantity_to_buy),
						                                                                  amount_in_db,
						                                                                  request.user.is_authenticated,
						                                                                  request.user.username,
						                                                                  shipping_details,
						                                                                  card_details, True,
						                                                                  total_amount)
						if not valid:
							messages.warning(request, 'can`t buy item : ' + str(item_id))
							messages.warning(request, 'reason : ' + str(messages_))
							loger.warning('buy from cart failed')
							return redirect('/login_redirect')

					if request.user.is_authenticated:
						cart = Cart.objects.get(customer=request.user)
						cart.items.remove(item1)
					else:
						cart_g = request.session['cart']
						cart_g['items_id'].remove(Decimal(item_id))
						request.session['cart'] = cart_g

				messages.success(request, ' total after discount : ' + str(res) + " instead of: " + str(res_before))
				logev.info('buy form cart successfully')
				return redirect('/login_redirect')
			else:
				err = '' + str(form.errors)
				messages.warning(request, 'error in :  ' + err)
				loger.warning('buy from cart failed')
				return redirect('/login_redirect')

		else:
			list_ = []
			if not request.user.is_authenticated:
				base_template_name = 'homepage_guest.html'
				list_ = make_guest_cart(request)
			else:
				if "store_owners" in request.user.groups.values_list('name', flat=True):
					base_template_name = 'store/homepage_store_owner.html'
				else:
					base_template_name = 'homepage_member.html'
				list_ = []

			form = CartForm(request.user, list_)
			q_list = QForm(request.user, list_)
			text = SearchForm()
			user_name = request.user.username
			items_of_user = []
			if request.user.is_authenticated:
				carts = Cart.objects.filter(customer=request.user)
				for cart in carts:
					items_of_user += list(cart.items.all())
			context = {
				'user_name': user_name,
				'text': text,
				'form': form,
				'base_template_name': base_template_name,
				'qua': q_list,
				'card': PayForm(),
				'shipping': ShippingForm(),
				'items_list': items_of_user + list_
			}
			return render(request, 'trading_system/cart_test.html', context)
	except DBFailedExceptionServiceToViews as e:
		messages.warning(request, e.msg)
		loger.warning(e.msg)
		return redirect('/login_redirect')


def view_discounts(request, pk):
	try:
		discounts = service.get_discounts_serach(pk)
		text = SearchForm()
		context = {
			'text': text,
			'discounts': discounts
		}
		return render(request, 'trading_system/view_discounts.html', context)
	except DBFailedExceptionServiceToViews as e:
		messages.warning(request, e.msg)
		loger.warning(e.msg)
		return redirect('/login_redirect')
