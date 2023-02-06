import json

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from card_antifraud_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture
def fetch_from(pgsql):
    def _inner(table, fields, *, variables=None, order_by=None):
        cursor = pgsql['card_antifraud'].cursor()
        sql = f'select {",".join(fields)} from card_antifraud.{table}'
        values = []

        if variables:
            keys = ' and '.join([f'{key} = %s' for key in variables])
            values.extend(variables.values())
            sql += ' where ' + keys

        if order_by:
            sql += ' order by ' + order_by

        cursor.execute(sql, values)

        return [dict(zip(fields, row)) for row in cursor]

    return _inner


@pytest.fixture
def mock_cardstorage_card(mockserver):
    def _inner(
            yandex_login_id,
            has_verification_details=False,
            status=200,
            is_family_member=False,
    ):
        @mockserver.json_handler('/cardstorage/v1/card')
        def _inner_mock(request):
            assert request.json['yandex_login_id'] == yandex_login_id
            sample_card = {
                'card_id': 'absent_card',
                'billing_card_id': 'billing_card_id',
                'permanent_card_id': 'permanent_card_id',
                'currency': 'rub',
                'expiration_month': 6,
                'expiration_year': 2050,
                'number': '111111***',
                'owner': 'owner',
                'possible_moneyless': False,
                'region_id': '181',
                'regions_checked': [],
                'system': 'VISA',
                'valid': True,
                'bound': True,
                'unverified': False,
                'busy': False,
                'busy_with': [],
                'from_db': False,
                'persistent_id': 'persistent_id',
            }
            if has_verification_details:
                sample_card['verification_details'] = {
                    'level': 'standard2_3ds',
                }
            elif is_family_member:
                sample_card['family'] = {'is_owner': False}
                sample_card['verification_details'] = {'level': 'unknown'}
            if status != 200:
                return mockserver.make_response(
                    json.dumps({'code': str(status), 'message': str(status)}),
                    status=status,
                )
            return sample_card

        return _inner_mock

    return _inner
