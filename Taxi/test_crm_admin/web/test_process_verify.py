# pylint: disable=unused-variable,unused-argument,protected-access

import itertools

from aiohttp import web
import pytest

from crm_admin import audience
from crm_admin import entity
from crm_admin import error_codes
from crm_admin import settings
from crm_admin import storage
from crm_admin.audience.utils import verify_utils
from crm_admin.entity import error
from crm_admin.utils import kibana
from crm_admin.utils import verify as process_verify


def is_sorted(rows, key):
    return all(rows[i][key] <= rows[i + 1][key] for i in range(len(rows) - 1))


async def test_gen_driver_verification_table(web_context, patch):
    class Campaign:
        entity_type = 'Driver'
        test_users = ['0x001_0x011', '0x002_0x022']

    class Segment:
        yt_table = 'path/to/table'

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.read_table',
    )
    async def read_table(*args, **kwargs):
        return [
            {
                'group_id': 'group1',
                'group_name': 'group1',
                'db_id': '0x1',
                'driver_uuid': '0x1',
                'phone': '+7xx',
                'city': 'A',
            },
            {
                'group_id': 'group2',
                'group_name': 'group2',
                'db_id': '0x2',
                'driver_uuid': '0x2',
                'phone': '+7xx',
                'city': 'B',
            },
        ]

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.write_table',
    )
    async def write_table(path, rows, *args, **kwargs):
        pass

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.get')
    async def get(*agrs, **kwargs):
        columns = [
            'group_id',
            'group_name',
            'db_id',
            'driver_uuid',
            'phone',
            'city',
        ]
        return [{'name': c, 'type': 'string'} for c in columns]

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.create')
    async def create(*agrs, **kwargs):
        assert kwargs['attributes']['schema'][0]['name'] == 'group_name'

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.exists')
    async def exists(*agrs, **kwargs):
        return True

    path = await process_verify._gen_verification_table(
        web_context, Campaign(), Segment(),
    )
    assert path == '//' + Segment.yt_table + '_verification'

    def gen_expected(users, rows):
        for user, row in itertools.product(users, rows):
            db_id, driver_uuid = user.split('_')
            yield {
                **row,
                'db_id': db_id,
                'driver_uuid': driver_uuid,
                'clean_col_db_id': row['db_id'],
                'clean_col_driver_uuid': row['driver_uuid'],
            }

    expected = list(gen_expected(Campaign.test_users, await read_table()))
    actual = write_table.calls[0]['rows']

    for item in expected:
        assert item in actual
    assert len(expected) == len(actual)
    assert is_sorted(actual, 'group_name')


async def test_gen_driver_verification_invalid_test_users(web_context, patch):
    class Campaign:
        entity_type = 'Driver'
        test_users = ['invalid123', 'invalid456']

    class Segment:
        yt_table = 'path/to/table'

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.read_table',
    )
    async def read_table(*args, **kwargs):
        return [
            {
                'group_id': 'group1',
                'group_name': 'group1',
                'db_id': '0x1',
                'driver_uuid': '0x1',
                'phone': '+7xx',
                'city': 'A',
            },
            {
                'group_id': 'group2',
                'group_name': 'group2',
                'db_id': '0x2',
                'driver_uuid': '0x2',
                'phone': '+7xx',
                'city': 'B',
            },
        ]

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.write_table',
    )
    async def write_table(path, rows, *args, **kwargs):
        pass

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.exists')
    async def exists(*args, **kwargs):
        if args[0] == '//path/to/table_verification':
            return True
        return False

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.create')
    async def create(*args, **kwargs):
        assert kwargs['attributes']['schema'][0]['name'] == 'group_name'

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.get')
    async def get(*args, **kwargs):
        return {}

    with pytest.raises(verify_utils.UserRetrievalError):
        await process_verify._gen_verification_table(
            context=web_context, campaign=Campaign(), segment=Segment(),
        )


