import datetime
from typing import Optional

import pytest

from rida.models import device as device_models
from rida.models import user as user_models
from test_rida import experiments_utils
from test_rida import helpers


IOS_PARAMS = {
    'deviceType': 'iPhone',
    'deviceScale': '2',
    'osVersion': '12.5.3',
    'applicationVersion': '200700',
    'applicationVersionName': '2.4.0',
    'deviceBrandModel': 'iPhone7,1',
    'applicationId': '05CD3E1E-39DC-48FA-B217-00705B75CE68',
}


async def _get_user(web_app, user_id: int) -> user_models.User:
    return await web_app['context'].user_repo.get_user(user_id)


async def _get_device(web_app, user_guid: str) -> device_models.Device:
    return await web_app['context'].device_repo.get_device(user_guid)


def _create_device_from_params(
        user_guid: str, params: dict,
) -> device_models.Device:
    return device_models.Device(
        id=0,
        user_guid=user_guid,
        device_uuid=params['applicationId'],
        device_name=params['deviceBrandModel'],
        device_os=device_models.DeviceOs.from_string(params['deviceType']),
        device_os_version=params['osVersion'],
        build_number=int(params['applicationVersion']),
        build_number_name=device_models.BuildNumberName.from_string(
            params['applicationVersionName'],
        ),
    )


@pytest.mark.parametrize(
    ['request_body_as_query'],
    [
        pytest.param(True, id='request_body_as_query'),
        pytest.param(False, id='request_body_as_json'),
    ],
)
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_launch.sql'])
async def test_happy_path(web_app_client, load_json, request_body_as_query):
    request_params = {}
    request_params['params'] = IOS_PARAMS

    request_body = {'country_code': 'ng'}
    headers = helpers.get_auth_headers(user_id=1449)

    request_body = {k: v for k, v in request_body.items() if v is not None}
    if request_body_as_query:
        request_params['data'] = request_body
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    else:
        request_params['json'] = request_body
        headers['Content-Type'] = 'application/json'

    request_params['headers'] = headers

    response = await web_app_client.post('/v1/launch', **request_params)

    assert response.status == 200
    response_json = await response.json()
    assert response_json == load_json('happy_path.json')


@pytest.mark.parametrize(
    [
        'position',
        'expected_bid_step',
        'expected_time_coefficient',
        'expected_min_offer_amount',
    ],
    [
        pytest.param(
            [7.475537, 9.053398],
            '500.00',
            '7.000000',
            '300.00',
            id='matched_zone',
        ),
        pytest.param(
            '[7.475537,9.053398]',
            '500.00',
            '7.000000',
            '300.00',
            id='point_is_str_matched_zone',
        ),
        pytest.param(
            '[]',
            '50.00',
            '2.000000',
            '125.00',
            id='point_is_str_not_matched_zone',
        ),
        pytest.param(
            [3.475537, 9.053398],
            '50.00',
            '2.000000',
            '125.00',
            id='not_matched_zone',
        ),
    ],
)
@pytest.mark.parametrize(
    ['request_body_as_query'],
    [
        pytest.param(True, id='request_body_as_query'),
        pytest.param(False, id='request_body_as_json'),
    ],
)
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_launch.sql'])
async def test_zone_by_point_detection(
        web_app_client,
        request_body_as_query,
        position,
        expected_bid_step,
        expected_time_coefficient,
        expected_min_offer_amount,
):
    request_params = {}
    request_params['params'] = IOS_PARAMS

    request_body = {'country_code': 'ng', 'position': position}
    headers = helpers.get_auth_headers(user_id=1449)

    request_body = {k: v for k, v in request_body.items() if v is not None}
    if request_body_as_query:
        request_params['data'] = request_body
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    else:
        request_params['json'] = request_body
        headers['Content-Type'] = 'application/json'

    request_params['headers'] = headers

    response = await web_app_client.post('/v1/launch', **request_params)

    assert response.status == 200
    response_json = await response.json()
    response_data = response_json['data']
    country = response_data['country']

    assert country['bid_step'] == expected_bid_step
    assert country['time_coefficient'] == expected_time_coefficient
    assert country['min_offer_amount'] == expected_min_offer_amount


