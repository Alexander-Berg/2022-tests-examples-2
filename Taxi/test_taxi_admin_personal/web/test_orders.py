import collections
import itertools
import json
import uuid

import aiohttp
import bson
import pytest

from taxi_admin_personal.internal import orders
from test_taxi_admin_personal import utils


async def test_search_by_pd_no_parameters(web_app_client):
    response = await utils.make_post_request(
        web_app_client, '/order/search/', data={},
    )
    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'EMPTY_BODY'


async def test_search_by_phone(
        web_app_client, mock_countries, mockserver, patch,
):
    @patch('taxi.clients.personal.PersonalApiClient.find')
    # pylint: disable=unused-variable
    async def find(*args, **kwargs):
        return {'id': '123123123123123123', 'phone': '+79250325273'}

    @mockserver.json_handler(
        '/user_api-api/user_phones/by_personal/retrieve_bulk',
    )
    # pylint: disable=unused-variable
    async def get_phones_info_by_personal(*args, **kwargs):
        items = [
            {'id': phone_id}
            for phone_id in [
                '539eb65be7e5b1f53980dfaa',
                '539eb65be7e5b1f53980dfa9',
            ]
        ]
        return {'items': items}

    response = await utils.post_ok_json_response(
        '/order/search/', {'user_phone': '+79250325273'}, web_app_client,
    )

    assert set(response.keys()) == {'users'}
    assert set(user['phone_id'] for user in response['users']) == {
        '539eb65be7e5b1f53980dfaa',
        '539eb65be7e5b1f53980dfa9',
    }


@pytest.mark.config(
    API_OVER_DATA_WORK_MODE={'__default__': {'__default__': 'newway'}},
)
async def test_search_by_driver_license(web_app_client):
    response = await utils.post_ok_json_response(
        '/order/search/', {'driver_license': '00000000000'}, web_app_client,
    )

    assert set(response.keys()) == {'drivers'}
    assert set(driver['id'] for driver in response['drivers']) == {
        '100112_ca3a2377daf2440097e2b9ec9749ca28',
        '100500_794513c94b864ad7ad1088063ec468e1',
        '100900_3580371a802b4c5b911ff3e0c0196244',
        '643753730335_b268d6727a7840ed9ca6dee4f5919c12',
    }


@pytest.mark.config(
    API_OVER_DATA_WORK_MODE={'__default__': {'__default__': 'newway'}},
)
async def test_search_by_all_pd(
        web_app_client, mockserver, patch, mock_countries,
):
    @patch('taxi.clients.personal.PersonalApiClient.find')
    # pylint: disable=unused-variable
    async def find(*args, **kwargs):
        return {'id': '123123123123123123', 'phone': '+79250325273'}

    @mockserver.json_handler(
        '/user_api-api/user_phones/by_personal/retrieve_bulk',
    )
    # pylint: disable=unused-variable
    async def get_phones_info_by_personal(*args, **kwargs):
        items = [
            {'id': phone_id}
            for phone_id in [
                '539eb65be7e5b1f53980dfaa',
                '539eb65be7e5b1f53980dfa9',
            ]
        ]
        return {'items': items}

    response = await utils.post_ok_json_response(
        '/order/search/',
        {'driver_license': '00000000000', 'user_phone': '+79250325273'},
        web_app_client,
    )

    assert set(response.keys()) == {'users', 'drivers'}

    assert set(user['phone_id'] for user in response['users']) == {
        '539eb65be7e5b1f53980dfaa',
        '539eb65be7e5b1f53980dfa9',
    }

    assert set(driver['id'] for driver in response['drivers']) == {
        '100112_ca3a2377daf2440097e2b9ec9749ca28',
        '100500_794513c94b864ad7ad1088063ec468e1',
        '100900_3580371a802b4c5b911ff3e0c0196244',
        '643753730335_b268d6727a7840ed9ca6dee4f5919c12',
    }


