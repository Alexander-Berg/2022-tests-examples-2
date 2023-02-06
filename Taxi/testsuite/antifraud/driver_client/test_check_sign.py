import datetime
import json
import time

import pytest

from antifraud import utils


def _make_proc(pub_version_valid=None):
    return {
        'sign_exists': True,
        'parse_success': True,
        'key_exists': True,
        'sign_decode_success': True,
        'sign_version_valid': True,
        'sign_pub_info_valid': True,
        'taximeter_pub_version_valid': (
            pub_version_valid if pub_version_valid is not None else True
        ),
        'sign_not_expired': True,
        'taximeter_version_valid': True,
    }


def _make_proc2(*args):
    _stages = [
        'sign_exists',
        'parse_success',
        'key_exists',
        'sign_decode_success',
        'sign_version_valid',
        'sign_pub_info_valid',
        'taximeter_pub_version_valid',
        'sign_not_expired',
        'taximeter_version_valid',
    ]

    proc = dict()
    args_len = len(args)

    for i in range(len(_stages)):
        if args_len > i:
            proc[_stages[i]] = bool(args[i])

    return proc


@utils.wait_for_correct(retries=100, period=0.1)
def _is_record_saved(db, udi):
    record = db.antifraud_driver_client_info.find_one({'_id': udi})
    return record is not None


def _find_driver_client_info(db, udi):
    _is_record_saved(db, udi)
    return db.antifraud_driver_client_info.find_one({'_id': udi})


def _make_request(
        signature_info=None,
        taximeter_version=None,
        udi=None,
        driver_id=None,
        user_agent_split=None,
        signature_exists=None,
        signature_version=None,
        license_pd_ids=None,
):
    request = {
        'unique_driver_id': udi if udi is not None else 'udi',
        'driver_id': driver_id if driver_id is not None else 'di',
        'signature_exists': (
            signature_exists if signature_exists is not None else True
        ),
        'license_pd_ids': (
            license_pd_ids if license_pd_ids is not None else ['license_pd_id']
        ),
        'taximeter_version': (
            taximeter_version
            if taximeter_version is not None
            else '8.78 (1073749275)'
        ),
    }

    if signature_info is not None:
        request['signature_info'] = signature_info

    if user_agent_split is not None:
        request['user_agent_split'] = user_agent_split

    if signature_version is not None:
        request['signature_version'] = signature_version

    return request


