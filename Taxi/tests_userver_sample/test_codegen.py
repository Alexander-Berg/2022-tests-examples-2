import json
import platform
import re

import pytest


DEFAULT_ERROR_CONTENT_TYPE = 'application/json; charset=utf-8'

# Max year representable by libstdc++ std::chrono::system_clock::time_point
PLATFORM_CPP_MAX_YEAR = 2262


MACOS_XFAIL = {
    'condition': platform.system() == 'Darwin',
    'reason': (
        'Tests fail on MacOS, see https://st.yandex-team.ru/TAXICOMMON-3902'
    ),
    'strict': True,
}


def assert_truncated_date(date: str) -> None:
    year = date.split('-')[0]
    assert len(year) == 4, f'Actual year is "{year}"'
    assert int(year) >= PLATFORM_CPP_MAX_YEAR, f'Actual year is "{year}"'


async def test_info_get_noquery(taxi_userver_sample):
    response = await taxi_userver_sample.get('autogen/info')
    assert response.status_code == 400
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


@pytest.mark.parametrize(
    'req_resp',
    [
        {'id-required': 0},  # required
        {'id-required': 0, 'registered': True},  # bool
        {'id-required': 0, 'minEx': -9},  # exclusive minimum
        {'id-required': 0, 'maxEx': 9},  # exclusive maximum
        {'id-required': 0, 'posDouble': 0.5},  # fp exclusive minimum
        {'id-required': 0, 'negDouble': -0.25},  # fp exclusive maximum
        {'id-required': -10},  # small integer
        {'id-required': 100},  # big integer
        {'id-required': 0, 'date': '2017-12-31'},  # date
    ],
)
async def test_autogen_info_get(taxi_userver_sample, mockserver, req_resp):
    version_re = re.compile(r'userver-sample/\d+\.\d+\.\d+ \(.*\) userver/.*')

    @mockserver.json_handler('/userver-sample/autogen/info')
    async def _handler(request):
        assert version_re.match(request.headers['User-Agent'])
        for key, value in req_resp.items():
            assert key in request.args
            if isinstance(value, bool):
                assert request.args[key].lower() == str(value).lower()
            elif isinstance(value, (int, float)):
                assert float(request.args[key]) == value
            else:
                assert request.args[key] == str(value)
        return mockserver.make_response(json=req_resp)

    response = await taxi_userver_sample.get('autogen/info', params=req_resp)
    assert response.status_code == 200
    assert response.json() == req_resp
    assert 'Server' in response.headers
    assert version_re.match(response.headers['Server'])
    assert '\n' not in response.headers['Server']
    assert _handler.times_called == 1


async def test_info_get_all(taxi_userver_sample, mockserver):
    request_params = {
        'id-required': 0,
        'id': '123',
        'array-csv': '1,2,3',
        'array-tsv': '4\t5,6\t,\t8|\t9',
    }
    json_response = {
        'id-required': 0,
        'id': '123',
        'array-csv': [1, 2, 3],
        'array-tsv': ['4', '5,6', ',', '8|', '9'],
    }

    @mockserver.json_handler('/userver-sample/autogen/info')
    async def _handler(request):
        for key in ('id', 'array-csv', 'array-tsv'):
            assert key in request.args
        return mockserver.make_response(json=json_response)

    response = await taxi_userver_sample.get(
        'autogen/info', params=request_params,
    )
    assert response.status_code == 200
    assert response.json() == json_response
    assert _handler.times_called == 1


async def test_parameter_enum(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/info',
        params={'enum': 'bar'},
        headers={'header-value-required': '1.0'},
    )
    assert response.status_code == 200
    assert response.headers['enum'] == 'this is bar'
    assert response.json() == {'header-value-required': 1.0}


async def test_array_wrong_item_type(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'autogen/info', params={'id-required': 'string', 'array-csv': '1,a,2'},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'invalid int32_t value of \'id_required\' in query: string',
    }
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


async def test_info_get_integer_bad(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'autogen/info', params={'id-required': 'string'},
    )
    assert response.status_code == 400


async def test_exclusive_minimum(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'autogen/info', params={'id-required': 0, 'minEx': -10},
    )
    assert response.status_code == 400


async def test_exclusive_maximum(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'autogen/info', params={'id-required': 0, 'maxEx': 10},
    )
    assert response.status_code == 400


async def test_exclusive_minimum_double(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'autogen/info', params={'id-required': 0, 'posDouble': 0},
    )
    assert response.status_code == 400