async def test_get_pd_no_order_id(web_app_client):
    response = await utils.make_post_request(
        web_app_client, '/order/retrieve/', data={},
    )
    assert response.status == 400


# pylint: disable=too-many-arguments
@pytest.mark.config(
    API_OVER_DATA_WORK_MODE={'__default__': {'__default__': 'newway'}},
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
    TVM_RULES=[{'src': 'taxi-admin-personal', 'dst': 'personal'}],
)
@pytest.mark.parametrize(
    (
        'user_id, user_phone_id, driver_id, driver_license, '
        'request_extra_user_phone_id, with_permissions, candidates, expected'
    ),
    [
        # tests that driver_license and user phone are, indeed,
        # taken from the archive API
        # response, not the db
        (
            '6e409dba84794165a34ac72ae27829ac',
            '539eb65be7e5b1f53980dfa8',
            '100500_3625641848644387a263e78b2c3a7a5c',
            'AB',
            'aaaaaaaae7e5b1f53980dfaa',
            ['view_driver_licenses', 'view_user_phones'],
            [
                {
                    'driver_license': '1234324213',
                    'phone': '+79000000000',
                    'driver_id': 'clid_uuid',
                },
            ],
            {
                'user': {
                    'phone': '+79000000000',
                    'order_phone': '+79000000000',
                },
                'driver': {'driver_license': 'AB'},
                'other_user': {},
                'other_performers': [
                    {'uuid': 'clid_uuid', 'driver_license': '1234324213'},
                ],
                'delivery': {
                    'destinations': [{}, {'phone': '79099575227'}, {}],
                    'source': {},
                },
            },
        ),
        # tests that missing data is not returned
        # but the top-level keys are still present
        (
            '2',
            'aaaaaaaae7e5b1f53980dfaa',
            '100500_13625641848644387a263e78b2c3a7a5c',
            None,
            'aaaaaaaaeaaab1f53980dfaa',
            [
                'view_driver_licenses',
                'view_driver_phones',
                'view_user_emails',
                'view_user_phones',
            ],
            [
                {
                    'driver_license': '1234324213',
                    'phone': '+78003000600',
                    'driver_id': 'clid_uuid',
                },
            ],
            {
                'user': {},
                'driver': {},
                'other_user': {},
                'other_performers': [
                    {
                        'uuid': 'clid_uuid',
                        'driver_license': '1234324213',
                        'phone': '+78003000600',
                    },
                ],
                'delivery': {
                    'destinations': [{}, {'phone': '79099575227'}, {}],
                    'source': {},
                },
            },
        ),
        # test with full data
        (
            '6e409dba84794165a34ac72ae27829ac',
            '539eb65be7e5b1f53980dfa8',
            '100500_3625641848644387a263e78b2c3a7a5c',
            'ABC',
            '539eb65be7e5b1f53980dfaa',
            [
                'view_driver_licenses',
                'view_driver_phones',
                'view_user_emails',
                'view_user_phones',
            ],
            [
                {
                    'driver_license': '1234324213',
                    'phone': '+78003000600',
                    'driver_id': 'clid_uuid',
                },
            ],
            {
                'user': {
                    'email': 'email1@test.com',
                    'email_status': 'confirmed',
                    'phone': '+79000000000',
                    'order_phone': '+79000000000',
                },
                'driver': {'driver_license': 'ABC', 'phone': '+79000000000'},
                'other_user': {'phone': '+79250325273'},
                'other_performers': [
                    {
                        'uuid': 'clid_uuid',
                        'driver_license': '1234324213',
                        'phone': '+78003000600',
                    },
                ],
                'delivery': {
                    'destinations': [{}, {'phone': '79099575227'}, {}],
                    'source': {},
                },
            },
        ),
    ],
)
async def test_get_pd(
        web_app_client,
        mockserver,
        order_archive_mock,
        user_id,
        user_phone_id,
        driver_id,
        driver_license,
        request_extra_user_phone_id,
        with_permissions,
        candidates,
        expected,
        mock_countries,
        load_json,
):
    def make_point(with_phone_id=None):
        return {'extra_data': {'contact_phone_id': with_phone_id}}

    personal = 'personal_'
    phone_id_source = None
    phone_id_destinations_1 = None
    phone_id_destinations_2 = 'phone_id_1'
    phone_id_destinations_3 = 'phone_id_2'

    clid, _uuid = driver_id.split('_')
    order_archive_mock.set_order_proc(
        {
            '_id': '1',
            'order': {
                'user_id': user_id,
                'user_phone_id': user_phone_id,
                'request': {
                    'extra_user_phone_id': bson.ObjectId(
                        request_extra_user_phone_id,
                    ),
                    'source': make_point(phone_id_source),
                    'destinations': [
                        make_point(phone_id_destinations_1),
                        make_point(phone_id_destinations_2),
                        make_point(phone_id_destinations_3),
                    ],
                },
                'performer': {
                    'clid': clid,
                    'uuid': _uuid,
                    'driver_license': driver_license,
                    'tariff': {'class': 'express'},
                },
            },
            'candidates': candidates,
        },
    )

    @mockserver.json_handler('/user_api-api/user_phones/get_bulk')
    # pylint: disable=unused-variable
    async def get_bulk_user_phones(request, *args, **kwargs):
        assert request.json == {
            'ids': [phone_id_destinations_2, phone_id_destinations_3],
            'primary_replica': False,
        }

        items = [
            {
                'id': phone_id_destinations_2,
                'personal_phone_id': personal + phone_id_destinations_2,
            },
            {
                'id': phone_id_destinations_3,
                'personal_phone_id': personal + phone_id_destinations_3,
            },
        ]
        return {'items': items}

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    # pylint: disable=unused-variable
    async def phones_bulk_retrieve(request):
        if request.json == {
                'items': [
                    {'id': personal + phone_id_destinations_2},
                    {'id': personal + phone_id_destinations_3},
                ],
        }:
            return {
                'items': [
                    {
                        'id': personal + phone_id_destinations_2,
                        'value': '79099575227',
                    },
                ],
            }

        return {
            'items': list(
                map(
                    lambda x: {
                        'id': x['id'],
                        'value': x['id'].replace('id_', ''),
                    },
                    request.json['items'],
                ),
            ),
        }

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    # pylint: disable=unused-variable
    async def retrieve_phone(request):
        user_phones_map = {
            '539eb65be7e5b1f53980dfa8': '+79000000000',
            '539eb65be7e5b1f53980dfa9': '+79250325273',
            '539eb65be7e5b1f53980dfaa': '+79250325273',
        }
        request_id = request.json.get('id')
        phone = user_phones_map.get(request_id)
        return {'id': request_id, 'value': phone}

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    # pylint: disable=unused-variable
    async def retrieve_email(request):
        personal_email_id = request.json['id']
        emails_doc = load_json('personal_emails.json')
        for doc in emails_doc:
            if doc['id'] == personal_email_id:
                return doc
        return aiohttp.web.Response(text='NotFound', status=404)

    @mockserver.json_handler('/user_api-api/user_phones/get')
    # pylint: disable=unused-variable
    async def get_user_phone(request, *args, **kwargs):
        phone_id = request.json['id']
        user_phones = load_json('user_phones.json')
        for doc in user_phones:
            if doc['id'] == phone_id:
                return doc
        return aiohttp.web.Response(text='NotFound', status=404)

    @mockserver.json_handler('/user_api-api/user_emails/get')
    # pylint: disable=unused-variable
    async def get_user_emails(request, *args, **kwargs):
        data = request.json
        email_docs = load_json('user_emails.json')
        phone_ids = data.get('phone_ids', [])
        yandex_uids = data.get('yandex_uids', [])

        items = []
        for doc in email_docs:
            if doc['yandex_uid'] in yandex_uids or (
                    doc['phone_id'] in phone_ids
            ):
                items.append(doc)
        return {'items': items}

    @mockserver.json_handler('/user_api-api/users/get')
    # pylint: disable=unused-variable
    async def get_user(request, *args, **kwargs):
        user_data = {'id': user_id, 'phone_id': user_phone_id}
        return user_data

    with utils.has_permissions(with_permissions):
        response = await utils.post_ok_json_response(
            '/order/retrieve/', {'id': '1'}, web_app_client,
        )
        assert response == expected


