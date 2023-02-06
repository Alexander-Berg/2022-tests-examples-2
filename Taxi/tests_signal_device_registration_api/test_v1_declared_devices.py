import csv
import datetime
import io
import secrets

import pytest

ENDPOINT = '/v1/declared-devices'

CONTENT_TYPE = 'text/csv'
PASSPORT_UID = '6755068'
CSV_HEADER_ROW = [
    'Serial number',
    'Public AES key',
    'IMEI',
    'MAC WLAN',
    'MAC Bluetooth',
    'SIM ICCID',
]
SERIAL_OLD = '31F648DBDEEA799F'
SERIAL_NEW = '5989F303C12FEA30'
SERIAL_NEW_2 = '3FEACB47B0663974'
EXISTING_ROW_NO_SERIAL = [
    'FAEE4CA3C30EE18148CE3ADA374664987D9DD7CC84B0731248B42700E521991E',
    '990000862471854',
    'dd:f2:68:a8:df:b3',
    '5b:38:fc:6a:88:0b',
    '8991101200003204514',
]

# `tvmknife unittest service --src 111 --dst 2016267`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxCLiHs:NnLj18bjvNK1BNWUBc'
    'HKTNjeXkLh7xHowhQUxF7XjcFEibaG5NLaTCtH-eKcfY3PcTWMNue'
    'reDTyW2pm9N5-rCd_p-RZ_cyFqqH8rq0w7Sj_jnE1sKs3XuzK3IPm'
    'C83XNKspEYsr4u_KgWGQcV_gIXmpPcTunHD1l72MzqYk7yg'
)
MOCK_USER_TICKET = 'valid_user_ticket'
COMMON_HEADERS = {
    'X-Ya-User-Ticket': MOCK_USER_TICKET,
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Yandex-UID': PASSPORT_UID,
    'Content-Type': CONTENT_TYPE,
}
YA_HEADERS = {'X-Ya-User-Ticket-Provider': 'yandex', **COMMON_HEADERS}
YA_TEAM_HEADERS = {
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    **COMMON_HEADERS,
}

FIELDS = [
    'id',
    'serial_number',
    'aes_key',
    'imei',
    'mac_wlan0',
    'mac_bluetooth',
    'sim_iccid',
    'created_at',
    'updated_at',
]


def _create_csv_from_rows(csv_rows):
    output = io.StringIO()
    writer = csv.writer(output, delimiter=',')
    for row in csv_rows:
        writer.writerow(row)
    return output.getvalue().replace('\r', '')


def _select_declared_devices(pgsql):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT {} FROM signal_device_api.declared_devices;'.format(
            ','.join(FIELDS),
        ),
    )
    db_declared_devices = list(db)
    return [
        {k: v for (k, v) in zip(FIELDS, db_declared_device)}
        for db_declared_device in db_declared_devices
    ]


def _generate_serial():
    return secrets.token_hex(8).upper()


def _assert_now(actual):
    assert isinstance(actual, datetime.datetime)
    assert actual.tzinfo is not None
    delta = datetime.datetime.now(datetime.timezone.utc) - actual
    assert (
        datetime.timedelta() <= delta < datetime.timedelta(minutes=1)
    ), f'found too big delta {delta}'