async def test_gen_driver_verification_table_size_idempotency(
        web_context, patch,
):
    class Campaign:
        entity_type = 'Driver'
        test_users = ['0x001_0x011', '0x002_0x022']

    class Segment:
        yt_table = 'path/to/table'

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.read_table',
    )
    async def read_table(*args, **kwargs):
        return [
            {
                'group_id': 'group1',
                'group_name': 'group1',
                'db_id': '0x1',
                'driver_uuid': '0x1',
                'phone': '+7xx',
                'city': 'A',
            },
            {
                'group_id': 'group2',
                'group_name': 'group2',
                'db_id': '0x2',
                'driver_uuid': '0x2',
                'phone': '+7xx',
                'city': 'B',
            },
        ]

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.write_table',
    )
    async def write_table(path, rows, *args, **kwargs):
        pass

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.get')
    async def get(*agrs, **kwargs):
        columns = [
            'group_id',
            'group_name',
            'db_id',
            'driver_uuid',
            'phone',
            'city',
        ]
        return [{'name': c, 'type': 'string'} for c in columns]

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.create')
    async def create(*agrs, **kwargs):
        assert kwargs['attributes']['schema'][0]['name'] == 'group_name'

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.exists')
    async def exists(*agrs, **kwargs):
        return True

    await process_verify._gen_verification_table(
        web_context, Campaign(), Segment(),
    )
    size = len(write_table.calls[-1]['rows'])

    for _ in range(3):
        await process_verify._gen_verification_table(
            web_context, Campaign(), Segment(),
        )
        assert len(write_table.calls[-1]['rows']) == size


@pytest.mark.parametrize('yandex_uid', [['1', '2', '3'], None])
async def test_gen_user_verification_table(
        web_context, patch, mock_user_api, yandex_uid,
):
    class Campaign:
        campaign_id = 1
        entity_type = 'User'
        test_users = ['+700001', '+700002']

        class Settings:
            field_id = 'brand'
            value = 'yandex'

        settings = [Settings()]

    class Segment:
        yt_table = 'path/to/table'

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.read_table',
    )
    async def read_table(*args, **kwargs):
        table = [
            {
                'group_id': 'group1',
                'group_name': 'group1',
                'user_id': '0x1',
                'phone': '+7xx',
                'city': 'A',
            },
            {
                'group_id': 'group2',
                'group_name': 'group2',
                'user_id': '0x2',
                'phone': '+7xx',
                'city': 'B',
            },
        ]

        if yandex_uid:
            table[0]['yandex_uid'] = yandex_uid[0]
            table[1]['yandex_uid'] = yandex_uid[1]

        return table

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.write_table',
    )
    async def write_table(path, rows, *args, **kwargs):
        if yandex_uid:
            for row in rows:
                assert row['yandex_uid'] == yandex_uid[2]

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.get')
    async def get(*agrs, **kwargs):
        return []

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.create')
    async def create(*args, **kwargs):
        assert kwargs['attributes']['schema'][0]['name'] == 'group_name'

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.exists')
    async def exists(*args, **kwargs):
        if args[0] == '//path/to/table_verification':
            return True
        return False

    @mock_user_api('/user_phones/by_number/retrieve_bulk')
    async def retrieve_bulk(request):
        phones = request.json['items']
        return web.json_response(
            {
                'items': [
                    {'id': str(i), 'personal_phone_id': str(i), **kwargs}
                    for i, kwargs in enumerate(phones)
                ],
            },
            status=200,
        )

    @mock_user_api('/users/search')
    async def users_search(request):
        phones = request.json['phone_ids']
        cursor = request.json.get('cursor', None)
        applications = request.json.get('applications', [])
        start = 0
        if cursor is None:
            phones = phones[:1]
            cursor = '2'
        elif cursor == '2':
            phones = phones[1:]
            cursor = None
            start = 1
        return web.json_response(
            {
                'items': [
                    {
                        'id': str(i),
                        'phone_id': p,
                        'updated': '2021-01-01 00:00:00',
                        'application': 'android',
                        'yandex_uid': yandex_uid[2],
                    }
                    if yandex_uid
                    else {
                        'id': str(i),
                        'phone_id': p,
                        'updated': '2021-01-01 00:00:00',
                        'application': 'android',
                    }
                    for i, p in enumerate(phones, start=start)
                    if 'android' in applications
                ],
                'cursor': cursor,
            },
            status=200,
        )

    await process_verify._gen_verification_table(
        web_context, Campaign(), Segment(),
    )

    assert retrieve_bulk.has_calls
    assert users_search.has_calls

    rows = write_table.call['rows']
    assert rows
    assert is_sorted(rows, 'group_name')


