import pytest

MECHANIC = 'taximeter'

MECHANICS_SETTINGS = {
    'taximeter': {
        'reasons': {
            '22222222-2222-2222-2222-222222222222': ['block_key_with_args'],
        },
    },
}


async def test_simple(taxi_blocklist, add_request, headers):
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert res.status_code == 200
    block_id = res.json()['block_id']

    res = await taxi_blocklist.post(
        '/internal/blocklist/v1/reason',
        json=dict(blocks=[block_id]),
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.07 (1234)',
        },
    )
    assert res.status_code == 200
    assert res.json()['reasons'][block_id] == dict(
        text='Причина блокировки 1', mechanics=MECHANIC,
    )


@pytest.mark.translations(
    taximeter_backend_driver_messages=dict(
        block_key_1=dict(ru='Машина %(number)s заблокирована без причин'),
    ),
)
async def test_with_args(taxi_blocklist, add_request, headers):
    add_request['meta'] = dict(number='12345')
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert res.status_code == 200
    block_id = res.json()['block_id']

    res = await taxi_blocklist.post(
        '/internal/blocklist/v1/reason',
        json=dict(blocks=[block_id]),
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.07 (1234)',
        },
    )
    assert res.status_code == 200
    assert res.json()['reasons'][block_id] == dict(
        text='Машина 12345 заблокирована без причин', mechanics=MECHANIC,
    )


async def test_empty_request(taxi_blocklist):
    res = await taxi_blocklist.post(
        '/internal/blocklist/v1/reason',
        json=dict(blocks=[]),
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.07 (1234)',
        },
    )
    assert res.status_code == 400


@pytest.mark.config(BLOCKLIST_MECHANICS_SETTINGS=MECHANICS_SETTINGS)
@pytest.mark.translations(
    taximeter_backend_driver_messages=dict(
        block_key_with_args=dict(
            en='Машина %(number)s заблокирована без причин',
        ),
    ),
)
async def test_fallback_without_key(taxi_blocklist, add_request, headers):
    add_request['meta'] = dict(number='12345')
    add_request['reason'] = dict(key='block_key_with_args')
    headers['Accept-Language'] = 'en'
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert res.status_code == 200
    block_id = res.json()['block_id']

    res = await taxi_blocklist.post(
        '/internal/blocklist/v1/reason',
        json=dict(blocks=[block_id]),
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.07 (1234)',
        },
    )
    assert res.status_code == 200
    assert res.json()['reasons'][block_id] == dict(
        text='За подробностями обратитесь в поддержку', mechanics=MECHANIC,
    )


@pytest.mark.translations(
    taximeter_backend_driver_messages=dict(
        block_key_1=dict(
            ru='Ваша машина заблокирована без причин',
            en='Машина %(car_number)s заблокирована без причин до %(data)s',
        ),
    ),
)
async def test_args_substitution(taxi_blocklist, add_request, headers):
    add_request['meta'] = dict(data='15.01.1999')
    headers['Accept-Language'] = 'ru'
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert res.status_code == 200
    block_id = res.json()['block_id']

    res = await taxi_blocklist.post(
        '/internal/blocklist/v1/reason',
        json=dict(blocks=[block_id]),
        headers={
            'Accept-Language': 'en',
            'User-Agent': 'Taximeter 9.07 (1234)',
        },
    )
    assert res.status_code == 200
    assert res.json()['reasons'][block_id] == dict(
        text='Машина car_number заблокирована без причин до 15.01.1999',
        mechanics=MECHANIC,
    )
