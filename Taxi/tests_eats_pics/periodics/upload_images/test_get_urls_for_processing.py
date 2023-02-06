# pylint: disable=too-many-lines
import datetime as dt
import hashlib
import pathlib
import re

import pytest

Path = pathlib.Path

PERIODIC_NAME = 'eats-pics_images-update-periodic'
# this path *is* whitelisted in config.json
MOCK_IMAGES_PATH = '/images/'


@pytest.mark.parametrize(
    'status, timestamp_field_name',
    [
        pytest.param('new', 'created_at', id='new'),
        pytest.param('error', 'retry_at', id='error'),
        pytest.param('done', 'last_checked_at', id='refreshable'),
    ],
)
async def test_processing_status(
        pg_cursor,
        taxi_eats_pics,
        taxi_config,
        testpoint,
        mockserver,
        mock_ext_image,
        status,
        timestamp_field_name,
):
    processing_timeout_threshold = dt.timedelta(seconds=10)

    update_config = taxi_config.get('EATS_PICS_UPDATE_SETTINGS')
    update_config.update(
        {
            'image_processing_timeout_in_ms': (
                processing_timeout_threshold / dt.timedelta(milliseconds=1)
            ),
        },
    )
    taxi_config.set(EATS_PICS_UPDATE_SETTINGS=update_config)

    refresh_image_period = update_config[
        'refresh_image_period_in_hours'
    ] * dt.timedelta(hours=1)

    mock_image_path = mock_ext_image.get_prefix()

    url_not_started = 'url1'
    url_in_progress = 'url2'
    url_timed_out = 'url3'

    urls = [url_not_started, url_in_progress, url_timed_out]

    time_in_past = dt.datetime.now() - refresh_image_period * 2

    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_IMAGES_PATH}/{i}'),
            status=status,
            **{timestamp_field_name: time_in_past},
        )
        for i in urls
    ]

    for i in image_data:
        base_url = i['base_url']
        if base_url == url_not_started:
            i['is_being_processed'] = 'false'
        elif base_url == url_in_progress:
            i['is_being_processed'] = 'true'
            i['processing_started_at'] = (
                dt.datetime.now() - processing_timeout_threshold / 2
            )
        elif base_url == url_timed_out:
            i['is_being_processed'] = 'true'
            i['processing_started_at'] = (
                dt.datetime.now() - processing_timeout_threshold * 2
            )

    expected_urls = [url_not_started, url_timed_out]

    @testpoint('eats-pics-processing_upload_images::urls-to-process')
    def task_urls_to_process(urls):
        assert set(urls) == {
            mockserver.url(f'{mock_image_path}/{i}') for i in expected_urls
        }

    id_to_url = _sql_add_source_images(pg_cursor, image_data)

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_urls_to_process.has_calls

    image_statuses = _sql_get_source_image_status(
        pg_cursor, list(id_to_url.keys()),
    )
    _add_base_url_to_image_statuses(image_statuses, id_to_url)
    _verify_source_image_status(
        image_statuses, expected_urls, [url_in_progress],
    )


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=False)


async def test_refreshable_no_subscription(
        pg_cursor,
        taxi_eats_pics,
        taxi_config,
        testpoint,
        mockserver,
        mock_ext_image,
):
    update_config = taxi_config.get('EATS_PICS_UPDATE_SETTINGS')
    refresh_image_period = update_config[
        'refresh_image_period_in_hours'
    ] * dt.timedelta(hours=1)

    mock_image_path = mock_ext_image.get_prefix()

    url_with_subscription = 'url1'
    url_without_subscription = 'url2'

    urls = [url_with_subscription, url_without_subscription]

    time_in_past = dt.datetime.now() - refresh_image_period * 2

    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_IMAGES_PATH}/{i}'),
            status='done',
            last_checked_at=time_in_past,
        )
        for i in urls
    ]

    for i in image_data:
        base_url = i['base_url']
        if base_url == url_with_subscription:
            i['has_active_subscriptions'] = 'true'
        elif base_url == url_without_subscription:
            i['has_active_subscriptions'] = 'false'

    expected_urls = [url_with_subscription]

    @testpoint('eats-pics-processing_upload_images::urls-to-process')
    def task_urls_to_process(urls):
        assert set(urls) == {
            mockserver.url(f'{mock_image_path}/{i}') for i in expected_urls
        }

    _sql_add_source_images(pg_cursor, image_data)

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_urls_to_process.has_calls


