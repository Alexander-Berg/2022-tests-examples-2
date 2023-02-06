import datetime
import string

import psycopg2.tz

GROCERY_CLIENT_ID = '94062943'

SERVICE_FEE_RUB_CLIENT_ID = '95332016'
SERVICE_FEE_RUB_CONTRACT_ID = '4469918'

SERVICE_FEE_BYN_CLIENT_ID = '97543826'
SERVICE_FEE_BYN_CONTRACT_ID = '5339784'

SERVICE_FEE_KZT_CLIENT_ID = '97543252'
SERVICE_FEE_KZT_CONTRACT_ID = '5339448'

DONATION_CLIENT_ID = '93696285'
DONATION_CONTRACT_ID = '3636412'


def deal_info(client_id, contract_id, mvp):
    info = {'mvp': mvp, 'contract_id': contract_id, 'id': client_id}

    return info


class DealIdTest:
    def __init__(self):
        self._request = None
        self._client_info = {'places': {}, 'couriers': {}, 'pickers': {}}
        self._expected = {'deal_id': None}
        self._expected_status = 200
        self._expected_response = {}
        self._should_fail = False
        self._order_nr = '123456'
        self._expected_data = {'data': {}, 'order_nr': self._order_nr}
        self._token = None

    def on_order_nr(self, order_nr):
        self._order_nr = order_nr
        self._expected_data['order_nr'] = self._order_nr
        return self

    def token(self):
        return self._token

    def on_picker(
            self, picker_id, place_type, delivery_type, assembly_type=None,
    ):
        self._request = {
            'counterparty_id': picker_id,
            'counterparty_type': 'picker',
            'order_nr': self._order_nr,
            'place_type': place_type,
            'delivery_type': delivery_type,
            'timestamp': '2021-03-18T15:00:00+03:00',
        }
        self._expected_data['place_type'] = place_type
        self._expected_data['delivery_type'] = delivery_type

        if assembly_type is not None:
            self._request['assembly_type'] = assembly_type
            self._expected_data['assembly_type'] = assembly_type
        return self

    def on_courier(
            self, courier_id, place_type, delivery_type, assembly_type=None,
    ):
        self._request = {
            'counterparty_id': courier_id,
            'counterparty_type': 'courier',
            'order_nr': self._order_nr,
            'place_type': place_type,
            'delivery_type': delivery_type,
            'timestamp': '2021-03-18T15:00:00+03:00',
        }
        self._expected_data['place_type'] = place_type
        self._expected_data['delivery_type'] = delivery_type

        if assembly_type is not None:
            self._request['assembly_type'] = assembly_type
            self._expected_data['assembly_type'] = assembly_type
        return self

    def on_place(
            self, place_id, place_type, delivery_type, assembly_type=None,
    ):
        self._request = {
            'counterparty_id': place_id,
            'counterparty_type': 'place',
            'order_nr': self._order_nr,
            'place_type': place_type,
            'delivery_type': delivery_type,
            'timestamp': '2021-03-18T15:00:00+03:00',
        }
        self._expected_data['place_type'] = place_type
        self._expected_data['delivery_type'] = delivery_type

        if assembly_type is not None:
            self._request['assembly_type'] = assembly_type
            self._expected_data['assembly_type'] = assembly_type
        return self

    def on_service_fee(
            self,
            place_type,
            delivery_type,
            currency,
            info,
            timestamp=None,
            assembly_type=None,
    ):
        self._request = {
            'place_type': place_type,
            'delivery_type': delivery_type,
            'assembly_type': assembly_type,
            'counterparty_type': 'service_fee',
            'currency': currency,
            'order_nr': self._order_nr,
            'timestamp': timestamp or '2021-03-18T15:00:00+03:00',
        }

        self._expected_data['data']['info'] = info
        self._expected_data['data']['version'] = '1'
        self._expected_data['data']['rule'] = 'default'
        self._expected_data['counterparty_type'] = 'service_fee'
        self._expected_data['counterparty_id'] = info['id']
        self._expected_data['data']['kind'] = 'service_fee'
        self._expected_data['timestamp'] = datetime.datetime(
            2021,
            3,
            18,
            12,
            0,
            0,
            0,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
        )
        return self

    def on_donation(self, currency, info, timestamp=None):
        self._request = {
            'counterparty_type': 'donation',
            'order_nr': self._order_nr,
            'currency': currency,
            'timestamp': timestamp or '2021-03-18T15:00:00+03:00',
        }
        self._expected_data['data']['info'] = info
        self._expected_data['data']['version'] = '1'
        self._expected_data['data']['rule'] = 'donation'
        self._expected_data['counterparty_type'] = 'donation'
        self._expected_data['counterparty_id'] = info['id']
        self._expected_data['data']['kind'] = 'donation'
        self._expected_data['timestamp'] = datetime.datetime(
            2021,
            3,
            18,
            12,
            0,
            0,
            0,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
        )
        return self

    def using_client_info(
            self,
            client_info,
            place_id=None,
            courier_id=None,
            picker_id=None,
            rule=None,
    ):
        counter = sum(
            map(
                lambda x: 0 if x is None else 1,
                [place_id, courier_id, picker_id],
            ),
        )
        if counter == 0:
            raise ValueError('place_id, courier_id or picker_id expected')
        elif counter != 1:
            raise ValueError(
                'Only one of place_id, courier_id and picker_id allowed',
            )

        counterparty_id = None
        client_dict = None
        if place_id is not None:
            counterparty_id = place_id
            client_dict = self._client_info['places']
            self._expected_data['data']['kind'] = 'place'
            self._expected_data['counterparty_type'] = 'place'
        elif courier_id is not None:
            counterparty_id = courier_id
            client_dict = self._client_info['couriers']
            self._expected_data['data']['kind'] = 'courier'
            self._expected_data['counterparty_type'] = 'courier'
        else:
            counterparty_id = picker_id
            client_dict = self._client_info['pickers']
            self._expected_data['data']['kind'] = 'picker'
            self._expected_data['counterparty_type'] = 'picker'

        self._expected_data['data']['info'] = client_info
        self._expected_data['data']['version'] = '1'
        self._expected_data['data']['rule'] = '' if rule is None else rule
        self._expected_data['counterparty_id'] = counterparty_id
        self._expected_data['timestamp'] = datetime.datetime(
            2021,
            3,
            18,
            12,
            0,
            0,
            0,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
        )

        client_dict[counterparty_id] = client_info

        return self

    def expected_rule_name(self, rule_name):
        self._expected_data['data']['rule'] = rule_name
        return self

    def should_fail(self, status, code, message):
        self._should_fail = True
        self._expected_status = status
        self._expected_response = {'code': code, 'message': message}
        return self

    async def run(self, fixtures):
        fixtures.client_info_mock(self._client_info)

        response = await fixtures.taxi_eats_billing_processor.post(
            '/v1/deal_id', json=self._request,
        )

        if self._should_fail:
            assert response.status == self._expected_status
            assert response.json() == self._expected_response
        else:
            cursor = fixtures.pgsql['eats_billing_processor'].cursor()
            cursor.execute(
                f"""select token, data, counterparty_type, counterparty_id,
                    order_nr, timestamp, rule_name
                    from eats_billing_processor.deals""",
            )
            res = cursor.fetchone()
            # if res:
            self._token = res[0]
            assert res[1] == self._expected_data['data']
            assert res[2] == self._expected_data['counterparty_type']
            assert res[3] == self._expected_data['counterparty_id']
            assert res[4] == self._expected_data['order_nr']
            assert res[5] == self._expected_data['timestamp']
            assert all(
                c in string.hexdigits for c in response.json()['deal_id']
            )