@pytest.mark.parametrize(
    'csv_data, error_msg',
    [
        (
            b'1',
            'Invalid header row "1", '
            'must be "Serial number,Public AES key,'
            'IMEI,MAC WLAN,MAC Bluetooth,SIM ICCID"',
        ),
        (_create_csv_from_rows([CSV_HEADER_ROW]), 'Empty CSV for processing'),
        (
            _create_csv_from_rows(
                [CSV_HEADER_ROW, [SERIAL_OLD] + EXISTING_ROW_NO_SERIAL[1:]],
            ),
            'Error in CSV row 1: CSV column number mismatch: 5 != 6',
        ),
        (
            _create_csv_from_rows(
                [
                    CSV_HEADER_ROW,
                    [SERIAL_OLD] + EXISTING_ROW_NO_SERIAL + ['0'],
                ],
            ),
            'Error in CSV row 1: CSV column number mismatch: 7 != 6',
        ),
        (
            _create_csv_from_rows(
                [
                    CSV_HEADER_ROW,
                    [_generate_serial()] + EXISTING_ROW_NO_SERIAL,
                    EXISTING_ROW_NO_SERIAL,
                ],
            ),
            'Error in CSV row 2: CSV column number mismatch: 5 != 6',
        ),
    ],
)
async def test_invalid_csv_format(
        taxi_signal_device_registration_api, pgsql, csv_data, error_msg,
):
    declared_devices_before = _select_declared_devices(pgsql)
    response = await taxi_signal_device_registration_api.post(
        ENDPOINT, headers=YA_TEAM_HEADERS, data=csv_data,
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': error_msg}
    assert _select_declared_devices(pgsql) == declared_devices_before


@pytest.mark.parametrize(
    'csv_data, error_msg',
    [
        (
            _create_csv_from_rows(
                [CSV_HEADER_ROW, ['абыравлг'] + EXISTING_ROW_NO_SERIAL],
            ),
            'Error in CSV row 1: '
            'Serial number абыравлг does not match format [0-9A-F]{6,16}',
        ),
        (
            _create_csv_from_rows(
                [
                    CSV_HEADER_ROW,
                    [_generate_serial()]
                    + ['абыравлг']
                    + EXISTING_ROW_NO_SERIAL[1:],
                ],
            ),
            'Error in CSV row 1: '
            'Public key абыравлг does not match format [0-9A-F]+',
        ),
        (
            _create_csv_from_rows(
                [
                    CSV_HEADER_ROW,
                    [_generate_serial()]
                    + EXISTING_ROW_NO_SERIAL[:1]
                    + ['абыравлг']
                    + EXISTING_ROW_NO_SERIAL[2:],
                ],
            ),
            'Error in CSV row 1: '
            'IMEI абыравлг does not match format [\\d]{15}',
        ),
        (
            _create_csv_from_rows(
                [
                    CSV_HEADER_ROW,
                    [_generate_serial()]
                    + EXISTING_ROW_NO_SERIAL[:2]
                    + ['абыравлг']
                    + EXISTING_ROW_NO_SERIAL[3:],
                ],
            ),
            'Error in CSV row 1: '
            'WLAN MAC address абыравлг does not match format '
            '([0-9a-f]{2}[:]){5}([0-9a-f]){2}',
        ),
        (
            _create_csv_from_rows(
                [
                    CSV_HEADER_ROW,
                    [_generate_serial()]
                    + EXISTING_ROW_NO_SERIAL[:3]
                    + ['абыравлг']
                    + EXISTING_ROW_NO_SERIAL[4:],
                ],
            ),
            'Error in CSV row 1: '
            'Bluetooth MAC address абыравлг does not match format '
            '([0-9a-f]{2}[:]){5}([0-9a-f]){2}',
        ),
    ],
)
async def test_invalid_data_format_in_row(
        taxi_signal_device_registration_api, pgsql, csv_data, error_msg,
):
    declared_devices_before = _select_declared_devices(pgsql)
    response = await taxi_signal_device_registration_api.post(
        ENDPOINT, headers=YA_TEAM_HEADERS, data=csv_data,
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': error_msg}
    assert _select_declared_devices(pgsql) == declared_devices_before


async def test_ok_null_iccid_select(
        taxi_signal_device_registration_api, pgsql,
):
    declared_devices_before = _select_declared_devices(pgsql)
    serial = '11F648DBDEEA799F'
    response = await taxi_signal_device_registration_api.post(
        ENDPOINT,
        headers=YA_TEAM_HEADERS,
        data=_create_csv_from_rows(
            [
                CSV_HEADER_ROW,
                [
                    serial,
                    '11EE4CA3C30EE18148CE3ADA37466498'
                    '7D9DD7CC84B0731248B42700E521991E',
                    '111100008671854',
                    'aa:f2:68:a8:df:b3',
                    'aa:38:fc:6a:88:0b',
                    'aa91101200003204514',
                ],
            ],
        ),
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': '409',
        'message': (
            f'Device with serial {serial} was declared with different data'
        ),
    }
    assert _select_declared_devices(pgsql) == declared_devices_before


async def test_403(taxi_signal_device_registration_api, pgsql):
    declared_devices_before = _select_declared_devices(pgsql)
    response = await taxi_signal_device_registration_api.post(
        ENDPOINT,
        headers=YA_HEADERS,
        data=_create_csv_from_rows(
            [CSV_HEADER_ROW, [_generate_serial()] + EXISTING_ROW_NO_SERIAL],
        ),
    )
    assert response.status_code == 403
    assert response.json() == {'code': '403', 'message': 'Unauthorized user'}
    assert _select_declared_devices(pgsql) == declared_devices_before


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'csv_data',
    [
        _create_csv_from_rows(
            [CSV_HEADER_ROW, [_generate_serial()] + EXISTING_ROW_NO_SERIAL],
        ),
        _create_csv_from_rows(
            [
                CSV_HEADER_ROW,
                [SERIAL_OLD] + EXISTING_ROW_NO_SERIAL,
                [_generate_serial()] + EXISTING_ROW_NO_SERIAL,
                [_generate_serial()] + EXISTING_ROW_NO_SERIAL,
            ],
        ),
        _create_csv_from_rows(
            [
                CSV_HEADER_ROW,
                [SERIAL_NEW_2] + EXISTING_ROW_NO_SERIAL,
                [SERIAL_NEW] + EXISTING_ROW_NO_SERIAL,
                [SERIAL_NEW] + EXISTING_ROW_NO_SERIAL,
                [SERIAL_NEW_2] + EXISTING_ROW_NO_SERIAL,
            ],
        ),
    ],
)
async def test_ok(taxi_signal_device_registration_api, pgsql, csv_data):
    declared_devices_before = _select_declared_devices(pgsql)
    response = await taxi_signal_device_registration_api.post(
        ENDPOINT, headers=YA_TEAM_HEADERS, data=csv_data,
    )
    assert response.status_code == 200, response.text
    declared_devices_after = _select_declared_devices(pgsql)
    new_declared_devices = [
        d for d in declared_devices_after if d not in declared_devices_before
    ]
    assert new_declared_devices
    for new_declared_device in new_declared_devices:
        _assert_now(new_declared_device['updated_at'])
        _assert_now(new_declared_device['created_at'])


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'row_to_insert',
    [
        [SERIAL_OLD]
        + [
            EXISTING_ROW_NO_SERIAL[j]
            if j != i
            else '0' + EXISTING_ROW_NO_SERIAL[j][1:]
            for j in range(len(EXISTING_ROW_NO_SERIAL))
        ]
        for i in range(len(EXISTING_ROW_NO_SERIAL) - 1)  # Do not use sim_iccid
    ],
)
async def test_409_with_db(
        taxi_signal_device_registration_api, pgsql, row_to_insert,
):
    declared_devices_before = _select_declared_devices(pgsql)
    response = await taxi_signal_device_registration_api.post(
        ENDPOINT,
        headers=YA_TEAM_HEADERS,
        data=_create_csv_from_rows([CSV_HEADER_ROW, row_to_insert]),
    )
    assert response.status_code == 409, response.text
    assert response.json() == {
        'code': '409',
        'message': (
            'Device with serial '
            + SERIAL_OLD
            + ' was declared with different data'
        ),
    }
    assert _select_declared_devices(pgsql) == declared_devices_before


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
async def test_multiple_conflict_declaration_in_csv(
        taxi_signal_device_registration_api, pgsql,
):
    declared_devices_before = _select_declared_devices(pgsql)
    response = await taxi_signal_device_registration_api.post(
        ENDPOINT,
        headers=YA_TEAM_HEADERS,
        data=_create_csv_from_rows(
            [
                CSV_HEADER_ROW,
                [SERIAL_OLD] + EXISTING_ROW_NO_SERIAL,
                [SERIAL_OLD]
                + [EXISTING_ROW_NO_SERIAL[0].replace('F', '1')]
                + EXISTING_ROW_NO_SERIAL[1:],
            ],
        ),
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': (
            'Error in CSV row 2: '
            'Device with serial number '
            + SERIAL_OLD
            + ' is listed multiple times with different data'
        ),
    }
    assert _select_declared_devices(pgsql) == declared_devices_before