@pytest.mark.parametrize(
    ['country_code', 'zone_id'],
    [
        pytest.param(None, None, id='detect_country_by_ip'),
        pytest.param('ng', None, id='known_country'),
        pytest.param('ng', 0, id='known_country_default_zone'),
        pytest.param('ng', 1, id='known_country_known_zone'),
        pytest.param('ng', '1', id='known_country_known_zone_str'),
    ],
)
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_launch.sql'])
async def test_country(web_app_client, country_code, zone_id):
    payload = {}
    if country_code is not None:
        payload['country_code'] = country_code
    if zone_id is not None:
        payload['zone_id'] = zone_id

    response = await web_app_client.post(
        '/v1/launch',
        params=IOS_PARAMS,
        headers=helpers.get_auth_headers(user_id=1449),
        json=payload,
    )

    assert response.status == 200
    response_json = await response.json()
    response_data = response_json['data']
    detected_country_code = response_data['detected_country_code']
    assert detected_country_code == 'ng'


@pytest.mark.parametrize(
    ['user_id', 'expected_passenger', 'expected_driver'],
    [
        pytest.param(
            None, False, False, id='unauth',
        ),  # NOTE: temporary disabled
        pytest.param(1449, True, True, id='user_with_driver'),
        pytest.param(1234, True, False, id='user_without_driver'),
    ],
)
async def test_passenger(
        web_app_client, user_id, expected_passenger, expected_driver,
):
    payload = {'country_code': 'ng'}
    headers = {}
    if user_id is not None:
        headers = helpers.get_auth_headers(user_id=user_id)
    response = await web_app_client.post(
        '/v1/launch', params=IOS_PARAMS, headers=headers, json=payload,
    )
    assert response.status == 200
    response_json = await response.json()
    response_data = response_json['data']

    passenger = response_data.get('passenger')
    if expected_passenger:
        assert passenger is not None
        driver = passenger.get('driver')
        if expected_driver:
            assert driver is not None
        else:
            assert driver is None
    else:
        assert passenger is None


@pytest.mark.mongodb_collections('rida_offers')
@pytest.mark.filldb()
@pytest.mark.now('2020-04-29T10:12:00.000+0000')
@pytest.mark.parametrize(
    ['user_id', 'expected_guid'],
    [
        pytest.param(1234, '', id='not_found'),  # NOTE: temporary disabled
        pytest.param(
            3456,
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
            id='user_mongo_in_progress_offer',
        ),
        pytest.param(
            5678,
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5Q',
            id='user_mongo_canceled_offer',
        ),
        pytest.param(
            1449,
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
            id='driver_mongo_in_progress_offer',
        ),
    ],
)
async def test_last_offer_guid_mongo(web_app_client, user_id, expected_guid):
    response = await web_app_client.post(
        '/v1/launch',
        params=IOS_PARAMS,
        headers=helpers.get_auth_headers(user_id=user_id),
        json={'country_code': 'ng'},
    )
    assert response.status == 200
    response_json = await response.json()
    response_data = response_json['data']
    assert response_data['last_order_guid'] == expected_guid


@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_offers.sql'])
@pytest.mark.now('2020-04-29T10:12:00.000+0000')
@pytest.mark.parametrize(
    ['user_id', 'expected_guid'],
    [
        pytest.param(
            1234, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G', id='user_pg_offer',
        ),
    ],
)
async def test_last_offer_guid_pg(web_app_client, user_id, expected_guid):
    response = await web_app_client.post(
        '/v1/launch',
        params=IOS_PARAMS,
        headers=helpers.get_auth_headers(user_id=user_id),
        json={'country_code': 'ng'},
    )
    assert response.status == 200
    response_json = await response.json()
    response_data = response_json['data']
    assert response_data['last_order_guid'] == expected_guid


