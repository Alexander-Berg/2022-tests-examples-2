import re

import pytest

HANDLER = '/v1/subscribe'


async def test_no_items(taxi_eats_pics):
    response = await taxi_eats_pics.post(
        HANDLER, json={'client_name': 'client_service', 'items': []},
    )
    assert response.status_code == 400


async def test_unknown_client(taxi_eats_pics, pg_cursor):
    _sql_add_client(pg_cursor, 'known_client')

    response = await taxi_eats_pics.post(
        HANDLER, json={'client_name': 'unknown_client', 'items': ['url']},
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'urls_before, urls_to_insert',
    [
        ([], ['http://url/1', 'https://url/2', 'https://url3/4']),
        (
            ['http://url/1', 'https://url/2', 'https://url3/4'],
            ['http://url/1', 'https://url/2', 'https://url3/4'],
        ),
        (
            ['http://url/1', 'https://url/2', 'https://url3/4'],
            ['http://url/1', 'https://url/5'],
        ),
        ([], ['invalid_url']),
    ],
)
async def test_single_client(
        taxi_eats_pics, pg_cursor, urls_before, urls_to_insert,
):

    client_name = 'client_service'
    urls_after = list(set(urls_before + urls_to_insert))

    client_id = _sql_add_client(pg_cursor, client_name)
    if urls_before:
        source_image_ids = _sql_add_source_images(
            pg_cursor,
            [
                {'url': i, 'has_active_subscriptions': True}
                for i in urls_before
            ],
        )
        _sql_add_client_images(pg_cursor, client_id, source_image_ids)

    response = await taxi_eats_pics.post(
        HANDLER, json={'client_name': client_name, 'items': urls_to_insert},
    )
    assert response.status_code == 204

    parsed_client_urls = _sql_get_client_images(pg_cursor, client_id)
    _verify_urls(parsed_client_urls, urls_after)
    if urls_to_insert == ['invalid_url']:
        assert (
            _sql_get_source_images_errors(pg_cursor)[0]['error_source']
            == 'internal'
        )
        assert (
            _sql_get_source_images_errors(pg_cursor)[0]['message_short']
            == 'url parsing failed'
        )
        assert (
            _sql_get_source_images_errors(pg_cursor)[0]['message_detailed']
            == ''
        )


async def test_multiple_clients(taxi_eats_pics, pg_cursor):

    client_name_1 = 'client_service_1'
    client_name_2 = 'client_service_2'

    data_before = [
        {
            'url': 'http://url/currently_no_subscription/1',
            'has_active_subscriptions': False,
        },
        {
            'url': 'http://url/always_no_subscription/2',
            'has_active_subscriptions': False,
        },
    ]

    urls_to_insert_1 = [
        'http://url/client_1',
        'http://url/client_1_2',
        'http://url/currently_no_subscription/1',
    ]
    urls_to_insert_2 = ['http://url/client_2', 'http://url/client_1_2']

    client_id_1 = _sql_add_client(pg_cursor, client_name_1)
    client_id_2 = _sql_add_client(pg_cursor, client_name_2)

    _sql_add_source_images(pg_cursor, data_before)

    response = await taxi_eats_pics.post(
        HANDLER,
        json={'client_name': client_name_1, 'items': urls_to_insert_1},
    )
    assert response.status_code == 204

    response = await taxi_eats_pics.post(
        HANDLER,
        json={'client_name': client_name_2, 'items': urls_to_insert_2},
    )
    assert response.status_code == 204

    parsed_client_urls_1 = _sql_get_client_images(pg_cursor, client_id_1)
    _verify_urls(parsed_client_urls_1, urls_to_insert_1)

    parsed_client_urls_2 = _sql_get_client_images(pg_cursor, client_id_2)
    _verify_urls(parsed_client_urls_2, urls_to_insert_2)

    all_urls = _sql_get_source_images(pg_cursor)
    assert {
        i['url'] for i in all_urls if i['has_active_subscriptions']
    } == set(urls_to_insert_1 + urls_to_insert_2)


