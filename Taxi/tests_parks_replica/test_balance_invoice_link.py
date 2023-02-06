import io
import typing
import xml.dom.minidom as minidom

import pytest

HEADERS = {
    'X-Park-Id': 'out_park_id',
    'X-Yandex-Uid': '135',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Ya-User-Ticket': (
        '3:serv:CBAQ__________9_IgUIbxCpEg:'
        'R7D7xzFeVTDH7MxPwLq3B79kd4OCuN1vdt'
        'tgoREgHWa37V2DP4IWvKSQyoXTLLtyeOxP'
        'NczqVvYw8r8t9lePEmYUOB4ZDtTgVbo15i'
        'gPTCwA9xjIoZhIA-V6Xlhyxntaz9N8Qp8S'
        'PoLjGgRRPrV-NtugVJR8nuETc-elGexalCw'
    ),
}


def _format_xml(xml: typing.Union[bytes, str]) -> str:
    if isinstance(xml, bytes):
        rdom = minidom.parse(io.BytesIO(xml))
    else:
        rdom = minidom.parse(io.StringIO(xml))
    txt = rdom.toprettyxml()
    return '\n'.join(
        x for x in txt.replace('\r', '\n').split('\n') if x.strip()
    )


@pytest.fixture(name='happy_path_fleet_parks')
def _fixture_fleet_parks(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _fleet_parks_parks_list(request):
        assert request.json == {'query': {'park': {'ids': ['out_park_id']}}}
        return {
            'parks': [
                {
                    'id': 'out_park_id',
                    'provider_config': {
                        'clid': 'our_clid',
                        'type': 'production',
                    },
                    'country_id': 'RUS',
                    # Unused fields
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    'login': 'some_login',
                    'city_id': 'some_city_id',
                    'name': 'some_park_name',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'locale': 'ru',
                    'demo_mode': False,
                },
            ],
        }


@pytest.fixture(name='happy_path_billing_replication')
def _billing_replication(mockserver):
    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    def _billing_replication_mock(request):
        if request.query['service_id'] == '111':
            assert dict(request.query) == {
                'service_id': '111',
                'active_ts': '2021-10-21T18:00:00+0000',
                'actual_ts': '2021-10-21T18:00:00+0000',
                'client_id': 'billing_client_id_0',
            }
            return [{'ID': 54321, 'CURRENCY': 'RUB'}]
        assert dict(request.query) == {
            'service_id': '1161',
            'active_ts': '2021-10-21T18:00:00+0000',
            'actual_ts': '2021-10-21T18:00:00+0000',
            'client_id': 'billing_client_id_0',
        }
        return [{'ID': 12121, 'CURRENCY': 'RUB'}]


@pytest.mark.now('2021-10-21T18:00+00:00')
@pytest.mark.parametrize(
    ('req_result_path', 'service_id'),
    [
        ('create_request2_success0.xml', 111),
        ('create_request2_success1.xml', 111),
        ('create_request2_success2.xml', 111),
        ('create_request2_success2.xml', 1161),
    ],
)
async def test_happy_path(
        taxi_parks_replica,
        mockserver,
        happy_path_billing_replication,
        happy_path_fleet_parks,
        load,
        req_result_path,
        service_id,
):
    @mockserver.handler('/ext-yandex-balance/xmlrpctvm')
    def _ext_ya_balance(request):
        assert request.headers['Content-Type'] == 'text/xml'
        req_xml = _format_xml(request.get_data())
        expected_req_cou = _format_xml(load('create_or_update_req.xml'))
        expected_req_cr2 = _format_xml(load('create_request2_req.xml'))
        expected_req_cou1161 = _format_xml(
            load('create_or_update_req1161.xml'),
        )
        expected_req_1161 = _format_xml(load('create_request_1161.xml'))
        print(req_xml)
        assert req_xml in {
            expected_req_cou,
            expected_req_cr2,
            expected_req_1161,
            expected_req_cou1161,
        }
        if req_xml in {expected_req_cou, expected_req_cou1161}:
            response_str = load('create_or_update_success.xml')
        elif req_xml in {expected_req_cr2, expected_req_1161}:
            response_str = load(req_result_path)

        assert isinstance(response_str, str)
        return mockserver.make_response(
            response_str, status=200, content_type='text/xml',
        )

    response = await taxi_parks_replica.post(
        'fleet/parks-replica/v1/balance-invoice-link/retrieve',
        json={'amount': '72.10', 'service_id': service_id},
        headers=dict(HEADERS),
    )
    assert response.status == 200, response.text
    assert response.json() == {
        'link': 'https://my-cool-payment.yx.ru/path/?arg1=bign',
    }


@pytest.mark.now('2021-10-21T18:00+00:00')
@pytest.mark.parametrize('fault_kind', ['create_or_update', 'create_request2'])
async def test_ya_balance_fault(
        taxi_parks_replica,
        mockserver,
        happy_path_billing_replication,
        happy_path_fleet_parks,
        load,
        fault_kind,
):
    @mockserver.handler('/ext-yandex-balance/xmlrpctvm')
    def _ext_ya_balance(request):
        assert request.headers['Content-Type'] == 'text/xml'
        req_xml = _format_xml(request.get_data())
        expected_req_cou = _format_xml(load('create_or_update_req.xml'))
        expected_req_cr2 = _format_xml(load('create_request2_req.xml'))
        assert req_xml in {expected_req_cou, expected_req_cr2}
        if req_xml == expected_req_cou:
            if fault_kind == 'create_or_update':
                response_str = load('balance_fault.xml')
            else:
                response_str = load('create_or_update_success.xml')
        elif req_xml == expected_req_cr2:
            if fault_kind == 'create_request2':
                response_str = load('balance_fault.xml')
            else:
                response_str = load('create_request2_success0.xml')
        assert isinstance(response_str, str)
        return mockserver.make_response(
            response_str, status=200, content_type='text/xml',
        )

    response = await taxi_parks_replica.post(
        'fleet/parks-replica/v1/balance-invoice-link/retrieve',
        json={'amount': '72.10', 'service_id': 111},
        headers=dict(HEADERS),
    )
    assert response.status == 500, response.text


@pytest.mark.now('2021-10-21T18:00+00:00')
async def test_no_clid(taxi_parks_replica, mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _fleet_parks_parks_list(request):
        assert request.json == {'query': {'park': {'ids': ['out_park_id']}}}
        return {
            'parks': [
                {
                    'id': 'out_park_id',
                    'provider_config': {'type': 'production'},
                    'country_id': 'RUS',
                    # Unused fields
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    'login': 'some_login',
                    'city_id': 'some_city_id',
                    'name': 'some_park_name',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'locale': 'ru',
                    'demo_mode': False,
                },
            ],
        }

    response = await taxi_parks_replica.post(
        'fleet/parks-replica/v1/balance-invoice-link/retrieve',
        json={'amount': '72.10', 'service_id': 111},
        headers=dict(HEADERS),
    )
    assert response.status == 409, response.text


@pytest.mark.filldb(parks='empty')
async def test_no_billing_client_id(
        taxi_parks_replica, happy_path_fleet_parks,
):
    response = await taxi_parks_replica.post(
        'fleet/parks-replica/v1/balance-invoice-link/retrieve',
        json={'amount': '72.10', 'service_id': 111},
        headers=dict(HEADERS),
    )
    assert response.status == 409, response.text


@pytest.mark.now('2021-10-21T18:00+00:00')
async def test_no_contract_currency(
        taxi_parks_replica, mockserver, happy_path_fleet_parks, load,
):
    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    def _billing_replication_mock(request):
        assert dict(request.query) == {
            'service_id': '111',
            'active_ts': '2021-10-21T18:00:00+0000',
            'actual_ts': '2021-10-21T18:00:00+0000',
            'client_id': 'billing_client_id_0',
        }
        return [{'ID': 54321}]

    response = await taxi_parks_replica.post(
        'fleet/parks-replica/v1/balance-invoice-link/retrieve',
        json={'amount': '72.10', 'service_id': 111},
        headers=dict(HEADERS),
    )
    assert response.status == 409, response.text
