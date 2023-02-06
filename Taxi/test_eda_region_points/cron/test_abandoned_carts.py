import datetime
import math

import pytest

from taxi.util import dates as dates_utils

from eda_region_points.generated.cron import run_cron

PLACES_RETRIEVE_BY_IDS_HANDLER = (
    '/eats-catalog-storage/internal/eats-catalog-storage/'
    'v1/places/retrieve-by-ids'
)

DEFAULT_TIME_LIMIT = 14 * 24 * 60 * 60  # 14 дней
EVENT_NEW_BULK_HANDLER = '/eventus-proxy/v1/topic/event/new/bulk'
PLACES = [1, 2]
PLACE_BY_BUSINESS = {'shop': PLACES[1], 'restaurant': PLACES[0]}
PLACE_ITEMS_COUNT = [(PLACES[0], 2), (PLACES[1], 3)]


def _sort_events(events):
    events.sort(key=lambda event: event['payload']['inactivity_at'])

    for event in events:
        event['payload']['cart_items'].sort(key=lambda item: item['id'])
        event['payload']['place']['categories'].sort(
            key=lambda item: item['id'],
        )


def _offset_to_datetime(offset: int) -> datetime.datetime:
    return datetime.datetime.now() - datetime.timedelta(seconds=offset)


def _get_expected_request(
        load_json,
        time_offset,
        time_limit,
        brands=None,
        business_types=None,
        min_total=None,
        min_items_count=None,
):
    interval_begin = _offset_to_datetime(time_offset)
    interval_end = _offset_to_datetime(time_limit)
    result = load_json('expected_eventus_proxy_request.json')

    places = set(PLACES)

    if business_types is not None:
        places.intersection_update(
            {PLACE_BY_BUSINESS[item] for item in business_types},
        )

    if min_items_count is not None:
        places.intersection_update(
            {
                item[0]
                for item in PLACE_ITEMS_COUNT
                if item[1] >= min_items_count
            },
        )

    def condition(event):
        payload = event['payload']
        inactivity_at = dates_utils.parse_timestring(payload['inactivity_at'])
        return (
            inactivity_at <= interval_begin
            and (interval_end is None or inactivity_at >= interval_end)
            and (brands is None or payload['place']['id'] in brands)
            and payload['place']['id'] in places
            and (min_total is None or payload['total'] >= min_total)
        )

    result['events'] = [
        event for event in result['events'] if condition(event)
    ]
    _sort_events(result['events'])

    return result


@pytest.mark.parametrize('business_types', [None, ['shop']])
@pytest.mark.parametrize('time_offset', [0, 90 * 60])
@pytest.mark.parametrize('time_limit', [DEFAULT_TIME_LIMIT, 90 * 60])
@pytest.mark.parametrize('brands', [None, [1]])
@pytest.mark.parametrize('min_total', [None, 200, 201])
@pytest.mark.parametrize('min_items_count', [None, 2, 3])
@pytest.mark.now('2022-01-01T05:00:00Z')
async def test_abandoned_carts(
        mockserver,
        taxi_config,
        load_json,
        time_offset,
        time_limit,
        brands,
        business_types,
        min_total,
        min_items_count,
):
    """
    Тест проверяет работу фильтрации для cron-задачи выгрузки брошенных корзин
    """
    taxi_config.set(
        EATS_ABANDONED_CART_SETTINGS={
            'time_offset': time_offset,
            'time_limit': time_limit,
            'brand_ids': brands,
            'business_types': business_types,
            'min_total': min_total,
            'min_items_count': min_items_count,
            'eventus_proxy_batch_size': 500,
            'catalog_storage_batch_size': 500,
        },
    )

    @mockserver.json_handler(PLACES_RETRIEVE_BY_IDS_HANDLER)
    def _mock_eats_catalog_storage(request):
        return load_json('eats_catalog_response.json')

    expected_request = _get_expected_request(
        load_json,
        time_offset,
        time_limit,
        brands,
        business_types,
        min_total,
        min_items_count,
    )

    @mockserver.json_handler(EVENT_NEW_BULK_HANDLER)
    def _v1_topic_event_new_bulk(request):
        for event in request.json['events']:
            del event['idempotency_token']

        _sort_events(request.json['events'])

        assert request.json == expected_request
        return {'key': 'value'}

    await run_cron.main(
        [f'eda_region_points.crontasks.abandoned_carts', '-t', '0'],
    )

    assert _mock_eats_catalog_storage.times_called == (
        1 if time_offset < time_limit else 0
    )

    if expected_request['events']:
        assert _v1_topic_event_new_bulk.times_called == 1


@pytest.mark.parametrize('eventus_proxy_batch_size', [100, 1])
@pytest.mark.parametrize('catalog_storage_batch_size', [100, 1])
@pytest.mark.now('2022-01-01T05:00:00Z')
async def test_abandoned_carts_batches(
        mockserver,
        taxi_config,
        load_json,
        eventus_proxy_batch_size,
        catalog_storage_batch_size,
):
    """
    Тест проверяет работу бэтчинга запросов
    """
    taxi_config.set(
        EATS_ABANDONED_CART_SETTINGS={
            'time_offset': 0,
            'time_limit': DEFAULT_TIME_LIMIT,
            'eventus_proxy_batch_size': eventus_proxy_batch_size,
            'catalog_storage_batch_size': catalog_storage_batch_size,
        },
    )

    @mockserver.json_handler(PLACES_RETRIEVE_BY_IDS_HANDLER)
    def _mock_eats_catalog_storage(request):
        return load_json('eats_catalog_response.json')

    events = []

    @mockserver.json_handler(EVENT_NEW_BULK_HANDLER)
    def _v1_topic_event_new_bulk(request):
        for event in request.json['events']:
            del event['idempotency_token']

        events.extend(request.json['events'])
        return {'key': 'value'}

    await run_cron.main(
        [f'eda_region_points.crontasks.abandoned_carts', '-t', '0'],
    )

    expected_events = _get_expected_request(load_json, 0, DEFAULT_TIME_LIMIT)[
        'events'
    ]
    _sort_events(events)

    assert events == expected_events

    assert _mock_eats_catalog_storage.times_called == math.ceil(
        len(events) / catalog_storage_batch_size,
    )
    assert _v1_topic_event_new_bulk.times_called == math.ceil(
        len(events) / eventus_proxy_batch_size,
    )
