import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from scooter_accumulator_plugins import *  # noqa: F403 F401


TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

# Эти поля присылает нанопай на команду open_cell:
# https://st.yandex-team.ru/SCOOTERDEV-257
OPEN_CELL_UNUSED_FIELDS = {
    'fan_is_on': False,
    'charger_is_on': False,
    'acc_voltage': 0.0,
    'acc_current': 0.0,
    'acc_charge': 0.0,
    'door_is_closed': True,
    'acc_bms_temperature1': 0.0,
    'cell_temperature': 0.0,
    'acc_bms_temperature2': 0.0,
    'acc_is_installed': False,
    'uart_is_connected': False,
    'acc_serial_number': '',
    'led_color': 'led_off',
    'led_pattern': 'led_off',
}


@pytest.fixture
def testpoint_cabinet_statuses(now):
    return {
        'messages': [
            {
                'topic': '$devices/aretl8d4gho7e6i3tvn1/state',
                'payload': {
                    'message_id': 'message_id1',
                    'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
                    'command_responses': [
                        {
                            'id': '1',
                            'command_name': 'cell_status',
                            'error_code': '200',
                            'error_message': '',
                            'response': {
                                'fan_is_on': False,
                                'charger_is_on': True,
                                'acc_voltage': 38.551,
                                'acc_current': 55,
                                'acc_charge': 0.0,
                                'door_is_closed': False,
                                'acc_bms_temperature1': 34.0,
                                'acc_bms_temperature2': 34.0,
                                'cell_temperature': 34.0,
                                'acc_is_installed': True,
                                'uart_is_connected': True,
                                'lock_is_closed': False,
                                'cell_id': 'cell_id2',
                                'acc_serial_number': '',
                                'led_color': 'led_off',
                                'led_pattern': 'led_off',
                            },
                        },
                        {
                            'id': 'wrong_status',
                            'command_name': 'cell_status',
                            'error_code': '200',
                            'error_message': '',
                            'response': {
                                'fan_is_on': False,
                                'charger_is_on': True,
                                'acc_voltage': 38.71,
                                'acc_current': 45,
                                'acc_charge': 0.0,
                                'door_is_closed': False,
                                'acc_bms_temperature1': 34.0,
                                'acc_bms_temperature2': 34.0,
                                'cell_temperature': 34.0,
                                'acc_is_installed': True,
                                'uart_is_connected': True,
                                'lock_is_closed': False,
                                'cell_id': 'non_existed_id',
                                'acc_serial_number': '0',
                                'led_color': 'led_off',
                                'led_pattern': 'led_off',
                            },
                        },
                        {
                            'id': '2',
                            'command_name': 'cell_status',
                            'error_code': '200',
                            'error_message': '',
                            'response': {
                                'fan_is_on': False,
                                'charger_is_on': True,
                                'acc_voltage': 38.71,
                                'acc_current': 45,
                                'acc_charge': 0.0,
                                'door_is_closed': False,
                                'acc_bms_temperature1': 34.0,
                                'acc_bms_temperature2': 34.0,
                                'cell_temperature': 34.0,
                                'acc_is_installed': True,
                                'uart_is_connected': True,
                                'lock_is_closed': False,
                                'cell_id': 'cell_id3',
                                'acc_serial_number': '0',
                                'led_color': 'led_off',
                                'led_pattern': 'led_off',
                            },
                        },
                    ],
                },
            },
            {
                'topic': '$devices/cabinet_id2/state',
                'payload': {
                    'message_id': 'message_id2',
                    'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
                    'command_responses': [
                        {
                            'id': '3',
                            'command_name': 'cell_status',
                            'error_code': '200',
                            'error_message': '',
                            'response': {
                                'fan_is_on': False,
                                'charger_is_on': True,
                                'acc_voltage': 38.851,
                                'acc_current': 55,
                                'acc_charge': 6,
                                'door_is_closed': True,
                                'acc_bms_temperature1': 34.0,
                                'acc_bms_temperature2': 34.0,
                                'cell_temperature': 34.0,
                                'acc_is_installed': False,
                                'uart_is_connected': True,
                                'lock_is_closed': True,
                                'cell_id': '1',
                                'acc_serial_number': 'serial_number4',
                                'led_color': 'led_off',
                                'led_pattern': 'led_off',
                            },
                        },
                    ],
                },
            },
            {
                'topic': '$devices/cabinet_id2/state',
                'payload': {
                    'message_id': 'message_id3',
                    'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
                    'command_responses': [
                        {
                            'id': '4',
                            'command_name': 'cell_status',
                            'error_code': '200',
                            'error_message': '',
                            'response': {
                                'fan_is_on': False,
                                'charger_is_on': True,
                                'acc_voltage': 338.851,
                                'acc_current': 45,
                                'acc_charge': 95,
                                'door_is_closed': True,
                                'acc_bms_temperature1': 34.0,
                                'acc_bms_temperature2': 34.0,
                                'cell_temperature': 34.0,
                                'acc_is_installed': True,
                                'uart_is_connected': True,
                                'lock_is_closed': True,
                                'cell_id': 'cell_id1',
                                'acc_serial_number': 'serial_number1',
                                'led_color': 'led_off',
                                'led_pattern': 'led_off',
                            },
                        },
                    ],
                },
            },
        ],
    }


