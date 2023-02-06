import pytest

from tests_order_offers import utils


@pytest.mark.experiments3(
    name='order_offers_mongo_shards',
    consumers=['sharded-mongo-wrapper/shards'],
    is_config=True,
    clauses=[
        {
            'enabled': True,
            'predicate': {
                'init': {
                    'set': ['exp-user-id'],
                    'arg_name': 'user_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {'shards': [{'id': 1, 'weight': 1}]},
        },
        {
            'enabled': True,
            'predicate': {
                'init': {
                    'set': ['exp-phone-id'],
                    'arg_name': 'phone_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {'shards': [{'id': 2, 'weight': 1}]},
        },
    ],
    default_value={'shards': [{'id': 0, 'weight': 1}]},
)
@pytest.mark.parametrize(
    'request_body, expected_shard_id',
    [
        ({'user_id': 'user-id', 'user_phone_id': 'phone-id'}, 0),
        ({'user_id': 'user-id'}, 0),
        ({'user_id': ''}, 0),
        ({'user_id': 'exp-user-id'}, 1),
        ({'user_id': 'user-id', 'user_phone_id': 'exp-phone-id'}, 2),
    ],
)
async def test_generate_id_kwargs(
        taxi_order_offers, request_body, expected_shard_id,
):
    response = await taxi_order_offers.post(
        '/v1/generate-offer-id', json=request_body,
    )
    assert response.status_code == 200

    offer_id = response.json().get('offer_id')
    assert isinstance(offer_id, str)
    assert len(offer_id) == 32
    assert utils.get_shard_id(offer_id) == expected_shard_id


@pytest.mark.parametrize(
    'expected_shard_id',
    [
        pytest.param(
            shard_id,
            marks=[
                pytest.mark.experiments3(
                    name='order_offers_mongo_shards',
                    consumers=['sharded-mongo-wrapper/shards'],
                    is_config=True,
                    default_value={'shards': [{'id': shard_id, 'weight': 1}]},
                ),
            ],
        )
        for shard_id in range(9)
    ],
)
async def test_generate_id_shards(taxi_order_offers, expected_shard_id):
    response = await taxi_order_offers.post(
        '/v1/generate-offer-id', json={'user_id': 'user-id'},
    )
    assert response.status_code == 200

    offer_id = response.json().get('offer_id')
    assert isinstance(offer_id, str)
    assert len(offer_id) == 32
    assert utils.get_shard_id(offer_id) == expected_shard_id