async def test_refreshing_disabled_urls(
        pg_cursor,
        taxi_eats_pics,
        taxi_config,
        testpoint,
        mockserver,
        mock_ext_image,
):
    update_config = taxi_config.get('EATS_PICS_UPDATE_SETTINGS')
    refresh_image_period = update_config[
        'refresh_image_period_in_hours'
    ] * dt.timedelta(hours=1)

    mock_image_path = mock_ext_image.get_prefix()

    url_check_enabled = 'url1'
    url_check_disabled = 'url2'

    urls = [url_check_enabled, url_check_disabled]

    time_in_past = dt.datetime.now() - refresh_image_period * 2

    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_IMAGES_PATH}/{i}'),
            status='done',
            last_checked_at=time_in_past,
        )
        for i in urls
    ]

    for i in image_data:
        base_url = i['base_url']
        if base_url == url_check_enabled:
            i['is_check_needed'] = 'true'
        elif base_url == url_check_disabled:
            i['is_check_needed'] = 'false'

    expected_urls = [url_check_enabled]

    @testpoint('eats-pics-processing_upload_images::urls-to-process')
    def task_urls_to_process(urls):
        assert set(urls) == {
            mockserver.url(f'{mock_image_path}/{i}') for i in expected_urls
        }

    _sql_add_source_images(pg_cursor, image_data)

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_urls_to_process.has_calls


async def test_under_max_batch_limit(
        pg_cursor,
        taxi_eats_pics,
        taxi_config,
        testpoint,
        mockserver,
        mock_ext_image,
):
    refresh_image_period = dt.timedelta(hours=2)

    update_config = taxi_config.get('EATS_PICS_UPDATE_SETTINGS')
    update_config.update(
        {
            'images_to_check_batch_size': 10000,
            # This is needed to trigger image refresh
            'refresh_image_period_in_hours': (
                refresh_image_period / dt.timedelta(hours=1)
            ),
        },
    )
    taxi_config.set(EATS_PICS_UPDATE_SETTINGS=update_config)

    mock_image_path = mock_ext_image.get_prefix()

    time_in_past = dt.datetime.now() - dt.timedelta(seconds=30)
    time_in_past_refreshable = dt.datetime.now() - refresh_image_period * 2
    time_in_past_not_refresh_yet = dt.datetime.now() - refresh_image_period / 2
    time_in_future = dt.datetime.now() + dt.timedelta(minutes=30)

    images_in_db = [
        {'url': 'complete', 'status': 'done'},
        {
            'url': 'refreshable_1',
            'status': 'done',
            'last_checked_at': time_in_past_refreshable,
        },
        {
            'url': 'refreshable_2',
            'status': 'done',
            'last_checked_at': time_in_past_refreshable,
        },
        {
            'url': 'not_refreshable_yet',
            'status': 'done',
            'last_checked_at': time_in_past_not_refresh_yet,
        },
        {'url': 'new_1', 'status': 'new'},
        {'url': 'new_2', 'status': 'new'},
        {'url': 'nonretryable_error', 'status': 'error'},
        {
            'url': 'retryable_error_1',
            'status': 'error',
            'retry_at': time_in_past,
        },
        {
            'url': 'retryable_error_2',
            'status': 'error',
            'retry_at': time_in_past,
        },
        {
            'url': 'retryable_error_in_future',
            'status': 'error',
            'retry_at': time_in_future,
        },
    ]
    expected_urls = [
        'refreshable_1',
        'refreshable_2',
        'new_1',
        'new_2',
        'retryable_error_1',
        'retryable_error_2',
    ]

    image_data = [
        _generate_image_data(
            base_url=i['url'],
            url=mockserver.url(f'{mock_image_path}/{i["url"]}'),
            status=i['status'],
            retry_at=i['retry_at'] if 'retry_at' in i else None,
            last_checked_at=i['last_checked_at']
            if 'last_checked_at' in i
            else None,
        )
        for i in images_in_db
    ]

    def verify_urls(urls):
        assert set(urls) == {
            mockserver.url(f'{mock_image_path}/{i}') for i in expected_urls
        }

    @testpoint('eats-pics-processing_upload_images::urls-to-process')
    def task_urls_to_process(urls):
        verify_urls(urls)

    id_to_url = _sql_add_source_images(pg_cursor, image_data)

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_urls_to_process.has_calls

    image_statuses = _sql_get_source_image_status(
        pg_cursor, list(id_to_url.keys()),
    )
    _add_base_url_to_image_statuses(image_statuses, id_to_url)
    _verify_source_image_status(image_statuses, list(id_to_url.values()), [])


