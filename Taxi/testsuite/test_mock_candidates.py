import pytest


@pytest.mark.parametrize(
    'allowed_classes, expected_candidates',
    [
        (None, ['1_1', '2_2']),
        (['courier'], ['1_1']),
        (['courier', 'express'], ['1_1', '2_2']),
        (['express'], ['2_2']),
        (['_unknown'], []),
    ],
)
async def test_order_search(
        mockserver_client,
        create_candidate,
        allowed_classes,
        expected_candidates,
):
    create_candidate(
        dbid_uuid='1_1', tariff_classes=['courier'], position=[55, 37],
    )
    create_candidate(
        dbid_uuid='2_2', tariff_classes=['express'], position=[55, 37],
    )
    data = {'point': [37.62, 55.75]}
    if allowed_classes is not None:
        data['allowed_classes'] = allowed_classes
    response = await mockserver_client.post(
        '/candidates/order-search', json=data,
    )
    r = response.json()
    assert {c['id'] for c in r['candidates']} == set(expected_candidates)


@pytest.mark.parametrize(
    'driver_ids, expected_result_driver_ids',
    [
        (['1_1'], ['1_1']),
        (['2_2'], ['2_2']),
        (['1_1', '2_2'], ['1_1', '2_2']),
        (['3_3'], []),
    ],
)
async def test_profiles(
        mockserver_client,
        create_candidate,
        driver_ids,
        expected_result_driver_ids,
):
    create_candidate(
        dbid_uuid='1_1', tariff_classes=['courier'], position=[55, 37],
    )
    create_candidate(
        dbid_uuid='2_2', tariff_classes=['express'], position=[55, 37],
    )

    data = {
        'driver_ids': [
            {'dbid': x.split('_')[0], 'uuid': x.split('_')[1]}
            for x in driver_ids
        ],
        'data_keys': ['transport'],
    }
    response = await mockserver_client.post('/candidates/profiles', data)
    r = response.json()

    assert 'drivers' in r
    assert set(expected_result_driver_ids) == {d['id'] for d in r['drivers']}
    assert all(['transport' in d for d in r['drivers']])