async def test_gen_user_verification_table_empty(
        web_context, patch, mock_user_api,
):
    class Campaign:
        campaign_id = 1
        entity_type = 'User'
        test_users = ['+700001', '+700002']

        class Settings:
            field_id = 'brand'
            value = 'yandex'

        settings = [Settings()]

    class Segment:
        yt_table = 'path/to/table'

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.read_table',
    )
    async def read_table(*args, **kwargs):
        return [
            {
                'group_id': 'group1',
                'group_name': 'group1',
                'user_id': '0x1',
                'phone': '+7xx',
                'city': 'A',
            },
            {
                'group_id': 'group2',
                'group_name': 'group2',
                'user_id': '0x2',
                'phone': '+7xx',
                'city': 'B',
            },
        ]

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.write_table',
    )
    async def write_table(path, rows, *args, **kwargs):
        pass

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.get')
    async def get(*agrs, **kwargs):
        return []

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.create')
    async def create(*args, **kwargs):
        assert kwargs['attributes']['schema'][0]['name'] == 'group_name'

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.exists')
    async def exists(*args, **kwargs):
        if args[0] == '//path/to/table_verification':
            return True
        return False

    @mock_user_api('/user_phones/by_number/retrieve_bulk')
    async def retrieve_bulk(request):
        return web.json_response({'items': []}, status=200)

    with pytest.raises(verify_utils.UserRetrievalError):
        await process_verify._gen_verification_table(
            web_context, Campaign(), Segment(),
        )


async def test_gen_eatsuser_verification_table(
        web_context, patch, mock_user_api, mock_eats_eaters,
):
    class Campaign:
        campaign_id = 1
        entity_type = 'EatsUser'
        test_users = ['+700001', '+700002']

        class Settings:
            field_id = 'brand'
            value = 'yandex'

        settings = [Settings()]

    class Segment:
        yt_table = 'path/to/table'

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.read_table',
    )
    async def read_table(*args, **kwargs):
        return [
            {
                'group_id': 'group1',
                'group_name': 'group1',
                'eda_client_id': '0x1',
                'phone': '+7xx',
                'city': 'A',
                'yandex_uid': '1',
            },
            {
                'group_id': 'group2',
                'group_name': 'group2',
                'eda_client_id': '0x2',
                'phone': '+7xx',
                'city': 'B',
                'yandex_uid': '2',
            },
        ]

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.write_table',
    )
    async def write_table(path, rows, *args, **kwargs):
        for row in rows:
            assert row['yandex_uid'] == '3'

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.get')
    async def get(*agrs, **kwargs):
        return []

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.create')
    async def create(*args, **kwargs):
        assert kwargs['attributes']['schema'][0]['name'] == 'group_name'

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.exists')
    async def exists(*args, **kwargs):
        if args[0] == '//path/to/table_verification':
            return True
        return False

    @mock_user_api('/user_phones/by_number/retrieve_bulk')
    async def retrieve_bulk(request):
        phones = request.json['items']
        return web.json_response(
            {
                'items': [
                    {'id': str(i), 'personal_phone_id': str(i), **kwargs}
                    for i, kwargs in enumerate(phones)
                ],
            },
            status=200,
        )

    @mock_eats_eaters('/v1/eaters/find-by-personal-phone-id')
    async def find_by_personal_phone_id(request):
        personal_phone_id = request.json['personal_phone_id']
        return web.json_response(
            {
                'eaters': [
                    {
                        'id': '001',
                        'uuid': 'cbaf7f9e-02b0-45a4-8c65-b3b5f796ca17',
                        'created_at': '2021-06-11T08:03:15.320605+00:00',
                        'updated_at': '2021-06-11T08:03:15.320605+00:00',
                        'personal_phone_id': personal_phone_id,
                        'passport_uid': '3',
                    },
                ],
                'pagination': {'limit': 1000, 'has_more': False},
            },
            status=200,
        )

    await process_verify._gen_verification_table(
        web_context, Campaign(), Segment(),
    )

    assert retrieve_bulk.has_calls
    assert find_by_personal_phone_id.has_calls

    rows = write_table.call['rows']
    assert rows
    assert is_sorted(rows, 'group_name')


