# pylint: disable=import-error,too-many-lines,import-only-modules
import datetime

from geobus_tools import geobus  # noqa: F401 C5521
import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary


DEFAULT_APPLICATION = 'app_name=iphone,app_ver1=3,app_ver2=2,app_ver3=1'

AUTH_HEADERS = {
    'X-YaTaxi-UserId': '12345678901234567890123456789012',
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-YaTaxi-Bound-Uids': '834149473,834149474',
    'X-AppMetrica-UUID': 'UUID',
    'X-Request-Application': DEFAULT_APPLICATION,
    'X-Request-Language': 'ru',
    'User-Agent': 'user-agent',
    'X-Remote-IP': '10.10.10.10',
}

ROUTER = {
    '37.660000,55.720000': (120, 1000),
    '37.660000,55.740000': (240, 2000),
    '37.660000,55.791000': (600, 2500),
    '37.100000,55.100000': (800, 3000),
    '37.300000,55.300000': (1000, 3500),
    '37.660000,55.730000': (1200, 4000),
    '37.660000,56.760000': (1400, 4500),
    '37.660000,56.750000': (1600, 5000),
    '37.660000,55.770000': (1800, 5500),
    '37.660000,55.710000': (2000, 6000),
}

NOW = datetime.datetime(2001, 9, 9, 1, 46, 39)


def _proto_driving_summary(src):
    time, distance = ROUTER[src]
    response = ProtoDrivingSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.time_with_traffic.value = time
    item.weight.time_with_traffic.text = ''
    item.weight.distance.value = distance
    item.weight.distance.text = ''
    item.flags.blocked = False
    return response.SerializeToString()


@pytest.mark.parametrize(
    'order_status,response_file',
    [
        ('transporting', 'only_search_resp.json'),
        ('complete', 'empty_resp.json'),
    ],
)
@pytest.mark.translations(
    client_messages={
        'combo.companion.body.text.search': {'ru': 'Тариф `С попутчиком`'},
        'combo.companion.title.search': {'ru': 'Поиск попутчика'},
        'combo.companion.subtitle.search': {
            'ru': 'По дороге к вам присоединится попутчик',
        },
        'combo.companion.arrow_button.text': {'ru': 'Подробнее'},
    },
)
@pytest.mark.experiments3(filename='exp3_combo_companions.json')
async def test_companions_not_found(
        taxi_combo_contractors, load_json, order_status, response_file,
):
    resp = await taxi_combo_contractors.post(
        'v1/companions/fetch-info',
        headers=AUTH_HEADERS,
        json={
            'dbid_uuid': 'dbid_uuid7',
            'order_id': 'requested_order',
            'order_status': order_status,
        },
    )

    assert resp.status_code == 200
    assert resp.json() == load_json(response_file)


