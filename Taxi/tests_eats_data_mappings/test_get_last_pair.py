import time
import logging
import json

import pytest


FIRST_PAIR = {
    'first_entity_type': 'a',
    'first_entity_value': 'b',
    'second_entity_type': 'c',
    'second_entity_value': 'd',
}
SECOND_PAIR = {
    'first_entity_type': 'a',
    'first_entity_value': 'b',
    'second_entity_type': 'c',
    'second_entity_value': 'dd',
}
THIRD_PAIR = {
    'first_entity_type': 'a',
    'first_entity_value': 'bb',
    'second_entity_type': 'c',
    'second_entity_value': 'ddd',
}
FOURTH_PAIR = {
    'first_entity_type': 'a',
    'first_entity_value': 'b',
    'second_entity_type': 'c',
    'second_entity_value': 'ddd',
}

SEARCH_PAIR = {
    'first_entity_type': 'a',
    'first_entity_value': 'b',
    'second_entity_type': 'c',
}
SEARCH_PAIR_INVERSE = {
    'first_entity_type': 'c',
    'first_entity_value': 'ddd',
    'second_entity_type': 'a',
}


@pytest.mark.config(TVM_SERVICES={'service1': 2345}, TVM_ENABLED=True)
@pytest.mark.entity(['yandex_uid', 'eater_id', 'a', 'c'])
@pytest.mark.mappings(
    [
        {
            'first_entity_type': 'yandex_uid',
            'second_entity_type': 'eater_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'a',
            'second_entity_type': 'c',
            'tvm_write': ['service1'],
            'tvm_read': ['service1'],
            'takeout_policies': [],
        },
    ],
)
async def test_get_one_pair_ok(
        get_all_pairs,
        taxi_eats_data_mappings,
        ticket_header,
        change_pair_order,
):
    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=FIRST_PAIR, headers=ticket_header,
    )
    assert response.status_code == 204

    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=SECOND_PAIR, headers=ticket_header,
    )
    assert response.status_code == 204

    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=THIRD_PAIR, headers=ticket_header,
    )
    assert response.status_code == 204

    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=FOURTH_PAIR, headers=ticket_header,
    )
    assert response.status_code == 204

    response = await taxi_eats_data_mappings.post(
        '/v1/get-last-pair', json=SEARCH_PAIR, headers=ticket_header,
    )
    assert response.status_code == 200
    assert response.json() == FOURTH_PAIR

    response = await taxi_eats_data_mappings.post(
        '/v1/get-last-pair', json=SEARCH_PAIR_INVERSE, headers=ticket_header,
    )
    assert response.status_code == 200
    assert response.json() == change_pair_order(FOURTH_PAIR)


SEARCH_PAIR_NONEXISTENT = {
    'first_entity_type': 'a',
    'first_entity_value': 'bbb',
    'second_entity_type': 'c',
}


@pytest.mark.config(TVM_SERVICES={'service1': 2345}, TVM_ENABLED=True)
@pytest.mark.entity(['yandex_uid', 'eater_id', 'a', 'c'])
@pytest.mark.mappings(
    [
        {
            'first_entity_type': 'yandex_uid',
            'second_entity_type': 'eater_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'a',
            'second_entity_type': 'c',
            'tvm_write': ['service1'],
            'tvm_read': ['service1'],
            'takeout_policies': [],
        },
    ],
)
async def test_get_one_pair_nonexistent(
        get_all_pairs, taxi_eats_data_mappings, ticket_header,
):

    response = await taxi_eats_data_mappings.post(
        '/v1/get-last-pair',
        json=SEARCH_PAIR_NONEXISTENT,
        headers=ticket_header,
    )
    assert response.status_code == 404


SEARCH_PAIR_NO_SETTINGS = {
    'first_entity_type': 'x',
    'first_entity_value': 'y',
    'second_entity_type': 'z',
}


