# pylint: disable=C5521
# pylint: disable=W0621
import datetime

import pytest

_TELEMEDICINE_URL = '/v1/drivers/telemedicine_checkups'
_DEPTRANS_API_KEY = 'deptrans_key'
_YANDEX_API_KEY = 'Yandex-Api-Key'
_NOW = datetime.datetime.fromtimestamp(1580282811)


def gen_data(entries_number: int, chunk_size: int):
    res = []
    for i in range(entries_number):
        i_str = str(i)
        i_chunk_str = str(i % chunk_size)
        days_ago = ((entries_number - 1) // chunk_size) - (i // chunk_size)
        res.append(
            {
                'id': i_str,
                'checkup_id': 'checkup_id_' + i_str,
                'driver_last_name': 'driver_last_name_' + i_chunk_str,
                'driver_license': i_str,
                'med_center_address': 'address_' + i_str,
                'med_center_name': 'med_name_' + i_str,
                'status': 'failed' if i % chunk_size == 0 else 'success',
                'utc_checkup_dttm': datetime.datetime.isoformat(
                    _NOW - datetime.timedelta(days=days_ago),
                ),
            },
        )


_CHECKUPS_RESULTS = [
    {
        'driver_id': (
            'b2940869da444d484a4d91d81916b67d6cf'
            '1b5b02ff3a20d8fd3b136766bcc06'
        ),
        'checkup_passed_at': '2020-01-29T10:16:51+00:00',
        'checkup_id': 'checkup_id_1',
        'medical_center': {'name': 'med_name_991', 'address': 'address_991'},
    },
    {
        'driver_id': (
            'd0165a1470295b08490bd1b737ced9a62e5'
            '1657eb95bea0e0b5f64175685ca46'
        ),
        'checkup_passed_at': '2020-01-29T10:16:51+00:00',
        'checkup_id': 'checkup_id_2',
        'medical_center': {'name': 'med_name_992', 'address': 'address_992'},
    },
    {
        'driver_id': (
            '83e24a6c7a129286c8584dc8bcf363751f9'
            'e1bfc220c8018551def72fe740120'
        ),
        'checkup_passed_at': '2020-01-29T10:16:51+00:00',
        'checkup_id': 'checkup_id_3',
        'medical_center': {'name': 'med_name_993', 'address': 'address_993'},
    },
    {
        'driver_id': (
            'c84a93a325f40933220220a20f0f40b99a0'
            'ea508b9f8cc30bedc33ecbff4543e'
        ),
        'checkup_passed_at': '2020-01-29T10:16:51+00:00',
        'checkup_id': 'checkup_id_4',
        'medical_center': {'name': 'med_name_994', 'address': 'address_994'},
    },
    {
        'driver_id': (
            'b0ece26d330cbc78caaaf321f33d2a49414'
            'b58f61798e3d3454929bb4424be96'
        ),
        'checkup_passed_at': '2020-01-29T10:16:51+00:00',
        'checkup_id': 'checkup_id_5',
        'medical_center': {'name': 'med_name_995', 'address': 'address_995'},
    },
    {
        'driver_id': (
            '28ad1d40194bdfe558ddd1a20bdfe9fdf86'
            '328ccec0b3508ae1aae5cc0565407'
        ),
        'checkup_passed_at': '2020-01-29T10:16:51+00:00',
        'checkup_id': 'checkup_id_6',
        'medical_center': {'name': 'med_name_996', 'address': 'address_996'},
    },
    {
        'driver_id': (
            '6c9b02d86f2c9ca7bad9c9e6125ce78acb3'
            '1ffd915daf2fc5f3b1a249731c5da'
        ),
        'checkup_passed_at': '2020-01-29T10:16:51+00:00',
        'checkup_id': 'checkup_id_7',
        'medical_center': {'name': 'med_name_997', 'address': 'address_997'},
    },
    {
        'driver_id': (
            '7fedcbed93a61c53a1713db5313f2a667a3'
            '6ee46add93c0577434e4a1100bba5'
        ),
        'checkup_passed_at': '2020-01-29T10:16:51+00:00',
        'checkup_id': 'checkup_id_8',
        'medical_center': {'name': 'med_name_998', 'address': 'address_998'},
    },
    {
        'driver_id': (
            '96f4fc29a76424c60b2121869e9f5cc5f0b'
            'f310f839fd17fa7999821a0fafb0c'
        ),
        'checkup_passed_at': '2020-01-29T10:16:51+00:00',
        'checkup_id': 'checkup_id_9',
        'medical_center': {'name': 'med_name_999', 'address': 'address_999'},
    },
]


def format_url(cursor: int, limit: int):
    return _TELEMEDICINE_URL + f'?cursor_from={cursor}&limit={limit}'


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(DEPTRANS_API_KEY=_DEPTRANS_API_KEY)
async def test_bad_headers(taxi_driver_regulatory_export):
    url_with_params = format_url(0, 100)
    response = await taxi_driver_regulatory_export.get(url_with_params)
    assert response.status_code == 400

    headers = {_YANDEX_API_KEY: _DEPTRANS_API_KEY + 'abacaba'}

    response = await taxi_driver_regulatory_export.get(
        url_with_params, headers=headers,
    )
    assert response.status_code == 401


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(DEPTRANS_API_KEY=_DEPTRANS_API_KEY)
@pytest.mark.skip('no yt mock for now')
async def test_handler(taxi_driver_regulatory_export):

    headers = {_YANDEX_API_KEY: _DEPTRANS_API_KEY}
    url_with_params = format_url(0, 1000)

    response = await taxi_driver_regulatory_export.get(
        url_with_params, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        'checkups': _CHECKUPS_RESULTS[0:5],
        'cursor': 995,
    }

    url_with_params = format_url(995, 5)

    response = await taxi_driver_regulatory_export.get(
        url_with_params, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        'checkups': _CHECKUPS_RESULTS[5:9],
        'cursor': 999,
    }


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(DEPTRANS_API_KEY=_DEPTRANS_API_KEY)
@pytest.mark.skip('no yt mock for now')
async def test_handler_big_limit(taxi_driver_regulatory_export):

    headers = {_YANDEX_API_KEY: _DEPTRANS_API_KEY}
    url_with_params = format_url(0, 1000)

    response = await taxi_driver_regulatory_export.get(
        url_with_params, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'checkups': _CHECKUPS_RESULTS, 'cursor': 999}
