# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks import grocery_cart as cart
# pylint: enable=import-error


DEFAULT_ORDER_ID = 'some_order_id'
DEFAULT_DISPATCH_ID = '1fe1aa6c-eacb-4563-a3d1-a6ed73a1e9c7'
DEFAULT_CART_ID = cart.DEFAULT_CART_ID

DEFAULT_INFORMER_TYPE = 'long_courier_search'
DEFAULT_COMPENSATION_TYPE = 'super_plus_voucher'
DEFAULT_SITUATION_CODE = 'default_situation_code'
DEFAULT_CANCEL_REASON = 'default_cancel_reason'
DEFAULT_COMPENSATION_INFO = {
    'compensation_value': 15,
    'numeric_value': '15',
    'status': 'success',
}