@pytest.mark.parametrize(
    'max_batch_limit, images_in_db, expected_urls',
    [
        pytest.param(
            2,
            [
                {
                    'url': 'new_1',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=3),
                },
                {
                    'url': 'new_2',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=2),
                },
                {
                    'url': 'new_3',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=1),
                },
            ],
            ['new_1', 'new_2'],
            id='new only',
        ),
        pytest.param(
            2,
            [
                {
                    'url': 'error_1',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=3),
                },
                {
                    'url': 'error_2',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=2),
                },
                {
                    'url': 'error_3',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=1),
                },
            ],
            ['error_1', 'error_2'],
            id='error only',
        ),
        pytest.param(
            2,
            [
                {
                    'url': 'refreshable_1',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=3,
                    ),
                },
                {
                    'url': 'refreshable_2',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=2,
                    ),
                },
                {
                    'url': 'refreshable_3',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=1,
                    ),
                },
            ],
            ['refreshable_1', 'refreshable_2'],
            id='refreshable only',
        ),
        pytest.param(
            3,
            [
                {
                    'url': 'new_1',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=3),
                },
                {
                    'url': 'new_2',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=2),
                },
                {
                    'url': 'error_1',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=3),
                },
                {
                    'url': 'error_2',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=2),
                },
            ],
            ['new_1', 'new_2', 'error_1'],
            id='new and error',
        ),
        pytest.param(
            3,
            [
                {
                    'url': 'error_1',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=3),
                },
                {
                    'url': 'error_2',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=2),
                },
                {
                    'url': 'refreshable_1',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=3,
                    ),
                },
                {
                    'url': 'refreshable_2',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=2,
                    ),
                },
            ],
            ['error_1', 'error_2', 'refreshable_1'],
            id='error and refreshable',
        ),
    ],
)
async def test_over_max_batch_limit(
        pg_cursor,
        taxi_eats_pics,
        taxi_config,
        testpoint,
        mockserver,
        mock_ext_image,
        max_batch_limit,
        images_in_db,
        expected_urls,
):
    update_config = taxi_config.get('EATS_PICS_UPDATE_SETTINGS')
    update_config.update({'images_to_check_batch_size': max_batch_limit})
    taxi_config.set(EATS_PICS_UPDATE_SETTINGS=update_config)

    refresh_image_period = update_config[
        'refresh_image_period_in_hours'
    ] * dt.timedelta(hours=1)

    mock_image_path = mock_ext_image.get_prefix()

    image_data = [
        _generate_image_data(
            base_url=i['url'],
            url=mockserver.url(f'{mock_image_path}/{i["url"]}'),
            status=i['status'],
            created_at=i['created_at'] if 'created_at' in i else None,
            retry_at=i['retry_at'] if 'retry_at' in i else None,
            last_checked_at=i['last_checked_at'] - 2 * refresh_image_period
            if 'last_checked_at' in i
            else None,
        )
        for i in images_in_db
    ]

    @testpoint('eats-pics-processing_upload_images::urls-to-process')
    def task_urls_to_process(urls):
        assert set(urls) == {
            mockserver.url(f'{mock_image_path}/{i}') for i in expected_urls
        }

    id_to_url = _sql_add_source_images(pg_cursor, image_data)

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_urls_to_process.has_calls

    image_statuses = _sql_get_source_image_status(
        pg_cursor, list(id_to_url.keys()),
    )
    _add_base_url_to_image_statuses(image_statuses, id_to_url)
    _verify_source_image_status(image_statuses, list(id_to_url.values()), [])


async def test_zora_host_limit_passthrough(
        pg_cursor,
        taxi_eats_pics,
        taxi_config,
        testpoint,
        mockserver,
        mock_ext_image,
):
    update_config = taxi_config.get('EATS_PICS_UPDATE_SETTINGS')
    update_config.update({'max_zora_per_host_rps': 1})
    taxi_config.set(EATS_PICS_UPDATE_SETTINGS=update_config)

    refresh_image_period = update_config[
        'refresh_image_period_in_hours'
    ] * dt.timedelta(hours=1)

    mock_image_path = mock_ext_image.get_prefix()

    time_in_past = dt.datetime.now() - dt.timedelta(seconds=30)
    time_in_past_refreshable = dt.datetime.now() - refresh_image_period * 2
    images_in_db = [
        {
            'url': 'refreshable_1',
            'status': 'done',
            'last_checked_at': time_in_past_refreshable,
        },
        {
            'url': 'refreshable_2',
            'status': 'done',
            'last_checked_at': time_in_past_refreshable,
        },
        {'url': 'new_1', 'status': 'new'},
        {'url': 'new_2', 'status': 'new'},
        {
            'url': 'retryable_error_1',
            'status': 'error',
            'retry_at': time_in_past,
        },
        {
            'url': 'retryable_error_2',
            'status': 'error',
            'retry_at': time_in_past,
        },
    ]
    expected_urls = [
        'refreshable_1',
        'refreshable_2',
        'new_1',
        'new_2',
        'retryable_error_1',
        'retryable_error_2',
    ]

    image_data = [
        _generate_image_data(
            base_url=i['url'],
            url=mockserver.url(f'{mock_image_path}/{i["url"]}'),
            status=i['status'],
            created_at=i['created_at'] if 'created_at' in i else None,
            retry_at=i['retry_at'] if 'retry_at' in i else None,
            last_checked_at=i['last_checked_at']
            if 'last_checked_at' in i
            else None,
        )
        for i in images_in_db
    ]

    @testpoint('eats-pics-processing_upload_images::urls-to-process')
    def task_urls_to_process(urls):
        assert set(urls) == {
            mockserver.url(f'{mock_image_path}/{i}') for i in expected_urls
        }

    id_to_url = _sql_add_source_images(pg_cursor, image_data)

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_urls_to_process.has_calls

    image_statuses = _sql_get_source_image_status(
        pg_cursor, list(id_to_url.keys()),
    )
    _add_base_url_to_image_statuses(image_statuses, id_to_url)
    _verify_source_image_status(image_statuses, list(id_to_url.values()), [])