async def test_exclusive_maximum_double(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'autogen/info', params={'id-required': 0, 'negDouble': 0},
    )
    assert response.status_code == 400


async def test_info_get_integer_small(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'autogen/info', params={'id-required': -11},
    )
    assert response.status_code == 400


async def test_info_get_integer_big(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'autogen/info', params={'id-required': 101},
    )
    assert response.status_code == 400


async def test_path(taxi_userver_sample):
    response = await taxi_userver_sample.get('autogen/myid')
    assert response.status_code == 200
    assert response.json() == {'id': 'myid'}


async def test_path_nested(taxi_userver_sample):
    response = await taxi_userver_sample.get('autogen/nested/mynestedid')
    assert response.status_code == 200
    assert response.json() == {'nested-id': 'mynestedid'}


async def test_path_nested_noslash(taxi_userver_sample):
    response = await taxi_userver_sample.get('autogen/nested')
    assert response.status_code == 200
    assert response.json() == {'id': 'nested'}


async def test_path_nested_slash(taxi_userver_sample):
    response = await taxi_userver_sample.get('autogen/nested/')
    assert response.status_code == 200
    assert response.json() == {'nested-id': ''}


async def test_path_nested_separate(taxi_userver_sample):
    response = await taxi_userver_sample.get('autogen/separate/nested/theirid')
    assert response.status_code == 200
    assert response.json() == {'id': 'theirid'}


async def test_path_nested_separate_noslash(taxi_userver_sample):
    response = await taxi_userver_sample.get('autogen/separate/nested')
    assert response.status_code == 404


async def test_header_required(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/info', headers={'header-value-required': '1.0'},
    )
    assert response.status_code == 200
    # epsilon?
    assert response.json() == {'header-value-required': 1.0}