@pytest.mark.parametrize(
    'sign_info,proc,expected_code',
    [
        # 1 [ECB] all ok
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6InRwSGhhSTZKT2pURHowTDgvY3lUckEifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            _make_proc(),
            200,
        ),
        # 2 [GCM] all ok
        (
            _make_request(
                signature_info=(
                    'CiBo+LYkf4ZMXqX9jakbz4BamwIAfawRPMGs2s65tsmTiRIQ'
                    'fA8zJBe2QW9rjO7UFEe45hoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoM52o36Ah5HbeViLJ6'
                ),
                taximeter_version='8.65 (3647)',
                user_agent_split='8.65 (2147483647)',
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
            ),
            _make_proc(),
            200,
        ),
        # 3 [GCM] bad pub taximeter_version (not present)
        (
            _make_request(
                signature_info=(
                    'CiBo+LYkf4ZMXqX9jakbz4BamwIAfawRPMGs2s65tsmTiRIQ'
                    'fA8zJBe2QW9rjO7UFEe45hoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoM52o36Ah5HbeViLJ6'
                ),
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
            ),
            _make_proc(pub_version_valid=False),
            200,
        ),
        # 4 [GCM] bad pub taximeter_version (empty)
        (
            _make_request(
                signature_info=(
                    'CiBo+LYkf4ZMXqX9jakbz4BamwIAfawRPMGs2s65tsmTiRIQ'
                    'fA8zJBe2QW9rjO7UFEe45hoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoM52o36Ah5HbeViLJ6'
                ),
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
                taximeter_version='',
            ),
            _make_proc(pub_version_valid=False),
            200,
        ),
        # 5 [GCM] bad pub taximeter_version (a.b)
        (
            _make_request(
                signature_info=(
                    'CiBo+LYkf4ZMXqX9jakbz4BamwIAfawRPMGs2s65tsmTiRIQ'
                    'fA8zJBe2QW9rjO7UFEe45hoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoM52o36Ah5HbeViLJ6'
                ),
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
                taximeter_version='a.b',
            ),
            _make_proc(pub_version_valid=False),
            200,
        ),
        # 6 [GCM] bad pub taximeter_version (major 9, not 8)
        (
            _make_request(
                signature_info=(
                    'CiBo+LYkf4ZMXqX9jakbz4BamwIAfawRPMGs2s65tsmTiRIQ'
                    'fA8zJBe2QW9rjO7UFEe45hoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoM52o36Ah5HbeViLJ6'
                ),
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
                taximeter_version='9.65 (2147483647)',
            ),
            _make_proc(pub_version_valid=False),
            200,
        ),
        # 7 [GCM] bad pub taximeter_version (minor 64, not 65)
        (
            _make_request(
                signature_info=(
                    'CiBo+LYkf4ZMXqX9jakbz4BamwIAfawRPMGs2s65tsmTiRIQ'
                    'fA8zJBe2QW9rjO7UFEe45hoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoM52o36Ah5HbeViLJ6'
                ),
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
                taximeter_version='8.64 (2147483647)',
            ),
            _make_proc(pub_version_valid=False),
            200,
        ),
        # 8 [GCM] bad pub taximeter_version (minor 64, not 2147483647)
        (
            _make_request(
                signature_info=(
                    'CiBo+LYkf4ZMXqX9jakbz4BamwIAfawRPMGs2s65tsmTiRIQ'
                    'fA8zJBe2QW9rjO7UFEe45hoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoM52o36Ah5HbeViLJ6'
                ),
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
                taximeter_version='8.65 (2147483646)',
            ),
            _make_proc(pub_version_valid=False),
            200,
        ),
        # 9 [GCM] bad signature (signature_version doesn't exists)
        (
            _make_request(
                signature_info=(
                    'CiBo+LYkf4ZMXqX9jakbz4BamwIAfawRPMGs2s65tsmTiRIQ'
                    'fA8zJBe2QW9rjO7UFEe45hoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoM52o36Ah5HbeViLJ6'
                ),
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                taximeter_version='8.78 (1073749275)',
            ),
            _make_proc2(1, 0),
            200,
        ),
        # 10 [GCM] bad signature (signature_version is unsupported)
        (
            _make_request(
                signature_info=(
                    'CiBo+LYkf4ZMXqX9jakbz4BamwIAfawRPMGs2s65tsmTiRIQ'
                    'fA8zJBe2QW9rjO7UFEe45hoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoM52o36Ah5HbeViLJ6'
                ),
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                taximeter_version='8.78 (1073749275)',
                signature_version=2,
            ),
            _make_proc2(1, 0),
            200,
        ),
        # 11 [GCM] bad signature (driver_id is invalid [last char 'c'->'d'])
        (
            _make_request(
                signature_info=(
                    'CiBo+LYkf4ZMXqX9jakbz4BamwIAfawRPMGs2s65tsmTiRIQ'
                    'fA8zJBe2QW9rjO7UFEe45hoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoM52o36Ah5HbeViLJ6'
                ),
                driver_id='d04c48b920d9496ea363ca1fbb90f98d',
                taximeter_version='8.78 (1073749275)',
                signature_version=3,
            ),
            _make_proc2(1, 1, 1, 0),
            200,
        ),
        # 12 [GCM] bad signature
        # (signature_info is invalid [last char '6'->'7'])
        (
            _make_request(
                signature_info=(
                    'CiBo+LYkf4ZMXqX9jakbz4BamwIAfawRPMGs2s65tsmTiRIQ'
                    'fA8zJBe2QW9rjO7UFEe45hoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoM52o36Ah5HbeViLJ7'
                ),
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                taximeter_version='8.78 (1073749275)',
                signature_version=3,
            ),
            _make_proc2(1, 1, 1, 0),
            200,
        ),
        # 13 [GCM] bad signature (signature_info is invalid [delete last char])
        (
            _make_request(
                signature_info=(
                    'CiBo+LYkf4ZMXqX9jakbz4BamwIAfawRPMGs2s65tsmTiRIQ'
                    'fA8zJBe2QW9rjO7UFEe45hoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoM52o36Ah5HbeViLJ'
                ),
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                taximeter_version='8.78 (1073749275)',
                signature_version=3,
            ),
            _make_proc2(1, 0),
            200,
        ),
        # 14 [ECB] bad signature (signature doesn't exists)
        (
            _make_request(
                taximeter_version='8.78 (1073749275)', signature_exists=False,
            ),
            _make_proc2(0),
            200,
        ),
        # 15 [ECB] bad signature_info (isn't valid base64)
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6InRwSGhhSTZKT2pURHowTDgvY3lUckEif'
                ),
                taximeter_version='8.78 (1073749275)',
            ),
            _make_proc2(1, 0),
            200,
        ),
        # 16 [ECB] bad signature_info (incorrect json base64)
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6InRwSGhhSTZKT2pURHowTDgvY3lUckEi'
                ),
                taximeter_version='8.78 (1073749275)',
            ),
            _make_proc2(1, 0),
            200,
        ),
        # 17 [ECB] bad signature_info
        # (key doesn't exists ['app_id': 'en.yandex.taximeter'])
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJlbi55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6InRwSGhhSTZKT2pURHowTDgvY3lUckEifQ'
                ),
                taximeter_version='8.78 (1073749275)',
            ),
            _make_proc2(1, 1, 0),
            200,
        ),
        # 18 [ECB] bad signature_info
        # (key doesn't exists ['app_version_code': 101])
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAxLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6ImNxcy9HSTNWWUIyOXVhbi9HYWtYM0EifQ'
                ),
                taximeter_version='8.78 (1073749275)',
            ),
            _make_proc2(1, 1, 0),
            200,
        ),
        # 19 [ECB] all ok (key exists ['sdk_version_code': 11])
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMSwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6InRwSGhhSTZKT2pURHowTDgvY3lUckEifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            _make_proc(),
            200,
        ),
        # 20 [ECB] bad signature_info
        # (unbase64 signature inside signature_info is too short)
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6InRwSGhhSTZKT2pURHowTDgvY3lUIn0'
                ),
                taximeter_version='8.46 (100)',
            ),
            _make_proc2(1, 1, 1, 1, 0, 0, 1),
            200,
        ),
        # 21 [ECB] bad sig_version (1 in key, 2 inside sign)
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJrci55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6IitCVkxQV2NlZVd2bVhrMlduc2lpSmcifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            _make_proc2(1, 1, 1, 1, 0, 1, 1),
            200,
        ),
        # 22 [ECB] all ok
        # (priv_sig_sec == now_sec + polling_state_delay - 1)
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgyOTk5OTQsInNp'
                    'Z25hdHVyZSI6Im85bFhpdW5sSnpiZjJGNjdtVFlxbkEifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            _make_proc(),
            200,
        ),
        # 23 [ECB] all ok
        # (priv_sig_sec == now_sec - expired_mul * polling_state_delay + 6000)
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODcxMDYwMDAsInNp'
                    'Z25hdHVyZSI6IndnWVQyQVNEYjR6SnFVdkFielV3dGcifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            _make_proc(),
            200,
        ),
        # 24 [ECB] bad sig expired
        # (priv_sig_sec == now_sec + polling_state_delay + 5000)
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgzMDUwMDAsInNp'
                    'Z25hdHVyZSI6IjlrMEQralJLS0dFbnZDWkp0TTVuc3cifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            _make_proc2(*([1] * 7), 0, 1),
            200,
        ),
        # 25 [ECB] bad sig expired
        # (priv_sig_sec == now_sec - expired_mul * polling_state_delay)
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODcxMDAwMDAsInNp'
                    'Z25hdHVyZSI6IlV4dnQybkFhKzVkNjN2OFlDdjBla0EifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            _make_proc2(1, 1, 1, 1, 1, 1, 1, 0, 1),
            200,
        ),
        # 26 [ECB] bad taximeter version
        # 'app_id':'ua.yandex.taximeter', 'app_version_code':100 =>
        # app_version_name -> 8.44
        # but 8.45 is minimal
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJ1YS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6Ikt6MWZhQURZUkljaGUwZGxCY2lVWVEifQ'
                ),
                taximeter_version='8.44 (100)',
            ),
            _make_proc2(1, 1, 1, 1, 1, 1, 1, 1, 0),
            200,
        ),
    ],
)
@pytest.mark.now('2018-10-01T10:00:00+0000')
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS={
        'current': '8.45',
        'disabled': [],
        'feature_support': {},
        'min': '8.45',
        'min_versions_cities': {},
    },
    TAXIMETER_POLLING_DELAYS={
        '/driver/map/order': 60,
        '/driver/polling/state': 300,
        '/driver/rating/item': 900,
    },
    AFS_SIGN_EXPIRED_MUL=3,
)
def test_check_sign_base(
        taxi_antifraud, db, sign_info, proc, expected_code, now,
):
    response = taxi_antifraud.post('driver_client/check_sign', json=sign_info)
    assert expected_code == response.status_code
    record = _find_driver_client_info(db, sign_info['unique_driver_id'])
    assert not record['frauder']
    assert record['fraud_reason']
    assert record['created'] == now
    assert record['proc'] == proc
    assert record['license'] == 'not_license_' + sign_info['unique_driver_id']
    assert record['unique_driver_id'] == sign_info['unique_driver_id']
    if record['proc']['sign_exists']:
        if record['proc'].get('parse_success', False):
            assert record['signature_info'] == (sign_info['signature_info'])