@pytest.fixture
def tp_open_booked_acc_previous_ok(now):
    return {
        'open_cell': {
            'message_id': '123',
            'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
            'command_responses': [
                {
                    'id': '1',
                    'command_name': 'open_cell',
                    'error_code': '200',
                    'error_message': '',
                    'response': {
                        **OPEN_CELL_UNUSED_FIELDS,
                        'cell_id': 'cell_id2',
                        'lock_is_closed': False,
                    },
                },
            ],
        },
        'cell_status': {
            'message_id': '123',
            'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
            'command_responses': [
                {
                    'id': '1',
                    'command_name': 'cell_status',
                    'error_code': '200',
                    'error_message': '',
                    'response': {
                        'fan_is_on': False,
                        'charger_is_on': True,
                        'acc_voltage': 423.0,
                        'acc_current': 0,
                        'acc_charge': 0.0,
                        'door_is_closed': True,
                        'acc_bms_temperature1': 34.0,
                        'acc_bms_temperature2': 34.0,
                        'cell_temperature': 34.0,
                        'acc_is_installed': False,
                        'uart_is_connected': False,
                        'lock_is_closed': True,
                        'cell_id': 'cell_id1',
                        'acc_serial_number': '',
                        'led_color': 'led_off',
                        'led_pattern': 'led_off',
                    },
                },
            ],
        },
    }


@pytest.fixture
def tp_open_booked_acc_previous_bad(now):
    return {
        'open_cell': {
            'message_id': '123',
            'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
            'command_responses': [
                {
                    'id': '1',
                    'command_name': 'open_cell',
                    'error_code': '200',
                    'error_message': '',
                    'response': {
                        **OPEN_CELL_UNUSED_FIELDS,
                        'cell_id': 'cell_id1',
                        'lock_is_closed': False,
                    },
                },
            ],
        },
        'cell_status': {
            'message_id': '123',
            'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
            'command_responses': [
                {
                    'id': '1',
                    'command_name': 'cell_status',
                    'error_code': '200',
                    'error_message': '',
                    'response': {
                        'fan_is_on': False,
                        'charger_is_on': True,
                        'acc_voltage': 423.0,
                        'acc_current': 90,
                        'acc_charge': 0.0,
                        'door_is_closed': True,
                        'acc_bms_temperature1': 34.0,
                        'acc_bms_temperature2': 34.0,
                        'cell_temperature': 34.0,
                        'acc_is_installed': True,
                        'uart_is_connected': True,
                        'lock_is_closed': True,
                        'cell_id': 'cell_id1',
                        'acc_serial_number': 'serial_number1',
                        'led_color': 'led_off',
                        'led_pattern': 'led_off',
                    },
                },
            ],
        },
    }


@pytest.fixture
def tp_open_booked_acc_door_is_open(now):
    return {
        'message_id': '123',
        'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
        'command_responses': [
            {
                'id': '1',
                'command_name': 'cell_status',
                'error_code': '200',
                'error_message': '',
                'response': {
                    'fan_is_on': False,
                    'charger_is_on': True,
                    'acc_voltage': 423.0,
                    'acc_current': 90,
                    'acc_charge': 0.0,
                    'door_is_closed': False,
                    'acc_bms_temperature1': 34.0,
                    'acc_bms_temperature2': 34.0,
                    'cell_temperature': 34.0,
                    'acc_is_installed': True,
                    'uart_is_connected': True,
                    'lock_is_closed': False,
                    'cell_id': 'cell_id1',
                    'acc_serial_number': 'serial_number1',
                    'led_color': 'led_off',
                    'led_pattern': 'led_off',
                },
            },
        ],
    }


