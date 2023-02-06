import pytest
import datetime

FIRST_PAIR = {
    'first_entity_type': 'a',
    'first_entity_value': 'b',
    'second_entity_type': 'c',
    'second_entity_value': 'd',
}
SECOND_PAIR = {
    'first_entity_type': 'aa',
    'first_entity_value': 'bb',
    'second_entity_type': 'cc',
    'second_entity_value': 'dd',
}
THIRD_PAIR = {
    'first_entity_type': 'a',
    'first_entity_value': 'bb',
    'second_entity_type': 'c',
    'second_entity_value': 'dd',
}
FOURTH_PAIR = {
    'first_entity_type': 'a',
    'first_entity_value': 'b',
    'second_entity_type': 'c',
    'second_entity_value': 'dd',
}


@pytest.mark.config(TVM_SERVICES={'service1': 2345}, TVM_ENABLED=True)
@pytest.mark.entity(['yandex_uid', 'eater_id', 'a', 'c', 'aa', 'cc'])
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
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'aa',
            'second_entity_type': 'cc',
            'tvm_write': ['service1'],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_insert_one_pair(
        get_all_pairs, taxi_eats_data_mappings, ticket_header,
):
    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=FIRST_PAIR, headers=ticket_header,
    )
    expected_pairs = get_all_pairs()
    assert response.status_code == 204

    # Second call of /v1/pair with the same arguments has no effect
    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=FIRST_PAIR, headers=ticket_header,
    )
    pairs = get_all_pairs()

    assert response.status_code == 204
    assert len(pairs) == len(expected_pairs)
    for pair in expected_pairs:
        assert pair in pairs


EXPECTED_PAIRS = [
    {
        'primary_entity_type': 'a',
        'primary_entity_value': 'b',
        'secondary_entity_type': 'c',
        'secondary_entity_value': 'd',
    },
    {
        'primary_entity_type': 'a',
        'primary_entity_value': 'b',
        'secondary_entity_type': 'c',
        'secondary_entity_value': 'dd',
    },
]
IMPORTANT_FIELDS = [
    'primary_entity_type',
    'primary_entity_value',
    'secondary_entity_type',
    'secondary_entity_value',
]


@pytest.mark.config(TVM_SERVICES={'service1': 2345}, TVM_ENABLED=True)
@pytest.mark.entity(['yandex_uid', 'eater_id', 'a', 'c', 'aa', 'cc'])
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
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'aa',
            'second_entity_type': 'cc',
            'tvm_write': ['service1'],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_insert_two_pairs_separate(
        get_all_pairs_noupdate, taxi_eats_data_mappings, ticket_header,
):
    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=FIRST_PAIR, headers=ticket_header,
    )
    assert response.status_code == 204

    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=FOURTH_PAIR, headers=ticket_header,
    )
    assert response.status_code == 204

    pairs = get_all_pairs_noupdate()
    assert len(pairs) == len(EXPECTED_PAIRS)
    for item in EXPECTED_PAIRS:
        assert item in pairs


@pytest.mark.config(TVM_SERVICES={'service1': 2345}, TVM_ENABLED=True)
@pytest.mark.entity(['yandex_uid', 'eater_id', 'a', 'c', 'aa', 'cc'])
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
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'aa',
            'second_entity_type': 'cc',
            'tvm_write': ['service1'],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_insert_two_pairs_together(
        get_all_pairs_noupdate, taxi_eats_data_mappings, ticket_header,
):
    response = await taxi_eats_data_mappings.post(
        '/v1/pairs',
        json={'pairs': [FIRST_PAIR, FOURTH_PAIR]},
        headers=ticket_header,
    )
    assert response.status_code == 204

    pairs = get_all_pairs_noupdate()
    assert len(pairs) == len(EXPECTED_PAIRS)
    for item in EXPECTED_PAIRS:
        assert item in pairs


@pytest.mark.config(TVM_SERVICES={'service1': 2345}, TVM_ENABLED=True)
@pytest.mark.entity(['yandex_uid', 'eater_id', 'a', 'c', 'aa', 'cc'])
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
            'first_entity_type': 'c',
            'second_entity_type': 'a',
            'tvm_write': ['service1'],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_insert_one_pair_reverse_mapping(
        get_all_pairs, taxi_eats_data_mappings, ticket_header,
):
    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=FIRST_PAIR, headers=ticket_header,
    )
    assert response.status_code == 204

    pairs = get_all_pairs()
    expected_pairs = [
        {
            'primary_entity_type': 'c',
            'primary_entity_value': 'd',
            'secondary_entity_type': 'a',
            'secondary_entity_value': 'b',
        },
    ]
    assert response.status_code == 204
    for pair in pairs:
        del pair['updated_at']
    assert len(pairs) == len(expected_pairs)
    for pair in expected_pairs:
        assert pair in pairs


