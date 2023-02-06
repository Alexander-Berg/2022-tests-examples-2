import pytest

from tests_bank_communications import utils

APP_1 = 'app_1'
APP_2 = 'app_2'


def get_headers(app_name=APP_1, platform='android'):
    return {
        'X-Yandex-BUID': '7948e3a9-623c-4524-a390-9e4264d27a11',
        'X-Yandex-UID': '1',
        'X-YaBank-PhoneID': 'phone_id1',
        'X-YaBank-SessionUUID': '1',
        'X-Request-Application': f'platform={platform},app_name={app_name}',
        'X-Request-Language': 'ru',
        'X-Ya-User-Ticket': 'user_ticket',
    }


def get_body():
    return {
        'push_token': 'push_token',
        'uuid': 'uuid',
        'device_id': 'device_id',
    }


@pytest.mark.parametrize('app_name', [APP_1, APP_2])
@pytest.mark.parametrize('Platform', ['android', 'ios'])
async def test_push_subscribe_ok(
        taxi_bank_communications, xiva_mock, pgsql, app_name, Platform,
):
    headers = get_headers(app_name=app_name, platform=Platform)
    response = await taxi_bank_communications.post(
        '/v1/communications/v1/push_subscribe',
        headers=headers,
        json=get_body(),
    )

    assert response.status_code == 200
    last_subs = utils.get_last_subscriptions(pgsql, 'uuid')
    last_subs[0].pop('subscription_id')
    assert last_subs[0] == {
        'bank_uid': headers['X-Yandex-BUID'],
        'xiva_subscription_id': 'xiva_subscription_id',
        'uuid': 'uuid',
        'device_id': 'device_id',
        'status': 'ACTIVE',
        'locale': 'ru',
    }


async def test_deactivate_old_sub(taxi_bank_communications, xiva_mock, pgsql):
    headers = get_headers()
    utils.insert_push_subscription(
        pgsql, 'uuid', headers['X-Yandex-BUID'], 'ACTIVE',
    )
    response = await taxi_bank_communications.post(
        '/v1/communications/v1/push_subscribe',
        headers=headers,
        json=get_body(),
    )

    assert response.status_code == 200
    last_subs = utils.get_last_subscriptions(pgsql, 'uuid')
    assert len(last_subs) == 2
    for i, status in enumerate(['ACTIVE', 'INACTIVE']):
        last_subs[i].pop('subscription_id')
        assert last_subs[i] == {
            'bank_uid': headers['X-Yandex-BUID'],
            'xiva_subscription_id': 'xiva_subscription_id',
            'uuid': 'uuid',
            'device_id': 'device_id',
            'status': status,
            'locale': 'ru',
        }


async def test_subscription_race(
        taxi_bank_communications, xiva_mock, pgsql, testpoint,
):
    @testpoint('subscription_race')
    def _insert_subscriptions(data):
        utils.insert_push_subscription(
            pgsql, 'uuid', '7948e3a9-623c-4524-a390-9e4264d27a11', 'ACTIVE',
        )

    headers = get_headers()
    response = await taxi_bank_communications.post(
        '/v1/communications/v1/push_subscribe',
        headers=headers,
        json=get_body(),
    )

    assert response.status_code == 500


async def test_masked_hit(taxi_bank_communications, xiva_mock, pgsql):
    headers = get_headers()
    headers['X-Yandex-BUID'] = '7948e3a9-623c-4524-a390-9e4264d27a11'
    response = await taxi_bank_communications.post(
        '/v1/communications/v1/push_subscribe',
        headers=headers,
        json=get_body(),
    )
    assert (
        xiva_mock.subscribe_handle.next_call()['request'].query['user']
        == '11111111-1111-1111-1111-111111111111'
    )
    assert response.status_code == 200


async def test_masked_miss(taxi_bank_communications, xiva_mock, pgsql):
    headers = get_headers()
    headers['X-Yandex-BUID'] = '024e7db5-9bd6-4f45-a1cd-2a442e15bdc2'
    response = await taxi_bank_communications.post(
        '/v1/communications/v1/push_subscribe',
        headers=headers,
        json=get_body(),
    )
    answer = xiva_mock.subscribe_handle.next_call()['request'].query['user']
    assert answer != '11111111-1111-1111-1111-111111111111'
    assert answer != '024e7db5-9bd6-4f45-a1cd-2a442e15bdc2'
    assert response.status_code == 200


@pytest.mark.config(BANK_COMMUNICATIONS_APPS_INFO_NEW={})
async def test_app_name_not_found_in_config(
        taxi_bank_communications, xiva_mock, pgsql,
):
    headers = get_headers()
    headers['X-Yandex-BUID'] = '024e7db5-9bd6-4f45-a1cd-2a442e15bdc2'
    response = await taxi_bank_communications.post(
        '/v1/communications/v1/push_subscribe',
        headers=headers,
        json=get_body(),
    )
    assert response.status_code == 400
    resp = response.json()
    assert 'message' in resp
    assert resp['message'] == f'unknown app {APP_1}'


async def test_push_platform(
        taxi_bank_communications, xiva_mock, pgsql, mockserver,
):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _mock_subscribe(request):
        assert request.method == 'POST'
        assert request.query.keys() == {
            'app_name',
            'uuid',
            'platform',
            'user',
            'service',
            'app_name',
            'device',
        }
        assert request.get_data().decode() == 'push_token=push_token'
        assert request.query['platform'] == 'hms'
        return mockserver.make_response(
            json={'subscription-id': 'xiva_subscription_id'},
        )

    headers = get_headers()
    response = await taxi_bank_communications.post(
        '/v1/communications/v1/push_subscribe',
        headers=headers,
        json={
            'push_token': 'push_token',
            'uuid': 'uuid',
            'device_id': 'device_id',
            'push_platform': 'huawei',
        },
    )
    assert response.status_code == 200
