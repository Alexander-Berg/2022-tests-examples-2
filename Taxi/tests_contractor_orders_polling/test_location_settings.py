# pylint: disable=wrong-import-order,import-error
from fbs.models.etag_cache import PerformerEtag
from fbs.models.etag_cache import Response
import flatbuffers
import pytest

from tests_contractor_orders_polling import utils

ETAG_KEY = 'location_settings_etag'
SETTINGS_KEY = 'location_settings'


def _gen_performer_etag(builder, performer):
    performer_id_offset = builder.CreateString(performer['id'])
    etag_offset = builder.CreateString(performer['etag'])

    PerformerEtag.PerformerEtagStart(builder)
    PerformerEtag.PerformerEtagAddPerformerId(builder, performer_id_offset)
    PerformerEtag.PerformerEtagAddEtag(builder, etag_offset)
    return PerformerEtag.PerformerEtagEnd(builder)


def _make_cache_response(performers, total_chunks=None):
    builder = flatbuffers.Builder(0)

    performers_fbs = [
        _gen_performer_etag(builder, performer) for performer in performers
    ]

    Response.ResponseStartEtagsVector(builder, len(performers))

    for performer_fbs in performers_fbs:
        builder.PrependUOffsetTRelative(performer_fbs)

    etags_offset = builder.EndVector(len(performers))

    Response.ResponseStart(builder)
    Response.ResponseAddEtags(builder, etags_offset)
    if total_chunks:
        Response.ResponseAddTotalChunks(builder, total_chunks)
    response = Response.ResponseEnd(builder)
    builder.Finish(response)
    return bytes(builder.Output())


def _make_headers(uuid):
    return {
        **utils.HEADERS,
        'X-YaTaxi-Park-Id': 'dbid',
        'X-YaTaxi-Driver-Profile-Id': uuid,
    }


async def _check(
        taxi_contractor_orders_polling, uuid, etag, etag_check, settings_check,
):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers=_make_headers(uuid),
        params={ETAG_KEY: etag},
    )
    assert response.status_code == 200

    response_obj = response.json()
    assert etag_check(response_obj.get(ETAG_KEY))
    assert settings_check(response_obj.get(SETTINGS_KEY))


def _is_none(x):
    return x is None


def _is_not_none(x):
    return x is not None


@pytest.mark.experiments3(filename='experiments3.json')
async def test_location_settings(
        taxi_contractor_orders_polling, mockserver, load_json,
):
    @mockserver.json_handler('/coord-control/location_settings')
    def _locaiton_settings(request):
        assert request.headers.get(ETAG_KEY) == 'another_etag'
        return location_settings_response

    @mockserver.handler('coord-control/etag-cache/full')
    async def _etag_cache_full(request):
        return mockserver.make_response(
            _make_cache_response([{'id': 'dbid_uuid_1', 'etag': 'some_etag'}]),
            content_type='application/flatbuffer',
        )

    location_settings_response = load_json('response.json')

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers=_make_headers('uuid_1'),
        params={ETAG_KEY: 'another_etag'},
    )
    assert response.status_code == 200
    assert _locaiton_settings.times_called == 1

    response_obj = response.json()
    assert response_obj.get(ETAG_KEY) == location_settings_response[ETAG_KEY]
    assert (
        response_obj.get(SETTINGS_KEY)
        == location_settings_response[SETTINGS_KEY]
    )

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers=_make_headers('uuid_1'),
        params={ETAG_KEY: 'some_etag'},
    )
    assert response.status_code == 200
    assert _locaiton_settings.times_called == 1
    response_obj = response.json()
    assert response_obj.get(ETAG_KEY) == 'some_etag'
    assert response_obj.get(SETTINGS_KEY) is None

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers=_make_headers('uuid_2'),
        params={ETAG_KEY: 'another_etag'},
    )
    assert response.status_code == 200
    assert _locaiton_settings.times_called == 1
    response_obj = response.json()
    assert response_obj.get(ETAG_KEY) is None
    assert response_obj.get(SETTINGS_KEY) is None


