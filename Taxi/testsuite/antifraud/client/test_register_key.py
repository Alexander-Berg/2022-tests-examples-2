import pytest

_PUB_MILLIS = 1538384400000
_MAX_DIFF = 60 * 60 * 1000


@pytest.mark.parametrize(
    'key_info,expected_code,api_key',
    [
        # all ok
        (
            {
                'app_id': 'ru.yandex.taximeter',
                'app_version_code': 100,
                'app_version_name': '8.46',
                'app_fingerprint_md5': '5UIpiKMskBIUANbOlLM5zw',
                'key': 'gq5E5CI4e5uAjheO1AX4Ww',
                'sig_version': 2,
                'millis': _PUB_MILLIS,
                'sdk_version_code': 10,
                'sdk_version_name': '0.6.0',
            },
            204,
            '100500',
        ),
        # bad apikey
        (
            {
                'app_id': 'ru.yandex.taximeter',
                'app_version_code': 100,
                'app_version_name': '8.46',
                'app_fingerprint_md5': '5UIpiKMskBIUANbOlLM5zw',
                'key': 'gq5E5CI4e5uAjheO1AX4Ww',
                'sig_version': 2,
                'millis': _PUB_MILLIS,
                'sdk_version_code': 10,
                'sdk_version_name': '0.6.0',
            },
            403,
            '500100',
        ),
        # no key field
        (
            {
                'app_id': 'ru.yandex.taximeter',
                'app_version_code': 100,
                'app_version_name': '8.46',
                'app_fingerprint_md5': '5UIpiKMskBIUANbOlLM5zw',
                'sig_version': 2,
                'millis': _PUB_MILLIS,
                'sdk_version_code': 10,
                'sdk_version_name': '0.6.0',
            },
            400,
            '100500',
        ),
        # no app_fingerprint_md5 field
        (
            {
                'app_id': 'ru.yandex.taximeter',
                'app_version_code': 100,
                'app_version_name': '8.46',
                'key': 'gq5E5CI4e5uAjheO1AX4Ww',
                'sig_version': 2,
                'millis': _PUB_MILLIS,
                'sdk_version_code': 10,
                'sdk_version_name': '0.6.0',
            },
            400,
            '100500',
        ),
        # bad key (base64)
        (
            {
                'app_id': 'ru.yandex.taximeter',
                'app_version_code': 100,
                'app_version_name': '8.46',
                'app_fingerprint_md5': '5UIpiKMskBIUANbOlLM5zw',
                'key': 'gq5E5CI4e5uAjheO1AX4W',
                'sig_version': 2,
                'millis': _PUB_MILLIS,
                'sdk_version_code': 10,
                'sdk_version_name': '0.6.0',
            },
            500,
            '100500',
        ),
        # bad app_fingerprint_md5 (base64)
        (
            {
                'app_id': 'ru.yandex.taximeter',
                'app_version_code': 100,
                'app_version_name': '8.46',
                'app_fingerprint_md5': '5UIpiKMskBIUANbOlLM5z',
                'key': 'gq5E5CI4e5uAjheO1AX4Ww',
                'sig_version': 2,
                'millis': _PUB_MILLIS,
                'sdk_version_code': 10,
                'sdk_version_name': '0.6.0',
            },
            500,
            '100500',
        ),
        # bad key (reverse_key fail, too short key)
        (
            {
                'app_id': 'ru.yandex.taximeter',
                'app_version_code': 100,
                'app_version_name': '8.46',
                'app_fingerprint_md5': '5UIpiKMskBIUANbOlLM5zw',
                'key': 'gq5E5CI4e5uAjheO1AX4',
                'sig_version': 2,
                'millis': _PUB_MILLIS,
                'sdk_version_code': 10,
                'sdk_version_name': '0.6.0',
            },
            400,
            '100500',
        ),
        # bad app_version_code
        (
            {
                'app_id': 'ru.yandex.taximeter',
                'app_version_code': 101,
                'app_version_name': '8.46',
                'app_fingerprint_md5': '5UIpiKMskBIUANbOlLM5zw',
                'key': 'gq5E5CI4e5uAjheO1AX4Ww',
                'sig_version': 2,
                'millis': _PUB_MILLIS,
                'sdk_version_code': 10,
                'sdk_version_name': '0.6.0',
            },
            403,
            '100500',
        ),
        # bad sdk_version_code
        (
            {
                'app_id': 'ru.yandex.taximeter',
                'app_version_code': 100,
                'app_version_name': '8.46',
                'app_fingerprint_md5': '5UIpiKMskBIUANbOlLM5zw',
                'key': 'gq5E5CI4e5uAjheO1AX4Ww',
                'sig_version': 2,
                'millis': _PUB_MILLIS,
                'sdk_version_code': 11,
                'sdk_version_name': '0.6.0',
            },
            403,
            '100500',
        ),
        # all ok (pub_millis == priv_millis + max_diff - 1)
        (
            {
                'app_id': 'ru.yandex.taximeter',
                'app_version_code': 100,
                'app_version_name': '8.46',
                'app_fingerprint_md5': '5UIpiKMskBIUANbOlLM5zw',
                'key': 'gq5E5CI4e5uAjheO1AX4Ww',
                'sig_version': 2,
                'millis': _PUB_MILLIS + _MAX_DIFF - 1,
                'sdk_version_code': 10,
                'sdk_version_name': '0.6.0',
            },
            204,
            '100500',
        ),
        # all ok (pub_millis == priv_millis - max_diff + 1)
        (
            {
                'app_id': 'ru.yandex.taximeter',
                'app_version_code': 100,
                'app_version_name': '8.46',
                'app_fingerprint_md5': '5UIpiKMskBIUANbOlLM5zw',
                'key': 'gq5E5CI4e5uAjheO1AX4Ww',
                'sig_version': 2,
                'millis': _PUB_MILLIS - _MAX_DIFF + 1,
                'sdk_version_code': 10,
                'sdk_version_name': '0.6.0',
            },
            204,
            '100500',
        ),
        # bad millis (pub_millis == priv_millis + max_diff)
        (
            {
                'app_id': 'ru.yandex.taximeter',
                'app_version_code': 100,
                'app_version_name': '8.46',
                'app_fingerprint_md5': '5UIpiKMskBIUANbOlLM5zw',
                'key': 'gq5E5CI4e5uAjheO1AX4Ww',
                'sig_version': 2,
                'millis': _PUB_MILLIS + _MAX_DIFF,
                'sdk_version_code': 10,
                'sdk_version_name': '0.6.0',
            },
            403,
            '100500',
        ),
        # bad millis (pub_millis == priv_millis - max_diff)
        (
            {
                'app_id': 'ru.yandex.taximeter',
                'app_version_code': 100,
                'app_version_name': '8.46',
                'app_fingerprint_md5': '5UIpiKMskBIUANbOlLM5zw',
                'key': 'gq5E5CI4e5uAjheO1AX4Ww',
                'sig_version': 2,
                'millis': _PUB_MILLIS - _MAX_DIFF,
                'sdk_version_code': 10,
                'sdk_version_name': '0.6.0',
            },
            403,
            '100500',
        ),
        # bad sig_version
        (
            {
                'app_id': 'ru.yandex.taximeter',
                'app_version_code': 100,
                'app_version_name': '8.46',
                'app_fingerprint_md5': '5UIpiKMskBIUANbOlLM5zw',
                'key': 'gq5E5CI4e5uAjheO1AX4Ww',
                'sig_version': 1,
                'millis': _PUB_MILLIS,
                'sdk_version_code': 10,
                'sdk_version_name': '0.6.0',
            },
            400,
            '100500',
        ),
    ],
)
@pytest.mark.now('2018-10-01T09:00:00+0000')
def test_register_key_base(
        taxi_antifraud, db, key_info, expected_code, api_key,
):
    response = taxi_antifraud.post(
        'client/register_key',
        json=key_info,
        headers={'X-Protector-ApiKey': api_key},
    )
    assert expected_code == response.status_code
    if response.status_code == 204:
        cursor = db.antifraud_client_keys.find(
            {
                'app_id': key_info['app_id'],
                'app_version_code': key_info['app_version_code'],
                'sdk_version_code': key_info['sdk_version_code'],
            },
        )
        count = cursor.count()
        assert count == 1
        record = cursor[0]
        assert record['app_id'] == key_info['app_id']
        assert record['app_version_code'] == key_info['app_version_code']
        assert record['app_version_name'] == key_info['app_version_name']
        assert record['app_fingerprint_md5'] == (
            key_info['app_fingerprint_md5']
        )
        assert record['key'] == key_info['key']
        assert record['sig_version'] == key_info['sig_version']
        assert record['sdk_version_code'] == key_info['sdk_version_code']
        assert record['sdk_version_name'] == key_info['sdk_version_name']


