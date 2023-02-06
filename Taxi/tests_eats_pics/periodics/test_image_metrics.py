import datetime as dt
import hashlib
import re

import pytest

PERIODIC_NAME = 'images-metrics-periodic'
METRIC_NAME = 'images-metrics'

# this path *is* whitelisted in config.json
MOCK_IMAGES_PATH = '/images/'

CLIENT_1 = 'imaclient'
CLIENT_2 = 'imaclienttoo'


@pytest.mark.parametrize(
    'image_status',
    [
        'new',
        'old_new',
        'old_done',
        'retryable_error',
        'nonretryable_error_not_viewed',
        'nonretryable_error_viewed',
        'done',
        'urls_to_refresh',
    ],
)
async def test_metrics_url_status(
        taxi_eats_pics,
        taxi_eats_pics_monitor,
        taxi_config,
        mockserver,
        testpoint,
        pg_cursor,
        image_status,
):
    if image_status == 'old_new':
        old_new_threshold = dt.timedelta(seconds=10)

        update_config = taxi_config.get('EATS_PICS_METRICS_SETTINGS')
        update_config.update(
            {
                'image_metric_old_new_threshold': (
                    old_new_threshold / dt.timedelta(seconds=1)
                ),
            },
        )
        taxi_config.set(EATS_PICS_METRICS_SETTINGS=update_config)
    elif image_status == 'old_done':
        old_done_threshold = dt.timedelta(seconds=10)
        refresh_time = dt.timedelta(hours=1)

        metrics_config = taxi_config.get('EATS_PICS_METRICS_SETTINGS')
        refresh_config = taxi_config.get('EATS_PICS_UPDATE_SETTINGS')
        metrics_config.update(
            {
                'image_metric_old_done_threshold': (
                    old_done_threshold / dt.timedelta(seconds=1)
                ),
            },
        )
        refresh_config.update(
            {
                'refresh_image_period_in_hours': (
                    refresh_time / dt.timedelta(hours=1)
                ),
            },
        )
        taxi_config.set(EATS_PICS_METRICS_SETTINGS=metrics_config)
        taxi_config.set(EATS_PICS_UPDATE_SETTINGS=refresh_config)
    elif image_status == 'urls_to_refresh':
        refresh_time = dt.timedelta(hours=1)
        refresh_config = taxi_config.get('EATS_PICS_UPDATE_SETTINGS')
        refresh_config.update(
            {
                'refresh_image_period_in_hours': (
                    refresh_time / dt.timedelta(hours=1)
                ),
            },
        )
        taxi_config.set(EATS_PICS_UPDATE_SETTINGS=refresh_config)

    client_1_urls = ['cl1_url1']
    client_2_urls = ['cl2_url1', 'cl2_url2']
    urls = client_1_urls + client_2_urls

    def gen_data_additional_data(url):
        # pylint: disable=no-else-return
        if image_status == 'new':
            return {'status': 'new'}
        elif image_status == 'old_new':
            return {
                'status': 'new',
                'created_at': dt.datetime.now() - old_new_threshold * 2,
            }
        elif image_status == 'old_done':
            return {
                'status': 'done',
                'last_checked_at': dt.datetime.now() - 2 * (
                    old_done_threshold + refresh_time
                ),
            }
        elif image_status == 'urls_to_refresh':
            return {
                'status': 'done',
                'last_checked_at': (
                    dt.datetime.now() - refresh_time - dt.timedelta(seconds=1)
                ),
            }
        elif image_status == 'retryable_error':
            return {'status': 'error', 'retry_at': dt.datetime.now()}
        elif image_status == 'nonretryable_error_not_viewed':
            return {'status': 'error', 'is_error_viewed': False}
        elif image_status == 'nonretryable_error_viewed':
            return {'status': 'error', 'is_error_viewed': True}
        elif image_status == 'done':
            return {
                'status': 'done',
                'binary': _img_generator(url),
                'ava_url': f'01/0101/{url}',
            }
        else:
            assert False
            return {}

    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_IMAGES_PATH}/{i}'),
            **gen_data_additional_data(i),
        )
        for i in urls
    ]

    @testpoint(f'eats-pics-{METRIC_NAME}::step-finished')
    def task_step_finished(arg):
        pass

    def gen_expected_metrics():
        status_to_name = {
            'new': 'new_urls',
            'old_new': 'new_urls',
            'retryable_error': 'urls_with_retryable_errors',
            'nonretryable_error_not_viewed': 'urls_with_nonretryable_errors',
            'nonretryable_error_viewed': 'urls_with_nonretryable_errors',
            'done': 'fetched_urls',
            'old_done': 'fetched_urls',
            'urls_to_refresh': 'urls_to_refresh',
        }

        metrics = {
            'urls': {
                'total': len(urls),
                'per_client': {
                    CLIENT_1: len(client_1_urls),
                    CLIENT_2: len(client_2_urls),
                },
            },
            status_to_name[image_status]: {
                'total': len(urls),
                'per_client': {
                    CLIENT_1: len(client_1_urls),
                    CLIENT_2: len(client_2_urls),
                },
            },
        }

        if image_status == 'nonretryable_error_viewed':
            del metrics[status_to_name[image_status]]
        elif image_status == 'old_new':
            metrics['old_new_urls'] = len(urls)
        elif image_status == 'old_done':
            metrics['old_done_urls'] = len(urls)
            metrics['urls_to_refresh'] = {
                'total': len(urls),
                'per_client': {
                    CLIENT_1: len(client_1_urls),
                    CLIENT_2: len(client_2_urls),
                },
            }
        elif image_status == 'urls_to_refresh':
            metrics['fetched_urls'] = {
                'total': len(urls),
                'per_client': {
                    CLIENT_1: len(client_1_urls),
                    CLIENT_2: len(client_2_urls),
                },
            }
        elif image_status == 'done':
            metrics['unique_images'] = {
                'total': len({i['md5'] for i in image_data}),
                'per_client': {
                    CLIENT_1: len(
                        {
                            i['md5']
                            for i in image_data
                            if i['base_url'] in client_1_urls
                        },
                    ),
                    CLIENT_2: len(
                        {
                            i['md5']
                            for i in image_data
                            if i['base_url'] in client_2_urls
                        },
                    ),
                },
            }

        return metrics

    if image_status == 'done':
        hash_to_id = _sql_add_ava_images(pg_cursor, image_data)
        _add_ava_image_id_to_image_data(image_data, hash_to_id)

    client_name_to_id = _sql_add_clients(pg_cursor, [CLIENT_1, CLIENT_2])
    url_to_id = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(
        pg_cursor,
        client_name_to_id[CLIENT_1],
        [url_to_id[i] for i in client_1_urls],
    )
    _sql_add_client_images(
        pg_cursor,
        client_name_to_id[CLIENT_2],
        [url_to_id[i] for i in client_2_urls],
    )

    await taxi_eats_pics.run_distlock_task(PERIODIC_NAME)
    assert task_step_finished.has_calls

    metrics = await taxi_eats_pics_monitor.get_metrics()
    image_metrics = metrics['images-metrics']

    _verify_image_metrics(image_metrics, gen_expected_metrics())


