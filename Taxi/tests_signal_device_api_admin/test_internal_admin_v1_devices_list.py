# pylint: disable=too-many-lines
import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'internal-admin/signal-device-api-admin/v1/devices/list'

CONSUMER = 'signal_device_api_admin/internal_admin_signal_device_api_admin_v1_devices_list'  # noqa: E501 pylint: disable=line-too-long
EXPERIMENTS_COND = {
    'match': {
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': ['AB4', 'AB6'],
                'arg_name': 'serial_number',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    'name': 'some1',
    'consumers': [CONSUMER],
    'clauses': [],
    'default_value': {
        'data': '1.0.0',
        'linux': '1.1.0',
        'rtos': '1.1.1',
        'is_critical': False,
    },
}


@pytest.fixture(name='signal_device_message_api', autouse=True)
def _mock_signal_device_message_api(mockserver):
    @mockserver.json_handler(
        '/signal-device-message-api/internal/v1/signal-device-message-api/mqtt-client-ids/retrieve',  # noqa: E501 pylint: disable=line-too-long
    )
    def _mock_mqtt_client_ids_retrieve(request):
        return {
            'devices': [
                {'serial_number': 'AB4', 'client_id': 'some_mqtt_client_id4'},
                {'serial_number': 'AB6', 'client_id': 'some_mqtt_client_id6'},
                {'serial_number': 'AB3', 'client_id': 'some_mqtt_client_id3'},
            ],
        }


def _response_projection(response, proj):
    def projection(obj, proj):
        assert isinstance(obj, dict)

        if isinstance(proj, list):
            res = {}
            for proj_elem in proj:
                if isinstance(proj_elem, dict):
                    res.update(projection(obj, proj_elem))
                elif isinstance(proj_elem, tuple):
                    assert len(proj_elem) == 2
                    if proj_elem[0] in obj:
                        tmp = projection(obj[proj_elem[0]], proj_elem[1])
                        res[proj_elem[0]] = tmp
                else:
                    res.update(projection(obj, proj_elem))
            return res
        if isinstance(proj, dict):
            return projection(obj, [(k, v) for k, v in proj.items()])
        if proj in obj:
            return {proj: obj[proj]}
        return {}

    return {'items': [projection(obj, proj) for obj in response['items']]}


DEVICE1 = {
    'device': {
        'id': 'move_to_other_park',
        'serial_number': 'AB4',
        'imei': '__IMEI1__',
        'mqtt_client_id': 'some_mqtt_client_id4',
    },
    'park_device_profile': {'park_id': 'p1'},
    'declared_serial_number': {
        'hw_id': 1,
        'hw_revision': 2,
        'factory_id': 3,
        'batch_number': 4,
        'order_number': 5,
        'manufacturing_date': '2021-01-08T00:00:00+00:00',
    },
    'status': {
        'sim_iccid': '89310410106543789300',
        'sim_imsi': '502130123456788',
        'software_version': '2.031-1',
        'gnss_latitude': 25.1111,
        'gnss_longitude': 12.2142,
        'cpu_temperature': 36,
        'disk_bytes_free_space': 107374182,
        'root_bytes_free_space': 107374183,
        'ram_bytes_free_space': 10737418,
        'updated_at': '2020-08-11T13:50:03+00:00',
    },
    'api_last_responses': {
        'v1_binaries_check_at': '2021-02-05T00:00:00+00:00',
        'v1_registration_at': '2021-02-01T00:00:00+00:00',
    },
    'expected_software_version': {
        'data': '1.0.0',
        'linux': '1.1.0',
        'rtos': '1.1.1',
        'is_critical': False,
    },
}

DEVICE2 = {
    'device': {
        'id': 'another_park_again',
        'serial_number': 'AB6',
        'imei': '__IMEI2__',
        'mqtt_client_id': 'some_mqtt_client_id6',
    },
    'park_device_profile': {},
    'declared_serial_number': {
        'hw_id': 1,
        'factory_id': 3,
        'batch_number': 4,
        'order_number': 15,
        'manufacturing_date': '2021-02-01T00:00:00+00:00',
    },
    'status': {
        'sim_iccid': '81522410106543789300',
        'sim_imsi': '102130123456789',
        'software_version': '000002.31-00002',
        'gnss_latitude': 73.3242,
        'gnss_longitude': 54.9885,
        'cpu_temperature': 36,
        'disk_bytes_free_space': 107374182,
        'root_bytes_free_space': 107374183,
        'ram_bytes_free_space': 10737418,
        'updated_at': '2020-08-11T14:59:03+00:00',
    },
    'api_last_responses': {},
    'expected_software_version': {
        'data': '1.0.0',
        'linux': '1.1.0',
        'rtos': '1.1.1',
        'is_critical': False,
    },
}

DEVICE3 = {
    'device': {'id': 'another_park', 'serial_number': 'AB5'},
    'park_device_profile': {'park_id': 'p2'},
    'declared_serial_number': {
        'hw_id': 1,
        'hw_revision': 2,
        'factory_id': 3,
        'batch_number': 4,
        'order_number': 5,
        'manufacturing_date': '2021-02-01T00:00:00+00:00',
    },
    'status': {
        'sim_iccid': '89310410106543789300',
        'sim_imsi': '502130123456788',
        'software_version': '2.0031-002',
        'cpu_temperature': 26,
        'disk_bytes_free_space': 117374182,
        'root_bytes_free_space': 107374183,
        'ram_bytes_free_space': 10737418,
        'updated_at': '2020-08-11T14:58:03+00:00',
    },
    'api_last_responses': {},
    'expected_software_version': {},
}

DEVICE4 = {
    'device': {
        'id': 'just_device',
        'serial_number': 'AB3',
        'mqtt_client_id': 'some_mqtt_client_id3',
    },
    'park_device_profile': {},
    'declared_serial_number': {
        'hw_id': 11,
        'hw_revision': 22,
        'factory_id': 3,
        'batch_number': 14,
        'order_number': 5,
        'manufacturing_date': '2021-01-08T00:00:00+00:00',
    },
    'status': {},
    'api_last_responses': {
        'v1_events_at': '2021-02-01T00:00:00+00:00',
        'v1_binaries_download_at': '2021-03-01T00:00:00+00:00',
        'v1_binaries_check_at': '2021-04-01T00:00:00+00:00',
        'v1_registration_at': '2021-05-01T00:00:00+00:00',
    },
    'expected_software_version': {},
}

DEVICE5 = {
    'device': {'id': 'without_driver', 'serial_number': 'AB2'},
    'park_device_profile': {},
    'declared_serial_number': {
        'hw_revision': 1,
        'factory_id': 55,
        'batch_number': 42,
        'order_number': 51,
        'manufacturing_date': '2021-01-04T00:00:00+00:00',
    },
    'status': {},
    'api_last_responses': {},
    'expected_software_version': {},
}

DEVICE6 = {
    'device': {'id': 'has_everything', 'serial_number': 'AB1'},
    'park_device_profile': {'park_id': 'p1'},
    'declared_serial_number': {
        'hw_id': 1,
        'hw_revision': 2,
        'factory_id': 3,
        'batch_number': 4,
        'order_number': 5,
        'manufacturing_date': '2021-01-05T00:00:00+00:00',
    },
    'status': {
        'sim_iccid': '89310410106543789301',
        'sim_imsi': '502130123456789',
        'software_version': '02.0031-3',
        'gnss_latitude': 53.3242,
        'gnss_longitude': 34.9885,
        'cpu_temperature': 36,
        'disk_bytes_free_space': 107374182,
        'root_bytes_free_space': 107374183,
        'ram_bytes_free_space': 10737418,
        'updated_at': '2020-08-11T11:50:03+00:00',
    },
    'api_last_responses': {'v1_registration_at': '2021-02-01T00:00:00+00:00'},
    'expected_software_version': {},
}

# ORDER: AB4, AB6, AB5, AB3, AB2, AB1
ALL_ITEMS = [DEVICE1, DEVICE2, DEVICE3, DEVICE4, DEVICE5, DEVICE6]


@pytest.mark.experiments3(**EXPERIMENTS_COND)
@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'fields, filter_conditions, filter_conditions_operator, '
    'response_projection, expected_response',
    [
        (None, None, None, None, {'items': ALL_ITEMS}),
        (
            ['devices.id', 'devices.imei', 'devices.serial_number'],
            None,
            None,
            {'device': ['id', 'imei', 'serial_number']},
            {'items': ALL_ITEMS},
        ),
        (
            ['devices.serial_number'],
            None,
            None,
            {'device': ['serial_number']},
            {'items': ALL_ITEMS},
        ),
        (
            ['park_device_profiles.park_id'],
            None,
            None,
            {'park_device_profile': ['park_id']},
            {'items': ALL_ITEMS},
        ),
        (
            ['declared_serial_numbers.hw_id', 'devices.mqtt_client_id'],
            None,
            None,
            {
                'declared_serial_number': ['hw_id'],
                'device': ['mqtt_client_id'],
            },
            {'items': ALL_ITEMS},
        ),
        (
            ['expected_software_versions.rtos'],
            None,
            None,
            {'expected_software_version': ['rtos']},
            {'items': ALL_ITEMS},
        ),
        (
            [
                'devices.id',
                'declared_serial_numbers.hw_id',
                'declared_serial_numbers.manufacturing_date',
                'park_device_profiles.park_id',
                'statuses.sim_iccid',
                'statuses.software_version',
                'devices.mqtt_client_id',
            ],
            None,
            None,
            {
                'device': ['id', 'mqtt_client_id'],
                'declared_serial_number': ['hw_id', 'manufacturing_date'],
                'park_device_profile': ['park_id'],
                'status': ['sim_iccid', 'software_version'],
            },
            {'items': ALL_ITEMS},
        ),
        (
            None,
            [
                {
                    'field': 'declared_serial_numbers.hw_id',
                    'comparison': 'eq',
                    'value': 1,
                },
            ],
            'and',
            None,
            {'items': [DEVICE1, DEVICE2, DEVICE3, DEVICE6]},
        ),
        (
            None,
            [
                {
                    'field': 'declared_serial_numbers.hw_id',
                    'comparison': 'ge',
                    'value': 1,
                },
            ],
            'and',
            None,
            {'items': [DEVICE1, DEVICE2, DEVICE3, DEVICE4, DEVICE6]},
        ),
        (
            None,
            [
                {
                    'field': 'devices.serial_number',
                    'comparison': 'in',
                    'value': ['AB2', 'AB3'],
                },
            ],
            'and',
            None,
            {'items': [DEVICE4, DEVICE5]},
        ),
        (
            None,
            [
                {
                    'field': 'devices.serial_number',
                    'comparison': 'not_in',
                    'value': ['AB2', 'AB3'],
                },
            ],
            'and',
            None,
            {'items': [DEVICE1, DEVICE2, DEVICE3, DEVICE6]},
        ),
        (
            None,
            [
                {
                    'field': 'declared_serial_numbers.hw_id',
                    'comparison': 'lt',
                    'value': 1,
                },
            ],
            'and',
            None,
            {'items': []},
        ),
        (
            None,
            [
                {
                    'field': 'declared_serial_numbers.manufacturing_date',
                    'comparison': 'lt',
                    'value': '2021-01-08T00:00:00+00:00',
                },
            ],
            'and',
            None,
            {'items': [DEVICE5, DEVICE6]},
        ),
        (
            None,
            [
                {
                    'field': 'declared_serial_numbers.hw_id',
                    'comparison': 'ne',
                    'value': 1,
                },
            ],
            'and',
            None,
            {'items': [DEVICE4]},
        ),
        (
            [
                'declared_serial_numbers.hw_id',
                'declared_serial_numbers.manufacturing_date',
                'park_device_profiles.park_id',
                'statuses.sim_iccid',
                'statuses.software_version',
                'devices.mqtt_client_id',
            ],
            [
                {
                    'field': 'declared_serial_numbers.hw_id',
                    'comparison': 'ge',
                    'value': 1,
                },
                {
                    'field': 'devices.id',
                    'comparison': 'like',
                    'value': 'nother_park',
                },
            ],
            'and',
            {
                'device': ['mqtt_client_id'],
                'declared_serial_number': ['hw_id', 'manufacturing_date'],
                'park_device_profile': ['park_id'],
                'status': ['sim_iccid', 'software_version'],
            },
            {'items': [DEVICE2, DEVICE3]},
        ),
        (
            ['statuses.sim_iccid'],
            [
                {
                    'field': 'declared_serial_numbers.hw_id',
                    'comparison': 'ge',
                    'value': 1,
                },
                {
                    'field': 'devices.id',
                    'comparison': 'like',
                    'value': 'nother_park',
                },
                {
                    'field': 'devices.id',
                    'comparison': 'ne',
                    'value': 'another_park',
                },
            ],
            'and',
            {'status': ['sim_iccid']},
            {'items': [DEVICE2]},
        ),
        (
            None,
            [
                {
                    'field': 'declared_serial_numbers.hw_id',
                    'comparison': 'ne',
                    'value': 1,
                },
                {
                    'field': 'devices.id',
                    'comparison': 'like',
                    'value': 'nother_park',
                },
            ],
            'or',
            None,
            {'items': [DEVICE2, DEVICE3, DEVICE4]},
        ),
    ],
)
async def test_internal_devices_list(
        taxi_signal_device_api_admin,
        fields,
        filter_conditions,
        filter_conditions_operator,
        response_projection,
        expected_response,
        mockserver,
):
    body = {}
    if fields is not None:
        body['fields'] = fields
    if filter_conditions is not None:
        body['filter'] = {
            'conditions': filter_conditions,
            'conditions_operator': filter_conditions_operator,
        }

    if response_projection is not None:
        expected_response = _response_projection(
            expected_response, response_projection,
        )

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers={**web_common.PARTNER_HEADERS_1},
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response


