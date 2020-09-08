from django.contrib.auth.models import User as m_User, Group

import trading_system.domain.cart as CartModule
import trading_system.domain.store as StoreModule
import trading_system.domain.domain as dom


class User:
	def __init__(self, model=None):
		if model != None:
			self._model = model

	@property
	def pk(self):
		return self._model.pk

	@property
	def username(self):
		return self._model.username

	@property
	def stores(self):
		return StoreModule.Store.get_owned_stores(user_id=self.pk)

	@property
	def cart(self):
		return CartModule.Cart.get_cart(user_id=self.pk)

	def have_no_more_stores(self):
		StoreModule.Store.owns_stores(user_id=self.pk) and StoreModule.Store.manages_stores(user_id=self.pk)

	def owns_no_more_stores(self):
		return StoreModule.Store.owns_stores(user_id=self.pk)

	def manages_no_more_stores(self):
		return StoreModule.Store.manages_stores(user_id=self.pk)

	def remove_from_owners(self):
		owners_group = Group.objects.get(name="store_owners")
		owners_group.user_set.remove(self._model)

	def remove_from_managers(self):
		owners_group = Group.objects.get(name="store_managers")
		owners_group.user_set.remove(self._model)

	def get_stores(self):
		return self.stores

	def is_authenticated(self):
		return self._model.is_authenticated

	@staticmethod
	def get_user(user_id):
		try:
			if user_id is None:
				model = m_User.objects.filter(username='AnonymousUser')[0]
			else:
				model = m_User.objects.get(pk=user_id)
			return User(model=model)
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')

	@staticmethod
	def len_of_super():
		try:
			return len(m_User.objects.filter(is_superuser=True))
		except Exception:
			raise dom.DBFailedExceptionDomainToService(msg='DB Failed')