@pytest.mark.parametrize(
    'host_limit, images_in_db, expected_urls',
    [
        pytest.param(
            2,
            [
                {
                    'url': 'http://host_1/1',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=6),
                },
                {
                    'url': 'http://host_1/2',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=5),
                },
                {
                    'url': 'http://host_1/3',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=4),
                },
                {
                    'url': 'http://host_2/1',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=3),
                },
                {
                    'url': 'http://host_2/2',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=2),
                },
                {
                    'url': 'http://host_2/3',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=1),
                },
            ],
            [
                'http://host_1/1',
                'http://host_1/2',
                'http://host_2/1',
                'http://host_2/2',
            ],
            id='new only',
        ),
        pytest.param(
            2,
            [
                {
                    'url': 'http://host_1/1',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=6),
                },
                {
                    'url': 'http://host_1/2',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=5),
                },
                {
                    'url': 'http://host_1/3',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=4),
                },
                {
                    'url': 'http://host_2/1',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=3),
                },
                {
                    'url': 'http://host_2/2',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=2),
                },
                {
                    'url': 'http://host_2/3',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=1),
                },
            ],
            [
                'http://host_1/1',
                'http://host_1/2',
                'http://host_2/1',
                'http://host_2/2',
            ],
            id='error only',
        ),
        pytest.param(
            2,
            [
                {
                    'url': 'http://host_1/1',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=6,
                    ),
                },
                {
                    'url': 'http://host_1/2',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=5,
                    ),
                },
                {
                    'url': 'http://host_1/3',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=4,
                    ),
                },
                {
                    'url': 'http://host_2/1',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=3,
                    ),
                },
                {
                    'url': 'http://host_2/2',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=2,
                    ),
                },
                {
                    'url': 'http://host_2/3',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=1,
                    ),
                },
            ],
            [
                'http://host_1/1',
                'http://host_1/2',
                'http://host_2/1',
                'http://host_2/2',
            ],
            id='refreshable only',
        ),
        pytest.param(
            3,
            [
                {
                    'url': 'http://host_1/1',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=3),
                },
                {
                    'url': 'http://host_1/2',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=2),
                },
                {
                    'url': 'http://host_2/1',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=1),
                },
                {
                    'url': 'http://host_1/3',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=5),
                },
                {
                    'url': 'http://host_1/4',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=4),
                },
                {
                    'url': 'http://host_2/2',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=3),
                },
                {
                    'url': 'http://host_2/3',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=2),
                },
                {
                    'url': 'http://host_2/4',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=1),
                },
            ],
            [
                'http://host_1/1',
                'http://host_1/2',
                'http://host_1/3',
                'http://host_2/1',
                'http://host_2/2',
                'http://host_2/3',
            ],
            id='new and error',
        ),
        pytest.param(
            3,
            [
                {
                    'url': 'http://host_1/1',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=3),
                },
                {
                    'url': 'http://host_1/2',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=2),
                },
                {
                    'url': 'http://host_2/1',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=1),
                },
                {
                    'url': 'http://host_1/3',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=5,
                    ),
                },
                {
                    'url': 'http://host_1/4',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=4,
                    ),
                },
                {
                    'url': 'http://host_2/2',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=3,
                    ),
                },
                {
                    'url': 'http://host_2/3',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=2,
                    ),
                },
                {
                    'url': 'http://host_2/4',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=1,
                    ),
                },
            ],
            [
                'http://host_1/1',
                'http://host_1/2',
                'http://host_1/3',
                'http://host_2/1',
                'http://host_2/2',
                'http://host_2/3',
            ],
            id='error and refreshable',
        ),
    ],
)
async def test_zora_host_limit(
        pg_cursor,
        taxi_eats_pics,
        taxi_config,
        component_config,
        testpoint,
        host_limit,
        images_in_db,
        expected_urls,
):
    node_count = component_config.get('pics-service-settings', 'node_count')
    assert node_count

    update_config = taxi_config.get('EATS_PICS_UPDATE_SETTINGS')
    update_config.update({'max_zora_per_host_rps': host_limit * node_count})
    taxi_config.set(EATS_PICS_UPDATE_SETTINGS=update_config)

    refresh_image_period = update_config[
        'refresh_image_period_in_hours'
    ] * dt.timedelta(hours=1)

    image_data = [
        _generate_image_data(
            base_url=i['url'],
            url=i['url'],
            status=i['status'],
            created_at=i['created_at'] if 'created_at' in i else None,
            retry_at=i['retry_at'] if 'retry_at' in i else None,
            last_checked_at=i['last_checked_at'] - refresh_image_period * 2
            if 'last_checked_at' in i
            else None,
        )
        for i in images_in_db
    ]

    @testpoint('eats-pics-processing_upload_images::urls-to-process')
    def task_urls_to_process(urls):
        assert set(urls) == set(expected_urls)

    @testpoint('eats-pics-processing_upload_images::download-abort')
    def task_download_abort(param):
        # Have to abort here to avoid forced service crash
        # caused by the unsupported mock url prefix
        return {'inject_failure': True}

    id_to_url = _sql_add_source_images(pg_cursor, image_data)

    try:
        await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
        assert False, 'Periodic task should\'ve failed'
    except taxi_eats_pics.PeriodicTaskFailed:
        assert task_urls_to_process.has_calls
        assert task_download_abort.has_calls

    image_statuses = _sql_get_source_image_status(
        pg_cursor, list(id_to_url.keys()),
    )
    _add_base_url_to_image_statuses(image_statuses, id_to_url)
    unprocessed_urls = [
        url for url in id_to_url.values() if url not in expected_urls
    ]
    _verify_source_image_status(
        image_statuses, unprocessed_urls, expected_urls,
    )