@pytest.mark.experiments3(**EXPERIMENTS_COND)
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_INTERNAL_DEVICES_LIST_LIMIT={'limit': 3},
)
@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'filter_conditions, filter_conditions_operator, '
    'expected_response1, expected_response2',
    [
        pytest.param(
            None,
            None,
            {
                'items': [DEVICE1, DEVICE2, DEVICE3, DEVICE4],
                'cursor': utils.get_encoded_internal_devices_list_cursor(
                    created_at='2019-12-17T06:38:54.000001+00:00',
                    public_id='just_device',
                ),
            },
            {'items': [DEVICE5, DEVICE6]},
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_ADMIN_INTERNAL_DEVICES_LIST_LIMIT={
                    'limit': 4,
                },
            ),
        ),
        pytest.param(
            [
                {
                    'field': 'declared_serial_numbers.hw_id',
                    'comparison': 'ge',
                    'value': 1,
                },
                {
                    'field': 'devices.id',
                    'comparison': 'like',
                    'value': 'nother_park',
                },
            ],
            'and',
            {
                'items': [DEVICE2],
                'cursor': utils.get_encoded_internal_devices_list_cursor(
                    created_at='2019-12-17T07:38:54.000001+00:00',
                    public_id='another_park_again',
                ),
            },
            {
                'items': [DEVICE3],
                'cursor': utils.get_encoded_internal_devices_list_cursor(
                    created_at='2019-12-17T07:38:54.000001+00:00',
                    public_id='another_park',
                ),
            },
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_ADMIN_INTERNAL_DEVICES_LIST_LIMIT={
                    'limit': 1,
                },
            ),
        ),
    ],
)
async def test_internal_devices_list_with_cursor(
        taxi_signal_device_api_admin,
        filter_conditions,
        filter_conditions_operator,
        expected_response1,
        expected_response2,
        mockserver,
):
    body = {}
    if filter_conditions is not None:
        body['filter'] = {
            'conditions': filter_conditions,
            'conditions_operator': filter_conditions_operator,
        }

    response1 = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers={**web_common.PARTNER_HEADERS_1},
    )

    assert response1.status_code == 200, response1.text
    assert response1.json() == expected_response1

    body['cursor'] = expected_response1['cursor']
    response2 = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers={**web_common.PARTNER_HEADERS_1},
    )

    assert response2.status_code == 200, response2.text
    assert response2.json() == expected_response2