@pytest.mark.config(
    API_OVER_DATA_WORK_MODE={'__default__': {'__default__': 'newway'}},
    TVM_RULES=[{'src': 'taxi-admin-personal', 'dst': 'personal'}],
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
)
async def test_get_pd_field_permissions(
        web_app_client,
        mockserver,
        order_archive_mock,
        mock_countries,
        load_json,
        mock_pd_phones,
):
    order_archive_mock.set_order_proc(
        {
            '_id': '1',
            'order': {
                'user_id': '6e409dba84794165a34ac72ae27829ac',
                'user_phone_id': '539eb65be7e5b1f53980df10',
                'request': {
                    'extra_user_phone_id': bson.ObjectId(
                        '539eb65be7e5b1f53980dfa9',
                    ),
                },
                'performer': {
                    'clid': '100500',
                    'uuid': '3625641848644387a263e78b2c3a7a5c',
                    'driver_license': 'ABCD',
                },
            },
            'candidates': [
                {
                    'driver_license': '1234324213',
                    'phone': '+78003000600',
                    'driver_id': 'clid_uuid',
                },
            ],
        },
    )

    @mockserver.json_handler('/personal/v1/phones/find')
    # pylint: disable=unused-variable
    async def find(*args, **kwargs):
        return {'id': '539eb65be7e5b1f53980dfa8', 'value': 'phone'}

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    # pylint: disable=unused-variable
    async def phone_retrieve(request):
        user_phones_map = {
            '539eb65be7e5b1f53980dfa8': '+79000000000',
            '539eb65be7e5b1f53980dfa9': '+79250325273',
            '539eb65be7e5b1f53980df10': '+79250325299',
            '539eb65be7e5b1f53980dfaa': '+79250325273',
        }
        request_id = request.json['id']
        phone = user_phones_map.get(request_id)
        return {'id': request_id, 'value': phone}

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    # pylint: disable=unused-variable
    async def email_retrieve(request):
        request_id = request.json['id']
        return {'id': request_id, 'value': 'email'}

    @mockserver.json_handler('/user_api-api/user_emails/get')
    # pylint: disable=unused-variable
    async def get_user_emails(request):
        items = []
        phone_ids = request.json['phone_ids']
        for phone_id in phone_ids:
            items.append(
                {
                    'personal_email_id': phone_id,
                    '_id': uuid.uuid4().hex,
                    'confirmed': True,
                },
            )
        return {'items': items}

    @mockserver.json_handler('/user_api-api/user_phones/get')
    # pylint: disable=unused-variable
    async def get_user_phone(request):
        phone_id = request.json['id']
        docs = load_json('user_phones.json')
        doc = docs[0]
        doc['personal_phone_id'] = phone_id
        return doc

    @mockserver.json_handler('/user_api-api/users/get')
    # pylint: disable=unused-variable
    async def get_user(request, *args, **kwargs):
        user_data = {
            'id': '6e409dba84794165a34ac72ae27829ac',
            'phone_id': '539eb65be7e5b1f53980dfa8',
        }
        return user_data

    fields_by_permissions = collections.defaultdict(set)
    for _, subsection in orders.FIELD_PERMISSIONS.items():
        for field, permission in subsection.items():
            fields_by_permissions[permission].add(field)

    for permissions_num in range(0, len(fields_by_permissions)):
        for with_permissions in itertools.combinations(
                fields_by_permissions.keys(), permissions_num,
        ):
            with utils.has_permissions(with_permissions):
                response = await utils.post_ok_json_response(
                    '/order/retrieve/', {'id': '1'}, web_app_client,
                )

            for subsection_key, subsection in orders.FIELD_PERMISSIONS.items():
                assert_response(
                    subsection_key, subsection, with_permissions, response,
                )

    assert mock_pd_phones.bulk_retrieve_count == 15