async def test_header(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/info',
        headers={'header-value-required': '1', 'header-value': 'aaa'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'header-value-required': 1,
        'header-value': 'aaa',
    }


async def test_info_datetime_rfc(taxi_userver_sample, mockserver):
    req_resp = {'id-required': 0, 'date-time': '2017-04-04T15:32:22+10:00'}

    @mockserver.json_handler('/userver-sample/autogen/info')
    async def _handler(request):
        return mockserver.make_response(json=req_resp)

    response = await taxi_userver_sample.get('autogen/info', params=req_resp)
    assert response.status_code == 200
    assert response.json() == {
        'id-required': 0,
        'date-time': '2017-04-04T05:32:22+00:00',
    }
    assert _handler.times_called == 1


@pytest.mark.xfail(**MACOS_XFAIL)
async def test_info_datetime_rfc_overflow(taxi_userver_sample, mockserver):
    req_resp = {'id-required': 0, 'date-time': '9999-12-31T23:59:59+00:00'}

    @mockserver.json_handler('/userver-sample/autogen/info')
    async def _handler(request):
        return mockserver.make_response(json=req_resp)

    response = await taxi_userver_sample.get('autogen/info', params=req_resp)
    assert response.status_code == 200
    assert _handler.times_called == 1

    assert_truncated_date(response.json()['date-time'])


async def test_info_datetime_backcompat(taxi_userver_sample, mockserver):
    resp = {'id-required': 0, 'date-time': '2017-04-04T05:32:22+00:00'}

    @mockserver.json_handler('/userver-sample/autogen/info')
    async def _handler(request):
        return mockserver.make_response(json=resp)

    response = await taxi_userver_sample.get(
        'autogen/info',
        params={'id-required': 0, 'date-time': '2017-04-04T15:32:22+1000'},
    )
    assert response.status_code == 200
    assert response.json() == resp
    assert _handler.times_called == 1


@pytest.mark.xfail(**MACOS_XFAIL)
async def test_info_datetime_backcompat_overflow(
        taxi_userver_sample, mockserver,
):
    req_resp = {'id-required': 0, 'date-time': '9999-12-31T23:59:59+1000'}

    @mockserver.json_handler('/userver-sample/autogen/info')
    async def _handler(request):
        assert_truncated_date(request.args['date-time'])
        return mockserver.make_response(json=req_resp)

    response = await taxi_userver_sample.get('autogen/info', params=req_resp)
    assert response.status_code == 200
    assert_truncated_date(response.json()['date-time'])
    assert _handler.times_called == 1


async def test_info_datetime_nonrfc(taxi_userver_sample, mockserver):
    resp = {'id-required': 0, 'date-time': '2017-04-04T05:32:22+00:00'}

    @mockserver.json_handler('/userver-sample/autogen/info')
    async def _handler(request):
        return mockserver.make_response(json=resp)

    response = await taxi_userver_sample.get(
        'autogen/info',
        params={
            'id-required': 0,
            'date-time-non-rfc': '2017-04-04T15:32:22+1000',
        },
    )
    assert response.status_code == 200
    assert response.json() == resp
    assert _handler.times_called == 1


@pytest.mark.xfail(**MACOS_XFAIL)
async def test_info_datetime_nonrfc_overflow(taxi_userver_sample, mockserver):
    resp = {'id-required': 0, 'date-time': '9999-12-31T23:59:59+1000'}

    @mockserver.json_handler('/userver-sample/autogen/info')
    async def _handler(request):
        assert_truncated_date(request.args['date-time-non-rfc'])
        return mockserver.make_response(json=resp)

    response = await taxi_userver_sample.get(
        'autogen/info',
        params={
            'id-required': 0,
            'date-time-non-rfc': '9999-12-31T23:59:59+1000',
        },
    )
    assert response.status_code == 200
    assert_truncated_date(response.json()['date-time'])
    assert _handler.times_called == 1


@pytest.mark.xfail(**MACOS_XFAIL)
async def test_info_date_nonrfc_overflow(taxi_userver_sample, mockserver):
    req_resp = {'id-required': 0, 'date': '9999-12-31'}

    @mockserver.json_handler('/userver-sample/autogen/info')
    async def _handler(request):
        assert_truncated_date(request.args['date'])
        return mockserver.make_response(json=req_resp)

    response = await taxi_userver_sample.get('autogen/info', params=req_resp)
    assert response.status_code == 200
    assert_truncated_date(response.json()['date'])
    assert _handler.times_called == 1


async def test_info_int64(taxi_userver_sample, mockserver):
    bigint = 9223372036854775807
    assert bigint > 2 ** 32
    request_response = {'id-required': 0, 'int64': bigint}

    @mockserver.json_handler('/userver-sample/autogen/info')
    async def _handler(request):
        return mockserver.make_response(json=request_response)

    response = await taxi_userver_sample.get(
        'autogen/info', params=request_response,
    )
    assert response.status_code == 200
    assert response.json() == request_response
    assert _handler.times_called == 1


@pytest.mark.parametrize(
    'int_value', ['0qwe', 'asd', str(2 ** 128), '-0qwe', '0xFF'],
)
async def test_info_bad_integral_format(taxi_userver_sample, int_value):
    faled_to_parse_int64 = {
        'code': '400',
        'message': 'invalid int64_t value of \'int64\' in query: ' + int_value,
    }
    faled_to_parse_minex = {
        'code': '400',
        'message': 'invalid int32_t value of \'minex\' in query: ' + int_value,
    }

    response = await taxi_userver_sample.get(
        'autogen/info', params={'id-required': 0, 'int64': int_value},
    )
    assert response.status_code == 400
    assert response.json() == faled_to_parse_int64

    response = await taxi_userver_sample.get(
        'autogen/info', params={'id-required': 0, 'minEx': int_value},
    )
    assert response.status_code == 400
    assert response.json() == faled_to_parse_minex


@pytest.mark.parametrize(
    'uuid',
    [
        '12345678-1234-1234-1234-123412345678',
        '12345678123412341234123412345678',
        '{12345678-1234-1234-1234-123412345678}',
        '{12345678123412341234123412345678}',
    ],
)
async def test_info_uuid(taxi_userver_sample, mockserver, uuid):
    response_json = {
        'id-required': 0,
        'uuid': '12345678-1234-1234-1234-123412345678',
    }

    @mockserver.json_handler('/userver-sample/autogen/info')
    async def _handler(request):
        assert request.args['uuid'] == response_json['uuid']
        return mockserver.make_response(json=response_json)

    response = await taxi_userver_sample.get(
        'autogen/info', params={'id-required': 0, 'uuid': uuid},
    )
    assert response.status_code == 200
    assert response.json() == response_json
    assert _handler.times_called == 1


@pytest.mark.parametrize(
    'uuid', ['0qwe', 'asd', str(2 ** 128), '-0qwe', '0xFF'],
)
async def test_info_bad_uuid_format(taxi_userver_sample, uuid):
    faled_to_parse = {
        'code': '400',
        'message': 'invalid UUID value of \'uuid\' in query: ' + uuid,
    }

    response = await taxi_userver_sample.get(
        'autogen/info', params={'id-required': 0, 'uuid': uuid},
    )
    assert response.status_code == 400
    assert response.json() == faled_to_parse


async def test_common_parameters(taxi_userver_sample):
    response = await taxi_userver_sample.get('autogen/common')
    assert response.status_code == 200
    assert response.json() == {}


async def test_private_parameters(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'autogen/common',
        params={'common': '123', 'common2': '345', 'private': '2'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'common': '123',
        'common2': '345',
        'private': '2',
    }


async def test_default(taxi_userver_sample):
    response = await taxi_userver_sample.get('autogen/default')
    assert response.status_code == 200
    assert response.json() == {'string': '1', 'int': 1, 'empty_string': ''}


async def test_default_pass(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'autogen/default',
        params={'string': '2', 'int': 2, 'empty_string': 'NOPE'},
    )
    assert response.status_code == 200
    assert response.json() == {'string': '2', 'int': 2, 'empty_string': 'NOPE'}


async def test_default_body(taxi_userver_sample):
    response = await taxi_userver_sample.post('autogen/default')
    assert response.status_code == 200
    assert response.json() == {'string': '1', 'int': 1, 'empty_string': ''}


async def test_default_body_pass(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/default',
        json={'string': '2', 'int': 2, 'empty_string': 'not empty string'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'string': '2',
        'int': 2,
        'empty_string': 'not empty string',
    }


async def test_ref(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/schema', data=json.dumps({'field1': 123}),
    )
    assert response.status_code == 200
    assert response.json() == {'field1': 123}


async def test_ref_optional_validation(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/schema',
        data=json.dumps({'field1': 123, 'field2': 200}),  # >maximum
    )
    assert response.status_code == 400


async def test_ref_validation(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/schema', data=json.dumps({'field1': -10}),  # <minimum
    )
    assert response.status_code == 400


async def test_ref_object(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/schema',
        data=json.dumps(
            {
                'field1': 123,
                'field3': {
                    'int': 123,
                    'double': 10.2,
                    'string': 'hello world',
                },
            },
        ),
    )
    assert response.status_code == 200
    assert response.json() == {
        'field1': 123,
        'field2': {'int': 123, 'double': 10.2, 'string': 'hello world'},
        'field3': {'int': 123, 'double': 10.2, 'string': 'hello world'},
    }


async def test_ref_to_map(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/schema',
        data=json.dumps({'field1': 123, 'map': {'a': 'b', 'c': 'd'}}),
    )
    assert response.status_code == 200
    assert response.json() == {'field1': 123, 'map': {'a': 'b', 'c': 'd'}}


async def test_external_ref(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'autogen/external-definitions', params={'zone_id': 'TeStZonE'},
    )
    assert response.status_code == 200
    assert response.json() == {'zone': {'zone_id': 'TeStZonE'}}


async def test_external_ref_error(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'autogen/external-definitions', params={'zone_id': 'missing'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'ZONE_NOT_FOUND',
        'message': 'Zone not found',
    }


async def test_external_ref_ok_schema(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'autogen/common-external-definitions',
    )
    assert response.status_code == 200
    assert response.json() == {'default_zone': {'zone_id': 'default'}}


async def test_4_0_noauth(taxi_userver_sample):
    response = await taxi_userver_sample.get('4.0/userver-sample/autogen/user')
    assert response.status_code == 401


async def test_4_0_authok(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        '4.0/userver-sample/autogen/user',
        headers={
            'X-Yandex-Login': 'userx',
            'X-Login-Id': 'login_id_xx',
            'X-Yandex-Uid': '100',
            'X-YaTaxi-UserId': 'test_user_id_xxx',
            'X-YaTaxi-PhoneId': 'test_phone_id_xxx',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'yandex_login': 'userx',
        'login_id': 'login_id_xx',
        'yandex_uid': '100',
    }


@pytest.mark.parametrize(
    'request_yandex_uid,response_yandex_uid,status_code',
    [('123', '123', 200)],
    # TODO(arteeemik): add test (None, None, 401) for passport-authproxy
)
async def test_passport_authproxy(
        taxi_userver_sample,
        request_yandex_uid,
        response_yandex_uid,
        status_code,
):
    headers = {}
    if request_yandex_uid:
        headers = {'X-Yandex-Uid': request_yandex_uid}
    response = await taxi_userver_sample.get(
        'test_passport_authproxy', headers=headers,
    )
    assert response.status_code == status_code
    if response_yandex_uid:
        assert response.json() == {'yandex_uid': response_yandex_uid}


async def test_4_0_auth_failure_pass(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        '4.0/userver-sample/autogen/user',
    )
    assert response.status_code == 200
    assert response.json() == {'is_authorized': 0}


async def test_4_0_auth_failure_pass_2(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        '4.0/userver-sample/autogen/user',
        headers={'X-Yandex-Login': 'userx', 'X-Yandex-Uid': '100'},
    )
    assert response.status_code == 200
    assert response.json() == {'is_authorized': 1}


@pytest.mark.parametrize(
    'request_json,response_text,response_code',
    [
        ({'variant': {'type': 'string', 'value': 'test'}}, 'test', 200),
        ({'variant': {'value': 'bad'}}, None, 400),
        ({'variant': {'type': 'boolean', 'value': True}}, None, 400),
        (
            {'variant': {'type': 'PolymorphicBoolean', 'value': True}},
            'true',
            200,
        ),
        ({'variant': {'type': 'int', 'value': -1}}, None, 400),
    ],
)
async def test_one_of(
        taxi_userver_sample, request_json, response_text, response_code,
):
    response = await taxi_userver_sample.post(
        'autogen/one_of', json=request_json,
    )
    assert response.status_code == response_code
    assert response.text == response_text or response_text is None


async def test_one_of_in_body(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/one_of_in_body', json={'type': 'string', 'value': 'test'},
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.parametrize(
    'json_data',
    [
        {'type': 'PolymorphicString', 'value': 'Testing OneOf response'},
        {'type': 'PolymorphicInteger', 'value': 42},
    ],
)
async def test_one_of_response(taxi_userver_sample, mockserver, json_data):
    @mockserver.json_handler('/userver-sample/autogen/one_of_response')
    async def _handler(request):
        return mockserver.make_response(json=json_data)

    response = await taxi_userver_sample.post(
        'autogen/one_of_response', json=json_data,
    )
    assert response.status_code == 200
    assert response.json() == json_data
    assert _handler.times_called == 1


@pytest.mark.parametrize(
    'request_json,response_json',
    [
        (
            {'value': 'very_bad'},
            {
                'code': '400',
                'message': (
                    'Parse error at pos 20, path \'\': '
                    'Value of \'/\' cannot be parsed as a variant'
                ),
            },
        ),
    ],
)
async def test_one_of_in_body_error(
        taxi_userver_sample, request_json, response_json,
):
    response = await taxi_userver_sample.post(
        'autogen/one_of_in_body', json=request_json,
    )
    assert response.status_code == 400
    assert response.json() == response_json


async def test_discriminator(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/discriminator',
        data=json.dumps(
            {
                'object_no_mapping': {
                    'type': 'PolymorphicString',
                    'value': 'Hello world',
                },
                'objectWithMapping': {'type': '3', 'value': 42},
            },
        ),
    )
    assert response.status_code == 200
    assert response.json() == {
        'object_no_mapping_type': 'string',
        'objectWithMappingType': 'integer',
        'echo_object_no_mapping': {
            'type': 'PolymorphicString',
            'value': 'Hello world',
        },
        'echoObjectWithMapping': [{'type': 'int', 'value': 42}],
    }


async def test_cache(taxi_userver_sample):
    response = await taxi_userver_sample.get('autogen/cache')
    assert response.status_code == 200
    assert response.json() == {'count': 0, 'client_qos_timeout_ms': 200}


async def test_enum_default(taxi_userver_sample):
    response = await taxi_userver_sample.post('autogen/types')
    assert response.status_code == 200
    assert response.json() == {
        'enum': 'foo',
        'query-array': [],
        'bool-default': False,
    }


async def test_datetime_rfc(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/types',
        data=json.dumps({'date-time': '2017-04-04T15:32:22+10:00'}),
    )
    assert response.status_code == 200
    assert response.json() == {
        'enum': 'foo',
        'date-time': '2017-04-04T05:32:22+00:00',
        'query-array': [],
        'bool-default': False,
    }


@pytest.mark.xfail(**MACOS_XFAIL)
async def test_datetime_rfc_overflow(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/types',
        data=json.dumps({'date-time': '9999-12-31T19:00:00+10:00'}),
    )
    assert response.status_code == 200
    assert_truncated_date(response.json()['date-time'])


async def test_datetime_nonrfc(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/types',
        data=json.dumps({'date-time-non-rfc': '2017-04-04T15:32:22+1000'}),
    )
    assert response.status_code == 200
    assert response.json() == {
        'enum': 'foo',
        'date-time-non-rfc': '2017-04-04T05:32:22+0000',
        'query-array': [],
        'bool-default': False,
    }


async def test_datetime_nonrfc_overflow(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/types',
        data=json.dumps({'date-time-non-rfc': '8500-04-04T15:32:22+1000'}),
    )
    assert response.status_code == 200
    assert_truncated_date(response.json()['date-time-non-rfc'])


async def test_uuid(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/types',
        data=json.dumps({'uuid': '12345678-1234-1234-1234-123412345678'}),
    )
    assert response.status_code == 200
    assert response.json() == {
        'enum': 'foo',
        'uuid': '12345678-1234-1234-1234-123412345678',
        'query-array': [],
        'bool-default': False,
    }


@pytest.mark.parametrize(
    'request_json,request_id_header,response_code',
    [
        ({'key': '123'}, '123456', 400),
        ({'key': '1234'}, '12345', 400),
        ({'key': '1234'}, '123456', 200),
        ({'key': 'Прив'}, 'ет мир', 200),
        ({'key': '1234'}, '1234567', 200),
        ({'key': 'Прив'}, 'ет мир!', 200),
        ({'key': '1234'}, '12345678', 400),
        ({'key': '12345'}, '12345', 400),
        ({'key': '12345'}, '123456', 200),
        ({'key': 'Приве'}, 'т мир!', 200),
        ({'key': '12345'}, '1234567', 200),
        ({'key': 'Приве'}, 'т мир!!', 200),
        ({'key': 'При в'}, 'т мир!!', 200),
        ({'key': '12345'}, '12345678', 400),
        ({'key': '123456'}, '123456', 400),
    ],
)
async def test_strlen(
        taxi_userver_sample, request_json, request_id_header, response_code,
):
    response = await taxi_userver_sample.post(
        'autogen/strlen',
        headers={'X-Id': request_id_header},
        json=request_json,
    )
    assert response.status_code == response_code


async def test_pattern_ok(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/pattern', data=json.dumps({'phone': '+71112223344'}),
    )
    assert response.status_code == 200


async def test_pattern_fail(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/pattern', data=json.dumps({'phone': '+71112223344666'}),
    )
    assert response.status_code == 400


async def test_array_minitems(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/types', data=json.dumps({'array': []}),
    )
    assert response.status_code == 400


async def test_array_maxitems(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/types', data=json.dumps({'array': ['1', '2', '3']}),
    )
    assert response.status_code == 400


async def test_array_okitems(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/types', data=json.dumps({'array': ['1', '2']}),
    )
    assert response.status_code == 200
    assert response.json() == {
        'enum': 'foo',
        'array': ['1', '2'],
        'query-array': [],
        'bool-default': False,
    }


async def test_array_geometry_position(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/types', data=json.dumps({'position': [1.0, 0.0]}),
    )
    assert response.status_code == 200
    assert response.json() == {
        'enum': 'foo',
        'position': [1.0, 0.0],
        'query-array': [],
        'bool-default': False,
    }


@pytest.mark.parametrize(
    'items,response_code',
    [
        (['1'], 400),
        (['1', '2', '3'], 200),
        (['1', '2', '3', '4'], 200),
        (['1', '2', '3', '4', '5'], 400),
    ],
)
async def test_query_array_minmaxitems(
        taxi_userver_sample, items, response_code,
):
    response = await taxi_userver_sample.post(
        'autogen/types', params={'query-array': ','.join(map(str, items))},
    )
    assert response.status_code == response_code
    if response_code == 200:
        assert response.json() == {
            'enum': 'foo',
            'query-array': items,
            'bool-default': False,
        }


async def test_response_headers(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'autogen/complex-response-headers',
    )
    assert response.status_code == 200
    assert response.headers['int'] == '444'
    assert response.headers['enum'] == 'value1'
    assert response.headers['array'] == '3,5,7'
    assert response.headers['string'] == 'value'


async def test_pinned_coroutines(taxi_userver_sample):
    response = await taxi_userver_sample.get('pinned')
    assert response.status_code == 200
    thread_id = response.json()['thread_id']

    for _ in range(10):
        response = await taxi_userver_sample.get('pinned')
        assert response.status_code == 200
        assert response.json() == {'thread_id': thread_id}
