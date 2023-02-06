import re

HANDLER = '/v1/unsubscribe'


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


async def test_request(taxi_eats_pics, pg_cursor):

    client_name = 'client_service'
    urls_before = ['http://url/1', 'https://url/2', 'http://url3/4']
    urls_to_remove = ['https://url/2', 'http://url3/4', 'http://unknown/url']

    client_id = _sql_add_client(pg_cursor, client_name)

    source_image_ids = _sql_add_source_images(
        pg_cursor,
        [{'url': i, 'has_active_subscriptions': True} for i in urls_before],
    )
    _sql_add_client_images(pg_cursor, client_id, source_image_ids)

    response = await taxi_eats_pics.post(
        HANDLER, json={'client_name': client_name, 'items': urls_to_remove},
    )
    assert response.status_code == 204

    parsed_client_urls = _sql_get_client_images(pg_cursor, client_id)
    assert {i['url'] for i in parsed_client_urls} == set(urls_before) - set(
        urls_to_remove,
    )


async def test_multiple_clients(taxi_eats_pics, pg_cursor):

    client_name_1 = 'client_service_1'
    client_name_2 = 'client_service_2'

    urls_before_1 = [
        'http://url/client_1/1',
        'http://url/client_1/2',
        'http://url/client_1_2/1',
    ]
    urls_before_2 = [
        'http://url/client_2/1',
        'http://url/client_2/2',
        'http://url/client_1_2/1',
    ]

    data_before = [
        {
            'url': 'http://url/currently_has_subscription/1',
            'has_active_subscriptions': True,
        },
        {
            'url': 'http://url/always_no_subscription/2',
            'has_active_subscriptions': False,
        },
    ]

    urls_to_remove_1 = ['http://url/client_1/1', 'http://url/client_1_2/1']
    urls_to_remove_2 = ['http://url/client_2/1']

    client_id_1 = _sql_add_client(pg_cursor, client_name_1)
    client_id_2 = _sql_add_client(pg_cursor, client_name_2)

    _sql_add_source_images(pg_cursor, data_before)
    source_image_ids_1 = _sql_add_source_images(
        pg_cursor,
        [{'url': i, 'has_active_subscriptions': True} for i in urls_before_1],
    )
    source_image_ids_2 = _sql_add_source_images(
        pg_cursor,
        [{'url': i, 'has_active_subscriptions': True} for i in urls_before_2],
    )

    _sql_add_client_images(pg_cursor, client_id_1, source_image_ids_1)
    _sql_add_client_images(pg_cursor, client_id_2, source_image_ids_2)

    response = await taxi_eats_pics.post(
        HANDLER,
        json={'client_name': client_name_1, 'items': urls_to_remove_1},
    )
    assert response.status_code == 204

    response = await taxi_eats_pics.post(
        HANDLER,
        json={'client_name': client_name_2, 'items': urls_to_remove_2},
    )
    assert response.status_code == 204

    parsed_client_urls_1 = _sql_get_client_images(pg_cursor, client_id_1)
    assert {i['url'] for i in parsed_client_urls_1} == set(
        urls_before_1,
    ) - set(urls_to_remove_1)

    parsed_client_urls_2 = _sql_get_client_images(pg_cursor, client_id_2)
    assert {i['url'] for i in parsed_client_urls_2} == set(
        urls_before_2,
    ) - set(urls_to_remove_2)

    all_urls = _sql_get_source_images(pg_cursor)
    assert {i['url'] for i in all_urls if i['has_active_subscriptions']} == (
        set(
            urls_before_1
            + urls_before_2
            + [i['url'] for i in data_before if i['has_active_subscriptions']],
        )
        - set(urls_to_remove_1).intersection(urls_to_remove_2)
    )


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
            on conflict(url)
            do nothing
            """,
            i,
        )

    pg_cursor.execute(
        """
        select id
        from eats_pics.source_images
        where url = any(%s)
        """,
        ([i['url'] for i in src_data],),
    )
    return [i['id'] for i in pg_cursor.fetchall()]


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
        """
        select url, si.is_https, si.host, si.path, si.has_active_subscriptions
        from eats_pics.source_images si
          join eats_pics.client_images ci
            on ci.source_image_id = si.id
        where client_id = %s
        """,
        (client_id,),
    )
    return [
        {
            'url': i['url'],
            'is_https': i['is_https'],
            'host': i['host'],
            'path': i['path'],
            'has_active_subscriptions': i['has_active_subscriptions'],
        }
        for i in pg_cursor.fetchall()
    ]


def _sql_get_source_images(pg_cursor):
    pg_cursor.execute(
        f"""
        select url, si.is_https, si.host, si.path, si.has_active_subscriptions
        from eats_pics.source_images si
        """,
    )
    return [
        {
            'url': i['url'],
            'is_https': i['is_https'],
            'host': i['host'],
            'path': i['path'],
            'has_active_subscriptions': i['has_active_subscriptions'],
        }
        for i in pg_cursor.fetchall()
    ]