def assert_response(subsection_key, subsection, with_permissions, response):
    if subsection_key == 'delivery':
        return
    for field, permission in subsection.items():
        if field == 'deptrans_id':
            continue
        if permission in with_permissions:
            if subsection_key == 'other_performers':
                assert field in response[subsection_key][0]
            else:
                assert field in response[subsection_key]
        else:
            assert field not in response.get(subsection_key, {})


async def test_get_pd_empty_order(order_archive_mock, web_app_client):
    order_archive_mock.set_order_proc({'_id': '1'})

    with utils.has_permissions(
            [
                'view_driver_licenses',
                'view_driver_phones',
                'view_user_emails',
                'view_user_phones',
            ],
    ):
        response = await utils.post_ok_json_response(
            '/order/retrieve/', {'id': '1'}, web_app_client,
        )

    assert response == {
        'delivery': {},
        'user': {},
        'driver': {},
        'other_user': {},
        'other_performers': [],
    }


@pytest.mark.parametrize(
    'user, driver, other_performers, other_user, expected',
    [
        (
            {
                'user_id': 'test_user_id',
                'user_phone_id': '539eb65be7e5b1f53980dfa0',
            },
            {
                'driver_id': 'test_driver_id',
                'driver_phone_id': '539eb65be7e5b1f53980dfa1',
                'driver_license': 'ABCD',
                'clid': '100666',
                'uuid': '3625641848644387a263e78b2c3a7a5c',
            },
            [
                {
                    'driver_license': 'other_performer_lic_1',
                    'phone': '+78003000600',
                    'driver_id': 'clid_uuid_1',
                },
                {
                    'driver_license': 'other_performer_lic_2',
                    'phone': '+78003000666',
                    'driver_id': 'clid_uuid_2',
                },
            ],
            {'other_user_phone_id': bson.ObjectId('9999b65be7e5999939809999')},
            {
                'user': {
                    'personal_phone_id': '5000005be000b1f00000dfa0',
                    'personal_email_id': '500eee5be7eee1eee980eee0',
                },
                'other_user': {
                    'personal_phone_id': '5bbbbb5be000b1fbbbbbdfa0',
                },
                'driver': {
                    'personal_license_id': '2222e78b91272f03f6112222',
                    'personal_phone_id': '1111e78b91272f03f6111111',
                },
                'other_performers': [
                    {
                        'personal_license_id': '3333e78b91272f03f611333',
                        'personal_phone_id': '5555e78b91272f03f6115555',
                        'uuid': 'clid_uuid_1',
                    },
                    {
                        'personal_license_id': '4444e78b91272f03f6114444',
                        'personal_phone_id': '6666e78b91272f03f6116666',
                        'uuid': 'clid_uuid_2',
                    },
                ],
            },
        ),
        # users.phones and driver.license is None
        (
            {
                'user_id': 'test_user_id',
                'user_phone_id': '539eb65be7e5b1f53980dfa1',
            },
            {
                'driver_id': 'test_driver_id',
                'driver_phone_id': '539eb65be7e5b1f53980dfa1',
                'driver_license': 'ABCDE',
                'clid': '100666',
                'uuid': '3625641848644387a263e78b2c3a7a5c',
            },
            [
                {
                    'driver_license': 'other_performer_lic_none',
                    'phone': '+78003000600',
                    'driver_id': 'clid_uuid_1',
                },
                {
                    'driver_license': 'other_performer_lic_none',
                    'phone': '+78003000666',
                    'driver_id': 'clid_uuid_2',
                },
            ],
            {'other_user_phone_id': bson.ObjectId('9999b65be7e5999939809990')},
            {
                'user': {'personal_email_id': '500eee5be7eee1eee980eee1'},
                'other_user': {},
                'driver': {'personal_phone_id': '1111e78b91272f03f6111111'},
                'other_performers': [
                    {
                        'personal_phone_id': '5555e78b91272f03f6115555',
                        'uuid': 'clid_uuid_1',
                    },
                    {
                        'personal_phone_id': '6666e78b91272f03f6116666',
                        'uuid': 'clid_uuid_2',
                    },
                ],
            },
        ),
        # users.emails None
        (
            {
                'user_id': 'test_user_id',
                'user_phone_id': '539eb65be7e5b1f53980dfa2',
            },
            {
                'driver_id': 'test_driver_id',
                'driver_phone_id': '539eb65be7e5b1f53980dfa2',
                'driver_license': 'ABCD',
                'clid': '100666',
                'uuid': '3625641848644387a263e78b2c3a7a55',
            },
            [
                {
                    'driver_license': 'other_performer_lic_1',
                    'phone': '+78003999999',
                    'driver_id': 'clid_uuid_1',
                },
                {
                    'driver_license': 'other_performer_lic_2',
                    'phone': '+78003999999',
                    'driver_id': 'clid_uuid_2',
                },
            ],
            {'other_user_phone_id': bson.ObjectId('9999b65be7e5999939809999')},
            {
                'user': {'personal_phone_id': '5000005be000b1f00000dfaa'},
                'other_user': {
                    'personal_phone_id': '5bbbbb5be000b1fbbbbbdfa0',
                },
                'driver': {
                    'personal_license_id': '2222e78b91272f03f6112222',
                    'personal_phone_id': '9999e78b91272f03f6119999',
                },
                'other_performers': [
                    {
                        'personal_license_id': '3333e78b91272f03f611333',
                        'uuid': 'clid_uuid_1',
                        'personal_phone_id': '9999e78b91272f03f6119999',
                    },
                    {
                        'personal_license_id': '4444e78b91272f03f6114444',
                        'uuid': 'clid_uuid_2',
                        'personal_phone_id': '9999e78b91272f03f6119999',
                    },
                ],
            },
        ),
        # other_performers has phone, others none
        (
            {
                'user_id': 'test_user_id',
                'user_phone_id': '539eb65be7e5b1f539800000',
            },
            {
                'driver_id': 'test_driver_id',
                'driver_phone_id': '539eb65be7e5b1f539800000',
                'driver_license': 'none',
                'clid': 'none',
                'uuid': '3625641848644387a263e78b2c3a0000',
            },
            [
                {'phone': '+78003999999', 'driver_id': 'clid_uuid_1'},
                {'phone': '+78003999999', 'driver_id': 'clid_uuid_2'},
            ],
            {'other_user_phone_id': bson.ObjectId('9999b65be7e5999939808888')},
            {
                'user': {},
                'other_user': {},
                'driver': {},
                'other_performers': [
                    {
                        'uuid': 'clid_uuid_1',
                        'personal_phone_id': '9999e78b91272f03f6119999',
                    },
                    {
                        'uuid': 'clid_uuid_2',
                        'personal_phone_id': '9999e78b91272f03f6119999',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.config(
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
    TVM_RULES=[{'src': 'taxi-admin-personal', 'dst': 'personal'}],
)
async def test_order_retrieve_personal_id(
        web_app_client,
        mockserver,
        order_archive_mock,
        mock_countries,
        user,
        driver,
        other_performers,
        other_user,
        expected,
        mock_pd_phones,
):
    order_archive_mock.set_order_proc(
        {
            '_id': '1',
            'order': {
                'user_id': user['user_id'],
                'request': {
                    'extra_user_phone_id': other_user['other_user_phone_id'],
                },
                'performer': {
                    'clid': driver['clid'],
                    'uuid': driver['uuid'],
                    'driver_license': driver['driver_license'],
                },
            },
            'candidates': other_performers,
        },
    )

    @mockserver.json_handler('/user_api-api/users/get')
    # pylint: disable=unused-variable
    async def get_user(request, *args, **kwargs):
        user_data = {'id': user['user_id'], 'phone_id': user['user_phone_id']}
        return user_data

    @mockserver.json_handler('/user_api-api/user_emails/get')
    # pylint: disable=unused-variable
    async def get_user_emails(request, *args, **kwargs):
        data = json.loads(request.get_data())
        items = []
        data_map = {
            '539eb65be7e5b1f53980dfa0': '500eee5be7eee1eee980eee0',  # user
            '539eb65be7e5b1f53980dfa1': '500eee5be7eee1eee980eee1',  # driver
        }
        for phone_id in data['phone_ids']:
            if data_map.get(phone_id):
                items.append(
                    {
                        'personal_email_id': data_map[phone_id],
                        '_id': uuid.uuid4().hex,
                        'confirmed': True,
                    },
                )
        return {'items': items}

    @mockserver.json_handler('/user_api-api/user_phones/get')
    # pylint: disable=unused-variable
    async def get_user_phone(request, *args, **kwargs):
        data = json.loads(request.get_data())
        data_map = {
            '539eb65be7e5b1f53980dfa0': '5000005be000b1f00000dfa0',  # user
            '539eb65be7e5b1f53980dfa2': '5000005be000b1f00000dfaa',  # user
            '9999b65be7e5999939809999': '5bbbbb5be000b1fbbbbbdfa0',  # other
        }
        personal_phone_id = data_map.get(data['id'])
        doc = {
            'id': '5d4be78b91272f03f611fe7e',
            'phone': '+79000000000',
            'type': 'test',
            'stat': 'stat',
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
            'personal_phone_id': personal_phone_id,
        }
        return doc

    @mockserver.json_handler('/personal/v1/phones/find')
    # pylint: disable=unused-variable
    async def phones_find(request):
        data = request.json
        phone = data['value']
        map_data = {
            '+79000000999': '1111e78b91272f03f6111111',  # driver phone
            '+78003000600': '5555e78b91272f03f6115555',  # other_performer_1
            '+78003000666': '6666e78b91272f03f6116666',  # other_performer_2
            '+78003999999': '9999e78b91272f03f6119999',  # other_performer_2
        }
        if map_data.get(phone):
            return {'id': map_data[phone], 'value': phone}
        return aiohttp.web.Response(text='NotFound', status=404)

    @mockserver.json_handler('/personal/v1/driver_licenses/find')
    # pylint: disable=unused-variable
    async def driver_licenses_find(request):
        data = request.json
        driver_license = data['value']
        map_data = {
            'ABCD': '2222e78b91272f03f6112222',  # driver license
            'other_performer_lic_1': '3333e78b91272f03f611333',
            'other_performer_lic_2': '4444e78b91272f03f6114444',
        }
        if map_data.get(driver_license):
            return {'id': map_data[driver_license], 'value': driver_license}
        return aiohttp.web.Response(text='NotFound', status=404)

    response = await utils.post_ok_json_response(
        '/order/retrieve_personal_ids/', {'id': '1'}, web_app_client,
    )
    assert response == expected

    assert mock_pd_phones.bulk_retrieve_count == (
        1 if expected['driver'] != {} else 0
    )


@pytest.mark.parametrize('deanonymize', [False, True])
async def test_order_retrieve_personal_id_anonymization(
        web_app_client,
        mockserver,
        order_archive_mock,
        mock_countries,
        mock_pd_phones,
        deanonymize,
):
    order_archive_mock.set_order_proc([])

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-order',
    )
    def _mock_order_core(request):
        return mockserver.make_response(
            status=404,
            json={'code': 'no_such_order', 'message': 'no_such_order'},
        )

    await utils.make_post_request(
        web_app_client,
        '/order/retrieve_personal_ids/',
        {'id': '1', 'deanonymize': deanonymize},
    )
    if deanonymize:
        assert _mock_order_core.has_calls
        assert not order_archive_mock.order_proc_retrieve.has_calls
    else:
        assert order_archive_mock.order_proc_retrieve.has_calls
        assert not _mock_order_core.has_calls