async def test_metrics_fwd_status(
        taxi_eats_pics,
        taxi_eats_pics_monitor,
        taxi_config,
        mockserver,
        testpoint,
        pg_cursor,
):
    old_fwd_threshold = dt.timedelta(seconds=10)

    update_config = taxi_config.get('EATS_PICS_METRICS_SETTINGS')
    update_config.update(
        {
            'image_metric_old_forward_threshold': (
                old_fwd_threshold / dt.timedelta(seconds=1)
            ),
        },
    )
    taxi_config.set(EATS_PICS_UPDATE_SETTINGS=update_config)

    client_1_urls_fwd = ['cl1_fwd_url1']
    client_1_urls_nofwd = ['cl1_nofwd_url1']
    client_1_urls = client_1_urls_fwd + client_1_urls_nofwd

    client_2_urls_fwd = ['cl2_fwd_url1', 'cl2_fwd_url2']
    client_2_urls_nofwd = ['cl2_nofwd_url1', 'cl2_nofwd_url2']
    client_2_urls_old_fwd = ['cl2_old_fwd_url1', 'cl2_old_fwd_url2']

    client_2_urls = (
        client_2_urls_fwd + client_2_urls_nofwd + client_2_urls_old_fwd
    )

    urls = client_1_urls + client_2_urls
    urls_fwd = client_1_urls_fwd + client_2_urls_fwd + client_2_urls_old_fwd

    image_data = [
        _generate_image_data(
            base_url=i, url=mockserver.url(f'{MOCK_IMAGES_PATH}/{i}'),
        )
        for i in urls
    ]

    @testpoint(f'eats-pics-{METRIC_NAME}::step-finished')
    def task_step_finished(arg):
        pass

    client_name_to_id = _sql_add_clients(pg_cursor, [CLIENT_1, CLIENT_2])
    url_to_id = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(
        pg_cursor,
        client_name_to_id[CLIENT_1],
        [url_to_id[i] for i in client_1_urls],
    )
    _sql_add_client_images(
        pg_cursor,
        client_name_to_id[CLIENT_2],
        [url_to_id[i] for i in client_2_urls],
    )
    _sql_set_fwd_status(
        pg_cursor,
        client_name_to_id[CLIENT_1],
        [url_to_id[i] for i in client_1_urls_fwd],
        needs_forwarding=True,
    )
    _sql_set_fwd_status(
        pg_cursor,
        client_name_to_id[CLIENT_2],
        [url_to_id[i] for i in client_2_urls_fwd],
        needs_forwarding=True,
    )
    _sql_set_fwd_status(
        pg_cursor,
        client_name_to_id[CLIENT_2],
        [url_to_id[i] for i in client_2_urls_old_fwd],
        needs_forwarding=True,
        updated_at=dt.datetime.now() - old_fwd_threshold * 2,
    )

    await taxi_eats_pics.run_distlock_task(PERIODIC_NAME)
    assert task_step_finished.has_calls

    metrics = await taxi_eats_pics_monitor.get_metrics()
    image_metrics = metrics['images-metrics']

    _verify_image_metrics(
        image_metrics,
        {
            'urls': {
                'total': len(urls),
                'per_client': {
                    CLIENT_1: len(client_1_urls),
                    CLIENT_2: len(client_2_urls),
                },
            },
            'new_urls': {
                'total': len(urls),
                'per_client': {
                    CLIENT_1: len(client_1_urls),
                    CLIENT_2: len(client_2_urls),
                },
            },
            'urls_to_forward': {
                'total': len(urls_fwd),
                'per_client': {
                    CLIENT_1: len(client_1_urls_fwd),
                    CLIENT_2: len(client_2_urls_fwd + client_2_urls_old_fwd),
                },
            },
            'old_forward_urls': len(client_2_urls_old_fwd),
        },
    )


