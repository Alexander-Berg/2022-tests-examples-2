import bson
import pymongo
import pytest


@pytest.mark.parametrize(
    'request_items',
    [[], [{'phone': '+79991112233', 'type': 'yandex'}] * 2000],
)
async def test_bulk_invalid_request(taxi_user_api, request_items):
    response = await _persist_user_phones(taxi_user_api, request_items)
    assert response.status_code == 400


@pytest.mark.config(USER_API_PERSONAL_PHONE_ID_REQUIRED=True)
async def test_when_inserting_new_phone_duplicate_then_one_is_inserted(
        taxi_user_api, mockserver,
):
    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _mock_personal(request):
        assert request.json == {
            'items': [{'value': '+79993332211'}],
            'validate': True,
        }

        return {'items': [{'id': 'personal-id', 'value': '+79993332211'}]}

    items = [
        {'phone': '+79993332211', 'type': 'yandex'},
        {'phone': '+79993332211', 'type': 'yandex'},
    ]

    response = await _persist_user_phones(taxi_user_api, items)

    assert response.status_code == 200

    response = response.json()['items']
    assert len(response) == 1


@pytest.mark.config(USER_API_PERSONAL_PHONE_ID_REQUIRED=True)
async def test_when_inserting_existing_phone_duplicate_then_none_is_inserted(
        taxi_user_api, mockserver,
):
    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _mock_personal(request):
        assert request.json == {
            'items': [{'value': '+79993332211'}],
            'validate': True,
        }

        return {'items': [{'id': 'personal-id', 'value': '+79993332211'}]}

    items = [{'phone': '+79993332211', 'type': 'yandex'}]
    await _persist_user_phones(taxi_user_api, items)
    assert _mock_personal.times_called == 1

    response = await _persist_user_phones(taxi_user_api, items * 2)
    assert _mock_personal.times_called == 1

    assert response.status_code == 200
    response = response.json()['items']
    assert len(response) == 1


@pytest.mark.parametrize(
    'request_data',
    [
        # create new phones
        (
            {'phone': '+79991112233', 'type': 'yandex', 'id': None},
            {'phone': '+79991112234', 'type': 'yandex', 'id': None},
            {'phone': '+79991112235', 'type': 'yandex', 'id': None},
        ),
        # find existing phones
        (
            {
                'phone': '+79991234567',
                'type': 'yandex',
                'id': '539e99e1e7e5b1f5397adc5d',
            },
            {
                'phone': '+79991234568',
                'type': 'yandex',
                'id': '539e99e1e7e5b1f5398adc5a',
            },
        ),
        # find existing phone and create another one
        (
            {
                'phone': '+79991234567',
                'type': 'yandex',
                'id': '539e99e1e7e5b1f5397adc5d',
            },
            {'phone': '+79991234569', 'type': 'yandex', 'id': None},
        ),
    ],
)
@pytest.mark.config(USER_API_PERSONAL_PHONE_ID_REQUIRED=True)
async def test_bulk_store_with_personal(
        taxi_user_api, mongodb, mockserver, request_data,
):
    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _mock_personal(request):
        request_phones = {item['value'] for item in request.json['items']}
        expected_phones = {
            item['phone'] for item in request_data if item['id'] is None
        }
        assert request_phones == expected_phones
        assert request.json['validate']

        return {
            'items': [
                {'id': 'pd_' + phone, 'value': phone}
                for phone in request_phones
            ],
        }

    request_items = [
        {'phone': item['phone'], 'type': item['type']} for item in request_data
    ]

    response = await _persist_user_phones(taxi_user_api, request_items)
    assert response.status_code == 200

    for response_item in response.json()['items']:
        assert (
            response_item['personal_phone_id']
            == 'pd_' + response_item['phone']
        )
        assert response_item['type'] == 'yandex'
        assert 'phone_hash' in response_item
        assert 'phone_salt' in response_item

        for item in request_data:
            if item['id'] == response_item['id']:
                assert item['phone'] == response_item['phone']
                assert item['type'] == response_item['type']

        mongo_doc = mongodb.user_phones.find_one(
            {'_id': bson.ObjectId(response_item['id'])},
        )
        assert mongo_doc['phone'] == response_item['phone']
        assert (
            mongo_doc['personal_phone_id']
            == response_item['personal_phone_id']
        )
        assert mongo_doc.get('type', 'yandex') == response_item['type']


@pytest.mark.config(USER_API_PERSONAL_PHONE_ID_REQUIRED=False)
async def test_bulk_store_race_taxidata_1246(
        taxi_user_api, mockserver, mongodb, testpoint,
):
    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _mock_personal(request):
        return mockserver.make_response(status=500)

    @testpoint('testpoint:before_upsert')
    def _upsert(phone_infos):
        result = mongodb.user_phones.bulk_write(
            [
                pymongo.UpdateOne(
                    phone_info,
                    {
                        '$setOnInsert': phone_info,
                        '$currentDate': {'updated': True, 'created': True},
                    },
                    upsert=True,
                )
                for phone_info in phone_infos
            ],
        )
        assert bool(result.bulk_api_result['upserted'])

    response = await _persist_user_phones(
        taxi_user_api,
        [
            {'phone': '+79991234568', 'type': 'yandex'},
            {'phone': '+73334445566', 'type': 'uber'},
            {'phone': '+79991234567', 'type': 'yandex'},
        ],
        strictness=True,
    )
    assert response.status_code == 200


async def _persist_user_phones(api, items, strictness=True):
    request = {'items': items}

    if strictness is not None:
        request['validate_phones'] = strictness

    return await api.post('user_phones/bulk', json=request)
