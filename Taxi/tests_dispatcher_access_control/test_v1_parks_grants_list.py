import json

import pytest

from testsuite.utils import ordered_object

from tests_dispatcher_access_control import utils


def get_grants(with_marketplace=False, enabled_list=None):
    return {
        'grants': [
            utils.make_grant(x, x in sorted(enabled_list))
            if enabled_list is not None
            else utils.make_grant(x)
            for x in (
                sorted(utils.GRANTS)
                if not with_marketplace
                else sorted(utils.GRANTS + utils.GRANTS_MARKETPLACE)
            )
        ],
    }


def build_request(group_id=None):
    park = {'id': 'park_valid1'}
    if group_id:
        park['group'] = {'id': group_id}
    return {'query': {'park': park}}


ENDPOINT = 'v1/parks/grants/list'

BAD_REQUEST = {'query': {'park': {'id': 'park_invalid1'}}}

TEST_MARKETPLACE_PARAMS = [
    (
        BAD_REQUEST,
        {
            'enable': False,
            'cities': [],
            'countries': [],
            'dbs': [],
            'home_url': '',
        },
        400,
        {'code': '400', 'message': 'Park not found'},
    ),
    (
        build_request(),
        {
            'enable': False,
            'cities': [],
            'countries': [],
            'dbs': [],
            'home_url': '',
        },
        200,
        get_grants(False),
    ),
    (
        build_request(),
        {
            'enable': True,
            'cities': [],
            'countries': [],
            'dbs': [],
            'home_url': '',
        },
        200,
        get_grants(True),
    ),
    (
        build_request(),
        {
            'enable': True,
            'cities': [],
            'countries': [],
            'dbs': ['park_valid1'],
            'home_url': '',
        },
        200,
        get_grants(True),
    ),
    (
        build_request(),
        {
            'enable': True,
            'cities': ['city1'],
            'countries': [],
            'dbs': [],
            'home_url': '',
        },
        200,
        get_grants(True),
    ),
    (
        build_request(),
        {
            'enable': True,
            'cities': [],
            'countries': ['cid1'],
            'dbs': [],
            'home_url': '',
        },
        200,
        get_grants(True),
    ),
    (
        build_request(),
        {
            'enable': True,
            'cities': ['some_city'],
            'countries': ['some_country'],
            'dbs': ['some_park_id'],
            'home_url': '',
        },
        200,
        get_grants(False),
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1': json.dumps(
                {'Name': 'Name1', 'Group': 'Group1', 'YandexUid': '100'},
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'payload, marketplace, code, expected_response', TEST_MARKETPLACE_PARAMS,
)
async def test_get_grants(
        taxi_dispatcher_access_control,
        taxi_config,
        mock_fleet_parks_list,
        payload,
        marketplace,
        code,
        expected_response,
):
    taxi_config.set_values(dict(TAXIMETER_MARKETPLACE=marketplace))
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        json=payload,
        headers={'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == code
    ordered_object.assert_eq(response.json(), expected_response, ['grants'])


GROUPS_PARAMS = [
    (
        build_request(group_id='1'),
        get_grants(enabled_list=['driver_read_common', 'driver_write_common']),
    ),
    (
        build_request(group_id='2'),
        get_grants(enabled_list=['car_read_common', 'car_write_common']),
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1': json.dumps(
                {'Name': 'Name1', 'Group': '1', 'YandexUid': '100'},
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'1': json.dumps({'Name': 'Group1'})},
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'2': json.dumps({'Name': 'Group2'})},
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid1:1',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '12',
                        '13',
                        '21',
                        '22',
                        '23',
                        '24',
                        '32',
                        '33',
                        '41',
                        '42',
                        '43',
                        '53',
                        '55',
                        '56',
                        'parks',
                        'cashbox',
                        'carriers',
                        '61',
                        '71',
                        '72',
                        '75',
                        '76',
                        '77',
                        'recurringPayments',
                        'supportChats',
                        'segments',
                        '82',
                        '44',
                        'map',
                    ],
                },
            ),
            'Driver': json.dumps(
                {
                    'tabtaximeter': True,
                    'tabbalance': True,
                    'tabstatus': True,
                    'tabgps': True,
                    'tabrating': True,
                    'tabrobot': True,
                    'tabhistory': True,
                    'tabcomplaints': True,
                    'tabdocuments': True,
                    'tabrecords': True,
                    'tabaccess': True,
                    'tabcheckcar': True,
                    'disableLimit': True,
                    'disableFIO': True,
                    'disableLicense': True,
                    'disablePriority': True,
                    'disablePhone': True,
                    'disableAlhoritm': True,
                    'disableChangeCar': True,
                    'disableChangeStatus': True,
                    'disableProvider': True,
                    'disableRobot': True,
                    'disableBalancePlus': True,
                    'disableBalanceMinus': True,
                    'disableDocumentAdd': True,
                    'disableDocumentDelete': True,
                    'disableScoringRead': True,
                    'disableScoringBuy': True,
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid1:2',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '12',
                        '13',
                        '21',
                        '22',
                        '23',
                        '24',
                        '32',
                        '33',
                        '41',
                        '42',
                        '43',
                        '52',
                        '53',
                        '56',
                        'parks',
                        'cashbox',
                        'carriers',
                        '61',
                        '71',
                        '72',
                        '75',
                        '76',
                        '77',
                        'recurringPayments',
                        'supportChats',
                        'segments',
                        '82',
                        '44',
                        'map',
                    ],
                },
            ),
            'Car': json.dumps({'tabdrivers': True, 'tabdocuments': True}),
        },
    ],
)
@pytest.mark.parametrize('payload, expected_grants', GROUPS_PARAMS)
async def test_parks_group_grants(
        taxi_dispatcher_access_control,
        mock_fleet_parks_list,
        payload,
        expected_grants,
):
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        json=payload,
        headers={'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 200
    assert (
        sorted(response.json()['grants'], key=lambda elem: elem['id'])
        == expected_grants['grants']
    )
