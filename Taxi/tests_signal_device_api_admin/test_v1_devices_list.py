import pytest

ENDPOINT = 'v1/devices/list'

DEVICE_1_ID = 'e58e753c44e548ce9edaec0e0ef9c8c1'
DEVICE_1 = {
    'device': {
        'name': 'SignalQ1_1',
        'is_alive': True,
        'device_id': DEVICE_1_ID,
        'public_key': 'pub_key_1',
        'imei': '990000862471854',
        'mac_address': {'wlan0': '07:f2:74:af:8b:b1'},
        'serial_number': 'AB1',
        'hardware_version': '1.01',
        'created_at': '2019-12-17T07:38:54+00:00',
        'updated_at': '2019-12-17T07:38:54+00:00',
    },
    'status': {
        'cpu_temperature': 36,
        'disk_bytes_free_space': 107374182,
        'disk_bytes_total_space': 1073741824,
        'ram_bytes_free_space': 10737418,
        'root_bytes_free_space': 107374183,
        'root_bytes_total_space': 1073741835,
        'sim_imsi': '502130123456789',
        'gps_position': {'lat': 73.3242, 'lon': 54.9885},
        'sim_iccid': '89310410106543789301',
        'sim_phone_number': '+7 (913) 617-82-58',
        'software_version': '2.31',
        'uptime_ms': 90555,
        'status_at': '2020-01-23T15:44:02+00:00',
        'created_at': '2019-09-04T08:18:54+00:00',
        'updated_at': '2020-01-23T15:44:30+00:00',
    },
    'vehicle': {'plate_number': 'K 444 AB 55'},
    'partner': {'name': '54591353'},
}

DEVICE_2_ID = '4306de3dfd82406d81ea3c098c80e9ba'
DEVICE_2 = {
    'device': {
        'name': 'custom%_name',
        'is_alive': True,
        'device_id': DEVICE_2_ID,
        'public_key': 'pub_key_2',
        'imei': '351756051523999',
        'mac_address': {
            'eth0': '78:ff:28:f2:69:b1',
            'wlan0': 'a5:90:c5:98:95:48',
        },
        'serial_number': 'AB12FE45DD',
        'hardware_version': '1.02',
        'total_ram_bytes': 65536,
        'comment': '{}',
        'created_at': '2019-12-17T08:38:54+00:00',
        'updated_at': '2019-12-17T08:38:54+00:00',
    },
    'status': {
        'cpu_temperature': 77,
        'disk_bytes_free_space': 10000000000,
        'disk_bytes_total_space': 10000000001,
        'ram_bytes_free_space': 1000000,
        'root_bytes_free_space': 2000000000,
        'root_bytes_total_space': 20000000000,
        'sim_imsi': '502130123456789',
        'sim_iccid': '89658808121000111424',
        'sim_phone_number': '+7 (905) 663-92-51',
        'software_version': '1.1',
        'uptime_ms': 600000,
        'status_at': '2020-01-14T15:44:44+00:00',
        'created_at': '2019-09-04T09:00:00+00:00',
        'updated_at': '2020-01-14T15:44:46+00:00',
    },
    'partner': {'name': '54591353'},
    'vehicle': {'plate_number': 'K 123 KK 777'},
}

DEVICE_3_ID = '6b3b9123656f4a808ce3e7c52a0be835'
DEVICE_3 = {
    'device': {
        'name': 'signalq1_3',
        'is_alive': True,
        'device_id': DEVICE_3_ID,
        'public_key': 'pub_key_3',
        'mac_address': {
            'usb_modem': '63:72:bf:26:5a:b3',
            'wlan0': 'ca:ff:4d:64:f2:79',
        },
        'serial_number': 'FFEE33',
        'hardware_version': '2.01',
        'total_ram_bytes': 256,
        'comment': '{"foo":"bar"}',
        'created_at': '2019-12-17T09:38:54+00:00',
        'updated_at': '2019-12-17T09:38:54+00:00',
    },
    'partner': {'name': '54591353'},
}