@pytest.mark.config(TVM_SERVICES={'service1': 2345}, TVM_ENABLED=True)
@pytest.mark.entity(['yandex_uid', 'eater_id', 'a', 'c', 'aa', 'cc'])
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
            'first_entity_type': 'aa',
            'second_entity_type': 'c',
            'tvm_write': ['service1'],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'a',
            'second_entity_type': 'cc',
            'tvm_write': ['service1'],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_insert_one_pair_fail_validation(
        taxi_eats_data_mappings, ticket_header,
):
    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=FIRST_PAIR, headers=ticket_header,
    )
    assert response.status_code == 400

    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=SECOND_PAIR, headers=ticket_header,
    )
    assert response.status_code == 400


@pytest.mark.config(
    TVM_SERVICES={'service1': 2345, 'service2': 1111}, TVM_ENABLED=True,
)
@pytest.mark.entity(['yandex_uid', 'eater_id', 'a', 'c', 'aa', 'cc'])
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
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'aa',
            'second_entity_type': 'cc',
            'tvm_write': ['service2'],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_insert_one_pair_fail_validation_by_access(
        taxi_eats_data_mappings, ticket_header,
):
    # FIRST_PAIR fails validation access due to empty tvm_write list
    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=FIRST_PAIR, headers=ticket_header,
    )
    assert response.status_code == 403

    # SECOND_PAIR fails validation access due to service1 (ticket_header)
    # not in the tvm_write list
    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=SECOND_PAIR, headers=ticket_header,
    )
    assert response.status_code == 403


@pytest.mark.config(TVM_SERVICES={'service1': 2345}, TVM_ENABLED=True)
@pytest.mark.entity(['yandex_uid', 'eater_id', 'a', 'c', 'aa', 'cc'])
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
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'aa',
            'second_entity_type': 'cc',
            'tvm_write': ['service1'],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_insert_few_pairs(
        taxi_eats_data_mappings, get_all_pairs, ticket_header,
):
    # Call /v1/pairs with two equal pairs,
    # we should save only one of them in DB,
    # the second one should be ignored
    response = await taxi_eats_data_mappings.post(
        '/v1/pairs',
        json={'pairs': [FIRST_PAIR, SECOND_PAIR, FIRST_PAIR]},
        headers=ticket_header,
    )
    pairs = get_all_pairs()
    expected_pairs = [
        {
            'primary_entity_type': 'a',
            'primary_entity_value': 'b',
            'secondary_entity_type': 'c',
            'secondary_entity_value': 'd',
        },
        {
            'primary_entity_type': 'aa',
            'primary_entity_value': 'bb',
            'secondary_entity_type': 'cc',
            'secondary_entity_value': 'dd',
        },
    ]

    assert response.status_code == 204
    for pair in pairs:
        del pair['updated_at']
    assert len(pairs) == len(expected_pairs)
    for pair in expected_pairs:
        assert pair in pairs


@pytest.mark.config(TVM_SERVICES={'service1': 2345}, TVM_ENABLED=True)
@pytest.mark.entity(['yandex_uid', 'eater_id', 'a', 'c', 'aa', 'cc'])
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
            'first_entity_type': 'c',
            'second_entity_type': 'a',
            'tvm_write': ['service1'],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'cc',
            'second_entity_type': 'aa',
            'tvm_write': ['service1'],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_insert_few_pairs_reverse_mapping(
        taxi_eats_data_mappings, get_all_pairs, ticket_header,
):
    # Call /v1/pairs with two equal pairs,
    # we should save only one of them in DB,
    # the second one should be ignored and
    # order should be changed in DP due to
    # entity_mappings settings
    response = await taxi_eats_data_mappings.post(
        '/v1/pairs',
        json={'pairs': [FIRST_PAIR, SECOND_PAIR, FIRST_PAIR, THIRD_PAIR]},
        headers=ticket_header,
    )
    pairs = get_all_pairs()
    expected_pairs = [
        {
            'primary_entity_type': 'c',
            'primary_entity_value': 'd',
            'secondary_entity_type': 'a',
            'secondary_entity_value': 'b',
        },
        {
            'primary_entity_type': 'cc',
            'primary_entity_value': 'dd',
            'secondary_entity_type': 'aa',
            'secondary_entity_value': 'bb',
        },
        {
            'primary_entity_type': 'c',
            'primary_entity_value': 'dd',
            'secondary_entity_type': 'a',
            'secondary_entity_value': 'bb',
        },
    ]

    assert response.status_code == 204
    for pair in pairs:
        del pair['updated_at']
    assert len(pairs) == len(expected_pairs)
    for pair in expected_pairs:
        assert pair in pairs


