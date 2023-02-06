import datetime

import bson
import pytest

HEADERS = {'X-Yandex-UID': '4003514353', 'X-Request-Language': 'ru'}
URL = '/4.0/order-search-status/v1/long-search-info'
SOME_ETA_DATETIME = datetime.datetime(
    2021, 6, 4, 13, 34, 0, 0, tzinfo=datetime.timezone.utc,
)
SOME_CREATED_DATETIME = datetime.datetime(
    2021, 6, 4, 13, 25, 0, 0, tzinfo=datetime.timezone.utc,
)


@pytest.mark.experiments3(filename='search_radius_experiments.json')
@pytest.mark.now('2021-06-04T13:30:0Z')
@pytest.mark.config(
    DISPATCH_CLASSES_ORDER=['econom', 'business', 'comfortplus', 'vip'],
)
@pytest.mark.parametrize(
    'has_track,show_max_allowed_class,hide_clases,result_class,hashed_id',
    [
        (False, True, None, 'vip', 'cc8789f02154eb3325c8aa956b7b5ac1'),
        (True, True, None, 'vip', 'ea19e69fbeca113eca3acf471485b5db'),
        (True, False, None, 'business', '405ec7dd92601911c1e7a94c80c82c15'),
        (
            True,
            True,
            ['vip'],
            'comfortplus',
            '51e5b88aeddd61eee7fc01540fbe91ae',
        ),
        (True, False, ['vip'], 'business', '405ec7dd92601911c1e7a94c80c82c15'),
    ],
)
async def test_happy_path(
        mockserver,
        taxi_order_search_status,
        load_binary,
        has_track,
        show_max_allowed_class,
        hide_clases,
        result_class,
        hashed_id,
        taxi_config,
):
    cfg = {'SHOW_MAX_ALLOWED_CLASS': show_max_allowed_class}
    if hide_clases is not None:
        cfg['HIDE_DISPLAY_CLASSES'] = hide_clases
    taxi_config.set_values(cfg)

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_get_fields(request):
        args = request.args
        body = bson.BSON.decode(request.get_data())
        assert args['order_id'] == 'some_order_id'
        assert args['require_latest'] == 'true'
        assert body == {
            'fields': [
                'performer.candidate_index',
                'candidates.db_id',
                'candidates.driver_id',
                'candidates.time',
                'created',
                'order.request.class',
                'order.nz',
            ],
        }

        response_fields = {
            'document': {
                '_id': args['order_id'],
                'created': SOME_CREATED_DATETIME,
                'performer': {'candidate_index': 0},
                'order': {
                    'request': {'class': ['econom', 'business']},
                    'nz': 'spb',
                },
                'candidates': [
                    {
                        'db_id': (
                            '7f74df331eb04ad78bc2ff25ff88a8f2'
                            if has_track
                            else 'dbid_without_track'
                        ),
                        'driver_id': 'clid1_0a4cf9fc1c944aeda69d551e1d20afab',
                        'time': 240,
                    },
                ],
            },
            'revision': {'processing.version': 1, 'order.version': 1},
        }

        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(response_fields),
        )

    @mockserver.handler('/driver-trackstory/v2/shorttracks')
    def _mock_trackstory(request):
        # use flatc if need, e.g.
        # flatc -b --force-defaults schemas/fbs/driver-trackstory/handlers/shorttracks_extended_response.fbs  services/driver-map/testsuite/tests_driver_map/static/test_driver_nearestdrivers/mock_trackstory_fbs.json # noqa: E501
        return mockserver.make_response(
            response=load_binary('mock_trackstory_fbs.bin'),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    response = await taxi_order_search_status.get(
        URL, headers=HEADERS, params={'order_id': 'some_order_id'},
    )
    assert response.status_code == 200

    res = response.json()

    res_positions = res['performer'].pop('positions')
    if has_track:

        assert len(res_positions) == 15
        assert res_positions[0:2] == [
            {
                'direction': 0.0,
                'lat': 55.82018,
                'lon': 37.592092,
                'speed': 0.0,
                'timestamp': '2019-06-26T12:41:29+0000',
            },
            {
                'direction': 0.0,
                'lat': 55.820564,
                'lon': 37.591501,
                'speed': 0.0,
                'timestamp': '2019-06-26T12:41:34+0000',
            },
        ]
    else:
        assert res_positions == []

    assert res == {
        'eta': 240,
        'hints': {'search_status': 'Предлагаем заказ кандидату'},
        'performer': {'display_tariff': result_class, 'id': hashed_id},
        'radius': 1000,
    }


@pytest.mark.now('2021-06-04T13:30:0Z')
@pytest.mark.config(
    DISPATCH_CLASSES_ORDER=['econom', 'business', 'comfortplus', 'vip'],
    NEAREST_DRIVERS_REPLACE_DISPLAY_CLASSES=['econom'],
)
@pytest.mark.parametrize(
    'order_classes,result_class,hashed_id',
    [
        (['econom'], 'econom', '07f17e215c3805aea09d3d399359e4c6'),
        (
            ['econom', 'business'],
            'business',
            '405ec7dd92601911c1e7a94c80c82c15',
        ),
    ],
)
async def test_replace_display_class(
        mockserver,
        taxi_order_search_status,
        load_binary,
        order_classes,
        result_class,
        hashed_id,
):
    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_get_fields(request):
        args = request.args
        body = bson.BSON.decode(request.get_data())
        assert args['order_id'] == 'some_order_id'
        assert args['require_latest'] == 'true'
        assert body == {
            'fields': [
                'performer.candidate_index',
                'candidates.db_id',
                'candidates.driver_id',
                'candidates.time',
                'created',
                'order.request.class',
                'order.nz',
            ],
        }

        response_fields = {
            'document': {
                '_id': args['order_id'],
                'created': SOME_CREATED_DATETIME,
                'performer': {'candidate_index': 0},
                'order': {'request': {'class': order_classes}, 'nz': 'spb'},
                'candidates': [
                    {
                        'db_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
                        'driver_id': 'clid1_0a4cf9fc1c944aeda69d551e1d20afab',
                        'time': 240,
                    },
                ],
            },
            'revision': {'processing.version': 1, 'order.version': 1},
        }

        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(response_fields),
        )

    @mockserver.handler('/driver-trackstory/v2/shorttracks')
    def _mock_trackstory(request):
        # use flatc if need, e.g.
        # flatc -b --force-defaults schemas/fbs/driver-trackstory/handlers/shorttracks_extended_response.fbs  services/driver-map/testsuite/tests_driver_map/static/test_driver_nearestdrivers/mock_trackstory_fbs.json # noqa: E501
        return mockserver.make_response(
            response=load_binary('mock_trackstory_fbs.bin'),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    response = await taxi_order_search_status.get(
        URL, headers=HEADERS, params={'order_id': 'some_order_id'},
    )
    assert response.status_code == 200

    res = response.json()
    del res['performer']['positions']
    assert res == {
        'eta': 240,
        'hints': {'search_status': 'Предлагаем заказ кандидату'},
        'performer': {'display_tariff': result_class, 'id': hashed_id},
        'radius': 1500,
    }


@pytest.mark.parametrize('has_previous_candidate', [True, False])
@pytest.mark.now('2021-06-04T13:30:0Z')
async def test_no_candidate(
        mockserver, taxi_order_search_status, has_previous_candidate,
):
    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_get_fields(request):
        args = request.args

        response_fields = {
            'document': {
                '_id': args['order_id'],
                'created': SOME_CREATED_DATETIME,
                'performer': {'candidate_index': None},
                'order': {'nz': 'spb'},
                'candidates': (
                    [{'time': 240}] if has_previous_candidate else []
                ),
            },
            'revision': {'processing.version': 1, 'order.version': 1},
        }

        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(response_fields),
        )

    response = await taxi_order_search_status.get(
        URL, headers=HEADERS, params={'order_id': 'some_order_id'},
    )
    assert response.status_code == 200

    etalon = {'hints': {'search_status': 'Ищем машины'}, 'radius': 1500}
    if has_previous_candidate:
        etalon['eta'] = 240

    assert response.json() == etalon


async def test_order_core_404(mockserver, taxi_order_search_status):
    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_get_fields(request):
        return mockserver.make_response(
            status=404,
            json={
                'code': 'no_such_order',
                'message': 'No such order in order_core_response.json',
            },
        )

    response = await taxi_order_search_status.get(
        URL, headers=HEADERS, params={'order_id': 'some_order_id'},
    )
    assert response.status_code == 404


async def test_order_core_500(mockserver, taxi_order_search_status):
    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_get_fields(request):
        return mockserver.make_response(status=500)

    response = await taxi_order_search_status.get(
        URL, headers=HEADERS, params={'order_id': 'some_order_id'},
    )
    assert response.status_code == 500