@pytest.mark.parametrize(
    'sign_info,frauder,reason',
    [
        # 1 [ECB]
        # 'sig_root' : 0,
        # 'sig_emulator' : 0,
        # 'sig_fake_gps' : 0,
        # 'sig_hook' : 0,
        # 'sig_plane_switch' : 0,
        # 'sig_gps_switch' : 0,
        # 'sig_net_switch' : 0,
        # 'sig_version_code' : 100,
        # =>   frauder = false
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6InRwSGhhSTZKT2pURHowTDgvY3lUckEifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            False,
            'no_fraud',
        ),
        # 2 [GCM]
        # 'sig_root' : 0,
        # 'sig_emulator' : 0,
        # 'sig_fake_gps' : 0,
        # 'sig_hook' : 0,
        # 'sig_plane_switch' : 0,
        # 'sig_gps_switch' : 0,
        # 'sig_net_switch' : 0,
        # 'sig_version_code' : 2147483647,
        # =>   frauder = false
        (
            _make_request(
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
                signature_info=(
                    'CiDSllU6IT/QOdL+k8zW6ewpDb8NayiIkwfkvG+MMfyIsBIQ'
                    'B3OrtLhb+jV10LcKvpxWvBoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoMfa9c7Bbqt0M27PYP'
                ),
                taximeter_version='8.65 (2147483647)',
            ),
            False,
            'no_fraud',
        ),
        # 3 [ECB]
        # sig_fake_gps == 1
        # but license_pd_id 'white_license_pd_id' in white_list
        # =>  frauder = false
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6IkJFSjRsZEE0YitDb2tOM2QvSDVWTkEifQ'
                ),
                taximeter_version='8.46 (100)',
                license_pd_ids=['white_license_pd_id'],
            ),
            False,
            'no_fraud',
        ),
        # 4 [GCM]
        # sig_fake_gps == 1
        # but udi 'white_udi' in white_list  =>  frauder = false
        (
            _make_request(
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
                signature_info=(
                    'CiDx/TqzAumlf8Ur3it3u374Sf0W2392r6pLpXokazOlSxIQ'
                    'X3RxppVl1uRpuXd72IMf4xoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoM/9fkYA3GhgrDGRza'
                ),
                taximeter_version='8.46 (100)',
                license_pd_ids=['white_license_pd_id'],
            ),
            False,
            'no_fraud',
        ),
        # 5 [ECB]
        # sig_fake_gps == 1   =>   frauder = true
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6IkJFSjRsZEE0YitDb2tOM2QvSDVWTkEifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            True,
            'fake_gps',
        ),
        # 6 [GCM]
        # sig_fake_gps == 1   =>   frauder = true
        (
            _make_request(
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
                signature_info=(
                    'CiDx/TqzAumlf8Ur3it3u374Sf0W2392r6pLpXokazOlSxIQ'
                    'X3RxppVl1uRpuXd72IMf4xoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoM/9fkYA3GhgrDGRza'
                ),
                taximeter_version='8.65 (2147483647)',
            ),
            True,
            'fake_gps',
        ),
        # 7 [ECB]
        # sig_emulator == 1   =>   frauder = true
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6InFVWTJrcUFnSmxaeHJua0VTcFNHQWcifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            True,
            'emulator',
        ),
        # 8 [GCM]
        # sig_emulator == 1   =>   frauder = true
        (
            _make_request(
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
                signature_info=(
                    'CiCY1v9bJ0go7+KvttPAVbRH6/m3Q5U3DiXwPe46L7lB9hIQ'
                    'oopYxRUgQld7dvU9pAQ/ohoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoMyT0Any8HiE4TjZoX'
                ),
                taximeter_version='8.65 (2147483647)',
            ),
            True,
            'emulator',
        ),
        # 9 [ECB]
        # sig_hook == 9   =>   frauder = true
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6IlhpM0xMU09EUDg0T1I1YjF3Q28vY0EifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            True,
            'hook',
        ),
        # 10 [GCM]
        # sig_hook == 7   =>   frauder = true
        (
            _make_request(
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
                signature_info=(
                    'CiBUjC8D9AWoz87BbSHInSS8v0OZwuTHNPruOyelelqynxIQ'
                    'CGpEpcdegGB/s6uxRyMDRxoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoMWfwKk+Dq5DsyjRXc'
                ),
                taximeter_version='8.65 (2147483647)',
            ),
            True,
            'hook',
        ),
        # 11 [ECB]
        # sig_gps_switch == 11   =>   frauder = true
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6IldDVUFNQzVrTi9JbXl1d3pUODFwM3cifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            True,
            'gps_switch',
        ),
        # 12 [GCM]
        # sig_gps_switch == 11   =>   frauder = true
        (
            _make_request(
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
                signature_info=(
                    'CiAHz5qZZLX5OqBTIVI7/BY55mvKScA5RyNhEcKgqZbBEhIQ'
                    'f3hXCW28dcLQA/MxCoLZvBoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoMZFub44j9x88nOZjp'
                ),
                taximeter_version='8.65 (2147483647)',
            ),
            True,
            'gps_switch',
        ),
        # 13 [ECB]
        # sig_gps_switch == 10   =>   frauder = false
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6Ik50dThadm5zcGhBZXFSZmNkd3piVEEifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            False,
            'no_fraud',
        ),
        # 14 [GCM]
        # sig_gps_switch == 10   =>   frauder = false
        (
            _make_request(
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
                signature_info=(
                    'CiCqMNgmgVD3b7U9D6v2FE5OmMoX+iZw1AiSj3Ogh6rMSBIQ'
                    'wgHhXPZa8+XDyUi8RPMHyxoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoMn8VJ8ny9BkleJMXn'
                ),
                taximeter_version='8.65 (2147483647)',
            ),
            False,
            'no_fraud',
        ),
        # 15 [ECB]
        # sig_net_switch == 11   =>   frauder = true
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6InRDWHA4cVM5Y3FoQW5nVVVwOUFwK1EifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            True,
            'net_switch',
        ),
        # 16 [ECB]
        # sig_net_switch == 10   =>   frauder = false
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6InZ4a3p3VGp5ZjBQUUpER2RpSXNPNGcifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            False,
            'no_fraud',
        ),
        # 17 [ECB]
        # sig_plane_switch == 6   =>   frauder = true
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6IldrNDFzcXU0R2o0ZlVJcDBRQkRwVHcifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            True,
            'plane_switch',
        ),
        # 18 [ECB]
        # sig_plane_switch == 5   =>   frauder = false
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6IkQzR01rT21admtvcThSK1FSZmpVQ0EifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            False,
            'no_fraud',
        ),
        # 19 [ECB]
        # there is not ban for root now
        # sig_root == 1   =>   frauder = false
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6IlBqUGw4U0JnT2dxeE52NDI0WmNURWcifQ'
                ),
                taximeter_version='8.46 (100)',
            ),
            False,
            'no_fraud',
        ),
        # 20 [ECB]
        # bad signature_info, hack case
        # (try to replace pub app_version_code to 99)
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6OTksInNka192ZXJzaW9uX2NvZGUi'
                    'OjEwLCJ0aW1lX21pbGxpcyI6MTUzODM4ODAwMDAwMCwic2ln'
                    'bmF0dXJlIjoiYVFBZFFwRm56bGNxWno5QXUzc0VidyJ9'
                ),
                taximeter_version='8.46 (100)',
            ),
            True,
            'bad_signature',
        ),
        # 21 [ECB]
        # bad taximeter version
        # 'app_id':'ua.yandex.taximeter', 'app_version_code':100 =>
        # app_version_name -> 8.44
        # but 8.45 is minimal
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJ1YS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6Ikt6MWZhQURZUkljaGUwZGxCY2lVWVEifQ'
                ),
                taximeter_version='8.44 (100)',
            ),
            True,
            'taximeter_version',
        ),
        # 22 [GCM]
        # 'sig_root' : 0,
        # 'sig_emulator' : 0,
        # 'sig_fake_gps' : 0,
        # 'sig_hook' : 0,
        # 'sig_plane_switch' : 0,
        # 'sig_gps_switch' : 0,
        # 'sig_net_switch' : 0,
        # 'sig_version_code' : 2147483647,
        # but pub taximeter version 9.65 (2147483647) (want 8.65 (2147483647))
        # =>   frauder = true
        (
            _make_request(
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
                signature_info=(
                    'CiDSllU6IT/QOdL+k8zW6ewpDb8NayiIkwfkvG+MMfyIsBIQ'
                    'B3OrtLhb+jV10LcKvpxWvBoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoMfa9c7Bbqt0M27PYP'
                ),
                taximeter_version='9.65 (2147483647)',
            ),
            True,
            'bad_signature',
        ),
        # 23 [GCM]
        # 'sig_root' : 0,
        # 'sig_emulator' : 0,
        # 'sig_fake_gps' : 0,
        # 'sig_hook' : 0,
        # 'sig_plane_switch' : 0,
        # 'sig_gps_switch' : 0,
        # 'sig_net_switch' : 0,
        # 'sig_version_code' : 2147483647,
        # but pub taximeter version 8.69 (2147483647) (want 8.65 (2147483647))
        # =>   frauder = true
        (
            _make_request(
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
                signature_info=(
                    'CiDSllU6IT/QOdL+k8zW6ewpDb8NayiIkwfkvG+MMfyIsBIQ'
                    'B3OrtLhb+jV10LcKvpxWvBoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoMfa9c7Bbqt0M27PYP'
                ),
                taximeter_version='8.69 (2147483647)',
            ),
            True,
            'bad_signature',
        ),
        # 24 [GCM]
        # 'sig_root' : 0,
        # 'sig_emulator' : 0,
        # 'sig_fake_gps' : 0,
        # 'sig_hook' : 0,
        # 'sig_plane_switch' : 0,
        # 'sig_gps_switch' : 0,
        # 'sig_net_switch' : 0,
        # 'sig_version_code' : 2147483647,
        # but pub taximeter version 8.65 (2147483640) (want 8.65 (2147483647))
        # =>   frauder = true
        (
            _make_request(
                driver_id='d04c48b920d9496ea363ca1fbb90f98c',
                signature_version=3,
                signature_info=(
                    'CiDSllU6IT/QOdL+k8zW6ewpDb8NayiIkwfkvG+MMfyIsBIQ'
                    'B3OrtLhb+jV10LcKvpxWvBoTcnUueWFuZGV4LnRheGltZXRl'
                    'ciD/////BygDMID6x/jiLDoMfa9c7Bbqt0M27PYP'
                ),
                taximeter_version='8.65 (2147483640)',
            ),
            True,
            'bad_signature',
        ),
    ],
)
@pytest.mark.now('2018-10-01T10:00:00+0000')
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS={
        'current': '8.45',
        'disabled': [],
        'feature_support': {},
        'min': '8.45',
        'min_versions_cities': {},
    },
    TAXIMETER_POLLING_DELAYS={
        '/driver/map/order': 60,
        '/driver/polling/state': 300,
        '/driver/rating/item': 900,
    },
    AFS_SIGN_EXPIRED_MUL=3,
    AFS_SIGN_CHECK_DRIVER=True,
    AFS_SIGN_CHECK_DRIVER_FAKE_GPS=True,
    AFS_SIGN_CHECK_DRIVER_SIGNATURE_VALID=True,
    AFS_SIGN_CHECK_DRIVER_EMULATOR=True,
    AFS_SIGN_CHECK_DRIVER_HOOK=True,
    AFS_SIGN_CHECK_DRIVER_GPS_SWITCH=True,
    AFS_SIGN_CHECK_DRIVER_NET_SWITCH=True,
    AFS_SIGN_CHECK_DRIVER_PLANE_SWITCH=True,
    AFS_SIGN_CHECK_DRIVER_TAXIMETER_VERSION=True,
    AFS_SIGN_CHECK_TAXIMETER_PUB_VERSION_VALID=True,
    AFS_SIGN_DRIVER_WHITE_LIST=['white_license_pd_id'],
)
def test_check_sign_fraud_on(taxi_antifraud, db, sign_info, frauder, reason):
    taxi_antifraud.post('driver_client/check_sign', json=sign_info)
    record = _find_driver_client_info(db, sign_info['unique_driver_id'])
    assert record['frauder'] == frauder
    assert record['fraud_reason'] == reason


