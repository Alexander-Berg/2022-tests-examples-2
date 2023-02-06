from aiohttp import web
import pytest

from drive_integration_worker.generated.cron import run_cron


@pytest.fixture(name='secdist_with_apikey')
def _secdist_with_apikey(simple_secdist):
    simple_secdist['DRIVE_INTEGRATION_APIKEY_FOR_DRIVE'] = 'apikeyvalue'
    return simple_secdist


@pytest.mark.now('2020-01-12T20:42:46+00:00')
@pytest.mark.config(DRIVE_INTEGRATION_PARKS=['park_id1'])
async def test_sync(
        mock_ext_carsharing,
        mock_driver_profiles,
        mock_personal,
        load,
        cron_context,
        secdist_with_apikey,
):
    error_response_stub = load('error_response.json')

    @mock_driver_profiles('/v1/driver/profiles/retrieve_by_park_id')
    async def _driver_profiles(request):
        assert request.json == {
            'park_id_in_set': ['park_id1'],
            'projection': [
                'data.park_id',
                'data.uuid',
                'data.providers',
                'data.work_status',
                'data.full_name.first_name',
                'data.full_name.middle_name',
                'data.full_name.last_name',
                'data.license.pd_id',
                'data.license.country',
                'data.license.is_verified',
            ],
        }
        response_datas = [
            # Should link to Drive
            {
                'park_id': 'park_id1',
                'uuid': 'did1',
                'providers': ['yandex'],
                'work_status': 'working',
                'full_name': {
                    'first_name': 'FN1',
                    'middle_name': 'MN1',
                    'last_name': 'LN1',
                },
                'license': {
                    'pd_id': 'pd1',
                    'country': 'rus',
                    'is_verified': True,
                },
            },
            # Already linked to Drive
            {
                'park_id': 'park_id1',
                'uuid': 'did2',
                'providers': ['yandex'],
                'work_status': 'working',
                'full_name': {
                    'first_name': 'FN2',
                    'middle_name': 'MN2',
                    'last_name': 'LN2',
                },
                'license': {
                    'pd_id': 'pd2',
                    'country': 'rus',
                    'is_verified': True,
                },
            },
            # Should unlink from Drive
            {
                'park_id': 'park_id1',
                'uuid': 'did3',
                'providers': ['park'],
                'work_status': 'working',
                'full_name': {
                    'first_name': 'FN3',
                    'middle_name': 'MN3',
                    'last_name': 'LN3',
                },
                'license': {
                    'pd_id': 'pd3',
                    'country': 'rus',
                    'is_verified': True,
                },
            },
            {
                'park_id': 'park_id1',
                'uuid': 'did4',
                'providers': ['yandex'],
                'work_status': 'fired',
                'full_name': {
                    'first_name': 'FN4',
                    'middle_name': 'MN4',
                    'last_name': 'LN4',
                },
                'license': {
                    'pd_id': 'pd4',
                    'country': 'rus',
                    'is_verified': True,
                },
            },
            # Not linked to Drive
            {
                'park_id': 'park_id1',
                'uuid': 'did5',
                'providers': [],
                'work_status': 'fired',
                'full_name': {
                    'first_name': 'FN5',
                    'middle_name': 'MN5',
                    'last_name': 'LN5',
                },
                'license': {
                    'pd_id': 'pd5',
                    'country': 'rus',
                    'is_verified': True,
                },
            },
            # No license available
            {
                'park_id': 'park_id1',
                'uuid': 'did6',
                'providers': ['yandex'],
                'work_status': 'working',
                'full_name': {
                    'first_name': 'FN6',
                    'middle_name': 'MN6',
                    'last_name': 'LN6',
                },
                'license': {
                    'pd_id': 'pd6',
                    'country': 'rus',
                    'is_verified': True,
                },
            },
            # Missing in drive, to add
            {
                'park_id': 'park_id1',
                'uuid': 'did7',
                'providers': ['yandex'],
                'work_status': 'working',
                'full_name': {
                    'first_name': 'FN7',
                    'middle_name': 'MN7',
                    'last_name': 'LN7',
                },
                'license': {
                    'pd_id': 'pd7',
                    'country': 'rus',
                    'is_verified': True,
                },
            },
            # Missing in drive, to remove
            {
                'park_id': 'park_id1',
                'uuid': 'did8',
                'providers': [],
                'work_status': 'fired',
                'full_name': {
                    'first_name': 'FN8',
                    'middle_name': 'MN8',
                    'last_name': 'LN8',
                },
                'license': {
                    'pd_id': 'pd8',
                    'country': 'rus',
                    'is_verified': True,
                },
            },
            # Different middle names, leading and trailing spaces
            {
                'park_id': 'park_id1',
                'uuid': 'did9',
                'providers': ['yandex'],
                'work_status': 'not_working',
                'full_name': {
                    'first_name': ' FN9  ',
                    'middle_name': '',
                    'last_name': '  LN9 ',
                },
                'license': {
                    'pd_id': 'pd9',
                    'country': 'rus',
                    'is_verified': True,
                },
            },
            # Missing driver name
            {
                'park_id': 'park_id1',
                'uuid': 'did10',
                'providers': ['yandex'],
                'work_status': 'working',
                'full_name': {'middle_name': '', 'last_name': '   '},
                'license': {
                    'pd_id': 'pd10',
                    'country': 'rus',
                    'is_verified': True,
                },
            },
            # fields property is null
            {
                'park_id': 'park_id1',
                'uuid': 'did11',
                'providers': ['yandex'],
                'work_status': 'working',
                'full_name': {
                    'first_name': ' FN11  ',
                    'middle_name': '',
                    'last_name': '  LN11',
                },
                'license': {
                    'pd_id': 'pd11',
                    'country': 'rus',
                    'is_verified': True,
                },
            },
            # fields property is null
            {
                'park_id': 'park_id1',
                'uuid': 'did12',
                'providers': ['yandex'],
                'work_status': 'working',
                'full_name': {
                    'first_name': ' FN12  ',
                    'middle_name': '',
                    'last_name': '  LN12',
                },
                'license': {
                    'pd_id': 'pd12',
                    'country': 'rus',
                    'is_verified': True,
                },
            },
        ]
        return {
            'profiles_by_park_id': [
                {
                    'park_id': 'park_id1',
                    'profiles': [
                        {
                            'park_driver_profile_id': (
                                data['park_id'] + data['uuid']
                            ),
                            'data': data,
                        }
                        for data in response_datas
                    ],
                },
            ],
        }

    @mock_personal('/v1/driver_licenses/bulk_retrieve')
    async def _personal_licenses(request):
        request.json['items'].sort(key=lambda x: x['id'])
        assert request.json == {
            'items': [
                {'id': 'pd1'},
                {'id': 'pd10'},
                {'id': 'pd11'},
                {'id': 'pd12'},
                {'id': 'pd2'},
                {'id': 'pd3'},
                {'id': 'pd4'},
                {'id': 'pd5'},
                {'id': 'pd6'},
                {'id': 'pd7'},
                {'id': 'pd8'},
                {'id': 'pd9'},
            ],
            'primary_replica': False,
        }
        return {
            'items': [
                {'id': 'pd1', 'value': 'LICENSE1'},
                {'id': 'pd2', 'value': 'LICENSE2'},
                {'id': 'pd7', 'value': 'LICENSE7'},
                {'id': 'pd3', 'value': 'LICENSE3'},
                {'id': 'pd4', 'value': 'LICENSE4'},
                {'id': 'pd5', 'value': 'LICENSE5'},
                {'id': 'pd9', 'value': 'LIСЕNSЕ9'},
                {'id': 'pd10', 'value': 'LIСЕNSЕ10'},
                {'id': 'pd11', 'value': 'LIСЕNSЕ11'},
                {'id': 'pd12', 'value': 'LIСЕNSЕ12'},
            ],
        }

    @mock_ext_carsharing('/api/taxisharing/user/remap')
    async def _taxisharing_user_remap(request):
        drive_users = [
            {
                'id': 'user_id1',
                'driver_license': 'LICENSE1',
                'first_name': 'FN1',
                'last_name': 'LN1',
                'p_name': 'MN1',
                'status': 'active',
            },
            {
                'id': 'user_id2',
                'driver_license': 'LICENSE2',  # cyrillic
                'first_name': 'FN2',
                'last_name': 'LN2',
                'p_name': 'MN2',
                'status': 'active',
            },
            {
                'id': 'user_id3',
                'driver_license': 'LICENSE3',
                'first_name': 'FN3',
                'last_name': 'LN3',
                'p_name': 'MN3',
                'status': 'active',
            },
            {
                'id': 'user_id4',
                'driver_license': 'LIСЕNSЕ4',  # cyrillic
                'first_name': 'FN4',
                'last_name': 'LN4',
                'p_name': 'MN4',
                'status': 'active',
            },
            {
                'id': 'user_id9',
                'driver_license': 'LIСЕNSЕ9',  # cyrillic
                'first_name': '   FN9',
                'last_name': ' LN9   ',
                'p_name': '-',
                'status': 'active',
            },
            {
                'id': 'user_id10',
                'driver_license': 'LIСЕNSЕ10',  # cyrillic
                'first_name': '  ',
                'p_name': '-',
                'status': 'active',
            },
            {
                'id': 'user_id11',
                'driver_license': 'LIСЕNSЕ11',  # cyrillic
                'first_name': '   FN11',
                'last_name': ' LN11   ',
                'p_name': '-',
                'status': 'active',
            },
            {
                'id': 'user_id12',
                'driver_license': 'LIСЕNSЕ12',  # cyrillic
                'first_name': '   FN12',
                'last_name': ' LN12   ',
                'p_name': '-',
                'status': 'active',
            },
        ]

        licenses = set(request.json['driver_licenses'])
        assert licenses in (
            {
                'LICENSE1',
                'LICENSE2',
                'LICENSE7',
                'LIСЕNSЕ1',
                'LIСЕNSЕ2',
                'LIСЕNSЕ7',
                'LIСЕNSЕ10',
                'LIСЕNSЕ11',
                'LIСЕNSЕ12',
            },
            {
                'LICENSE3',
                'LICENSE4',
                'LICENSE5',
                'LIСЕNSЕ3',
                'LIСЕNSЕ4',
                'LIСЕNSЕ5',
                'LIСЕNSЕ9',
            },
        ), licenses
        return {
            'users': [
                x for x in drive_users if x['driver_license'] in licenses
            ],
        }

    @mock_ext_carsharing('/api/taxisharing/user_tags/list')
    async def _taxisharing_user_tags_list(request):
        user_id = request.query['object_id']
        if user_id == 'user_id11':
            return web.json_response(
                status=403,
                headers={'X-Req-Id': 'some id', 'Other-Header': 'asdf'},
                body=error_response_stub,
            )
        if user_id == 'user_id12':
            return {
                'records': [
                    {
                        'object_id': user_id,
                        'tag': 'taxi_taxisharing_fleet_auth_info',
                    },
                ],
            }
        assert user_id in {
            'user_id1',
            'user_id2',
            'user_id3',
            'user_id4',
            'user_id5',
            'user_id9',
            'user_id10',
        }
        tag_data = {
            'user_id2': ('park_id1', 'did2'),
            'user_id3': ('park_id1', 'did3'),
            'user_id4': ('park_id1', 'did4'),
            'user_id9': ('park_id1', 'did9'),
        }
        if user_id not in tag_data:
            return {'records': []}
        park_id, driver_id = tag_data[user_id]
        return {
            'records': [
                {
                    'object_id': user_id,
                    'tag': 'taxi_taxisharing_fleet_auth_info',
                    'fields': [
                        {'key': 'park_id', 'value': park_id},
                        {'key': 'profile_id', 'value': driver_id},
                    ],
                },
            ],
        }

    @mock_ext_carsharing('/api/taxisharing/accounts')
    async def _taxisharing_accounts(request):
        user_id = request.query['user_id']
        assert user_id in {
            'user_id1',
            'user_id2',
            'user_id3',
            'user_id4',
            'user_id5',
            'user_id9',
            'user_id10',
            'user_id11',
            'user_id12',
        }
        user_id_to_acc = {
            'user_id2': 2,
            'user_id3': 3,
            'user_id4': 4,
            'user_id9': 9,
        }
        if user_id not in user_id_to_acc:
            return {'accounts': []}
        acc = user_id_to_acc[user_id]
        return {
            'accounts': [
                {
                    'id': acc,
                    'is_active': True,
                    'is_actual': True,
                    'disabled': False,
                    'type_name': 'taxisharing',
                },
            ],
        }

    # User ids only
    linked_accs = set()
    unlinked_accs = set()
    added_tags = set()
    removed_tags = set()

    @mock_ext_carsharing('/api/taxisharing/accounts/link')
    async def _taxisharing_account_link(request):
        req_js = request.json
        assert req_js['action'] in ['link', 'unlink']
        if req_js['action'] == 'link':
            users = req_js.pop('users')
            assert users
            assert req_js == {
                'action': 'link',
                'active_flag': True,
                'name': 'taxisharing',
            }
            linked_accs.update(users)
            if users == ['user_id1']:
                return {'account_ids': [1]}
            if users == ['user_id10']:
                return {'account_ids': [10]}
            if users == ['user_id11']:
                return {'account_ids': [11]}
            if users == ['user_id12']:
                return {'account_ids': [12]}
            assert users == []
        if req_js['action'] == 'unlink':
            acc_id = req_js['account_id']
            assert acc_id in [3, 4, 9]
            assert req_js == {
                'account_id': acc_id,
                'action': 'unlink',
                'users': [f'user_id{acc_id}'],
            }
            unlinked_accs.update(req_js['users'])
            return {'account_ids': [acc_id]}
        assert False, request.json

    @mock_ext_carsharing('/api/taxisharing/user_tags/add')
    async def _taxisharing_add_tag(request):
        assert request.json in (
            {
                'add_tags': [
                    {
                        'display_name': 'Доступ к таксишерингу',
                        'fields': [
                            {'key': 'apikey', 'value': 'apikeyvalue'},
                            {'key': 'client_id', 'value': 'yndx.drive'},
                            {'key': 'park_id', 'value': 'park_id1'},
                            {'key': 'profile_id', 'value': 'did1'},
                        ],
                        'tag': 'taxi_taxisharing_fleet_auth_info',
                    },
                ],
                'object_id': 'user_id1',
            },
            {
                'add_tags': [
                    {
                        'display_name': 'Доступ к таксишерингу',
                        'fields': [
                            {'key': 'apikey', 'value': 'apikeyvalue'},
                            {'key': 'client_id', 'value': 'yndx.drive'},
                            {'key': 'park_id', 'value': 'park_id1'},
                            {'key': 'profile_id', 'value': 'did10'},
                        ],
                        'tag': 'taxi_taxisharing_fleet_auth_info',
                    },
                ],
                'object_id': 'user_id10',
            },
            {
                'add_tags': [
                    {
                        'display_name': 'Доступ к таксишерингу',
                        'fields': [
                            {'key': 'apikey', 'value': 'apikeyvalue'},
                            {'key': 'client_id', 'value': 'yndx.drive'},
                            {'key': 'park_id', 'value': 'park_id1'},
                            {'key': 'profile_id', 'value': 'did11'},
                        ],
                        'tag': 'taxi_taxisharing_fleet_auth_info',
                    },
                ],
                'object_id': 'user_id11',
            },
            {
                'add_tags': [
                    {
                        'display_name': 'Доступ к таксишерингу',
                        'fields': [
                            {'key': 'apikey', 'value': 'apikeyvalue'},
                            {'key': 'client_id', 'value': 'yndx.drive'},
                            {'key': 'park_id', 'value': 'park_id1'},
                            {'key': 'profile_id', 'value': 'did12'},
                        ],
                        'tag': 'taxi_taxisharing_fleet_auth_info',
                    },
                ],
                'object_id': 'user_id12',
            },
        )
        added_tags.add(request.json['object_id'])
        return {}

    @mock_ext_carsharing('/api/taxisharing/user_tags/remove')
    async def _taxisharing_remove_tag(request):
        user_id = request.json['object_ids'][0]
        assert user_id in {'user_id3', 'user_id4', 'user_id9'}
        removed_tags.update(request.json['object_ids'])
        assert request.json == {
            'object_ids': [user_id],
            'tag_names': ['taxi_taxisharing_fleet_auth_info'],
        }

    await run_cron.main(
        ['drive_integration_worker.crontasks.sync_drivers', '-t', '0'],
    )

    assert linked_accs == {'user_id1', 'user_id10', 'user_id12'}
    assert unlinked_accs == {'user_id3', 'user_id4', 'user_id9'}
    assert added_tags == {'user_id1', 'user_id10', 'user_id12'}
    assert removed_tags == {'user_id3', 'user_id4', 'user_id9'}
