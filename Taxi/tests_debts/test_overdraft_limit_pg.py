import pytest

from tests_debts import common


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.config(TVM_SERVICES=common.TVM_SERVICES)
async def test_pg_phoneid(debts_client, mock_antifraud_limit):
    request = debts_client.make_request(phone_id='phone_id_1', brand='yataxi')
    await debts_client.get_limit(request)

    af_request = mock_antifraud_limit.last_request
    assert af_request['debts'] == [
        {'value': 300, 'currency': 'RUB'},
        {'value': 40, 'currency': 'USD'},
    ]


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.config(TVM_SERVICES=common.TVM_SERVICES)
async def test_pg_phoneid_uid(debts_client, mock_antifraud_limit):
    request = debts_client.make_request(
        phone_id='phone_id_1', yandex_uid='yandex_uid_4', brand='yataxi',
    )
    await debts_client.get_limit(request)

    af_request = mock_antifraud_limit.last_request
    assert af_request['debts'] == [
        {'value': 300, 'currency': 'RUB'},
        {'value': 40, 'currency': 'USD'},
        {'value': 15, 'currency': 'EUR'},
    ]


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.config(TVM_SERVICES=common.TVM_SERVICES)
async def test_pg_uid_only_search(debts_client, mock_antifraud_limit):
    request = debts_client.make_request(
        phone_id='no_phone_id', yandex_uid='yandex_uid_3',
    )
    await debts_client.get_limit(request)

    af_request = mock_antifraud_limit.last_request
    assert af_request['debts'] == [{'value': 3, 'currency': 'BTC'}]


@pytest.mark.config(TVM_SERVICES=common.TVM_SERVICES)
async def test_pg_no_debts_limit(debts_client):
    request = debts_client.make_request(
        phone_id='no_phone_id', yandex_uid='yandex_uid_3',
    )
    content = await debts_client.get_limit(request)
    assert content['has_debts'] is False
    assert content['remaining_limit'] == 0