async def test_subscribe_to_processed_url(taxi_eats_pics, pg_cursor):

    client_name_1 = 'client_service_1'
    client_name_2 = 'client_service_2'
    client_id_1 = _sql_add_client(pg_cursor, client_name_1)
    client_id_2 = _sql_add_client(pg_cursor, client_name_2)

    urls_to_insert = [
        'http://url/client_1_subscription/1',
        'http://url/client_1_subscription_failed/2',
    ]

    response = await taxi_eats_pics.post(
        HANDLER, json={'client_name': client_name_1, 'items': urls_to_insert},
    )
    assert response.status_code == 204

    _sql_set_url_status(urls_to_insert[0], 'done', pg_cursor)
    _sql_set_url_status(urls_to_insert[1], 'error', pg_cursor)

    response = await taxi_eats_pics.post(
        HANDLER, json={'client_name': client_name_2, 'items': urls_to_insert},
    )
    assert response.status_code == 204

    client_2_images = _sql_get_client_images_raw(pg_cursor, client_id_2)
    assert len(client_2_images) == 2
    for client_image in client_2_images:
        assert client_image['needs_forwarding']

    client_1_images = _sql_get_client_images_raw(pg_cursor, client_id_1)
    assert len(client_1_images) == 2
    for client_image in client_1_images:
        assert not client_image['needs_forwarding']


def _sql_add_client(pg_cursor, client_name):
    pg_cursor.execute(
        """
        insert into eats_pics.clients(name)
        values (%s)
        returning id
        """,
        (client_name,),
    )
    return pg_cursor.fetchone()['id']


def _sql_add_source_images(pg_cursor, url_data):
    src_data = []
    for data in url_data:
        result = re.search(
            '(http|https)://(.+?)/(.+)', data['url'], re.IGNORECASE,
        )
        src_data.append(
            {
                'url': data['url'],
                'host': result.group(2) if result else None,
                'path': result.group(3) if result else None,
                'is_https': result.group(1) == 'https' if result else None,
                'has_active_subscriptions': data['has_active_subscriptions'],
            },
        )

    source_image_ids = []
    for i in src_data:
        pg_cursor.execute(
            """
            insert into eats_pics.source_images(
                url,
                host,
                path,
                is_https,
                has_active_subscriptions)
            values(
                %(url)s,
                %(host)s,
                %(path)s,
                %(is_https)s,
                %(has_active_subscriptions)s
            )
            returning id
            """,
            i,
        )
        source_image_ids.append(pg_cursor.fetchone()['id'])

    return source_image_ids


def _sql_add_client_images(pg_cursor, client_id, source_image_ids):
    pg_cursor.execute(
        """
        insert into eats_pics.client_images(client_id, source_image_id)
        values (%s, unnest(%s))
        """,
        (client_id, source_image_ids),
    )


def _sql_get_client_images(pg_cursor, client_id):
    pg_cursor.execute(
        f"""
        select
            si.url,
            si.is_https,
            si.host,
            si.path,
            si.has_active_subscriptions,
            si.status,
            ci.needs_forwarding
        from eats_pics.source_images si
          join eats_pics.client_images ci
            on ci.source_image_id = si.id
        where client_id = %s
        """,
        (client_id,),
    )
    return pg_cursor.fetchall()


def _sql_get_source_images(pg_cursor):
    pg_cursor.execute(
        f"""
        select url, is_https, host, path, has_active_subscriptions
        from eats_pics.source_images
        """,
    )
    return pg_cursor.fetchall()


def _sql_get_source_images_errors(pg_cursor):
    pg_cursor.execute(
        f"""
        select
            si.url,
            sie.error_source,
            sie.message_short,
            sie.message_detailed
        from eats_pics.source_images si
        join eats_pics.source_image_errors sie on sie.source_image_id = si.id
        """,
    )
    return pg_cursor.fetchall()


def _sql_get_client_images_raw(pg_cursor, client_id):
    pg_cursor.execute(
        f"""
        select * from eats_pics.client_images
        where client_id = {client_id}
        """,
    )
    return pg_cursor.fetchall()


def _sql_set_url_status(url, status, pg_cursor):
    pg_cursor.execute(
        f"""
        update eats_pics.source_images
        set status = '{status}'
        where url = '{url}'
        """,
    )


def _verify_urls(parsed_urls, expected_urls):
    parsed_urls_copy = parsed_urls.copy()
    for i in parsed_urls_copy:
        i.pop('has_active_subscriptions')

    assert {i['url'] for i in parsed_urls_copy} == set(expected_urls)
    for parsed_url in parsed_urls_copy:
        url = parsed_url['url']
        result = re.search('(http|https)://(.+?)/(.+)', url, re.IGNORECASE)
        assert parsed_url == {
            'url': url,
            'host': result.group(2) if result else None,
            'path': result.group(3) if result else None,
            'is_https': result.group(1) == 'https' if result else None,
            'status': 'new' if result else 'error',
            'needs_forwarding': not result,
        }
