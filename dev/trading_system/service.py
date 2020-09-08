import json

from trading_system.domain import domain
from trading_system.domain.domain import DBFailedExceptionDomainToService


def search(txt):
	return domain.search(txt)


def add_manager(user_name, picked, is_owner, store_pk, request_user_name, is_partner):
	try:
		"""

		:param user_name:
		:param picked:
		:param is_owner:
		:param store_pk:
		:param request_user_name:
		:return: True if failing
		"""
		return domain.add_manager(user_name, picked, is_owner, store_pk, request_user_name, False)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't add manager/owner")


def open_store(store_name, desc, user_id):
	try:
		return domain.open_store(store_name, desc, user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't add store")


def add_base_rule_to_store(rule_type, store_id, parameter, user_id):
	try:
		return domain.add_base_rule_to_store(rule_type, store_id, parameter, user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't add base rule to store")


def add_complex_rule_to_store_1(rule_type, prev_rule, store_id, operator, parameter, user_id):
	try:
		return domain.add_complex_rule_to_store_1(rule_type, prev_rule, store_id, operator, parameter, user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't add complex rule to store")


def add_complex_rule_to_store_2(rule1, parameter1, rule2, parameter2, store_id, operator1, operator2, prev_rule,
                                user_id):
	try:
		return domain.add_complex_rule_to_store_2(rule1, parameter1, rule2, parameter2, store_id, operator1, operator2,
		                                          prev_rule, user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't add complex rule to store")


def add_base_rule_to_item(item_id, rule, parameter, user_id):
	try:
		return domain.add_base_rule_to_item(item_id, rule, parameter, user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't add base rule to item")


def add_complex_rule_to_item_1(item_id, prev_rule, rule, operator, parameter, user_id):
	try:
		return domain.add_complex_rule_to_item_1(item_id, prev_rule, rule, operator, parameter, user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't add complex rule to item")


def add_complex_rule_to_item_2(item_id, prev_rule, rule1, parameter1, rule2, parameter2, operator1, operator2, user_id):
	try:
		return domain.add_complex_rule_to_item_2(item_id, prev_rule, rule1, parameter1, rule2, parameter2, operator1,
		                                         operator2, user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't add complex rule to item")


def add_item_to_store(item_json, store_id, user_id):
	try:
		item_dict = json.loads(item_json)
		return domain.add_item_to_store(price=item_dict['price'],
		                                name=item_dict['name'],
		                                description=item_dict['description'],
		                                category=item_dict['category'],
		                                quantity=item_dict['quantity'],
		                                store_id=store_id,
		                                user_id=user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't add item")


def can_remove_store(store_id, user_id):
	try:
		return domain.can_remove_store(store_id=store_id, user_id=user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't remove store")


def have_no_more_stores(user_pk):
	try:
		return domain.have_no_more_stores(user_pk=user_pk)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't remove store")


def delete_store(store_id, user_id):
	try:
		return domain.delete_store(store_id=store_id, user_id=user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't remove store")


def get_store_details(store_id):
	try:
		return domain.get_store_details(store_id=store_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't view store")


def get_store_items(store_id):
	try:
		return domain.get_store_items(store_id=store_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't view store")


def get_store_managers(store_id):
	try:
		return domain.get_store_managers(store_id=store_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't view store")


def get_store_owners(store_id):
	try:
		return domain.get_store_owners(store_id=store_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't view store")


def get_user_store_list(user_id):
	try:
		return domain.get_user_store_list(user_id=user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't view stores")


def get_item_details(item_id):
	try:
		return domain.get_item_details(item_id=item_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't view item")


def get_store_by_id(store_id):
	try:
		return domain.get_store_by_id(store_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't get store")


def remove_manager_from_store(store_id, m_id):
	try:
		return domain.remove_manager_from_store(store_id, m_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't remove manager")


def len_of_super():
	try:
		return domain.len_of_super()
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't view superusers")


def is_authenticated(user_id):
	try:
		return domain.is_authenticated(user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't get user details")


def update_item(item_id, item_dict, user_id):
	try:
		return domain.update_item(item_id=item_id, item_dict=item_dict, user_id=user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't update item")


def add_discount(store_id, type, amount, percentage, end_date, item_id, user_id):
	try:
		return domain.add_discount(store_id=store_id, type=type, amount=amount, percentage=percentage,
		                           end_date=end_date, item_id=item_id, user_id=user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't add discount")


def item_rules_string(itemId):
	try:
		return domain.item_rules_string(itemId)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't get item rules")


def store_rules_string(store_id):
	try:
		return domain.store_rules_string(store_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't get store rules")


def update_store(store_id, store_dict):
	try:
		return domain.update_store(store_id, store_dict)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't update store")


def delete_item(item_id, user_id):
	try:
		return domain.delete_item(item_id, user_id=user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't remove item")


def get_store_creator(store_id):
	try:
		return domain.get_store_creator(store_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't get store creator")


def get_user_notifications(user_id):
	try:
		return domain.get_user_notifications(user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't get user notifications")


def mark_notification_read(user_id):
	try:
		return domain.mark_notification_read(user_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't get user notifications")


def add_item_to_cart(user_id, item_id):
	try:
		return domain.add_item_to_cart(user_id, item_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't add item to cart")


def get_item(id1):
	try:
		return domain.get_item(id1)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't get item details")


def add_complex_discount(store_id, left, right, operator):
	try:
		return domain.add_complex_discount_to_store(store_id, left, right, operator)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't add discount")


def buy_logic(pk, amount, amount_in_db, is_auth, username, shipping_details, card_details, is_cart, total_amount, user_id=None):
	try:
		return domain.buy_logic(pk, amount, amount_in_db, is_auth, username, shipping_details, card_details, is_cart,
		                        user_id, total_amount)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't buy items")


def store_discounts_string(store_id):
	try:
		return domain.store_discounts_string(store_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't get store discounts")


def delete_complex_rule(rule_id):
	try:
		return domain.delete_complex(rule_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't remove rule")


def delete_base_rule(rule_id):
	try:
		return domain.delete_base(rule_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't remove rule")


def delete_complex_item_rule(rule_id):
	try:
		return domain.delete_complex_item(rule_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't remove rule")


def delete_base_item_rule(rule_id):
	try:
		return domain.delete_base_item(rule_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't remove rule")


def delete_complex_discount(disc):
	try:
		return domain.delete_complex_discount(disc)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't remove discount")


def delete_base_store_discount(disc):
	try:
		return domain.delete_base_discount(disc)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't remove discount")


def get_discounts_serach(item_id):
	try:
		return domain.get_discounts_serach(item_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't get discounts")


def get_quantity(item_id):
	try:
		return domain.get_quantity(item_id)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't get item details")


def apply_discounts_for_cart(list_of_items):
	try:
		return domain.apply_discounts_for_cart(list_of_items)
	except DBFailedExceptionDomainToService as e:
		raise DBFailedExceptionServiceToViews(msg="DB fail: can't apply discounts")


class DBFailedExceptionServiceToViews(Exception):
	def __init__(self, msg=None):
		self.msg = msg


def check_if_user_is_approved(user_id, store_id):
	return domain.check_if_user_is_approved(user_id, store_id)


def agreement_by_partner(partner_id, store_pk, user_pk):
	return domain.agreement_by_partner(partner_id, store_pk, user_pk)

def get_all_wait_agreement_t_need_to_approve(manager_id):
	return domain.get_all_wait_agreement_t_need_to_approve(manager_id)