@pytest.mark.config(TVM_SERVICES={'service1': 2345}, TVM_ENABLED=True)
@pytest.mark.entity(['yandex_uid', 'eater_id', 'a', 'c', 'aa', 'cc'])
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
            'first_entity_type': 'cc',
            'second_entity_type': 'a',
            'tvm_write': ['service1'],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'aa',
            'second_entity_type': 'c',
            'tvm_write': ['service1'],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_insert_few_pairs_fail_validation(
        taxi_eats_data_mappings, ticket_header,
):
    response = await taxi_eats_data_mappings.post(
        '/v1/pairs',
        json={'pairs': [FIRST_PAIR, SECOND_PAIR, FIRST_PAIR]},
        headers=ticket_header,
    )
    assert response.status_code == 400

    # Second call of /v1/pairs with different order of pairs,
    # result should be the same
    response = await taxi_eats_data_mappings.post(
        '/v1/pairs',
        json={'pairs': [SECOND_PAIR, SECOND_PAIR, FIRST_PAIR]},
        headers=ticket_header,
    )
    assert response.status_code == 400


@pytest.mark.config(
    TVM_SERVICES={'service1': 2345, 'service2': 1111}, TVM_ENABLED=True,
)
@pytest.mark.entity(['yandex_uid', 'eater_id', 'a', 'c', 'aa', 'cc'])
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
            'first_entity_type': 'c',
            'second_entity_type': 'a',
            'tvm_write': ['service1'],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'aa',
            'second_entity_type': 'cc',
            'tvm_write': ['service2'],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_insert_few_pairs_fail_validation_by_access(
        taxi_eats_data_mappings, ticket_header,
):
    # FIRST_PAIR passes access validation, but SECOND_PAIR fails it
    response = await taxi_eats_data_mappings.post(
        '/v1/pairs',
        json={'pairs': [FIRST_PAIR, SECOND_PAIR]},
        headers=ticket_header,
    )
    assert response.status_code == 403

    # FIRST_PAIR passes access validation, but SECOND_PAIR fails it
    response = await taxi_eats_data_mappings.post(
        '/v1/pairs',
        json={'pairs': [SECOND_PAIR, FIRST_PAIR]},
        headers=ticket_header,
    )
    assert response.status_code == 403


PAIR_WITH_DATE = {
    'first_entity_type': 'a',
    'first_entity_value': 'b',
    'second_entity_type': 'c',
    'second_entity_value': 'd',
    'created_at': '2021-12-31T10:59:59+03:00',
}
PAIR_WITH_DATE_2 = {
    'first_entity_type': 'a',
    'first_entity_value': 'bb',
    'second_entity_type': 'c',
    'second_entity_value': 'dd',
    'created_at': '2021-12-31T10:59:59+03:00',
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
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_insert_pair_with_created_at(
        get_all_pairs_with_created_at,
        taxi_eats_data_mappings,
        ticket_header,
        ensure_inner,
):
    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=PAIR_WITH_DATE, headers=ticket_header,
    )
    assert response.status_code == 204

    response = await taxi_eats_data_mappings.post(
        '/v1/pair', json=PAIR_WITH_DATE_2, headers=ticket_header,
    )
    assert response.status_code == 204

    received_pairs = get_all_pairs_with_created_at()
    expected_pairs = [
        ensure_inner(PAIR_WITH_DATE),
        ensure_inner(PAIR_WITH_DATE_2),
    ]
    for pair in expected_pairs:
        pair['created_at'] = datetime.datetime.fromisoformat(
            pair['created_at'],
        )

    assert len(expected_pairs) == len(received_pairs)
    for pair in expected_pairs:
        assert pair in received_pairs


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
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_insert_pairs_with_created_at(
        get_all_pairs_with_created_at,
        taxi_eats_data_mappings,
        ticket_header,
        ensure_inner,
):
    response = await taxi_eats_data_mappings.post(
        '/v1/pairs',
        json={'pairs': [PAIR_WITH_DATE, PAIR_WITH_DATE_2]},
        headers=ticket_header,
    )
    assert response.status_code == 204

    received_pairs = get_all_pairs_with_created_at()
    expected_pairs = [
        ensure_inner(PAIR_WITH_DATE),
        ensure_inner(PAIR_WITH_DATE_2),
    ]
    for pair in expected_pairs:
        pair['created_at'] = datetime.datetime.fromisoformat(
            pair['created_at'],
        )

    assert len(expected_pairs) == len(received_pairs)
    for pair in expected_pairs:
        assert pair in received_pairs