# sign_sec = 1522059785 (2018-03-26T13:23:05+0300)
@pytest.mark.parametrize(
    'sign_info,frauder',
    [
        # sig_emulator = 1, but ANTIFRAUD_CHECK_DRIVER=false   =>
        # frauder = false
        (
            _make_request(
                signature_info=(
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
                    'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
                    'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
                    'Z25hdHVyZSI6InFVWTJrcUFnSmxaeHJua0VTcFNHQWcifQ'
                ),
            ),
            False,
        ),
    ],
)
@pytest.mark.now('2018-10-01T10:00:00+0000')
@pytest.mark.config(
    TAXIMETER_POLLING_DELAYS={
        '/driver/map/order': 60,
        '/driver/polling/state': 300,
        '/driver/rating/item': 900,
    },
    AFS_SIGN_EXPIRED_MUL=3,
    AFS_SIGN_CHECK_DRIVER=False,
    AFS_SIGN_CHECK_DRIVER_EMULATOR=True,
)
def test_check_sign_fraud_off(taxi_antifraud, db, sign_info, frauder):
    taxi_antifraud.post('driver_client/check_sign', json=sign_info)
    record = _find_driver_client_info(db, sign_info['unique_driver_id'])
    assert record['frauder'] == frauder


@pytest.mark.now('2018-10-01T10:00:00+0000')
@pytest.mark.config(
    TAXIMETER_POLLING_DELAYS={
        '/driver/map/order': 60,
        '/driver/polling/state': 300,
        '/driver/rating/item': 900,
    },
    AFS_SIGN_EXPIRED_MUL=3,
    AFS_SIGN_CHECK_DRIVER=True,
    AFS_SIGN_CHECK_DRIVER_EMULATOR=True,
    AFS_SIGN_CHECK_DRIVER_FAKE_GPS=True,
    AFS_SIGN_BLOCK_DRIVER=True,
    AFS_SIGN_BLOCK_DRIVER_DURATION=27,
)
@pytest.mark.skip(reason='not implemented now')
def test_check_sign_block_base(taxi_antifraud, config, now, db):
    def check(
            info,
            dt,
            duration,
            frauder,
            block,
            fraud_reason,
            block_reason,
            block_count=None,
    ):
        taxi_antifraud.post('driver_client/check_sign', json=info)
        records = _find_driver_client_info(db, info['licenses'])
        for record in records:
            assert record['frauder'] is frauder
            assert record['fraud_reason'] == fraud_reason
            assert record['block'] is block
            assert record['block_reason'] == block_reason
            assert record['block_begin'] == dt
            assert record['block_duration'] == duration
            if block_count is not None:
                assert record['block_count'] == block_count
            else:
                assert 'block_count' not in record

    # sig_emulator == 1   =>   frauder = true
    sign_info_frauder_emulator = {
        'licenses': ['1', '2'],
        'signature_exists': True,
        'signature_info': (
            'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
            'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
            'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
            'Z25hdHVyZSI6InFVWTJrcUFnSmxaeHJua0VTcFNHQWcifQ'
        ),
    }

    # sig_fake_gps == 1   =>   frauder = true
    sign_info_frauder_fakegps = {
        'licenses': ['1', '2'],
        'signature_exists': True,
        'signature_info': (
            'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
            'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
            'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
            'Z25hdHVyZSI6IkJFSjRsZEE0YitDb2tOM2QvSDVWTkEifQ'
        ),
    }

    # all ok              =>  frauder = false
    sign_info_not_frauder = {
        'licenses': ['1', '2'],
        'signature_exists': True,
        'signature_info': (
            'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiwiYXBw'
            'X3ZlcnNpb25fY29kZSI6MTAwLCJzZGtfdmVyc2lvbl9jb2Rl'
            'IjoxMCwidGltZV9taWxsaXMiOjE1MzgzODgwMDAwMDAsInNp'
            'Z25hdHVyZSI6InRwSGhhSTZKT2pURHowTDgvY3lUckEifQ'
        ),
    }

    check(
        sign_info_frauder_emulator,
        now,
        27,
        False,
        True,
        'no_fraud',
        'emulator',
    )

    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=26, seconds=59),
        invalidate_caches=True,
    )
    check(
        sign_info_frauder_emulator,
        now,
        27,
        False,
        True,
        'no_fraud',
        'emulator',
    )

    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=27), invalidate_caches=True,
    )
    check(
        sign_info_frauder_emulator,
        now + datetime.timedelta(minutes=27),
        27,
        False,
        True,
        'no_fraud',
        'emulator',
    )

    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=30), invalidate_caches=True,
    )
    check(
        sign_info_frauder_fakegps,
        now + datetime.timedelta(minutes=27),
        27,
        False,
        True,
        'no_fraud',
        'emulator',
    )

    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=35), invalidate_caches=True,
    )
    check(
        sign_info_not_frauder,
        now + datetime.timedelta(minutes=27),
        27,
        False,
        True,
        'no_fraud',
        'emulator',
    )

    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=54), invalidate_caches=True,
    )
    check(
        sign_info_not_frauder,
        now + datetime.timedelta(minutes=27),
        27,
        False,
        False,
        'no_fraud',
        'no_fraud',
    )

    ##
    ##

    config.set_values(
        dict(
            AFS_SIGN_BLOCK_DRIVER_DEFERRED=True,
            AFS_SIGN_BLOCK_DRIVER_DEFERRED_DURATION=10,
        ),
    )
    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=54), invalidate_caches=True,
    )

    check(
        sign_info_frauder_fakegps,
        now + datetime.timedelta(minutes=64),
        27,
        False,
        True,
        'no_fraud',
        'fake_gps',
    )

    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=57), invalidate_caches=True,
    )
    check(
        sign_info_not_frauder,
        now + datetime.timedelta(minutes=64),
        27,
        False,
        True,
        'no_fraud',
        'fake_gps',
    )

    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=60), invalidate_caches=True,
    )
    check(
        sign_info_frauder_emulator,
        now + datetime.timedelta(minutes=64),
        27,
        False,
        True,
        'no_fraud',
        'fake_gps',
    )

    ##
    ##

    config.set_values(
        dict(
            AFS_SIGN_BLOCK_DRIVER_PROLONG=True,
            AFS_SIGN_BLOCK_DRIVER_PROLONG_DURATION=7,
        ),
    )
    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=61), invalidate_caches=True,
    )

    check(
        sign_info_not_frauder,
        now + datetime.timedelta(minutes=64),
        27,
        False,
        True,
        'no_fraud',
        'fake_gps',
    )

    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=62), invalidate_caches=True,
    )
    check(
        sign_info_frauder_fakegps,
        now + datetime.timedelta(minutes=64),
        27,
        False,
        True,
        'no_fraud',
        'fake_gps',
    )

    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=63), invalidate_caches=True,
    )
    check(
        sign_info_frauder_emulator,
        now + datetime.timedelta(minutes=64),
        27,
        False,
        True,
        'no_fraud',
        'fake_gps',
    )

    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=100), invalidate_caches=True,
    )
    check(
        sign_info_frauder_emulator,
        now + datetime.timedelta(minutes=110),
        27,
        False,
        True,
        'no_fraud',
        'emulator',
        1,
    )

    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=105), invalidate_caches=True,
    )
    check(
        sign_info_frauder_fakegps,
        now + datetime.timedelta(minutes=110),
        27,
        False,
        True,
        'no_fraud',
        'emulator',
        1,
    )

    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=115), invalidate_caches=True,
    )
    check(
        sign_info_frauder_emulator,
        now + datetime.timedelta(minutes=110),
        27,
        False,
        True,
        'no_fraud',
        'emulator',
        1,
    )

    ##

    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=140), invalidate_caches=True,
    )
    check(
        sign_info_frauder_fakegps,
        now + datetime.timedelta(minutes=150),
        34,
        False,
        True,
        'no_fraud',
        'fake_gps',
        2,
    )

    taxi_antifraud.tests_control(
        now + datetime.timedelta(minutes=190), invalidate_caches=True,
    )
    check(
        sign_info_frauder_emulator,
        now + datetime.timedelta(minutes=200),
        41,
        False,
        True,
        'no_fraud',
        'emulator',
        3,
    )