@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_offers.sql'])
@pytest.mark.now('2020-04-29T10:12:00.000+0000')
@pytest.mark.parametrize(
    'review_type, should_see_offer',
    [('user_review', False), ('driver_review', True)],
)
async def test_last_offer_guid_pg_with_review(
        web_app_client, web_context, review_type: str, should_see_offer: bool,
):
    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G'
    user_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B'
    driver_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'
    query = (
        'INSERT INTO user_ratings (offer_guid, user_guid, '
        'driver_guid, review_type, rating) VALUES '
        f'(\'{offer_guid}\', \'{user_guid}\', '
        f'\'{driver_guid}\', \'{review_type}\', 5);'
    )
    async with web_context.pg.rw_pool.acquire() as conn:
        await conn.execute(query)
    response = await web_app_client.post(
        '/v1/launch',
        params=IOS_PARAMS,
        headers=helpers.get_auth_headers(user_id=1234),
        json={'country_code': 'ng'},
    )
    assert response.status == 200
    response_json = await response.json()
    response_data = response_json['data']
    if should_see_offer:
        assert response_data['last_order_guid'] == offer_guid
    else:
        assert response_data['last_order_guid'] == ''


@pytest.mark.mongodb_collections('rida_bids')
@pytest.mark.filldb()
@pytest.mark.now('2020-04-29T10:12:00.000+0000')
@pytest.mark.parametrize(
    ['user_id', 'expected_guid'],
    [
        pytest.param(
            1449, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D', id='user_pg_offer',
        ),
        pytest.param(
            1450, '9373F48B-C6B4-4812-A2D0-413F3AFB0000', id='offer_by_bid',
        ),
        pytest.param(
            1451,
            '9373F48B-C6B4-4812-A2D0-413F3AFB0050',
            id='offer_by_multiple_bids',
        ),
    ],
)
async def test_last_offer_guid_from_bid(
        web_app_client, user_id: int, expected_guid: str,
):
    response = await web_app_client.post(
        '/v1/launch',
        params=IOS_PARAMS,
        headers=helpers.get_auth_headers(user_id=user_id),
        json={'country_code': 'ng'},
    )
    assert response.status == 200
    response_json = await response.json()
    response_data = response_json['data']
    assert response_data['last_order_guid'] == expected_guid


@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_launch.sql'])
async def test_update_country(web_app, web_app_client):
    user_id = 1234
    user = await _get_user(web_app, user_id)
    assert user.country_code is None

    response = await web_app_client.post(
        '/v1/launch',
        params=IOS_PARAMS,
        headers=helpers.get_auth_headers(user_id=user_id),
        json={'country_code': 'ng'},
    )
    assert response.status == 200
    user = await _get_user(web_app, user_id)
    assert user.country_code == 'ng'


@pytest.mark.now('2020-04-29T10:12:00.000+0000')
@pytest.mark.parametrize(
    ['user_id', 'device_exists'],
    [
        pytest.param(3457, False, id='create_entry'),
        pytest.param(1234, True, id='update_entry'),
    ],
)
async def test_user_device(
        web_app, web_app_client, web_context, user_id, device_exists,
):
    user = await _get_user(web_app, user_id)
    device = _create_device_from_params(user.guid, IOS_PARAMS)
    current_device = await _get_device(web_app, user.guid)

    if device_exists:
        assert current_device != device
    else:
        assert current_device is None

    response = await web_app_client.post(
        '/v1/launch',
        params=IOS_PARAMS,
        headers=helpers.get_auth_headers(user_id=user_id),
        json={'country_code': 'ng'},
    )
    assert response.status == 200
    new_device = await _get_device(web_app, user.guid)
    assert new_device == device

    async with web_context.pg.ro_pool.acquire() as conn:
        sql_query = f"""
            SELECT
                created_at,
                updated_at
            FROM devices
            WHERE user_guid=\'{user.guid}\'
        """
        raw_device = await conn.fetchrow(sql_query)
        if device_exists:
            assert raw_device['created_at'] == datetime.datetime(
                2020, 4, 29, 10, 10,
            )
        else:
            assert raw_device['created_at'] == datetime.datetime(
                2020, 4, 29, 10, 12,
            )
        assert raw_device['updated_at'] == datetime.datetime(
            2020, 4, 29, 10, 12,
        )