@pytest.mark.parametrize(
    """
    max_batch_limit,
    min_batch_limit_percent,
    host_limit,
    images_in_db,
    expected_urls
    """,
    [
        pytest.param(
            3,
            50,
            2,
            [
                {
                    'url': 'http://host_1/1',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=5),
                },
                {
                    'url': 'http://host_1/2',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=4),
                },
                {
                    'url': 'http://host_1/3',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=3),
                },
                {
                    'url': 'http://host_2/1',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=2),
                },
                {
                    'url': 'http://host_2/2',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=1),
                },
            ],
            ['http://host_1/1', 'http://host_1/2'],
            id='new only, one cycle',
        ),
        pytest.param(
            4,
            76,
            2,
            [
                {
                    'url': 'http://host_1/1',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=6),
                },
                {
                    'url': 'http://host_1/2',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=5),
                },
                {
                    'url': 'http://host_1/3',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=4),
                },
                {
                    'url': 'http://host_2/1',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=3),
                },
                {
                    'url': 'http://host_2/2',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=2),
                },
                {
                    'url': 'http://host_2/3',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=1),
                },
            ],
            [
                'http://host_1/1',
                'http://host_1/2',
                'http://host_2/1',
                'http://host_2/2',
            ],
            id='new only, two cycles',
        ),
        pytest.param(
            3,
            50,
            2,
            [
                {
                    'url': 'http://host_1/1',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=5),
                },
                {
                    'url': 'http://host_1/2',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=4),
                },
                {
                    'url': 'http://host_1/3',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=3),
                },
                {
                    'url': 'http://host_2/1',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=2),
                },
                {
                    'url': 'http://host_2/2',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=1),
                },
            ],
            ['http://host_1/1', 'http://host_1/2'],
            id='error only, one cycle',
        ),
        pytest.param(
            4,
            76,
            2,
            [
                {
                    'url': 'http://host_1/1',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=6),
                },
                {
                    'url': 'http://host_1/2',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=5),
                },
                {
                    'url': 'http://host_1/3',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=4),
                },
                {
                    'url': 'http://host_2/1',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=3),
                },
                {
                    'url': 'http://host_2/2',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=2),
                },
                {
                    'url': 'http://host_2/3',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=1),
                },
            ],
            [
                'http://host_1/1',
                'http://host_1/2',
                'http://host_2/1',
                'http://host_2/2',
            ],
            id='error only, two cycles',
        ),
        pytest.param(
            3,
            50,
            2,
            [
                {
                    'url': 'http://host_1/1',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=5,
                    ),
                },
                {
                    'url': 'http://host_1/2',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=4,
                    ),
                },
                {
                    'url': 'http://host_1/3',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=3,
                    ),
                },
                {
                    'url': 'http://host_2/1',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=2,
                    ),
                },
                {
                    'url': 'http://host_2/2',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=1,
                    ),
                },
            ],
            ['http://host_1/1', 'http://host_1/2'],
            id='refreshable only, one cycle',
        ),
        pytest.param(
            4,
            76,
            2,
            [
                {
                    'url': 'http://host_1/1',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=6,
                    ),
                },
                {
                    'url': 'http://host_1/2',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=5,
                    ),
                },
                {
                    'url': 'http://host_1/3',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=4,
                    ),
                },
                {
                    'url': 'http://host_2/1',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=3,
                    ),
                },
                {
                    'url': 'http://host_2/2',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=2,
                    ),
                },
                {
                    'url': 'http://host_2/3',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=1,
                    ),
                },
            ],
            [
                'http://host_1/1',
                'http://host_1/2',
                'http://host_2/1',
                'http://host_2/2',
            ],
            id='refreshable only, two cycles',
        ),
        pytest.param(
            4,
            76,
            2,
            [
                {
                    'url': 'http://host_1/1',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=6),
                },
                {
                    'url': 'http://host_1/2',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=5),
                },
                {
                    'url': 'http://host_1/3',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=4),
                },
                {
                    'url': 'http://host_2/1',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=3),
                },
                {
                    'url': 'http://host_2/2',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=2),
                },
                {
                    'url': 'http://host_2/3',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=1),
                },
            ],
            [
                'http://host_1/1',
                'http://host_1/2',
                'http://host_2/1',
                'http://host_2/2',
            ],
            id='new and error, two cycles',
        ),
        pytest.param(
            4,
            76,
            2,
            [
                {
                    'url': 'http://host_1/1',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=6),
                },
                {
                    'url': 'http://host_1/2',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=5),
                },
                {
                    'url': 'http://host_1/3',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=4),
                },
                {
                    'url': 'http://host_2/1',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=3,
                    ),
                },
                {
                    'url': 'http://host_2/2',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=2,
                    ),
                },
                {
                    'url': 'http://host_2/3',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=1,
                    ),
                },
            ],
            [
                'http://host_1/1',
                'http://host_1/2',
                'http://host_2/1',
                'http://host_2/2',
            ],
            id='error and refreshable, two cycles',
        ),
    ],
)
async def test_zora_host_limit_with_min_limit(
        pg_cursor,
        taxi_eats_pics,
        taxi_config,
        component_config,
        testpoint,
        max_batch_limit,
        min_batch_limit_percent,
        host_limit,
        images_in_db,
        expected_urls,
):
    node_count = component_config.get('pics-service-settings', 'node_count')
    assert node_count

    update_config = taxi_config.get('EATS_PICS_UPDATE_SETTINGS')
    update_config.update(
        {
            'max_zora_per_host_rps': host_limit * node_count,
            'images_to_check_batch_size': max_batch_limit,
            'images_to_check_batch_min_percent': min_batch_limit_percent,
        },
    )
    taxi_config.set(EATS_PICS_UPDATE_SETTINGS=update_config)

    refresh_image_period = update_config[
        'refresh_image_period_in_hours'
    ] * dt.timedelta(hours=1)

    image_data = [
        _generate_image_data(
            base_url=i['url'],
            url=i['url'],
            status=i['status'],
            created_at=i['created_at'] if 'created_at' in i else None,
            retry_at=i['retry_at'] if 'retry_at' in i else None,
            last_checked_at=i['last_checked_at'] - refresh_image_period * 2
            if 'last_checked_at' in i
            else None,
        )
        for i in images_in_db
    ]

    @testpoint('eats-pics-processing_upload_images::urls-to-process')
    def task_urls_to_process(urls):
        assert set(urls) == set(expected_urls)

    @testpoint('eats-pics-processing_upload_images::download-abort')
    def task_download_abort(param):
        # Have to abort here to avoid forced service crash
        # caused by the unsupported mock url prefix
        return {'inject_failure': True}

    id_to_url = _sql_add_source_images(pg_cursor, image_data)

    try:
        await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
        assert False, 'Periodic task should\'ve failed'
    except taxi_eats_pics.PeriodicTaskFailed:
        assert task_urls_to_process.has_calls
        assert task_download_abort.has_calls

    image_statuses = _sql_get_source_image_status(
        pg_cursor, list(id_to_url.keys()),
    )
    _add_base_url_to_image_statuses(image_statuses, id_to_url)
    unprocessed_urls = [
        url for url in id_to_url.values() if url not in expected_urls
    ]
    _verify_source_image_status(
        image_statuses, unprocessed_urls, expected_urls,
    )