@pytest.mark.now('2018-10-01T10:00:00+0000')
@pytest.mark.parametrize(
    'sign',
    [
        'emxxRDJ5ckZHczlzXc7RlzRSmFTSUgKe/Hcfbsx5fHIq'
        '81bFPCuKHNFdN1IC+ZFBiuBxk6QY9aKgAekSK7SBew==',
        'djljT2NEdWQ0V00yXc7clDHDrK0uCuaqI+VHYkC3xFcP'
        '0qFKgVec9BpwoqEWOjENnxmYSu3NPfFRIZ5mWNcoYQ==',
    ],
)
@pytest.mark.config(
    AFS_CLIENT_DRIVER_IOS_CHECK_ENABLED=True,
    AFS_CLIENT_DRIVER_IOS_SIMPLE_SIGNATURE_CHECK=True,
    AFS_CLIENT_DRIVER_IOS_SIMPLE_SIGNATURE_FAIL_CHECK=True,
    AFS_CLIENT_DRIVER_IOS_PRIVATE_HASH=[
        '7dFO+fEizmFMTiL+UJAadDCgovGQyLBiGMVViT4MVs4=',
        '1qsVVg+HnznWUcbLKOLwSXsx2SSG8DEHXEtqzlmrVrM=',
    ],
    AFS_CLIENT_DRIVER_IOS_UDID=['5d4d5b24b8e3f879683d7a55'],
)
def test_check_sign_ios_tmp_base(taxi_antifraud, sign, db):
    _request = {
        'driver_id': '9ca583658bce4c00b19b3bb4a121d564',
        'signature_exists': False,
        'signature_ios_tmp': sign,
        'taximeter_version': '9.99 (1073759157)',
        'unique_driver_id': '5d4d5b24b8e3f879683d7a55',
        'license_pd_ids': ['license_pd_id'],
    }

    response = taxi_antifraud.post('driver_client/check_sign', _request)
    assert response.status_code == 200
    db_info = _find_driver_client_info(db, _request['unique_driver_id'])
    assert db_info['created'] == datetime.datetime(2018, 10, 1, 10, 0)
    assert db_info['frauder'] is False
    assert db_info['fraud_reason'] == 'no_fraud'
    assert db_info['license'] == 'not_license_' + _request['unique_driver_id']
    assert db_info['unique_driver_id'] == _request['unique_driver_id']