async def test_gen_eatsuser_verification_table_empty(
        web_context, patch, mock_user_api, mock_eats_eaters,
):
    class Campaign:
        campaign_id = 1
        entity_type = 'EatsUser'
        test_users = ['+700001', '+700002']

        class Settings:
            field_id = 'brand'
            value = 'yandex'

        settings = [Settings()]

    class Segment:
        yt_table = 'path/to/table'

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.read_table',
    )
    async def read_table(*args, **kwargs):
        return [
            {
                'group_id': 'group1',
                'group_name': 'group1',
                'eda_client_id': '0x1',
                'phone': '+7xx',
                'city': 'A',
            },
            {
                'group_id': 'group2',
                'group_name': 'group1',
                'eda_client_id': '0x2',
                'phone': '+7xx',
                'city': 'B',
            },
        ]

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.write_table',
    )
    async def write_table(path, rows, *args, **kwargs):
        pass

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.get')
    async def get(*agrs, **kwargs):
        return []

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.create')
    async def create(*args, **kwargs):
        assert kwargs['attributes']['schema'][0]['name'] == 'group_name'

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.exists')
    async def exists(*args, **kwargs):
        if args[0] == '//path/to/table_verification':
            return True
        return False

    @mock_user_api('/user_phones/by_number/retrieve_bulk')
    async def retrieve_bulk(request):
        return web.json_response({'items': []}, status=200)

    with pytest.raises(verify_utils.UserRetrievalError):
        await process_verify._gen_verification_table(
            web_context, Campaign(), Segment(),
        )


@pytest.mark.parametrize(
    'entity_type, test_users, campaign_id, field_id, value',
    [
        ('Driver', ['0x001_0x011', '0x002_0x022'], None, None, None),
        ('User', ['+700001', '+700002'], 1, 'brand', 'yandex'),
        ('EatsUser', ['+700001', '+700002'], 1, 'brand', 'yandex'),
    ],
)
async def test_gen_verification_table_do_not_exist_table(
        web_context,
        patch,
        entity_type,
        test_users,
        campaign_id,
        field_id,
        value,
):
    class Campaign:
        def __init__(self, entity_type, test_users, campaign_id):
            self.entity_type = entity_type
            self.test_users = test_users
            self.campaign_id = campaign_id
            self.settings = []

        class Settings:
            def __init__(self, field_id, value):
                self.field_id = field_id
                self.value = value

    class Segment:
        yt_table = 'path/to/table'

    campaign = Campaign(entity_type, test_users, campaign_id)
    campaign.settings.append(Campaign.Settings(field_id, value))

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.exists')
    async def exists(*agrs, **kwargs):
        return False

    with pytest.raises(entity.NoData):
        await process_verify._gen_verification_table(
            web_context, campaign, Segment(),
        )


@pytest.mark.parametrize(
    'entity_type, test_users, campaign_id, field_id, value',
    [
        ('Driver', ['0x001_0x011', '0x002_0x022'], None, None, None),
        ('User', ['+700001', '+700002'], 1, 'brand', 'yandex'),
        ('EatsUser', ['+700001', '+700002'], 1, 'brand', 'yandex'),
    ],
)
async def test_gen_verification_table_empty_table(
        web_context,
        patch,
        entity_type,
        test_users,
        campaign_id,
        field_id,
        value,
):
    class Campaign:
        def __init__(self, entity_type, test_users, campaign_id):
            self.entity_type = entity_type
            self.test_users = test_users
            self.campaign_id = campaign_id
            self.settings = []

        class Settings:
            def __init__(self, field_id, value):
                self.field_id = field_id
                self.value = value

    class Segment:
        yt_table = 'path/to/table'

    campaign = Campaign(entity_type, test_users, campaign_id)
    campaign.settings.append(Campaign.Settings(field_id, value))

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.read_table',
    )
    async def read_table(*args, **kwargs):
        return []

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.exists')
    async def exists(*agrs, **kwargs):
        return True

    with pytest.raises(entity.NoData):
        await process_verify._gen_verification_table(
            web_context, campaign, Segment(),
        )


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_request_error(web_app_client, patch):
    campaign_id = 1

    @patch(
        'crm_admin.utils.validation.filters_yt_validators'
        '.validate_filters_values',
    )
    async def validation(*agrs, **kwargs):
        return []

    @patch('crm_admin.utils.verify.pre_check')
    async def pre_check(context, campaign_id):
        raise error.RequestError('error')

    response = await web_app_client.post(
        '/v1/process/segment', params={'id': campaign_id},
    )
    assert response.status == 424