@pytest.fixture
def tp_open_booked_previous_ok(now):
    return {
        'open_cell': {
            'message_id': '123',
            'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
            'command_responses': [
                {
                    'id': '1',
                    'command_name': 'open_cell',
                    'error_code': '200',
                    'error_message': '',
                    'response': {
                        **OPEN_CELL_UNUSED_FIELDS,
                        'cell_id': 'cell_id2',
                        'lock_is_closed': False,
                    },
                },
            ],
        },
        'cell_status': {
            'message_id': '123',
            'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
            'command_responses': [
                {
                    'id': '1',
                    'command_name': 'cell_status',
                    'error_code': '200',
                    'error_message': '',
                    'response': {
                        'fan_is_on': False,
                        'charger_is_on': True,
                        'acc_voltage': 423.0,
                        'acc_current': 90,
                        'acc_charge': 0.0,
                        'door_is_closed': True,
                        'acc_bms_temperature1': 34.0,
                        'acc_bms_temperature2': 34.0,
                        'cell_temperature': 34.0,
                        'acc_is_installed': True,
                        'uart_is_connected': True,
                        'lock_is_closed': True,
                        'cell_id': 'cell_id1',
                        'acc_serial_number': 'serial_number1',
                        'led_color': 'led_off',
                        'led_pattern': 'led_off',
                    },
                },
            ],
        },
    }


@pytest.fixture
def tp_open_booked_previous_bad(now):
    return {
        'open_cell': {
            'message_id': '123',
            'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
            'command_responses': [
                {
                    'id': '1',
                    'command_name': 'open_cell',
                    'error_code': '200',
                    'error_message': '',
                    'response': {
                        **OPEN_CELL_UNUSED_FIELDS,
                        'cell_id': 'cell_id1',
                        'lock_is_closed': False,
                    },
                },
            ],
        },
        'cell_status': {
            'message_id': '123',
            'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
            'command_responses': [
                {
                    'id': '1',
                    'command_name': 'cell_status',
                    'error_code': '200',
                    'error_message': '',
                    'response': {
                        'fan_is_on': False,
                        'charger_is_on': True,
                        'acc_voltage': 423.0,
                        'acc_current': 30,
                        'acc_charge': 0.0,
                        'door_is_closed': True,
                        'acc_bms_temperature1': 34.0,
                        'acc_bms_temperature2': 34.0,
                        'cell_temperature': 34.0,
                        'acc_is_installed': False,
                        'uart_is_connected': False,
                        'lock_is_closed': True,
                        'cell_id': 'cell_id1',
                        'acc_serial_number': '',
                        'led_color': 'led_off',
                        'led_pattern': 'led_off',
                    },
                },
            ],
        },
    }


@pytest.fixture
def tp_validate_cell_without_accum(now):
    return {
        'message_id': '123',
        'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
        'command_responses': [
            {
                'id': '1',
                'command_name': 'cell_status',
                'error_code': '200',
                'error_message': '',
                'response': {
                    'fan_is_on': False,
                    'charger_is_on': True,
                    'acc_voltage': 423.0,
                    'acc_current': 0,
                    'acc_charge': 0.0,
                    'door_is_closed': True,
                    'acc_bms_temperature1': 34.0,
                    'acc_bms_temperature2': 34.0,
                    'cell_temperature': 34.0,
                    'acc_is_installed': False,
                    'uart_is_connected': False,
                    'lock_is_closed': True,
                    'cell_id': 'cell_id1',
                    'acc_serial_number': '',
                    'led_color': 'led_off',
                    'led_pattern': 'led_off',
                },
            },
        ],
    }


@pytest.fixture
def tp_validate_cell_with_accum(now):
    return {
        'message_id': '123',
        'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
        'command_responses': [
            {
                'id': '1',
                'command_name': 'cell_status',
                'error_code': '200',
                'error_message': '',
                'response': {
                    'fan_is_on': False,
                    'charger_is_on': True,
                    'acc_voltage': 423.0,
                    'acc_current': 90,
                    'acc_charge': 0.0,
                    'door_is_closed': True,
                    'acc_bms_temperature1': 34.0,
                    'acc_bms_temperature2': 34.0,
                    'cell_temperature': 34.0,
                    'acc_is_installed': True,
                    'uart_is_connected': True,
                    'lock_is_closed': True,
                    'cell_id': 'cell_id1',
                    'acc_serial_number': 'serial_number1',
                    'led_color': 'led_off',
                    'led_pattern': 'led_off',
                },
            },
        ],
    }


