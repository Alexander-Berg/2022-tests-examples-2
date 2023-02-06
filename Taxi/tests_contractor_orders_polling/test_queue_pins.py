import pytest

from tests_contractor_orders_polling import utils

KEY = 'queue_pins'
ETAG = 'queue_pins_etag'
ICON_ID = 'airport'


def _make_headers(uuid):
    return {
        **utils.HEADERS,
        'X-YaTaxi-Park-Id': 'dbid',
        'X-YaTaxi-Driver-Profile-Id': uuid,
    }


@pytest.mark.config(
    CONTRACTOR_ORDERS_POLLING_DAV_CACHE_UPDATE_ENABLED=True,
    CONTRACTOR_ORDERS_POLLING_DAV_SUPPLY_ENABLED=False,
)
async def test_queue_infos_supply_off(
        taxi_contractor_orders_polling, mockserver, taxi_config,
):
    @mockserver.json_handler('/dispatch-airport-view/v1/etag-cache/full')
    def _full(request):
        return {
            'current_chunk': 0,
            'total_chunks': 1,
            'etags': [{'dbid_uuid': 'dbid_uuid0', 'etag': 1000}],
        }

    @mockserver.json_handler('/dispatch-airport-view/v1/preview')
    def _preview(request):
        return {'previews': [], 'etag': 1000}

    # taximeter request (without etag/with empty etag/with etag)
    for test_etag in (None, '', 900):
        params = {}
        if test_etag is not None:
            params[ETAG] = test_etag
        response = await taxi_contractor_orders_polling.get(
            utils.HANDLER_URL, headers=_make_headers('uuid0'), params=params,
        )
        assert response.status_code == 200
        assert _preview.times_called == 0
        r_json = response.json()
        assert ETAG not in r_json
        assert KEY not in r_json


@pytest.mark.config(
    CONTRACTOR_ORDERS_POLLING_DAV_CACHE_UPDATE_ENABLED=True,
    CONTRACTOR_ORDERS_POLLING_DAV_SUPPLY_ENABLED=True,
)
async def test_queue_infos_supply_on(
        taxi_contractor_orders_polling, mockserver, taxi_config,
):
    @mockserver.json_handler('/dispatch-airport-view/v1/etag-cache/full')
    def _full(request):
        return {
            'current_chunk': 0,
            'total_chunks': 1,
            'etags': [
                {'dbid_uuid': 'dbid_uuid0', 'etag': 1000},
                {'dbid_uuid': 'dbid_uuid1', 'etag': 1001},
            ],
        }

    @mockserver.json_handler('/dispatch-airport-view/v1/preview')
    def _preview(request):
        etag = 1000 if request.query.get('dbid_uuid') == 'dbid_uuid0' else 1001
        return {
            'previews': [
                {
                    'airport_id': 'ekb',
                    'pin_point': [1.0, 2.0],
                    'is_allowed': True,
                    'icon_id': ICON_ID,
                },
                {
                    'airport_id': 'svo',
                    'pin_point': [2.0, 3.0],
                    'is_allowed': False,
                    'icon_id': ICON_ID,
                },
            ],
            'etag': etag,
        }

    # taximeter request (without etag/with empty etag/with etag) + no dav etag
    for test_etag in (None, '', 900):
        params = {}
        if test_etag is not None:
            params[ETAG] = test_etag
        response = await taxi_contractor_orders_polling.get(
            utils.HANDLER_URL, headers=_make_headers('unknown'), params=params,
        )
        assert response.status_code == 200
        assert _preview.times_called == 0
        r_json = response.json()
        assert ETAG not in r_json
        assert KEY not in r_json

    # taximeter request (without etag/with empty etag/with etag) + dav etag
    for test_etag in (None, '', 900):
        params = {}
        if test_etag is not None:
            params[ETAG] = test_etag
        response = await taxi_contractor_orders_polling.get(
            utils.HANDLER_URL, headers=_make_headers('uuid0'), params=params,
        )
        assert response.status_code == 200
        r_json = response.json()
        if test_etag is not None:
            assert r_json[ETAG] == 1000
            assert r_json[KEY] == [
                {
                    'airport_id': 'ekb',
                    'pin_point': [1.0, 2.0],
                    'is_allowed': True,
                    'icon_id': ICON_ID,
                },
                {
                    'airport_id': 'svo',
                    'pin_point': [2.0, 3.0],
                    'is_allowed': False,
                    'icon_id': ICON_ID,
                },
            ]
        else:
            assert ETAG not in r_json
            assert KEY not in r_json

    assert _preview.times_called == 2

    # taximeter request with etag >= dav etag
    for more_or_eq_etag in (1000, 1010):
        response = await taxi_contractor_orders_polling.get(
            utils.HANDLER_URL,
            headers=_make_headers('uuid0'),
            params={ETAG: more_or_eq_etag},
        )
        assert response.status_code == 200
        r_json = response.json()
        assert r_json[ETAG] == more_or_eq_etag
        assert KEY not in r_json
    assert _preview.times_called == 2


@pytest.mark.config(
    CONTRACTOR_ORDERS_POLLING_DAV_CACHE_UPDATE_ENABLED=True,
    CONTRACTOR_ORDERS_POLLING_DAV_SUPPLY_ENABLED=True,
)
@pytest.mark.parametrize('error_type', ('timeout', 'not_found'))
async def test_queue_infos_supply_on_driver_not_found(
        taxi_contractor_orders_polling, mockserver, taxi_config, error_type,
):
    @mockserver.json_handler('/dispatch-airport-view/v1/etag-cache/full')
    def _full(request):
        return {
            'current_chunk': 0,
            'total_chunks': 1,
            'etags': [{'dbid_uuid': 'dbid_uuid0', 'etag': 1000}],
        }

    @mockserver.json_handler('/dispatch-airport-view/v1/preview')
    def _preview(request):
        if error_type == 'not_found':
            return mockserver.make_response(
                json={
                    'code': 'no_driver_pins',
                    'message': 'Driver not_found_driver_id without pins',
                },
                status=404,
            )

        raise mockserver.TimeoutError()

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL, headers=_make_headers('uuid0'), params={ETAG: 900},
    )
    assert response.status_code == 200
    r_json = response.json()
    assert _preview.times_called == 1

    if error_type == 'not_found':
        assert ETAG not in r_json
    else:
        assert r_json[ETAG] == 900

    assert KEY not in r_json