@pytest.mark.parametrize(
    'source_limit, images_in_db, expected_urls',
    [
        pytest.param(
            2,
            [
                {
                    'url': 'url1',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=4),
                    'is_zora': True,
                },
                {
                    'url': 'url2',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=3),
                    'is_zora': True,
                },
                {
                    'url': 'url3',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=2),
                    'is_zora': True,
                },
                {
                    'url': 'url4',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=1),
                    'is_zora': False,
                },
            ],
            ['url1', 'url2', 'url4'],
            id='new only',
        ),
        pytest.param(
            2,
            [
                {
                    'url': 'url1',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=4),
                    'is_zora': True,
                },
                {
                    'url': 'url2',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=3),
                    'is_zora': True,
                },
                {
                    'url': 'url3',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=2),
                    'is_zora': True,
                },
                {
                    'url': 'url4',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=1),
                    'is_zora': False,
                },
            ],
            ['url1', 'url2', 'url4'],
            id='error only',
        ),
        pytest.param(
            2,
            [
                {
                    'url': 'url1',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=4,
                    ),
                    'is_zora': True,
                },
                {
                    'url': 'url2',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=3,
                    ),
                    'is_zora': True,
                },
                {
                    'url': 'url3',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=2,
                    ),
                    'is_zora': True,
                },
                {
                    'url': 'url4',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=1,
                    ),
                    'is_zora': False,
                },
            ],
            ['url1', 'url2', 'url4'],
            id='refreshable only',
        ),
        pytest.param(
            2,
            [
                {
                    'url': 'url1',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=5),
                    'is_zora': True,
                },
                {
                    'url': 'url2',
                    'status': 'new',
                    'created_at': dt.datetime.now() - dt.timedelta(seconds=4),
                    'is_zora': False,
                },
                {
                    'url': 'url3',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=3),
                    'is_zora': True,
                },
                {
                    'url': 'url4',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=2),
                    'is_zora': True,
                },
                {
                    'url': 'url5',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=1),
                    'is_zora': False,
                },
            ],
            ['url1', 'url2', 'url3', 'url5'],
            id='new and error',
        ),
        pytest.param(
            2,
            [
                {
                    'url': 'url1',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=5),
                    'is_zora': True,
                },
                {
                    'url': 'url2',
                    'status': 'error',
                    'retry_at': dt.datetime.now() - dt.timedelta(seconds=4),
                    'is_zora': False,
                },
                {
                    'url': 'url3',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=3,
                    ),
                    'is_zora': True,
                },
                {
                    'url': 'url4',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=2,
                    ),
                    'is_zora': True,
                },
                {
                    'url': 'url5',
                    'status': 'done',
                    'last_checked_at': dt.datetime.now() - dt.timedelta(
                        seconds=1,
                    ),
                    'is_zora': False,
                },
            ],
            ['url1', 'url2', 'url3', 'url5'],
            id='error and refreshable',
        ),
    ],
)
async def test_zora_source_limit(
        pg_cursor,
        taxi_eats_pics,
        taxi_config,
        mockserver,
        component_config,
        testpoint,
        source_limit,
        images_in_db,
        expected_urls,
):
    node_count = component_config.get('pics-service-settings', 'node_count')
    assert node_count

    update_config = taxi_config.get('EATS_PICS_UPDATE_SETTINGS')
    update_config.update({'max_zora_source_rps': source_limit * node_count})
    taxi_config.set(EATS_PICS_UPDATE_SETTINGS=update_config)

    refresh_image_period = update_config[
        'refresh_image_period_in_hours'
    ] * dt.timedelta(hours=1)

    def _generate_full_url(url, is_zora):
        # pylint: disable=no-else-return
        if is_zora:
            # not whitelisted url
            return f'http://host/{url}'
        else:
            # whitelisted url
            return mockserver.url(f'{MOCK_IMAGES_PATH}/{url}')

    image_data = [
        _generate_image_data(
            base_url=i['url'],
            url=_generate_full_url(i['url'], i['is_zora']),
            status=i['status'],
            created_at=i['created_at'] if 'created_at' in i else None,
            retry_at=i['retry_at'] if 'retry_at' in i else None,
            last_checked_at=i['last_checked_at'] - refresh_image_period * 2
            if 'last_checked_at' in i
            else None,
        )
        for i in images_in_db
    ]

    @testpoint('eats-pics-processing_upload_images::urls-to-process')
    def task_urls_to_process(urls):
        assert len(urls) == len(expected_urls)
        assert set(urls) == {
            i['url'] for i in image_data if i['base_url'] in expected_urls
        }

    @testpoint('eats-pics-processing_upload_images::download-abort')
    def task_download_abort(param):
        # Have to abort here to avoid forced service crash
        # caused by the unsupported mock url prefix
        return {'inject_failure': True}

    id_to_url = _sql_add_source_images(pg_cursor, image_data)

    try:
        await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
        assert False, 'Periodic task should\'ve failed'
    except taxi_eats_pics.PeriodicTaskFailed:
        assert task_urls_to_process.has_calls
        assert task_download_abort.has_calls

    image_statuses = _sql_get_source_image_status(
        pg_cursor, list(id_to_url.keys()),
    )
    _add_base_url_to_image_statuses(image_statuses, id_to_url)
    unprocessed_urls = [
        url for url in id_to_url.values() if url not in expected_urls
    ]
    _verify_source_image_status(
        image_statuses, unprocessed_urls, expected_urls,
    )


