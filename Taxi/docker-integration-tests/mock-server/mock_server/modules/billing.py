import inspect
import uuid

from aiohttp import web
from aiohttp_xmlrpc import handler


def balance_simple(name):
    def _decorator(func):
        func.rpc_name = 'BalanceSimple.' + name
        return func
    return _decorator


def convert_to_json_format(payment_methods):
    result = []
    for card_id, card in payment_methods.items():
        result.append({
            'type': card['type'],
            'id': card_id,
            'payment_system': card['system'],
            'number': card['number'],
            'currency': card['currency'],
            'name': card.get('name', ''),
            'region_id': card['region_id'],
            'service_labels': card.get('service_labels', []),
            'expiration_year': card['expiration_year'],
            'expiration_month': card['expiration_month'],
        })
    return result


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.router.add_route('*', '/simple/xmlrpc', XMLRPCHandler)
        self.router.add_get('/bindings-external/v2.0/bindings/',
                            self.handle_bindings)
        self.router.add_post('/change_payment_methods',
                             self.change_payment_methods)
        self.router.add_post(
            '/trust-payments/v2/payment-methods/{card_id}/labels',
            self.handle_set_label)
        self.router.add_post('/get_data', self.get_data)
        self.router.add_post('/set_basket_status', self.set_basket_status)

    def handle_bindings(self, request):
        user_data = self.data.get(request.headers['X-Uid'], {})
        if user_data.get('status') == 'error':
            return web.Response(status=500)
        payment_methods = user_data.get('payment_methods', {})
        cards = convert_to_json_format(payment_methods)
        return web.json_response({'bindings': cards})

    async def change_payment_methods(self, request):
        data = await request.json()
        user_data = self.data.setdefault(data['uid'], {})
        user_data.update({
            'status': data['status'],
            'rules': data['rules'],
            'payment_methods': data['payment_methods'],
        })
        return web.Response()

    async def handle_set_label(self, request):
        user_data = self.data.get(request.headers['X-Uid'], {})
        payment_methods = user_data.get('payment_methods', {})
        card_id = request.match_info['card_id']
        card = payment_methods.get(card_id)
        if not card:
            return web.Response(status=404)
        if 'service_labels' not in card:
            card['service_labels'] = []
        body = await request.json()
        card['service_labels'].append(body['label'])
        return web.json_response({'status': 'success'})

    async def get_data(self, request):
        data = await request.json()
        return web.json_response(self.data[data['uid']])

    async def set_basket_status(self, request):
        data = await request.json()
        for basket in self.data[data['uid']].get('baskets', ()):
            if basket['trust_payment_id'] == data['trust_payment_id']:
                basket['status'] = data['status']
                if 'extra' in data:
                    basket['extra'] = data['extra']
                return web.Response()
        return web.Response(status=404)


