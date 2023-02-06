import pytest

import testsuite


HISTORY = [
    {
        'eater_id': '0',
        'initiator_id': '1',
        'initiator_type': 'admin',
        'changeset': '{"name":["", "name"]}',
        'update_time': '2019-12-31T10:59:59+00:00',
    },
    {
        'eater_id': '0',
        'initiator_id': '2',
        'initiator_type': 'user',
        'changeset': '{"name":["name", "name_1"]}',
        'update_time': '2020-12-31T10:59:59+03:00',
    },
    {
        'eater_id': '0',
        'initiator_type': 'system',
        'changeset': '{"name":["name_1", "name_2"], "sex": ["m", "f"]}',
        'update_time': '2021-01-31T10:59:59+03:00',
    },
]

EXPECTED = {
    0: [
        {
            'initiator_type': 'system',
            'changeset': {'name': ['name_1', 'name_2'], 'sex': ['m', 'f']},
            'update_time': '2021-01-31T07:59:59+00:00',
        },
        {
            'initiator_id': '2',
            'initiator_type': 'user',
            'changeset': {'name': ['name', 'name_1']},
            'update_time': '2020-12-31T07:59:59+00:00',
        },
        {
            'initiator_id': '1',
            'initiator_type': 'admin',
            'changeset': {'name': ['', 'name']},
            'update_time': '2019-12-31T10:59:59+00:00',
        },
    ],
    1: [],
}


@pytest.mark.parametrize(
    'history, expected', [pytest.param(HISTORY, EXPECTED)],
)
async def test_200(taxi_eats_eaters, history, expected, insert_history_to_db):
    eaters = insert_history_to_db(history)
    for eater_id in eaters:
        response = await taxi_eats_eaters.post(
            '/v1/eaters/get-eater-change-history', json={'id': str(eater_id)},
        )
        assert response.status_code == 200

        response_json = response.json()
        assert 'history' in response_json

        assert expected[eater_id] == response_json['history']


@pytest.mark.parametrize(
    'history, expected, limit', [pytest.param(HISTORY, EXPECTED, 2)],
)
async def test_pagination(
        taxi_eats_eaters, history, expected, limit, insert_history_to_db,
):
    eaters = insert_history_to_db(history)
    for eater_id in eaters:
        has_more = True
        before = ''
        start_index = 0
        while has_more:
            request_json = {
                'id': str(eater_id),
                'pagination': {'limit': limit},
            }
            if before:
                request_json['pagination']['before'] = before

            response = await taxi_eats_eaters.post(
                '/v1/eaters/get-eater-change-history', json=request_json,
            )
            assert response.status_code == 200

            response_json = response.json()

            assert 'history' in response_json
            assert (
                expected[eater_id][start_index : start_index + limit]
                == response_json['history']
            )

            assert 'pagination' in response_json
            has_more = response_json['pagination']['has_more']
            assert has_more == (len(expected[eater_id]) > start_index + limit)

            before = response_json['history'][-1]['update_time']
            start_index += limit


@pytest.mark.parametrize('default_page_size', [-1, 9999])
async def test_incorrect_config(
        taxi_eats_eaters, taxi_config, default_page_size,
):
    taxi_config.set_values(
        {'EATS_EATERS_HISTORY_DEFAULT_PAGE_SIZE': default_page_size},
    )
    try:
        await taxi_eats_eaters.invalidate_caches()
        assert False, 'Service is not in a broken state'
    except testsuite.utils.http.HttpResponseError:
        pass


INCORRECT_PAGINATION_CASES = [
    # negative limit
    (HISTORY, -1, 0),  # limit  # eater_id
    # limit more than maximum
    (HISTORY, 9999, 0),  # limit  # eater_id
]


@pytest.mark.parametrize(
    'history, limit, eater_id', INCORRECT_PAGINATION_CASES,
)
async def test_incorrect_pagination_request(
        taxi_eats_eaters, history, limit, eater_id, insert_history_to_db,
):
    insert_history_to_db(history)

    request_json = {'id': str(eater_id), 'pagination': {'limit': limit}}
    response = await taxi_eats_eaters.post(
        '/v1/eaters/get-eater-change-history', json=request_json,
    )
    assert response.status_code == 400