@pytest.mark.now('2019-11-29T09:00:00+0000')
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS={
        'current': '8.45',
        'disabled': [],
        'feature_support': {},
        'min': '8.45',
        'min_versions_cities': {},
    },
    TAXIMETER_POLLING_DELAYS={
        '/driver/map/order': 60,
        '/driver/polling/state': 300,
        '/driver/rating/item': 900,
    },
    AFS_SIGN_EXPIRED_MUL=3,
    AFS_SIGNATURE_STORE_METRICS=True,
)
@pytest.mark.experiments3(
    name='afs_signature_get_driver_app_profile',
    consumers=['afs/signature'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={},
)
@pytest.mark.parametrize(
    'park_db_id,reason',
    [('parkdbid1', 'bad_signature'), ('parkdbid2', 'fake_gps')],
)
def test_check_sign_protocol_v4_base(
        taxi_antifraud, db, testpoint, mockserver, park_db_id, reason,
):
    _request = {
        'driver_id': 'f235ee4a119d4e9ca7d1c3309bba2597',
        'park_db_id': park_db_id,
        'signature_exists': True,
        'signature_info': (
            'ChB50kWIY1P23M1l4+8kVkUsEhCEKL1jSRA+D73Qa9scA0mbGhNydS55YW5'
            'kZXgudGF4aW1ldGVyIP3///8HKAQwpqL1sustOgz+fni9NGH0c2q/q1dCjg'
            'EKABIQ6DrcerHJuqc96Hy9sTmUgRoTcnUueWFuZGV4LnRheGltZXRlciD9/'
            '///BygEMOjC9bLrLToMCLf+Dxgq6TWzEm57SkYKABIQmjQ0d8xo0rawAs7e'
            'kUFgihoTcnUueWFuZGV4LnRheGltZXRlciD9////BygEMMbD9bLrLToMDoY'
            'Oy8TiHUSjpJjRSk0KB7isyx/iOHkSENRVjLqxG8Bnt7yk14eCKFIaE3J1Ln'
            'lhbmRleC50YXhpbWV0ZXIg/f///wcoBDCmovWy6y06DAnQ+2kjQRuR9wE6i'
            'A=='
        ),
        'signature_version': 4,
        'taximeter_version': '9.17 (3645)',
        'user_agent_split': '9.17 (2147483645)',
        'unique_driver_id': '5982f59a9bb9610c238acaab',
        'license_pd_ids': ['license_pd_id'],
        'platform': 'ios',
    }
    _metrica_device_id = '42fcdd3a72202922c1ceb6bc776ee33e'
    _device_model = 'XIAOMI REDMI 5 PLUS'

    @mockserver.json_handler(
        '/driver_profile_base/v1/driver/app/profiles/retrieve', prefix=True,
    )
    def mock_driver_app_profiles_retrieve(request):
        full_id = '{}_{}'.format(_request['park_db_id'], _request['driver_id'])
        assert json.loads(request.get_data()) == {
            'id_in_set': [full_id],
            'projection': ['data.metrica_device_id', 'data.device_model'],
        }
        assert (
            request.path
            == '/driver_profile_base/v1/driver/app/profiles/retrieve'
        )
        assert request.args['consumer'] == 'antifraud'
        return {
            'profiles': [
                {
                    'data': {
                        'device_model': _device_model,
                        'metrica_device_id': _metrica_device_id,
                    },
                    'park_driver_profile_id': full_id,
                },
            ],
        }

    @testpoint('sign_fetch_driver_app_profile')
    def sign_fetch_driver_app_profile(data):
        assert data == {
            'metrica_device_id': _metrica_device_id,
            'device_model': _device_model,
        }

    def ios_by_version(path):
        return 'signature.by_platform.ios.by_version.9_17.{}'.format(path)

    def ios_values(path):
        return 'signature.by_platform.ios.values.{}'.format(path)

    @testpoint('sign_store_metrics')
    def sign_store_metrics(_):
        return {
            'need_replace': True,
            'proc': {
                'sign_exists': True,
                'parse_success': True,
                'key_exists': True,
                'sign_decode_success': True,
                'sign_version_valid': False,
                'sign_pub_info_valid': False,
                'taximeter_pub_version_valid': False,
                'sign_not_expired': False,
                'taximeter_version_valid': False,
            },
            'legacy': {'root': 1, 'fake_gps': 1},
            'vm': [1, 2, 5, 6],
        }

    @testpoint('merge_metrics')
    def merge_metrics(data):
        assert data == {
            ios_by_version('legacy.fake_gps'): 1,
            ios_by_version('legacy.root'): 1,
            ios_by_version('proc.sign_not_expired'): 1,
            ios_by_version('proc.sign_pub_info_valid'): 1,
            ios_by_version('proc.sign_version_valid'): 1,
            ios_by_version('proc.taximeter_pub_version_valid'): 1,
            ios_by_version('vm.hook'): 1,
            ios_by_version('vm.jail_break'): 1,
            ios_by_version('vm.root'): 1,
            ios_by_version('vm.taxa'): 1,
            'signature.by_platform.ios.total': 1,
            ios_values('legacy.fake_gps'): 1,
            ios_values('legacy.root'): 1,
            ios_values('proc.sign_not_expired'): 1,
            ios_values('proc.sign_pub_info_valid'): 1,
            ios_values('proc.sign_version_valid'): 1,
            ios_values('proc.taximeter_pub_version_valid'): 1,
            ios_values('vm.hook'): 1,
            ios_values('vm.jail_break'): 1,
            ios_values('vm.root'): 1,
            ios_values('vm.taxa'): 1,
        }

    response = taxi_antifraud.post('driver_client/check_sign', _request)
    assert response.status_code == 200

    mock_driver_app_profiles_retrieve.wait_call()
    sign_fetch_driver_app_profile.wait_call()
    sign_store_metrics.wait_call()
    merge_metrics.wait_call()

    db_info = _find_driver_client_info(db, _request['unique_driver_id'])
    assert db_info['block'] is False
    # assert db_info['block_begin'] == datetime.datetime(2019, 11, 29, 9, 30)
    # assert db_info['block_duration'] == 60
    # assert db_info['block_reason'] == 'bad_signature'
    assert db_info['created'] == datetime.datetime(2019, 11, 29, 9, 0)
    assert db_info['fraud_reason'] == reason
    assert db_info['frauder'] is True
    assert db_info['last_success_proc'] == datetime.datetime(
        2019, 11, 29, 9, 0,
    )
    assert db_info['license'] == 'not_license_' + _request['unique_driver_id']
    assert db_info['unique_driver_id'] == _request['unique_driver_id']
    assert db_info['signature_info'] == _request['signature_info']
    assert db_info['proc'] == {
        'key_exists': True,
        'parse_success': True,
        'sign_decode_success': True,
        'sign_exists': True,
        'sign_not_expired': True,
        'sign_pub_info_valid': True,
        'sign_version_valid': True,
        'taximeter_pub_version_valid': True,
    }
    assert db_info.get('signature', {}) == {
        'legacy': {
            'emulator': 0,
            'entropy_counter': 1,
            'fake_gps': 0,
            'gps_switch': 0,
            'hook': 0,
            'net_switch': 0,
            'plane_switch': 0,
            'proto_version': 3,
            'root': 0,
            'time_millis': 1575017599270,
            'version_code': 2147483645,
        },
        'vm': [],
    }
    assert db_info['decode_status'] == 0


@pytest.mark.now('2018-10-01T10:00:00+0000')
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS={
        'current': '8.45',
        'disabled': [],
        'feature_support': {},
        'min': '8.45',
        'min_versions_cities': {},
    },
    TAXIMETER_POLLING_DELAYS={
        '/driver/map/order': 60,
        '/driver/polling/state': 300,
        '/driver/rating/item': 900,
    },
    AFS_SIGN_EXPIRED_MUL=3,
    AFS_SIGN_CHECK_AP4_USE_FOR_OLD=True,
)
def test_check_sign_protocol_v4_for_v3(taxi_antifraud, db):
    _request = {
        'driver_id': 'd04c48b920d9496ea363ca1fbb90f98c',
        'park_db_id': 'park_db_id',
        'signature_exists': True,
        'signature_info': (
            'CiBo+LYkf4ZMXqX9jakbz4BamwIAfawRPMGs2s65tsmTiRIQ'
            'fA8zJBe2QW9rjO7UFEe45hoTcnUueWFuZGV4LnRheGltZXRl'
            'ciD/////BygDMID6x/jiLDoM52o36Ah5HbeViLJ6'
        ),
        'signature_version': 3,
        'taximeter_version': '8.65 (2147483647)',
        'unique_driver_id': '5982f59a9bb9610c238acaab',
        'license_pd_ids': ['license_pd_id'],
    }

    response = taxi_antifraud.post('driver_client/check_sign', _request)
    assert response.status_code == 200
    db_info = _find_driver_client_info(db, _request['unique_driver_id'])
    assert db_info['block'] is False
    # assert db_info['block_begin'] == datetime.datetime(2018, 10, 1, 10, 0)
    # assert db_info['block_duration'] == 240
    # assert db_info['block_reason'] == 'bad_signature'
    assert db_info['created'] == datetime.datetime(2018, 10, 1, 10, 0)
    assert db_info['fraud_reason'] == 'bad_signature'
    assert db_info['frauder'] is True
    assert db_info['last_success_proc'] == datetime.datetime(
        2018, 10, 1, 10, 0,
    )
    assert db_info['license'] == 'not_license_5982f59a9bb9610c238acaab'
    assert db_info['unique_driver_id'] == '5982f59a9bb9610c238acaab'
    assert db_info['signature_info'] == _request['signature_info']
    assert db_info['proc'] == {
        'key_exists': True,
        'parse_success': True,
        'sign_decode_success': True,
        'sign_exists': True,
        'sign_not_expired': True,
        'sign_pub_info_valid': True,
        'sign_version_valid': True,
        'taximeter_pub_version_valid': True,
    }
    assert db_info['signature'] == {
        'legacy': {
            'emulator': 0,
            'entropy_counter': 13,
            'fake_gps': 0,
            'gps_switch': 0,
            'hook': 0,
            'net_switch': 0,
            'plane_switch': 0,
            'proto_version': 3,
            'root': 0,
            'time_millis': 1538388000000,
            'version_code': 2147483647,
        },
    }


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS={
        'current': '8.78',
        'disabled': [],
        'feature_support': {
            'activity_reuse_order_details': '8.92',
            'chair_categories': '8.55',
            'chair_requirements_fix': '9.07',
            'corp_order': '8.47',
            'fix_driver_waiting_costs': '8.78',
            'gzip_push': '9.99',
            'hold_subventions': '8.43',
            'json_geoareas': '8.30',
            'pool': '8.43',
            'qc_push': '8.52',
            'request_confirm_disable_translate_status': '8.00',
            'selfemployed_referral': '8.91',
            'selfreg_self_employment': '9.99',
            'service_push_types': '8.40',
            'subvention': '8.33',
            'taximeter_waiting_in_transporting': '8.75',
        },
        'min': '8.92',
        'min_versions_cities': {
            'Абиджан': '8.78',
            'Аккра': '8.78',
            'Ашкелон': '9.07',
            'БАКУ': '8.78',
            'Тель-Авив': '9.07',
        },
    },
    TAXIMETER_POLLING_DELAYS={
        '/driver/cost': 30,
        '/driver/map/order': 60,
        '/driver/payment-type': 300,
        '/driver/personal-subvention-groups': 600,
        '/driver/polling/state': 300,
        '/driver/polling/subventions_status': 30,
        '/driver/rating/item': 900,
    },
    AFS_SIGN_EXPIRED_MUL=3,
    AFS_SIGN_VERIFY_DESERIALIZED_DATA=True,
)
def test_check_sign_protocol_v4_verify(taxi_antifraud, db):
    _request = {
        'driver_id': 'a0eda188fa9edae631bae450935eef6c',
        'park_db_id': 'park_db_id',
        'license_pd_ids': ['cd2126965f63437ca7862dc7fe45be91'],
        'licenses': ['4789746289'],
        'signature_exists': True,
        'signature_info': (
            'CgASENlI0Uuq0Uktf2K9+2sXORoaH3J1LnlhbmRleC50YXhpbWV0ZXIuZmx1dHR'
            'lci5pb3MgkAEoBDDkxqLloy46DAJsC8hMHEr9KQgIDEKgAQoAEhB1vicLq113uX'
            'ext8A87yMIGh9ydS55YW5kZXgudGF4aW1ldGVyLmZsdXR0ZXIuaW9zIJABKAQwu'
            'smi5aMuOgyHsXuBo45Z/WClIGFKTwoAEhAUb8a+32TBohcVz7oZ5yRCGh9ydS55'
            'YW5kZXgudGF4aW1ldGVyLmZsdXR0ZXIuaW9zIJABKAQw/Mqi5aMuOgyuFPfPzHo'
            'D6Rgr7VpKTwoAEhBtUId0F8tbyiBZAGryylRNGh9ydS55YW5kZXgudGF4aW1ldG'
            'VyLmZsdXR0ZXIuaW9zIJABKAQw5Mai5aMuOgycVXCunzIwjosbRZQ='
        ),
        'signature_version': 4,
        'taximeter_version': '1.0',
        'unique_driver_id': '5dcebe228fe28d5ce4f64e48',
    }

    response = taxi_antifraud.post('driver_client/check_sign', _request)
    assert response.status_code == 200
    record = _find_driver_client_info(db, _request['unique_driver_id'])
    del record['updated']
    del record['created']
    assert record == {
        '_id': '5dcebe228fe28d5ce4f64e48',
        'block': False,
        'fraud_reason': 'no_fraud',
        'frauder': False,
        'license': 'not_license_5dcebe228fe28d5ce4f64e48',
        'proc': {'parse_success': False, 'sign_exists': True},
        'signature_info': (
            'CgASENlI0Uuq0Uktf2K9+2sXORoaH3J1LnlhbmRleC50YXhpb'
            'WV0ZXIuZmx1dHRlci5pb3MgkAEoBDDkxqLloy46DAJsC8hMHE'
            'r9KQgIDEKgAQoAEhB1vicLq113uXext8A87yMIGh9ydS55YW5'
            'kZXgudGF4aW1ldGVyLmZsdXR0ZXIuaW9zIJABKAQwusmi5aMu'
            'OgyHsXuBo45Z/WClIGFKTwoAEhAUb8a+32TBohcVz7oZ5yRCG'
            'h9ydS55YW5kZXgudGF4aW1ldGVyLmZsdXR0ZXIuaW9zIJABKA'
            'Qw/Mqi5aMuOgyuFPfPzHoD6Rgr7VpKTwoAEhBtUId0F8tbyiB'
            'ZAGryylRNGh9ydS55YW5kZXgudGF4aW1ldGVyLmZsdXR0ZXIu'
            'aW9zIJABKAQw5Mai5aMuOgycVXCunzIwjosbRZQ='
        ),
        'unique_driver_id': '5dcebe228fe28d5ce4f64e48',
    }