@pytest.mark.translations(
    client_messages={
        'combo.companion.subtitle.status_waiting_for_the_car': {
            'ru': 'Ожидает подачи машины',
        },
        'combo.companion.subtitle.status_joining_after': {
            'ru': 'Присоединится через ~%(eta)s',
        },
        'combo.companion.title.not_found': {'ru': 'Попутчик не нашелся'},
        'combo.companion.subtitle.not_found': {'ru': 'Но цена не изменится'},
        'combo.companion.arrow_button.text': {'ru': 'Подробнее'},
        'combo.companion.body.text.search': {'ru': 'Тариф `С попутчиком`'},
        'combo.companion.title.search': {'ru': 'Поиск попутчика'},
        'combo.companion.subtitle.search': {
            'ru': 'По дороге к вам присоединится попутчик',
        },
        'combo.companion.title.number_0': {'ru': 'Попутчик'},
        'combo.companion.title.number_1': {'ru': 'Первый попутчик'},
        'combo.companion.title.number_2': {'ru': 'Второй попутчик'},
        'combo.companion.subtitle.status_already_in_the_car': {
            'ru': 'Уже в машине',
        },
        'combo.companion.subtitle.status_finishes_first': {
            'ru': 'Выйдет через %(eta)s',
        },
        'combo.companion.subtitle.status_finishes_last': {
            'ru': 'Выйдет после вас',
        },
        'combo.companion.subtitle.status_planned': {
            'ru': 'Присоединится через %(eta)s',
        },
        'combo.companion.subtitle.status_finished': {'ru': 'Уже вышел'},
        'shortcuts.route_eta.round.hours_minutes': {
            'ru': '%(hours).0f ч %(minutes).0f мин',
        },
        'shortcuts.route_eta.round.hours': {'ru': '%(value).0f ч'},
        'shortcuts.route_eta.round.tens_minutes': {'ru': '%(value).0f мин'},
    },
)
@pytest.mark.parametrize(
    'dbid_uuid,order_status,testcase,requester_eta,expected_router_request',
    [
        (
            'dbid_uuid0',
            'transporting',
            'already_in_the_car',
            2000,
            '37.660000,55.710000~37.200000,55.200000~37.300000,55.300000',
        ),
        (
            'dbid_uuid1',
            'driving',
            'finishes_first_driving',
            120,
            '37.660000,55.720000~37.000000,55.000000~37.100000,55.100000',
        ),
        (
            'dbid_uuid1',
            'transporting',
            'finishes_first',
            120,
            '37.660000,55.720000~37.200000,55.200000~37.300000,55.300000',
        ),
        (
            'dbid_uuid2',
            'transporting',
            'finishes_last',
            1200,
            '37.660000,55.730000~37.300000,55.300000',
        ),
        (
            'dbid_uuid3',
            'transporting',
            'join_and_finish_first',
            240,
            '37.660000,55.740000~37.000000,55.000000~37.200000,55.200000~37.300000,55.300000',
        ),
        (
            'dbid_uuid4',
            'transporting',
            'old_exists_and_searching',
            1600,
            '37.660000,56.750000~37.300000,55.300000',
        ),
        ('dbid_uuid4', 'complete', 'old_exists', None, None),
        (
            'dbid_uuid5',
            'transporting',
            'only_search',
            1400,
            '37.660000,56.760000~37.200000,55.200000',
        ),
        ('dbid_uuid5', 'complete', 'only_not_found', None, None),
        ('', 'transporting', 'only_search', None, None),
        ('', 'complete', 'empty', None, None),
        (
            'dbid_uuid6',
            'transporting',
            'two_finished_and_search',
            1800,
            '37.660000,55.770000~37.300000,55.300000',
        ),
        ('dbid_uuid6', 'complete', 'two_finished', None, None),
        ('dbid_uuid7', 'transporting', 'waiting_for_the_car', None, None),
        ('dbid_uuid8', 'transporting', 'already_in_the_car', None, None),
        (
            'dbid_uuid9',
            'driving',
            'joining_after',
            600,
            '37.660000,55.791000~37.100000,55.100000',
        ),
        (
            'dbid_uuid9',
            'transporting',
            'joining_after',
            600,
            '37.660000,55.791000~37.000000,55.000000~37.200000,55.200000~37.300000,55.300000',
        ),
        ('dbid_uuid10', 'transporting', 'waiting_for_the_car', None, None),
        ('dbid_uuid11', 'transporting', 'chain', None, None),
        ('dbid_uuid12', 'transporting', 'stuck_in_transporting', None, None),
    ],
)
@pytest.mark.experiments3(filename='exp3_combo_companions.json')
@pytest.mark.now(f'{NOW:%Y-%m-%d %H:%M:%S%z}')
async def test_companions_cases(
        taxi_combo_contractors,
        mockserver,
        load_json,
        pgsql,
        load,
        redis_store,
        testpoint,
        dbid_uuid,
        order_status,
        testcase,
        requester_eta,
        expected_router_request,
):
    router_requests = []

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_pedestrian_router(request):
        src = request.args['rll'].split('~')[0]
        router_requests.append(request.args['rll'])
        return mockserver.make_response(
            response=_proto_driving_summary(src),
            status=200,
            content_type='application/x-protobuf',
        )

    @testpoint('geobus-positions_payload_processed')
    def geobus_payload_processed(data):
        pass

    await taxi_combo_contractors.enable_testpoints()

    positions = load_json('positions.json')
    redis_store.publish(
        'channel:yaga:edge_positions',
        geobus.serialize_edge_positions_v2(positions, datetime.datetime.now()),
    )

    await geobus_payload_processed.wait_call()

    cursor = pgsql['combo_contractors'].cursor()
    cursor.execute(load(f'{testcase}.sql'))

    resp = await taxi_combo_contractors.post(
        'v1/companions/fetch-info',
        headers=AUTH_HEADERS,
        json={
            'dbid_uuid': dbid_uuid,
            'order_id': 'requested_order',
            'order_status': order_status,
        },
    )
    resp_json = resp.json()
    resp_requester_eta = resp_json.pop('requester_eta', None)

    assert resp.status_code == 200
    assert resp_json == load_json(f'{testcase}_resp.json')
    assert resp_requester_eta == requester_eta
    if expected_router_request is not None:
        assert expected_router_request in router_requests