@pytest.mark.parametrize(
    'infos',
    [
        (
            {
                'key_info': {
                    'app_id': 'ru.yandex.taximeter',
                    'app_version_code': 100,
                    'app_version_name': '8.46',
                    'app_fingerprint_md5': '5UIpiKMskBIUANbOlLM5zw',
                    'key': 'gq5E5CI4e5uAjheO1AX4Ww',
                    'sig_version': 2,
                    'millis': 1538384400000,
                    'sdk_version_code': 10,
                    'sdk_version_name': '0.6.0',
                },
                'expected_code': 204,
            },
            {
                'key_info': {
                    'app_id': 'ru.yandex.taximeter',
                    'app_version_code': 101,
                    'app_version_name': '8.46',
                    'app_fingerprint_md5': 'WJzAlRhPFV4FFE+NY2FoUQ',
                    'key': 'LK0C64IO/wwpD4atx+NLZw',
                    'sig_version': 2,
                    'millis': 1538384400000,
                    'sdk_version_code': 10,
                    'sdk_version_name': '0.6.0',
                },
                'expected_code': 204,
            },
            {
                'key_info': {
                    'app_id': 'ru.yandex.taximeter',
                    'app_version_code': 100,
                    'app_version_name': '8.46',
                    'app_fingerprint_md5': 'Rcjo395N4Qf9nItNWupouA',
                    'key': 'BGHEl4GoPXFDbaKNk4LSRw',
                    'sig_version': 2,
                    'millis': 1538384400000,
                    'sdk_version_code': 11,
                    'sdk_version_name': '0.6.0',
                },
                'expected_code': 409,
            },
        ),
    ],
)
@pytest.mark.now('2018-10-01T09:00:00+0000')
def test_register_key_duplicate(taxi_antifraud, infos):
    for info in infos:
        response = taxi_antifraud.post(
            'client/register_key',
            json=info['key_info'],
            headers={'X-Protector-ApiKey': '100500'},
        )
        assert response.status_code == info['expected_code']