@pytest.mark.config(
    AFS_SIGNATURE_INFO_JS_PASS={
        'default_size': 0,
        'vm_detects': [{'type': 3, 'size': 16}],
        'aux_data': [{'type': 1}],
        'vm_aux_data': [],
    },
    AFS_SIGN_CHECK_SAVE_AUX_DATA=True,
    AFS_SIGN_CHECK_SAVE_AUX_DATA_WHITELIST=[{'type': 1, 'value': '5'}],
    AFS_SIGN_CHECK_SAVE_VM_DETECTS=True,
)
def test_check_sign_vm_detects_pass(taxi_antifraud, testpoint, db):
    vm_detect_not_found = []
    vm_detect_too_large = []
    aux_not_found = []
    aux_too_large = []

    @testpoint('sign_vm_detect_not_found')
    def sign_vm_detect_not_found(data):
        vm_detect_not_found.append(data)

    @testpoint('sign_vm_detect_too_large')
    def sign_vm_detect_too_large(data):
        vm_detect_too_large.append(data)

    @testpoint('sign_aux_not_found')
    def sign_aux_not_found(data):
        aux_not_found.append(data)

    @testpoint('sign_aux_too_large')
    def sign_aux_too_large(data):
        aux_too_large.append(data)

    _request = {
        'driver_id': 'a6632b45002553ef01259b05e49850cb',
        'license_pd_ids': ['931416e262014c8ab82a9073f2f247eb'],
        'park_db_id': '7ad36bc7560449998acbe2c57a75c293',
        'platform': 'android',
        'signature_exists': True,
        'signature_info': (
            'ChCnXN0PEOenO1rsa4+TC5qPEhBx5PkEU1P6nacje6GH/Wu/GhNydS55YW5kZXgu'
            'dGF4aW1ldGVyIP/nhoAEKAQww6uMsMsuOgx+E02RH8uoQW0+X8JC1gUKxwRW7T+K'
            'QqeuBch39RDJIA5ZiWLKi5GCokdiLO75sIBfFZ0vilTLE2v1J7RjYtr+gOAWcBZb'
            'bgpZ+m+U1huaScuSSHXuRt9+/yfAcXCel87OAUeM9ffk8rSfeMhuc/ZyxRQI9uTc'
            '55yJ/3tNgIPmaA6p5fN44kDN8XsoUjucOygdtHd0NeFcPi2P/O421/RMJeO/ZxaH'
            'tQo9Tnj/Oaik5+39N8nQZBEWP7V+yDboaU5GPURmDwFqs5OH3zyznWo/wYTu6N4U'
            'kDZyhueIgcSoagmph0f8QKnifbLzSaun1VoI5Gut3C9X38eZl0J4oQxFEDngQv15'
            'pUNGzS9ak0uRDNGFNIVdI9kLOtFThUzxlgcKQU+6C6Jb+SxU1y5oH7sg4poNMpYk'
            'RkSM3xz1XpSlBjfZzRyyjh0hYoBqd3L/DiY/33rwTmGmn9/b6QjZeLUrmyZLY5IE'
            '/ehxi4ccmp2b+SBgDXaMjm3PFK2whhm49YAkLYFdYvIc6w6ap9INnMkw6QB883mN'
            'i302SOAtIwtycLdi9CU3dqRFhnWf00Qq5xD4bafiUjaEQrdc/xH7ZD+brKCN3cfz'
            'I0FELSLmUp/0wnR+p4vTipffTSd3XZ2JNzq/RZ/V1zpYKWJaiUy+fQ5Pj7kOeF8v'
            'IFXfoX7SsRq38b8Urku+1/fRYilbkkRsoXrgPFF9oPKvPBjWS7TOPNCvOXjQ8S3R'
            'XI7mLy3GjljhPZc8kaVEiXEmP5gcLgQ5fyC8MSfGIYOwk9a4tNr6kFm/Q79ou5D6'
            'YcIwEhD/UZuD8qA94eCwdLpnyNw4GhNydS55YW5kZXgudGF4aW1ldGVyIP/nhoAE'
            'KAQw6buMsMsuOgyxZhaeZjBphEFPc+BKRgoAEhBawhLx6zT8fwCR90+cM3xwGhNy'
            'dS55YW5kZXgudGF4aW1ldGVyIP/nhoAEKAQwgLyMsMsuOgxoS/uvcH7uB0rXZ31K'
            'VAoOPoIRctB8b1/PV90rOlMSEK7THhnBCe1LHZiEZ2CJuWAaE3J1LnlhbmRleC50'
            'YXhpbWV0ZXIg/+eGgAQoBDDDq4ywyy46DL5GLr2Xk9YAmIEvZg=='
        ),
        'signature_version': 4,
        'taximeter_version': '9.28 (1073853439)',
        'unique_driver_id': '5e2ec8eebcf349534666d041',
        'user_agent': 'Taximeter 9.28 (1073853439)',
        'user_agent_split': '9.28 (1073853439)',
    }

    response = taxi_antifraud.post('driver_client/check_sign', _request)
    assert response.status_code == 200

    assert vm_detect_not_found == [
        {'id': 2, 'type': 1, 'value': '/system/bin/su'},
        {'id': 2, 'type': 1, 'value': '/system/xbin/su'},
        {'id': 3, 'type': 1, 'value': '/system/app/Superuser'},
    ]
    assert vm_detect_too_large == [
        {'id': 2, 'type': 3, 'value': '/ueventd.vbox86.rc'},
        {'id': 2, 'type': 3, 'value': '/system/bin/mount.vboxsf'},
        {'id': 2, 'type': 3, 'value': '/system/bin/genybaseband'},
        {'id': 2, 'type': 3, 'value': '/system/etc/init.genymotion.sh'},
        {'id': 2, 'type': 3, 'value': '/system/lib/vboxguest.ko'},
        {'id': 2, 'type': 3, 'value': '/system/lib/vboxsf.ko'},
        {'id': 2, 'type': 3, 'value': '/system/lib/egl/libEGL_emulation.so'},
        {
            'id': 2,
            'type': 3,
            'value': '/system/lib/egl/libGLESv1_CM_emulation.so',
        },
        {
            'id': 2,
            'type': 3,
            'value': '/system/lib/egl/libGLESv2_emulation.so',
        },
        {
            'id': 2,
            'type': 3,
            'value': '/system/usr/keylayout/Genymotion_Virtual_Input.kl',
        },
        {'id': 3, 'type': 3, 'value': '/system/genymotion'},
        {'id': 3, 'type': 3, 'value': '/sys/module/vboxguest'},
        {'id': 3, 'type': 3, 'value': '/sys/module/vboxsf'},
    ]
    assert aux_not_found == [{'type': 2, 'value': '0'}]
    assert aux_too_large == [{'type': 1, 'value': '5'}]

    expected_vm_detects = [
        {
            'driver_uuid': 'a6632b45002553ef01259b05e49850cb',
            'vm_detect_id': 2,
            'vm_detect_type': 3,
        },
        {
            'driver_uuid': 'a6632b45002553ef01259b05e49850cb',
            'vm_detect_id': 3,
            'vm_detect_type': 3,
        },
        {
            'driver_uuid': 'a6632b45002553ef01259b05e49850cb',
            'vm_detect_id': 2,
            'vm_detect_type': 1,
        },
        {
            'driver_uuid': 'a6632b45002553ef01259b05e49850cb',
            'vm_detect_id': 3,
            'vm_detect_type': 1,
        },
    ]

    while db.antifraud_vm_detects.count() < len(expected_vm_detects):
        # wait for unacknowledged write
        time.sleep(0.01)

    assert (
        list(
            db.antifraud_vm_detects.find(
                {}, {'_id': False, 'last_time_detected_at': False},
            ),
        )
        == expected_vm_detects
    )

    expected_aux_data = [
        {
            'driver_uuid': 'a6632b45002553ef01259b05e49850cb',
            'type': 1,
            'value': '5',
        },
    ]

    while db.antifraud_protector_aux_data.count() < len(expected_aux_data):
        # wait for unacknowledged write
        time.sleep(0.01)

    assert (
        list(
            db.antifraud_protector_aux_data.find(
                {}, {'_id': False, 'last_time_detected_at': False},
            ),
        )
        == expected_aux_data
    )