@pytest.mark.config(TVM_SERVICES={'service1': 2345}, TVM_ENABLED=True)
@pytest.mark.entity(['yandex_uid', 'eater_id', 'a', 'c'])
@pytest.mark.mappings(
    [
        {
            'first_entity_type': 'yandex_uid',
            'second_entity_type': 'eater_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'a',
            'second_entity_type': 'c',
            'tvm_write': ['service1'],
            'tvm_read': ['service1'],
            'takeout_policies': [],
        },
    ],
)
async def test_get_one_pair_no_settings(
        get_all_pairs, taxi_eats_data_mappings, ticket_header,
):
    response = await taxi_eats_data_mappings.post(
        '/v1/get-last-pair',
        json=SEARCH_PAIR_NO_SETTINGS,
        headers=ticket_header,
    )
    assert response.status_code == 400


FIFTH_PAIR = {
    'first_entity_type': 'i',
    'first_entity_value': 'n',
    'second_entity_type': 'j',
    'second_entity_value': 'm',
}

SEARCH_PAIR_FORBIDDEN = {
    'first_entity_type': 'i',
    'first_entity_value': 'n',
    'second_entity_type': 'j',
}


@pytest.mark.config(
    TVM_SERVICES={'service1': 2345, 'service2': 1111}, TVM_ENABLED=True,
)
@pytest.mark.entity(['yandex_uid', 'eater_id', 'a', 'c', 'i', 'j'])
@pytest.mark.mappings(
    [
        {
            'first_entity_type': 'yandex_uid',
            'second_entity_type': 'eater_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'a',
            'second_entity_type': 'c',
            'tvm_write': ['service1'],
            'tvm_read': ['service1'],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'i',
            'second_entity_type': 'j',
            'tvm_write': ['service1'],
            'tvm_read': ['service2'],
            'takeout_policies': [],
        },
    ],
)
async def test_get_one_pair_forbidden(
        get_all_pairs, taxi_eats_data_mappings, ticket_header,
):
    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=FIFTH_PAIR, headers=ticket_header,
    )
    assert response.status_code == 204

    response = await taxi_eats_data_mappings.post(
        '/v1/get-last-pair', json=SEARCH_PAIR_FORBIDDEN, headers=ticket_header,
    )
    assert response.status_code == 403


@pytest.mark.config(TVM_SERVICES={'service1': 2345}, TVM_ENABLED=True)
@pytest.mark.entity(['yandex_uid', 'eater_id', 'a', 'c'])
@pytest.mark.mappings(
    [
        {
            'first_entity_type': 'yandex_uid',
            'second_entity_type': 'eater_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'a',
            'second_entity_type': 'c',
            'tvm_write': ['service1'],
            'tvm_read': ['service1'],
            'takeout_policies': [],
        },
    ],
)
async def test_get_one_pair_deleted(
        get_all_pairs,
        taxi_eats_data_mappings,
        ticket_header,
        change_pair_order,
        get_cursor,
        ensure_inner,
):
    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=FIRST_PAIR, headers=ticket_header,
    )
    assert response.status_code == 204

    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=SECOND_PAIR, headers=ticket_header,
    )
    assert response.status_code == 204

    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=THIRD_PAIR, headers=ticket_header,
    )
    assert response.status_code == 204

    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=FOURTH_PAIR, headers=ticket_header,
    )
    assert response.status_code == 204

    cursor = get_cursor()
    query = (
        (
            'UPDATE eats_data_mappings.entity_pairs '
            'SET deleted_at=NOW() '
            'WHERE {0}'
        ).format(
            ' AND '.join(
                '{0}=\'{1}\''.format(key, value)
                for key, value in ensure_inner(FOURTH_PAIR).items()
            ),
        )
    )
    print(query)
    cursor.execute(query)

    response = await taxi_eats_data_mappings.post(
        '/v1/get-last-pair', json=SEARCH_PAIR, headers=ticket_header,
    )
    assert response.status_code == 200
    assert response.json() == SECOND_PAIR

    response = await taxi_eats_data_mappings.post(
        '/v1/get-last-pair', json=SEARCH_PAIR_INVERSE, headers=ticket_header,
    )
    assert response.status_code == 200
    assert response.json() == change_pair_order(THIRD_PAIR)