@pytest.mark.parametrize(
    'brand, apps',
    [
        ('yandex', ['android', 'iphone']),
        (
            'uber',
            [
                'uber_android',
                'uber_iphone',
                'uber_az_android',
                'uber_az_iphone',
                'uber_kz_android',
                'uber_kz_iphone',
                'uber_by_android',
                'uber_by_iphone',
            ],
        ),
        ('yango', ['yango_android', 'yango_iphone']),
        (
            'yango_deli',
            [
                'yangodeli_android',
                'yangodeli_iphone',
                'yango_deli_android',
                'yango_deli_iphone',
            ],
        ),
        ('lavka', ['lavka_android', 'lavka_iphone']),
    ],
)
def test_user_apps(brand, apps):
    audience_cmp = audience.get_audience_by_type(
        audience.settings.AudienceType.USERS.value,
    )
    brand_apps = set(audience_cmp.verify._get_user_applications(brand))
    assert brand_apps == set(apps)


@pytest.mark.config(
    CRM_ADMIN_VERIFY_SEND_PERMISSIONS=[
        {
            'entity': 'Driver',
            'permissions': {
                'everybody_can_test': False,
                'users_can_test': ['all_good_user'],
                'user_tags_permission': ['user_tags_user'],
                'promocode_permission': ['promocode_user'],
            },
        },
    ],
    CRM_ADMIN_GROUPS_V2={'all_on': True},
)
@pytest.mark.parametrize(
    'group_id, yandex_login, status',
    [
        (1, 'user_tags_user', 200),
        (1, 'promocode_user', 200),
        (1, None, 200),
        (2, 'all_good_user', 200),
        (2, 'user_tags_user', 200),
        (2, 'promocode_user', 403),
        (2, None, 403),
        (7, 'all_good_user', 200),
        (7, 'promocode_user', 200),
        (7, 'user_tags_user', 403),
        (7, None, 403),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_login_verify_check(
        web_app_client, patch, yandex_login, status, group_id,
):
    @patch(
        'crm_admin.utils.validation.group_validators.'
        'promocode_series_validation',
    )
    async def group_update_validation(*args, **kwargs):
        return []

    campaign_id = 2
    body = [group_id]
    headers = {'X-Yandex-Login': yandex_login} if yandex_login else None

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.get')
    async def get(*args, **kwargs):
        return {}

    response = await web_app_client.post(
        '/v1/process/verify',
        headers=headers,
        params={'id': campaign_id},
        json=body,
    )

    assert response.status == status


@pytest.mark.config(CRM_ADMIN_GROUPS_V2={'all_on': True})
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_tags_without_creative_verify_check(web_app_client, patch):
    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.get')
    async def get(*args, **kwargs):
        return {}

    response = await web_app_client.post(
        '/v1/process/verify',
        headers={'X-Yandex-Login': 'yandex_login'},
        params={'id': 2},
        json=[3],
    )
    assert response.status == 200


# =============================================================================


@pytest.mark.config(CRM_ADMIN_GROUPS_V2={'all_on': True})
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.parametrize(
    'campaign_id, groups_id_list', [(3, [4, 5, 6]), (4, [4, 5]), (5, [6])],
)
async def test_error_start_stq(
        web_context, web_app_client, patch, campaign_id, groups_id_list,
):
    reason = 'test error'
    db_campaign = storage.DbCampaign(context=web_context)

    @patch('crm_admin.generated.service.stq_client.plugin.QueueClient.call')
    async def _call_stq(*args, **kwargs):
        raise Exception(reason)

    @patch('crm_admin.api.process_verify.groupings.process_verify_validation')
    async def _process_verify_validation(*args, **kwargs):
        return []

    db_group = storage.DbGroup(context=web_context)

    response = await web_app_client.post(
        '/v1/process/verify', params={'id': campaign_id}, json=groups_id_list,
    )

    assert response.status == 200
    assert _call_stq.calls
    assert _process_verify_validation.calls

    groups = await db_group.fetch_by_campaign_id(campaign_id)
    for group in groups:
        if group.group_id in groups_id_list:
            assert group.params.state == settings.GROUP_STATE_NEW

    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.VERIFY_ERROR
    assert campaign.error_code == error_codes.VERIFICATION_FAILED
    assert campaign.error_description == {
        'kibana': kibana.make_url(
            f'ngroups:taxi_crm-admin*'
            f' and uri:/v1/process/verify*?id={campaign_id}',
        ),
        'error_msg': reason,
    }


# =============================================================================