@pytest.fixture
def tp_validate_cell_is_open(now):
    return {
        'message_id': '123',
        'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
        'command_responses': [
            {
                'id': '1',
                'command_name': 'cell_status',
                'error_code': '200',
                'error_message': '',
                'response': {
                    'fan_is_on': False,
                    'charger_is_on': True,
                    'acc_voltage': 423.0,
                    'acc_current': 0,
                    'acc_charge': 0.0,
                    'door_is_closed': False,
                    'acc_bms_temperature1': 34.0,
                    'acc_bms_temperature2': 34.0,
                    'cell_temperature': 34.0,
                    'acc_is_installed': False,
                    'uart_is_connected': False,
                    'lock_is_closed': False,
                    'cell_id': 'cell_id1',
                    'acc_serial_number': '',
                    'led_color': 'led_off',
                    'led_pattern': 'led_off',
                },
            },
        ],
    }


@pytest.fixture
def tp_cell_statuses(now):
    return {
        'cell_id1': {
            'message_id': '123',
            'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
            'command_responses': [
                {
                    'id': '1',
                    'command_name': 'cell_status',
                    'error_code': '200',
                    'error_message': '',
                    'response': {
                        'fan_is_on': False,
                        'charger_is_on': True,
                        'acc_voltage': 423.0,
                        'acc_current': 0,
                        'acc_charge': 0.0,
                        'door_is_closed': False,
                        'acc_bms_temperature1': 34.0,
                        'acc_bms_temperature2': 34.0,
                        'cell_temperature': 34.0,
                        'acc_is_installed': True,
                        'uart_is_connected': False,
                        'lock_is_closed': True,
                        'cell_id': 'cell_id1',
                        'acc_serial_number': '',
                        'led_color': 'led_off',
                        'led_pattern': 'led_off',
                    },
                },
            ],
        },
        'cell_id2': {
            'message_id': '123',
            'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
            'command_responses': [
                {
                    'id': '1',
                    'command_name': 'cell_status',
                    'error_code': '200',
                    'error_message': '',
                    'response': {
                        'fan_is_on': False,
                        'charger_is_on': False,
                        'acc_voltage': 423.0,
                        'acc_current': 0,
                        'acc_charge': 0.0,
                        'door_is_closed': False,
                        'acc_bms_temperature1': 34.0,
                        'acc_bms_temperature2': 34.0,
                        'cell_temperature': 34.0,
                        'acc_is_installed': False,
                        'uart_is_connected': False,
                        'lock_is_closed': False,
                        'cell_id': 'cell_id2',
                        'acc_serial_number': '',
                        'led_color': 'led_off',
                        'led_pattern': 'led_off',
                    },
                },
            ],
        },
        'cell_id3': {
            'message_id': '123',
            'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
            'command_responses': [
                {
                    'id': '1',
                    'command_name': 'cell_status',
                    'error_code': '200',
                    'error_message': '',
                    'response': {
                        'fan_is_on': False,
                        'charger_is_on': False,
                        'acc_voltage': 423.0,
                        'acc_current': 0,
                        'acc_charge': 0.0,
                        'door_is_closed': False,
                        'acc_bms_temperature1': 34.0,
                        'acc_bms_temperature2': 34.0,
                        'cell_temperature': 34.0,
                        'acc_is_installed': False,
                        'uart_is_connected': False,
                        'lock_is_closed': True,
                        'cell_id': 'cell_id3',
                        'acc_serial_number': '',
                        'led_color': 'led_off',
                        'led_pattern': 'led_off',
                    },
                },
            ],
        },
        'cell_id4': {
            'message_id': '123',
            'timestamp': now.strftime(format=TIMESTAMP_FORMAT),
            'command_responses': [
                {
                    'id': '1',
                    'command_name': 'cell_status',
                    'error_code': '200',
                    'error_message': '',
                    'response': {
                        'fan_is_on': False,
                        'charger_is_on': False,
                        'acc_voltage': 423.0,
                        'acc_current': 0,
                        'acc_charge': 0.0,
                        'door_is_closed': True,
                        'acc_bms_temperature1': 34.0,
                        'acc_bms_temperature2': 34.0,
                        'cell_temperature': 34.0,
                        'acc_is_installed': True,
                        'uart_is_connected': True,
                        'lock_is_closed': True,
                        'cell_id': 'cell_id4',
                        'acc_serial_number': '',
                        'led_color': 'led_off',
                        'led_pattern': 'led_off',
                    },
                },
            ],
        },
    }