def _generate_image_data(
        base_url,
        url,
        ava_id=None,
        status='new',
        binary=b'',
        ava_url=None,
        retry_delay=None,
        retry_at=None,
        created_at=None,
        is_being_processed=None,
        processing_started_at=None,
        is_check_needed=True,
        last_checked_at=None,
        has_active_subscriptions=None,
):
    return {
        'base_url': base_url,
        'url': url,
        'ava_id': ava_id,
        'ava_url': ava_url,
        'created_at': created_at or dt.datetime.now(),
        'status': status,
        'error_text': 'error' if status == 'error' else None,
        'retry_delay': retry_delay,
        'retry_at': retry_at,
        'last_checked_at': last_checked_at,
        'is_being_processed': (
            is_being_processed if is_being_processed else False
        ),
        'is_check_needed': is_check_needed,
        'processing_started_at': processing_started_at,
        'binary': binary,
        'md5': hashlib.md5(binary).hexdigest(),
        'has_active_subscriptions': (
            has_active_subscriptions if has_active_subscriptions else True
        ),
    }


def _sql_add_source_images(pg_cursor, image_data):
    data = []
    image_data_copy = image_data.copy()
    for i in image_data_copy:
        result = re.search(
            '(http|https)://(.+?)/(.+)', i['url'], re.IGNORECASE,
        )
        i['host'] = result.group(2)
        i['path'] = result.group(3)
        i['is_https'] = result.group(1) == 'https'

    for i in image_data_copy:
        pg_cursor.execute(
            """
            insert into eats_pics.source_images(
                url,
                host,
                path,
                is_https,
                ava_image_id,
                status,
                retry_delay,
                retry_at,
                is_being_processed,
                processing_started_at,
                last_checked_at,
                has_active_subscriptions,
                is_check_needed
            )
            values(
                %(url)s,
                %(host)s,
                %(path)s,
                %(is_https)s,
                %(ava_id)s,
                %(status)s,
                %(retry_delay)s,
                %(retry_at)s,
                %(is_being_processed)s,
                %(processing_started_at)s,
                %(last_checked_at)s,
                %(has_active_subscriptions)s,
                %(is_check_needed)s
            )
            returning %(base_url)s as base_url, id
            """,
            i,
        )
        result = pg_cursor.fetchall()
        if 'error_text' in i and i['error_text'] is not None:
            pg_cursor.execute(
                f"""
                insert into eats_pics.source_image_errors(
                    source_image_id,
                    error_source,
                    message_short,
                    message_detailed
                )
                values(
                    {result[0]['id']},
                    'internal',
                    'error',
                    '{i['error_text']}'
                )
                """,
            )
        data += result
    return {i['id']: i['base_url'] for i in data}


def _sql_get_source_image_status(pg_cursor, src_ids):
    pg_cursor.execute(
        """
        select id, is_being_processed
        from eats_pics.source_images
        where id = any(%s)
        """,
        (src_ids,),
    )
    return [
        {'id': i['id'], 'is_being_processed': i['is_being_processed']}
        for i in pg_cursor.fetchall()
    ]


def _add_base_url_to_image_statuses(image_statuses, id_to_base_url):
    for status in image_statuses:
        status['base_url'] = id_to_base_url[status['id']]


def _verify_source_image_status(
        image_statuses, urls_not_in_progress, urls_in_progress,
):
    assert len(image_statuses) == (
        len(urls_not_in_progress) + len(urls_in_progress)
    )
    for status in image_statuses:
        base_url = status['base_url']
        assert base_url in urls_not_in_progress + urls_in_progress
        if base_url in urls_not_in_progress:
            assert not status['is_being_processed']
        elif base_url in urls_in_progress:
            assert status['is_being_processed']
