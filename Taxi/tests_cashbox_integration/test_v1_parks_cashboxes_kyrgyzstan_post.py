from tests_cashbox_integration import utils

ENDPOINT = '/fleet/cashbox/v1/parks/cashboxes'

KYRGYZSTAN_CASHBOX = {'cashbox_type': 'kyrgyzstan', 'uuid': 'super_park'}


def pop_secrets(cashbox):
    res = {**cashbox}
    res.pop('uuid')
    return res


async def test_ok(taxi_cashbox_integration, pgsql):
    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': '123'},
        json={'cashbox': KYRGYZSTAN_CASHBOX},
        headers={
            'X-Idempotency-Token': '100500',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-UID': '123',
        },
    )

    assert response.status_code == 200, response.text
    response_body = response.json()
    response_id = response_body.pop('id', None)
    assert response_id is not None
    assert response_body == {
        'cashbox': pop_secrets(KYRGYZSTAN_CASHBOX),
        'park_id': '123',
        'cashbox_state': 'valid',
    }

    rows = utils.get_all_cashboxes(pgsql)
    assert len(rows) == 1
    assert rows[0].pop('date_created', None) is not None
    assert rows[0].pop('date_updated', None) is not None
    assert rows[0] == {
        'id': response_id,
        'park_id': '123',
        'idempotency_token': '100500',
        'state': 'valid',
        'is_current': False,
        'cashbox_type': 'kyrgyzstan',
        'details': {},
        'secrets': {'uuid': 'M5a7svvcrnA7E5axBDY2sw=='},
    }