DEVICE_4_ID = '77748dae0a3244ebb9e1b8d244982c28'
DEVICE_4 = {
    'device': {
        'name': '',
        'is_alive': False,
        'device_id': DEVICE_4_ID,
        'public_key': 'pub_key_4',
        'mac_address': {
            'eth0': 'fb:43:3c:cd:1e:8f',
            'usb_modem': '23:5f:72:1c:04:39',
            'wlan0': '32:41:27:d5:fb:ed',
        },
        'serial_number': 'FFFDEAD4',
        'hardware_version': '2.02',
        'created_at': '2019-12-17T10:38:54+00:00',
        'updated_at': '2019-12-17T11:38:54+00:00',
    },
    'status': {
        'cpu_temperature': 0,
        'disk_bytes_free_space': 0,
        'disk_bytes_total_space': 0,
        'ram_bytes_free_space': 0,
        'root_bytes_free_space': 0,
        'root_bytes_total_space': 0,
        'sim_imsi': 'imsi_4',
        'sim_iccid': 'iccid_4',
        'sim_phone_number': 'phone_4',
        'software_version': 'sw_4',
        'uptime_ms': 20200000,
        'status_at': '2020-01-01T01:01:01+00:00',
        'created_at': '2020-01-01T01:01:01+00:00',
        'updated_at': '2020-01-01T01:01:01+00:00',
    },
    'partner': {'name': '121766829'},
}

DEVICE_5_ID = '12349fbd4c7767aef1a6c4a123456789'
DEVICE_5 = {
    'device': {
        'name': '',
        'is_alive': False,
        'device_id': DEVICE_5_ID,
        'public_key': 'pub_key_5',
        'mac_address': {'wlan0': '11:11:11:22:22:ff'},
        'serial_number': '1337587103',
        'hardware_version': 'hw_5',
        'total_ram_bytes': 65536,
        'created_at': '2019-12-17T10:38:54+00:00',
        'updated_at': '2019-12-17T11:38:54+00:00',
    },
    'status': {
        'cpu_temperature': 0,
        'disk_bytes_free_space': 0,
        'disk_bytes_total_space': 0,
        'ram_bytes_free_space': 0,
        'root_bytes_free_space': 0,
        'root_bytes_total_space': 0,
        'sim_imsi': 'imsi_5',
        'sim_iccid': 'iccid_5',
        'sim_phone_number': 'phone_5',
        'software_version': 'sw_5',
        'uptime_ms': 21474836471111,
        'status_at': '2020-01-01T01:01:01+00:00',
        'created_at': '2020-01-01T01:01:01+00:00',
        'updated_at': '2020-01-01T01:01:01+00:00',
    },
}

DEVICE_6_ID = '12349fbd4c7767578456c4a123456789'
DEVICE_6 = {
    'device': {
        'name': 'signalq1_6',
        'is_alive': True,
        'device_id': DEVICE_6_ID,
        'public_key': 'pub_key_6',
        'imei': '190000862471854',
        'mac_address': {'wlan0': '12:41:27:d5:fb:ed'},
        'serial_number': 'FFFFFF666',
        'hardware_version': '2.06',
        'created_at': '2019-12-17T11:49:54+00:00',
        'updated_at': '2019-12-17T12:50:54+00:00',
    },
    'status': {
        'cpu_temperature': 36,
        'disk_bytes_free_space': 107374182,
        'disk_bytes_total_space': 1073741824,
        'ram_bytes_free_space': 10737418,
        'root_bytes_free_space': 107374183,
        'root_bytes_total_space': 1073741835,
        'sim_imsi': '502130123456789',
        'gps_position': {'lat': 73.3242, 'lon': 54.9885},
        'sim_iccid': '89310410106543789306',
        'sim_phone_number': '+7 (913) 617-82-56',
        'software_version': '6.31',
        'uptime_ms': 90555,
        'status_at': '2020-01-23T15:44:02+00:00',
        'created_at': '2019-12-17T14:18:54+00:00',
        'updated_at': '2020-01-23T15:44:30+00:00',
    },
    'vehicle': {'plate_number': 'B 666 AB 52'},
    'partner': {'name': '54591353'},
}