def _verify_image_metrics(image_metrics, expected_modified_metrics):
    expected_metrics = {
        'urls': {'total': 0, 'per_client': {}},
        'new_urls': {'total': 0, 'per_client': {}},
        'urls_with_retryable_errors': {'total': 0, 'per_client': {}},
        'urls_with_nonretryable_errors': {'total': 0, 'per_client': {}},
        'fetched_urls': {'total': 0, 'per_client': {}},
        'urls_to_forward': {'total': 0, 'per_client': {}},
        'unique_images': {'total': 0, 'per_client': {}},
        'old_forward_urls': 0,
        'old_new_urls': 0,
        'old_done_urls': 0,
        'urls_to_refresh': {'total': 0, 'per_client': {}},
    }
    expected_metrics.update(expected_modified_metrics)
    for metric in expected_metrics.values():
        if not isinstance(metric, dict):
            continue
        metric['per_client']['$meta'] = {
            'solomon_children_labels': 'client_name',
        }

    assert expected_metrics == image_metrics


def _generate_image_data(
        base_url,
        url,
        ava_url=None,
        status='new',
        binary=b'',
        retry_delay=None,
        retry_at=None,
        created_at=None,
        is_error_viewed=False,
        last_checked_at=None,
):
    return {
        'base_url': base_url,
        'url': url,
        'ava_url': None,
        'ava_image_id': None,
        'created_at': created_at or dt.datetime.now(),
        'status': status,
        'error_text': 'error' if status == 'error' else None,
        'is_error_viewed': is_error_viewed,
        'retry_delay': retry_delay,
        'retry_at': retry_at,
        'binary': binary,
        'md5': hashlib.md5(binary).hexdigest(),
        'last_checked_at': last_checked_at or dt.datetime.now(),
    }


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def _img_generator(url):
    return bytearray(b'I\'m an image! My url is %a' % url)


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
                created_at,
                ava_image_id,
                status,
                is_error_viewed,
                retry_delay,
                retry_at,
                last_checked_at
            )
            values(
                %(url)s,
                %(host)s,
                %(path)s,
                %(is_https)s,
                %(created_at)s,
                %(ava_image_id)s,
                %(status)s,
                %(is_error_viewed)s,
                %(retry_delay)s,
                %(retry_at)s,
                %(last_checked_at)s
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
    return {i['base_url']: i['id'] for i in data}


def _sql_get_source_image_status(pg_cursor):
    pg_cursor.execute(
        """
        select si.id, si.status,
        'Source: ' || sie.error_source
        || ', Error: ' || sie.message_short
        || ', Details: ' || sie.message_detailed as error_text,
        si.retry_delay, si.retry_at
        from eats_pics.source_images si
        left join eats_pics.source_image_errors sie
            on sie.source_image_id = si.id
        """,
    )
    statuses = pg_cursor.fetchall()
    for status in statuses:
        if status['retry_at']:
            status['retry_at'] = status['retry_at'].replace(tzinfo=None)
    return statuses


def _sql_add_ava_images(pg_cursor, ava_images):
    data = []
    for i in ava_images:
        pg_cursor.execute(
            """
            insert into eats_pics.ava_images(url, hash)
            values(%(ava_url)s,%(md5)s)
            returning hash, id
            """,
            i,
        )
        data += pg_cursor.fetchall()
    return {i['hash']: i['id'] for i in data}


def _sql_add_clients(pg_cursor, client_names):
    data = []
    for i in client_names:
        pg_cursor.execute(
            """
            insert into eats_pics.clients(name)
            values (%s)
            returning name, id
            """,
            (i,),
        )
        data += pg_cursor.fetchall()
    return {i['name']: i['id'] for i in data}


def _sql_add_client_images(pg_cursor, client_id, source_image_ids):
    pg_cursor.execute(
        """
        insert into eats_pics.client_images(client_id, source_image_id)
        values (%s, unnest(%s))
        """,
        (client_id, source_image_ids),
    )


def _sql_set_fwd_status(
        pg_cursor,
        client_id,
        source_image_ids,
        needs_forwarding,
        updated_at=None,
):
    updated_at = updated_at or dt.datetime.now()

    pg_cursor.execute(
        """
        update eats_pics.client_images
        set
            needs_forwarding = %s,
            updated_at = %s
        where client_id = %s and source_image_id = any(%s)
        """,
        (needs_forwarding, updated_at, client_id, source_image_ids),
    )


def _add_ava_image_id_to_image_data(image_data, hash_to_id):
    for data in image_data:
        data['ava_image_id'] = hash_to_id[data['md5']]
