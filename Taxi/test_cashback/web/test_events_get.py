import pytest


@pytest.mark.parametrize(
    'external_ref,expected_ids',
    [
        ('order_id_1', ['event_id_1', 'event_id_3']),
        ('order_id_2', ['event_id_4']),
        ('order_id_3', []),
        ('order_id_4', []),
    ],
)
@pytest.mark.pgsql('cashback', files=['basic_cashback.sql'])
async def test_events_get(taxi_cashback_web, external_ref, expected_ids):
    params = {'external_ref': external_ref}
    response = await taxi_cashback_web.get('/internal/events', params=params)
    assert response.status == 200
    content = await response.json()

    event_ids = [ev['event_id'] for ev in content['events']]
    assert event_ids == expected_ids


@pytest.mark.parametrize(
    'external_ref,service,expected_ids',
    [
        ('order_id_1', 'uber', ['event_id_1']),
        ('order_id_1', 'yataxi', ['event_id_6']),
        ('order_id_2', 'lavka', ['event_id_4']),
        ('order_id_1', 'eda', ['event_id_3']),
        ('order_id_2', 'yataxi', []),
    ],
)
@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_events_get_service(
        taxi_cashback_web, service, external_ref, expected_ids,
):
    params = {'external_ref': external_ref, 'service': service}
    response = await taxi_cashback_web.get('/internal/events', params=params)
    assert response.status == 200
    content = await response.json()

    event_ids = [ev['event_id'] for ev in content['events']]
    assert event_ids == expected_ids

    for event in content['events']:
        assert event.get('yandex_uid') is not None
        assert event.get('payload') is None


@pytest.mark.parametrize(
    'external_ref,payload,yandex_uid',
    [
        ('order_id_4', {'eda': {'currency': 'RUB'}}, 'yandex_uid_1'),
        ('order_id_5', {'lavka': {'currency': 'RUB'}}, 'yandex_uid_2'),
        ('order_id_6', {'uber': {'currency': 'RUB'}}, 'yandex_uid_3'),
    ],
)
@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_events_get_service_payload_and_yandex_uid(
        taxi_cashback_web, payload, external_ref, yandex_uid,
):
    params = {'external_ref': external_ref, 'service': 'yataxi'}
    response = await taxi_cashback_web.get('/internal/events', params=params)
    assert response.status == 200
    content = await response.json()

    assert len(content['events']) == 1
    for event in content['events']:
        payment_json_response = event.get('payload')
        assert payment_json_response == payload
        assert event['yandex_uid'] == yandex_uid
