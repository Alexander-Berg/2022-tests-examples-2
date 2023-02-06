import functools
import uuid

import pytest

from taxi_tests import utils
from taxi_tests.utils import parks

BASKET_ERROR_MSG = 'Basket status has not been changed to statuses %s in time'
ORDER_ERROR_MSG = 'Order status %s has not been achieved in time'


# pylint: disable=too-many-instance-attributes
class Client:
    def __init__(self, protocol, session_maker, search_maps, billing,
                 **kwargs):
        self.protocol = protocol
        self.session = session_maker(**kwargs)
        self.search_maps = search_maps
        self.billing = billing
        self.user_id = None
        self.source = None
        self.destinations = []
        self.zone_name = 'moscow'
        self.surge = None
        self.offer = None
        self.order_id = None
        self.payment = 'cash'
        self.selected_class = 'econom'
        self.service_level = 50
        self.card = None
        self.current_park = '999011'

    def init_phone(self, phone='random'):
        self.session.init(phone=phone)

    def launch(self):
        data = {}
        if self.user_id is not None:
            data['id'] = self.user_id
        response = self.protocol.launch(data, session=self.session)
        assert response['authorized']
        self.user_id = response['id']
        return response

    def set_source(self, point, not_sticky=True, register=True):
        if register:
            self.search_maps.register_company(coordinates=point,
                                              text=uuid.uuid4().hex)

        response = self.protocol.nearestzone({
            'id': self.user_id,
            'point': point,
        }, session=self.session)
        self.zone_name = response['nearest_zone']

        response = self.protocol.nearestposition({
            'not_sticky': not_sticky,
            'supported': ['pickup_points'],
            'dx': 10,
            'id': self.user_id,
            'll': point,
        }, session=self.session)
        self.source = self.address_from_response(response)
        return self.routestats()

    def set_destinations(self, points, register=True):
        self.destinations = []
        for point in points:
            if isinstance(point, dict):
                self.destinations.append(point)
                continue
            if register:
                self.search_maps.register_company(coordinates=point,
                                                  text=uuid.uuid4().hex)

            response = self.protocol.nearestposition({
                'not_sticky': True,
                'dx': 0,
                'id': self.user_id,
                'll': point,
            }, session=self.session)

            self.destinations.append(self.address_from_response(response))

        return self.routestats()

    def set_current_park(self, park):
        self.current_park = park

    def _get_payment(self):
        data = {'type': self.payment.split('-')[0]}
        if self.payment != 'cash':
            data['payment_method_id'] = self.payment
        return data

    def add_card(self, card='default', status='success', rules=None):
        if card == 'default':
            payment_methods = self.billing.default_paymnet_methods
            self.payment = 'card-x1111'
        elif isinstance(card, dict):
            self.payment = 'card-' + card['id']
            payment_methods = {self.payment: card}
        else:
            assert False

        self.billing.change_payment_methods(
            self.session.yandex_uid,
            payment_methods,
            status=status,
            rules=rules,
        )

    def wait_for_basket_status(self, statuses):
        if isinstance(statuses, str):
            statuses = (statuses,)
        for _ in utils.wait_for(500, BASKET_ERROR_MSG % ','.join(statuses)):
            baskets = self.get_baskets()
            if not baskets:
                continue
            if baskets[0]['status'] in statuses:
                return baskets[0]
        return None

    def get_card_payments(self, statuses=('holded', 'cleared', 'refunded')):
        if isinstance(statuses, str):
            statuses = (statuses,)
        price = 0
        for basket in self.get_baskets():
            if basket['status'] not in statuses:
                continue
            for order in basket['request']['orders']:
                price += order['price']
            for refund in basket.get('refunds', ()):
                if refund['status'] == 'done':
                    for order in refund['orders']:
                        price -= order['delta_amount']
        return price

    def get_baskets(self):
        return (
            self.billing.get_data(self.session.yandex_uid).get('baskets', [])
        )

    def set_basket_status(self, basket, status, extra=None):
        self.billing.set_basket_status(
            self.session.yandex_uid, basket['trust_payment_id'], status, extra,
        )

    def routestats(self):
        assert self.source is not None
        data = {
            'extended_description': True,
            'format_currency': True,
            'id': self.user_id,
            'payment': self._get_payment(),
            'position_accuracy': 10,
            'route': [self.source['geopoint']],
            'selected_class_only': False,
            'skip_estimated_waiting': False,
            'summary_version': 2,
            'supported_markup': 'tml-0.1',
            'supports_forced_surge': True,
            'supports_hideable_tariffs': True,
            'supports_no_cars_available': True,
            'surge_fake_pin': False,
            'with_title': True,
            'zone_name': self.zone_name,
        }

        if self.destinations:
            data['route'] += [obj['geopoint'] for obj in self.destinations]
            data['selected_class'] = self.selected_class
            data['suggest_alternatives'] = True

        response = self.protocol.routestats(data, session=self.session)
        self.offer = response.get('offer')
        for service_level in response['service_levels']:
            if service_level['class'] == self.selected_class:
                self.service_level = service_level['service_level']
                self.surge = service_level.get('forced_surge', {}).get('value')

        return response

    def order(self, comment=''):
        assert self.user_id
        data = {
            'comment': comment,
            'dont_call': False,
            'dont_sms': False,
            'id': self.user_id,
            'parks': parks.excluded([self.current_park]),
            'payment': self._get_payment(),
            'route': [self.source] + self.destinations,
            'service_level': self.service_level,
            'zone_name': self.zone_name,
        }
        if self.offer:
            data['offer'] = self.offer
        if self.surge:
            data['forced_surge'] = {'value': self.surge}
        response = self.protocol.order(data, session=self.session)
        self.order_id = response['orderid']
        return response

    def taxiontheway(self, cancel=None):
        assert self.order_id
        data = {
            'id': self.user_id,
            'orderid': self.order_id,
            'format_currency': True,
        }
        if cancel:
            data['break'] = cancel
        return self.protocol.taxiontheway(data, session=self.session)

    def wait_for_order_status(self, status='complete', timeout=1000):
        statuses = ('complete', 'failed', 'cancelled', 'expired', status)
        for _ in utils.wait_for(timeout, ORDER_ERROR_MSG % status):
            response = self.taxiontheway()
            if response['status'] in statuses:
                assert response['status'] == status
                return response
        return None

    @staticmethod
    def address_from_response(address):
        mapper = {
            'short_text': 'short_text',
            'description': 'description',
            'exact': 'exact',
            'thoroughfare': 'street',
            'type': 'type',
            'object_type': 'object_type',
            'oid': 'oid',
            'premisenumber': 'house',
            'fullname': 'full_text',
            'country': 'country',
            'locality': 'city',
            'geopoint': 'point',
        }
        data = {
            'use_geopoint': True,
        }
        for key, value in mapper.items():
            if value in address:
                data[key] = address[value]
        return data

    def paymentmethods(self):
        return self.protocol.paymentmethods({'id': self.user_id},
                                            session=self.session)


@pytest.fixture
def client_maker(protocol, session_maker, search_maps, billing):
    return functools.partial(Client, protocol, session_maker, search_maps,
                             billing)