class XMLRPCHandler(handler.XMLRPCView):
    def _lookup_method(self, method_name):
        for name, method in inspect.getmembers(self):
            if (callable(method) and name.startswith('method_') and
                    getattr(method, 'rpc_name', None) == method_name):
                return method
        return super()._lookup_method(method_name)

    @balance_simple('ListPaymentMethods')
    def method_list_payment_methods(self, api_key, uid, user_ip, **kwargs):
        data = self.request.app.data.get(uid)
        if data is not None:
            return {
                'status': data.get('status', 'success'),
                'payment_methods': data.get('payment_methods', {}),
            }
        return {
            'status': 'success',
            'payment_methods': {},
        }

    @balance_simple('SetCardLabel')
    def method_set_card_label(self, api_key, uid, card_id, label, **kwargs):
        card_id = 'card-' + card_id
        data = self.request.app.data.get(uid)
        if data is not None and card_id in data['payment_methods']:
            data['payment_methods'][card_id].setdefault(
                'service_labels', [],
            ).append(label)
            return {'status': 'success'}
        return {'status': 'error'}

    # pylint: disable=invalid-name
    @balance_simple('CreateOrderOrSubscription')
    def method_create_order_or_subscription(
            self, api_key, user_ip, service_product_id, region_id,
            service_order_id, uid=None, start_ts=None, **kwargs):
        if uid is None:
            return {'status': 'error', 'status_code': 'uid'}
        data = self.request.app.data.setdefault(uid, {})
        if data.get('rules', {}).get('create_order') == 'error':
            return {'status': 'error', 'status_code': 'user_error'}
        data.setdefault('orders', []).append(service_order_id)
        return {'status': 'success'}

    # pylint: disable=too-many-arguments
    @balance_simple('CreateBasket')
    def method_create_basket(
            self, api_key, user_ip, currency, orders, paymethod_id,
            order_tag=None, user_phone=None, uid=None, back_url=None,
            wait_for_cvn=None, payment_timeout=None, pass_params=None,
            **kwargs):
        user_data = self.request.app.data.get(uid)
        status_code = None
        if user_data is None:
            status_code = 'wrong_uid'
        elif user_data['rules'].get('create') == 'error':
            status_code = 'user_error'

        if status_code is not None:
            response = {'status': 'error', 'status_code': status_code}
        else:
            basket = {
                'request': {
                    'user_ip': user_ip,
                    'currency': currency,
                    'orders': orders,
                    'paymethod_id': paymethod_id,
                    'order_tag': order_tag,
                    'user_phone': user_phone,
                    'uid': uid,
                    'back_url': back_url,
                    'wait_for_cvn': wait_for_cvn,
                    'payment_timeout': payment_timeout,
                    'pass_params': pass_params,
                },
                'status': 'init',
                'trust_payment_id': uuid.uuid4().hex,
                'updates': [],
            }
            response = {
                'status': 'success',
                'trust_payment_id': basket['trust_payment_id'],
            }
            user_data.setdefault('baskets', []).append(basket)
        return response

    @balance_simple('PayBasket')
    def method_pay_basket(self, api_key, user_ip, trust_payment_id, uid=None,
                          **kwargs):
        if uid is None or uid not in self.request.app.data:
            return {'status': 'error', 'status_code': 'uid'}
        user_data = self.request.app.data[uid]
        basket = None
        for basket in user_data['baskets']:
            if basket['trust_payment_id'] == trust_payment_id:
                break
        else:
            return {'status': 'error', 'status_code': 'trust_payment_id'}

        if basket['status'] in ('holding', 'holded'):
            return {'status': 'success'}
        if basket['status'] != 'init':
            return {'status': 'error', 'status_code': 'wrong_status'}
        if user_data['rules'].get('pay') == 'error':
            return {'status': 'error', 'status_code': 'user_error'}
        if user_data['rules'].get('pay') == 'manual':
            basket['status'] = 'holding'
        elif user_data['rules'].get('pay') == 'fail':
            basket['status'] = 'cancelled'
        else:
            basket['status'] = 'holded'
        return {'status': 'success'}

    @balance_simple('CheckBasket')
    def method_check_basket(self, api_key, user_ip, trust_payment_id, uid=None,
                            **kwargs):
        if uid is None or uid not in self.request.app.data:
            return {'status': 'error', 'status_code': 'uid'}
        user_data = self.request.app.data[uid]
        basket = None
        for basket in user_data['baskets']:
            if basket['trust_payment_id'] == trust_payment_id:
                break
        else:
            return {'status': 'error', 'status_code': 'trust_payment_id'}

        if basket['status'] in ('holded', 'cleared', 'resized', 'refunded'):
            return {'status': 'success'}
        result = {'status': basket['status']}
        if 'extra' in basket:
            result.update(basket['extra'])
        return result

    # pylint: disable=too-many-branches, too-many-return-statements
    @balance_simple('UpdateBasket')
    def method_update_basket(self, api_key, user_ip, reason_desc,
                             trust_payment_id, orders, uid=None, **kwargs):
        if uid is None or uid not in self.request.app.data:
            return {'status': 'error', 'status_code': 'uid'}
        user_data = self.request.app.data[uid]
        basket = None
        for basket in user_data['baskets']:
            if basket['trust_payment_id'] == trust_payment_id:
                break
        else:
            return {'status': 'error', 'status_code': 'trust_payment_id'}

        if reason_desc == 'clear':
            if basket['status'] in ('clearing', 'cleared'):
                return {'status': 'success'}
            if basket['status'] not in ('holded', 'resized'):
                return {'status': 'error', 'status_code': 'wrong_status'}
            if user_data['rules'].get('clear') == 'error':
                return {'status': 'error', 'status_code': 'user_error'}
            if user_data['rules'].get('clear') == 'manual':
                basket['status'] = 'clearing'
            else:
                basket['status'] = 'cleared'
        elif reason_desc == 'decrease_cost':
            if basket['status'] in ('resizing', 'resized'):
                return {'status': 'success'}
            if basket['status'] not in ('holded', 'resized'):
                return {'status': 'error', 'status_code': 'wrong_status'}
            if user_data['rules'].get('resize') == 'error':
                return {'status': 'error', 'status_code': 'user_error'}
            if user_data['rules'].get('resize') == 'manual':
                basket['status'] = 'resizing'
            else:
                basket['status'] = 'resized'
        else:
            return {'status': 'error', 'status_code': 'reason_desc'}
        basket['updates'].append({
            'reason_desc': reason_desc,
            'orders': orders,
        })
        return {'status': 'success'}

    @balance_simple('CreateRefund')
    def method_create_refund(self, api_key, user_ip, reason_desc,
                             trust_payment_id, orders, uid=None, **kwargs):
        if uid is None or uid not in self.request.app.data:
            return {'status': 'error', 'status_code': 'uid'}
        user_data = self.request.app.data[uid]
        basket = None
        for basket in user_data['baskets']:
            if basket['trust_payment_id'] == trust_payment_id:
                break
        else:
            return {'status': 'error', 'status_code': 'trust_payment_id'}

        if basket['status'] not in ('cleared', 'refunded'):
            return {'status': 'error', 'status_code': 'wrong_status'}

        trust_refund_id = uuid.uuid4().hex
        basket.setdefault('refunds', []).append({
            'trust_refund_id': trust_refund_id,
            'orders': orders,
            'reason_desc': reason_desc,
            'status': 'init',
        })
        return {'status': 'success', 'trust_refund_id': trust_refund_id}

    @balance_simple('DoRefund')
    def method_do_refund(self, api_key, user_ip, trust_refund_id, uid=None,
                         **kwargs):
        if uid is None or uid not in self.request.app.data:
            return {'status': 'error', 'status_code': 'uid'}
        user_data = self.request.app.data[uid]
        found_refund = None
        found_basket = None
        for basket in user_data['baskets']:
            for refund in basket.get('refunds', ()):
                if refund['trust_refund_id'] == trust_refund_id:
                    found_refund = refund
                    found_basket = basket
                    break
        if found_refund is None:
            return {'status': 'error', 'status_code': 'trust_payment_id'}
        found_refund['status'] = 'done'
        found_basket['status'] = 'refunded'
        return {'status': 'success'}

    @balance_simple('CheckCard')
    @staticmethod
    def method_check_card(*args, **kwargs):
        return {'status': 'success'}