_EXP_NAME = 'rida_ready_to_share'
_EXP_VALUE = {
    'enabled': True,
    'toggle_text_tk': 'toggle_text',
    'comment_tk': 'comment',
    'l10n': {
        'toggle_text': 'Ready to share',
        'comment': 'User is ready to share drive with other passengers',
    },
}
_CONFIG_NAME = 'rida_ready_to_share_config'
_EXPECTED_ARGS = [
    *experiments_utils.get_default_user_args(
        user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5G',
        device_uuid='05CD3E1E-39DC-48FA-B217-00705B75CE68',
        application='rida_ios',
        version='2.4.0',
    ),
    {'name': 'country_id', 'type': 'int', 'value': 12},
]


@pytest.mark.parametrize(
    ['is_typed_config_expected'],
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=pytest.mark.client_experiments3(
                consumer='client/rida',
                locale='en',
                config_name=_CONFIG_NAME,
                args=_EXPECTED_ARGS,
                value=_EXP_VALUE,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    ['is_typed_exp_expected'],
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=pytest.mark.client_experiments3(
                consumer='client/rida',
                locale='en',
                experiment_name=_EXP_NAME,
                args=_EXPECTED_ARGS,
                value=_EXP_VALUE,
            ),
        ),
    ],
)
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_launch.sql'])
async def test_typed_experiments(
        web_app_client,
        load_json,
        is_typed_config_expected: bool,
        is_typed_exp_expected: bool,
):
    response = await web_app_client.post(
        '/v1/launch',
        params=IOS_PARAMS,
        json={'country_code': 'ng'},
        headers={
            'Host': 'api.rida.app',
            **helpers.get_auth_headers(user_id=1449),
        },
    )

    assert response.status == 200
    response_json = await response.json()
    expected_response_json = load_json('happy_path.json')
    if is_typed_config_expected:
        expected_response_json['data']['typed_experiments']['items'].append(
            {'name': _CONFIG_NAME, 'value': _EXP_VALUE},
        )
    if is_typed_exp_expected:
        expected_response_json['data']['typed_experiments']['items'].append(
            {'name': _EXP_NAME, 'value': _EXP_VALUE},
        )
    assert response_json == expected_response_json


def _build_expected_args(zone_id: Optional[int]):
    args = _EXPECTED_ARGS.copy()
    if zone_id is not None:
        args.append({'name': 'zone_id', 'type': 'int', 'value': zone_id})
    return args


@pytest.mark.parametrize(
    ['payload'],
    [
        pytest.param(
            {'country_code': 'ng'},
            marks=pytest.mark.client_experiments3(
                consumer='client/rida',
                locale='en',
                experiment_name=_EXP_NAME,
                args=_EXPECTED_ARGS,
                value=_EXP_VALUE,
            ),
            id='zone_id_is_is_missing',
        ),
        pytest.param(
            {'country_code': 'ng', 'zone_id': 0},
            marks=pytest.mark.client_experiments3(
                consumer='client/rida',
                locale='en',
                experiment_name=_EXP_NAME,
                args=_build_expected_args(zone_id=0),
                value=_EXP_VALUE,
            ),
            id='zone_id_from_request',
        ),
        pytest.param(
            {'country_code': 'ng', 'position': [7.475537, 9.053398]},
            marks=pytest.mark.client_experiments3(
                consumer='client/rida',
                locale='en',
                experiment_name=_EXP_NAME,
                args=_build_expected_args(zone_id=3),
                value=_EXP_VALUE,
            ),
            id='zone_id_from_point',
        ),
        pytest.param(
            {
                'country_code': 'ng',
                'zone_id': 0,
                'position': [7.475537, 9.053398],
            },
            marks=pytest.mark.client_experiments3(
                consumer='client/rida',
                locale='en',
                experiment_name=_EXP_NAME,
                args=_build_expected_args(zone_id=0),
                value=_EXP_VALUE,
            ),
            id='zone_id_chose_from_request',
        ),
    ],
)
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_launch.sql'])
async def test_typed_experiments_zone_id_kwarg(web_app_client, payload: dict):
    response = await web_app_client.post(
        '/v1/launch',
        params=IOS_PARAMS,
        json=payload,
        headers={
            'Host': 'api.rida.app',
            **helpers.get_auth_headers(user_id=1449),
        },
    )

    assert response.status == 200
    response_json = await response.json()
    typed_experiments = {'items': [{'name': _EXP_NAME, 'value': _EXP_VALUE}]}
    assert response_json['data']['typed_experiments'] == typed_experiments