@pytest.mark.experiments3(filename='experiments3.json')
async def test_location_settings_incremental_cache(
        taxi_contractor_orders_polling, mockserver, load_json,
):
    @mockserver.json_handler('/coord-control/location_settings')
    def _locaiton_settings(request):
        return load_json('response.json')

    @mockserver.handler('coord-control/etag-cache/full')
    async def _etag_cache_full(request):
        return mockserver.make_response(
            _make_cache_response([{'id': 'dbid_uuid_1', 'etag': 'some_etag'}]),
            content_type='application/flatbuffer',
        )

    @mockserver.handler('coord-control/etag-cache/incremental')
    async def _etag_cache_incremental(request):
        return mockserver.make_response(
            _make_cache_response(
                [
                    {'id': 'dbid_uuid_1', 'etag': 'another_etag'},
                    {'id': 'dbid_uuid_2', 'etag': 'some_etag'},
                ],
            ),
            content_type='application/flatbuffer',
        )

    await _check(
        taxi_contractor_orders_polling,
        'uuid_1',
        'some_etag',
        _is_not_none,
        _is_none,
    )
    await _check(
        taxi_contractor_orders_polling,
        'uuid_2',
        'some_etag',
        _is_none,
        _is_none,
    )

    await taxi_contractor_orders_polling.invalidate_caches(clean_update=False)

    assert _etag_cache_incremental.times_called == 1

    await _check(
        taxi_contractor_orders_polling,
        'uuid_1',
        'another_etag',
        _is_not_none,
        _is_none,
    )
    await _check(
        taxi_contractor_orders_polling,
        'uuid_2',
        'some_etag',
        _is_not_none,
        _is_none,
    )


@pytest.mark.config(CONTRACTOR_ORDERS_POLLING_CC_CACHE_MAX_TASKS=2)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_location_settings_full_cache(
        taxi_contractor_orders_polling, mockserver, load_json,
):
    @mockserver.json_handler('/coord-control/location_settings')
    def _locaiton_settings(request):
        return load_json('response.json')

    @mockserver.handler('coord-control/etag-cache/full')
    async def _etag_cache_full(request):
        if request.query.get('total_chunks') is None:
            return mockserver.make_response(
                _make_cache_response(
                    [{'id': 'dbid_uuid_1', 'etag': 'some_etag'}], 4,
                ),
                content_type='application/flatbuffer',
            )
        if request.query.get('chunk_number') == '1':
            return mockserver.make_response(
                _make_cache_response(
                    [{'id': 'dbid_uuid_2', 'etag': 'some_etag'}], 4,
                ),
                content_type='application/flatbuffer',
            )
        if request.query.get('chunk_number') == '2':
            return mockserver.make_response(
                _make_cache_response(
                    [{'id': 'dbid_uuid_3', 'etag': 'some_etag'}], 4,
                ),
                content_type='application/flatbuffer',
            )
        if request.query.get('chunk_number') == '3':
            return mockserver.make_response(
                _make_cache_response(
                    [{'id': 'dbid_uuid_4', 'etag': 'some_etag'}], 4,
                ),
                content_type='application/flatbuffer',
            )
        assert False

    await _check(
        taxi_contractor_orders_polling,
        'uuid_1',
        'some_etag',
        _is_not_none,
        _is_none,
    )
    await _check(
        taxi_contractor_orders_polling,
        'uuid_2',
        'some_etag',
        _is_not_none,
        _is_none,
    )
    await _check(
        taxi_contractor_orders_polling,
        'uuid_3',
        'some_etag',
        _is_not_none,
        _is_none,
    )
    await _check(
        taxi_contractor_orders_polling,
        'uuid_4',
        'some_etag',
        _is_not_none,
        _is_none,
    )
    assert _etag_cache_full.times_called == 4


@pytest.mark.experiments3(filename='experiments3.json')
async def test_location_settings_empty_etag(
        taxi_contractor_orders_polling, mockserver,
):
    @mockserver.handler('coord-control/etag-cache/incremental')
    async def _etag_cache_incremental(request):
        return mockserver.make_response(
            _make_cache_response([{'id': 'dbid_uuid_1', 'etag': ''}]),
            content_type='application/flatbuffer',
        )

    await taxi_contractor_orders_polling.invalidate_caches(clean_update=False)

    await _etag_cache_incremental.wait_call()

    await _check(
        taxi_contractor_orders_polling,
        'uuid_1',
        'some_etag',
        _is_none,
        _is_none,
    )
