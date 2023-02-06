import pytest

from tests_blocklist import utils


async def test_v1_contractor_blocks(taxi_blocklist, add_request, headers):
    add_request['kwargs']['park_id'] = '412c4d1da9964f4a8d2c8c1e54ac52bc'
    _, block_id = await utils.add_block(taxi_blocklist, add_request, headers)

    response = await taxi_blocklist.post(
        '/admin/blocklist/v1/contractor/blocks',
        json=dict(
            contractors=[
                '412c4d1da9964f4a8d2c8c1e54ac52bc'
                '_a04867abd65a45dbb20a0d7495c71012',
                '412c4d1da9964f4a8d2c8c1e54ac52bc'
                '_bbb1cefd24754294a570c81f996661f6',
                '6e717fde199842b38d5ad3d62661d1a0'
                '_70fe4f57cde24f46ae7f24971d8fa618',
                'f65ffcc85d84425dadfa321420526490'
                '_60554cd900cc45d8a5b9e0e88b13c159',
            ],
        ),
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200
    contractors = response.json()['contractors']
    assert len(contractors) == 4
    contractors.sort(key=lambda x: x['park_contractor_profile_id'])
    assert contractors == [
        dict(
            park_contractor_profile_id='412c4d1da9964f4a8d2c8c1e54ac52bc'
            '_a04867abd65a45dbb20a0d7495c71012',
            data=dict(is_blocked=False),
        ),
        dict(
            park_contractor_profile_id='412c4d1da9964f4a8d2c8c1e54ac52bc'
            '_bbb1cefd24754294a570c81f996661f6',
            data=dict(
                is_blocked=True,
                blocks=[
                    dict(
                        block_id=block_id,
                        kwargs=dict(
                            car_number='NUМВЕR_1',
                            park_id='412c4d1da9964f4a8d2c8c1e54ac52bc',
                        ),
                        mechanics='taximeter',
                        predicate_id=utils.Predicates.PARK_CAR_NUMBER,
                        status='active',
                    ),
                ],
            ),
        ),
        dict(
            park_contractor_profile_id='6e717fde199842b38d5ad3d62661d1a0'
            '_70fe4f57cde24f46ae7f24971d8fa618',
            data=dict(is_blocked=False),
        ),
        dict(
            park_contractor_profile_id='f65ffcc85d84425dadfa321420526490'
            '_60554cd900cc45d8a5b9e0e88b13c159',
        ),
    ]


@pytest.mark.translations(
    taximeter_backend_driver_messages=dict(
        block_key_1=dict(ru='Причина блокировки 1'),
    ),
)
async def test_v1_contractor_blocks_history(
        taxi_blocklist, add_request, headers,
):
    add_request['kwargs'] = dict(
        park_id='412c4d1da9964f4a8d2c8c1e54ac52bc', car_number='number_1',
    )
    _, park_car_block_id = await utils.add_block(
        taxi_blocklist, add_request, headers,
    )

    add_request['kwargs'] = dict(car_number='number_1')
    add_request['predicate_id'] = utils.Predicates.CAR_NUMBER
    _, car_block_id = await utils.add_block(
        taxi_blocklist, add_request, headers,
    )

    assert park_car_block_id != car_block_id
    await utils.delete_block(
        taxi_blocklist,
        dict(
            block=dict(block_id=park_car_block_id, comment='test'),
            predicate_id=utils.Predicates.PARK_CAR_NUMBER,
        ),
        headers,
    )

    response = await taxi_blocklist.post(
        '/admin/blocklist/v1/contractor/blocks/history',
        json=dict(
            park_contractor_profile_id='412c4d1da9964f4a8d2c8c1e54ac52bc'
            '_bbb1cefd24754294a570c81f996661f6',
            limit=1000,
        ),
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200
    assert response.json()['blocks'] == {
        car_block_id: {
            'block_id': car_block_id,
            'kwargs': {'car_number': 'NUМВЕR_1'},
            'mechanics': 'taximeter',
            'predicate_id': utils.Predicates.CAR_NUMBER,
            'status': 'active',
            'text': 'Причина блокировки 1',
            'designation': 'car_number',
        },
        park_car_block_id: {
            'block_id': park_car_block_id,
            'kwargs': {
                'car_number': 'NUМВЕR_1',
                'park_id': '412c4d1da9964f4a8d2c8c1e54ac52bc',
            },
            'mechanics': 'taximeter',
            'predicate_id': utils.Predicates.PARK_CAR_NUMBER,
            'status': 'inactive',
            'text': 'Причина блокировки 1',
            'designation': 'park_car_number',
        },
    }

    events = response.json()['events']
    for event in events:
        event.pop('created')

    assert events == [
        {
            'action': 'remove',
            'block_id': park_car_block_id,
            'comment': 'test',
            'entity_id': '777',
            'entity_name': 'jorka',
            'entity_type': 'support',
        },
        {
            'action': 'add',
            'block_id': car_block_id,
            'comment': 'comment',
            'entity_id': '777',
            'entity_name': 'jorka',
            'entity_type': 'support',
        },
        {
            'action': 'add',
            'block_id': park_car_block_id,
            'comment': 'comment',
            'entity_id': '777',
            'entity_name': 'jorka',
            'entity_type': 'support',
        },
    ]