OK_PARAMS = [
    (
        {},
        {
            'devices': [
                DEVICE_1,
                DEVICE_2,
                DEVICE_3,
                DEVICE_4,
                DEVICE_5,
                DEVICE_6,
            ],
        },
    ),
    ({'limit': 3}, {'devices': [DEVICE_1, DEVICE_2, DEVICE_3]}),
    ({'limit': 2, 'offset': 1}, {'devices': [DEVICE_2, DEVICE_3]}),
    ({'offset': 6}, {'devices': []}),
    (
        {'query': {'device': {'ids': [DEVICE_2_ID, DEVICE_1_ID]}}},
        {'devices': [DEVICE_1, DEVICE_2]},
    ),
    ({'query': {'device': {'ids': [DEVICE_4_ID]}}}, {'devices': [DEVICE_4]}),
    ({'query': {'device': {'ids': ['INVALID_ID']}}}, {'devices': []}),
    (
        {'query': {'device': {'is_alive': True}}},
        {'devices': [DEVICE_1, DEVICE_2, DEVICE_3, DEVICE_6]},
    ),
    (
        {'query': {'device': {'is_alive': False}}},
        {'devices': [DEVICE_4, DEVICE_5]},
    ),
    ({'query': {'device': {'name': 'SignalQ1_1'}}}, {'devices': [DEVICE_1]}),
    ({'query': {'device': {'name': 'cust%'}}}, {'devices': [DEVICE_2]}),
    (
        {'query': {'device': {'serial_number': 'ab12fe45dd'}}},
        {'devices': [DEVICE_2]},
    ),
    (
        {'query': {'device': {'serial_number': 'AB12FE45DD'}}},
        {'devices': [DEVICE_2]},
    ),
    (
        {'query': {'device': {'hardware_version': '2%'}}},
        {'devices': [DEVICE_3, DEVICE_4, DEVICE_6]},
    ),
    (
        {'query': {'device': {'hardware_version': '1.0_'}}},
        {'devices': [DEVICE_1, DEVICE_2]},
    ),
    (
        {'query': {'status': {'software_version': '%'}}},
        {'devices': [DEVICE_1, DEVICE_2, DEVICE_4, DEVICE_5, DEVICE_6]},
    ),
    (
        {'query': {'status': {'software_version': '2.%'}}},
        {'devices': [DEVICE_1]},
    ),
    (
        {'query': {'partner': {'name': '54591353'}}},
        {'devices': [DEVICE_1, DEVICE_2, DEVICE_3, DEVICE_6]},
    ),
    ({'query': {'partner': {'name': '121766829'}}}, {'devices': [DEVICE_4]}),
    ({'query': {'partner': {'name': 'INVALID_PARTNER'}}}, {'devices': []}),
    (
        {'query': {'vehicle': {'plate_number': 'K 444 AB 55'}}},
        {'devices': [DEVICE_1]},
    ),
    (
        {'query': {'vehicle': {'plate_number': '%'}}},
        {'devices': [DEVICE_1, DEVICE_2, DEVICE_6]},
    ),
    (
        {'sort_order': {'field': 'status.updated_at', 'direction': 'asc'}},
        {
            'devices': [
                DEVICE_4,
                DEVICE_5,
                DEVICE_2,
                DEVICE_1,
                DEVICE_6,
                DEVICE_3,
            ],
        },
    ),
    (
        {'sort_order': {'field': 'status.updated_at', 'direction': 'desc'}},
        {
            'devices': [
                DEVICE_3,
                DEVICE_1,
                DEVICE_6,
                DEVICE_2,
                DEVICE_4,
                DEVICE_5,
            ],
        },
    ),
    (
        {'query': {'status': {'updated_at': {'empty': True}}}},
        {
            'devices': [
                DEVICE_1,
                DEVICE_2,
                DEVICE_3,
                DEVICE_4,
                DEVICE_5,
                DEVICE_6,
            ],
        },
    ),
    (
        {'query': {'status': {'updated_at': {'empty': False}}}},
        {'devices': [DEVICE_1, DEVICE_2, DEVICE_4, DEVICE_5, DEVICE_6]},
    ),
    (
        {
            'query': {
                'status': {
                    'updated_at': {
                        'empty': True,
                        'from': '2020-01-23T15:44:30+00:00',
                    },
                },
            },
        },
        {'devices': [DEVICE_1, DEVICE_3, DEVICE_6]},
    ),
    (
        {
            'query': {
                'status': {
                    'updated_at': {
                        'empty': False,
                        'from': '2020-01-23T15:44:30+00:00',
                    },
                },
            },
        },
        {'devices': [DEVICE_1, DEVICE_6]},
    ),
    (
        {
            'query': {
                'status': {
                    'updated_at': {
                        'empty': True,
                        'to': '2020-01-23T15:44:30+00:00',
                    },
                },
            },
        },
        {'devices': [DEVICE_2, DEVICE_3, DEVICE_4, DEVICE_5]},
    ),
    (
        {
            'query': {
                'status': {
                    'updated_at': {
                        'empty': False,
                        'to': '2020-01-23T15:44:30+00:00',
                    },
                },
            },
        },
        {'devices': [DEVICE_2, DEVICE_4, DEVICE_5]},
    ),
    (
        {
            'query': {
                'status': {
                    'updated_at': {
                        'empty': True,
                        'to': '2019-01-14T15:44:46+00:00',
                    },
                },
            },
        },
        {'devices': [DEVICE_3]},
    ),
    (
        {
            'query': {
                'status': {
                    'updated_at': {
                        'empty': False,
                        'to': '2019-01-14T15:44:46+00:00',
                    },
                },
            },
        },
        {'devices': []},
    ),
    (
        {
            'query': {
                'status': {
                    'updated_at': {
                        'empty': True,
                        'from': '2020-01-15T00:00:00+00:00',
                        'to': '2020-01-23T15:44:30+00:00',
                    },
                },
            },
        },
        {'devices': [DEVICE_3]},
    ),
    (
        {
            'query': {
                'status': {
                    'updated_at': {
                        'empty': False,
                        'from': '2020-01-15T00:00:00+00:00',
                        'to': '2020-01-23T15:44:30+00:00',
                    },
                },
            },
        },
        {'devices': []},
    ),
    (
        {
            'query': {
                'status': {
                    'updated_at': {
                        'empty': True,
                        'from': '2020-01-13T00:00:00+00:00',
                        'to': '2020-01-24T00:00:00+00:00',
                    },
                },
            },
        },
        {'devices': [DEVICE_1, DEVICE_2, DEVICE_3, DEVICE_6]},
    ),
    (
        {
            'query': {
                'status': {
                    'updated_at': {
                        'empty': False,
                        'from': '2020-01-13T00:00:00+00:00',
                        'to': '2020-01-24T00:00:00+00:00',
                    },
                },
            },
        },
        {'devices': [DEVICE_1, DEVICE_2, DEVICE_6]},
    ),
    (
        {
            'query': {
                'status': {
                    'updated_at': {
                        'empty': False,
                        'from': '2020-01-23T15:43:00+00:00',
                        'to': '2020-01-23T15:45:00+00:00',
                    },
                },
            },
        },
        {'devices': [DEVICE_1, DEVICE_6]},
    ),
]


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize('json_request, json_response', OK_PARAMS)
async def test_ok(taxi_signal_device_api_admin, json_request, json_response):
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=json_request,
    )

    assert response.status_code == 200, response.text
    json_response['limit'] = json_request.pop('limit', 100)
    json_response['offset'] = json_request.pop('offset', 0)
    assert response.json() == json_response


async def test_bad_interval(taxi_signal_device_api_admin):
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'query': {
                'status': {
                    'updated_at': {
                        'empty': False,
                        'from': '2020-01-13T00:00:01+00:00',
                        'to': '2020-01-13T00:00:00+00:00',
                    },
                },
            },
        },
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': 'invalid query.status.updated_at interval',
    }
