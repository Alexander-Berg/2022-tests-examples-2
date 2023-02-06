import copy
import hashlib
import itertools
import re

PERIODIC_NAME = 'images-forward-periodic'

KNOWN_STQS = [
    {
        'stq_name': 'eats_nomenclature_update_pics',
        'client_name': 'eats-nomenclature',
    },
    {
        'stq_name': 'eats_core_update_pics',
        'client_name': 'eats-core-update-pics',
    },
]


async def test_notify_data(pg_cursor, taxi_eats_pics, stq, component_config):
    default_ava_base_url = component_config.get(
        'pics-service-settings', 'ava_base_url',
    )

    test_data = _generate_test_data()

    def _generate_url(i, cl_name, test_params):
        fwd = 'forward' if test_params['needs_forwarding'] else 'not_forward'
        ava_url = 'has_ava' if test_params['has_ava_url'] else 'no_ava'
        ava_base = (
            'has_ava_base'
            if test_params['has_ava_base_url']
            else 'no_ava_base'
        )
        error = (
            'has_error_text' if test_params['error_text'] else 'no_error_text'
        )
        error_si = (
            'has_error_text_source_images'
            if test_params['error_text_source_images']
            else 'no_error_text_source_images'
        )
        return f'{cl_name}_{ava_url}_{ava_base}_{error}_{error_si}_{fwd}_{i}'

    image_data = [
        _generate_image_data(
            url=_generate_url(i[0], i[1]['client_name'], i[2]),
            client_name=i[1]['client_name'],
            has_ava_url=i[2]['has_ava_url'],
            needs_forwarding=i[2]['needs_forwarding'],
            error_text=i[2]['error_text'],
            error_text_source_images=i[2]['error_text_source_images'],
            has_ava_base_url=i[2]['has_ava_base_url'],
        )
        for i in itertools.product(range(2), KNOWN_STQS, test_data)
    ]
    image_data += [
        _generate_image_data_with_invalid_url(
            url=_generate_url(i[0], i[1]['client_name'], i[2]),
            client_name=i[1]['client_name'],
            needs_forwarding=i[2]['needs_forwarding'],
            error_text_source_images=i[2]['error_text_source_images'],
        )
        for i in itertools.product(range(2), KNOWN_STQS, test_data)
    ]

    def _get_stq_expected_items(stq_name):
        def map_item(item):
            status_map = {'done': 'updated', 'error': 'error'}
            mapped_item = {
                'source_url': item['source_url'],
                'status': (
                    status_map[item['status']]
                    if item['status'] in status_map
                    else 'unknown'
                ),
            }
            if item['error_text']:
                mapped_item['error_text'] = (
                    f'Source: internal\nError: error\n'
                    f"""Details: {item['error_text']}"""
                )
            if item['ava_url']:
                current_base = (
                    item['ava_base_url']
                    if item['ava_base_url']
                    else default_ava_base_url
                )
                mapped_item[
                    'ava_url'
                ] = f'https://{current_base}/get-eda/{item["ava_url"]}/orig'
            if not item['ava_url'] and not item['error_text']:
                if item['error_text_source_images']:
                    error_text = item['error_text_source_images']
                else:
                    error_text = 'Error: missing error text'
                mapped_item['error_text'] = error_text
            return mapped_item

        return [
            map_item(i)
            for i in image_data_with_ids
            if stq_name in i['source_url'] and i['needs_forwarding']
        ]

    image_data_with_ids = _sql_add_images(pg_cursor, image_data)
    await taxi_eats_pics.run_distlock_task(PERIODIC_NAME)
    for i in KNOWN_STQS:
        stq_item = getattr(stq, i['stq_name'])

        assert stq_item.has_calls

        # check notification data
        stq_items = stq_item.next_call()['kwargs']['items']
        expected_items = _get_stq_expected_items(i['client_name'])
        assert _sort_by_src_url(stq_items) == _sort_by_src_url(expected_items)

    # check that all forwarding switches were flipped back
    index_to_needs_forwarding = _sql_get_forward_status(
        pg_cursor, image_data_with_ids,
    )
    assert len(index_to_needs_forwarding) == len(image_data_with_ids)
    assert True not in index_to_needs_forwarding.values()


async def test_unknown_client(pg_cursor, taxi_eats_pics, stq, testpoint):
    client_name = 'unknown_client'

    image_data = [
        _generate_image_data(
            url=f'url/client_name',
            client_name=client_name,
            has_ava_url=True,
            has_ava_base_url=False,
            needs_forwarding=True,
            error_text=None,
        ),
    ]

    @testpoint('eats-pics-processing_forward_images::unknown-client')
    def task_unknown_client(unknown_name):
        assert client_name == unknown_name

    _sql_add_images(pg_cursor, image_data)

    await taxi_eats_pics.run_distlock_task(PERIODIC_NAME)
    assert task_unknown_client.has_calls
    for i in KNOWN_STQS:
        stq_item = getattr(stq, i['stq_name'])
        # there should be no calls to other stq's
        assert not stq_item.has_calls


def _generate_test_data():
    return [
        {
            'has_ava_url': True,
            'has_ava_base_url': False,
            'needs_forwarding': True,
            'error_text': None,
            'error_text_source_images': None,
        },
        {
            'has_ava_url': True,
            'has_ava_base_url': True,
            'needs_forwarding': True,
            'error_text': None,
            'error_text_source_images': None,
        },
        {
            'has_ava_url': False,
            'has_ava_base_url': False,
            'needs_forwarding': True,
            'error_text': 'error',
            'error_text_source_images': None,
        },
        {
            'has_ava_url': False,
            'has_ava_base_url': False,
            'needs_forwarding': True,
            'error_text': 'error',
            'error_text_source_images': 'error_text_from_source_images_table',
        },
        {
            'has_ava_url': True,
            'has_ava_base_url': False,
            'needs_forwarding': False,
            'error_text': None,
            'error_text_source_images': None,
        },
        {
            'has_ava_url': False,
            'has_ava_base_url': False,
            'needs_forwarding': False,
            'error_text': 'error',
            'error_text_source_images': None,
        },
        {
            'has_ava_url': False,
            'has_ava_base_url': False,
            'needs_forwarding': True,
            'error_text': None,
            'error_text_source_images': None,
        },
        {
            'has_ava_url': False,
            'has_ava_base_url': False,
            'needs_forwarding': False,
            'error_text': None,
            'error_text_source_images': None,
        },
        {
            'has_ava_url': False,
            'has_ava_base_url': False,
            'needs_forwarding': True,
            'error_text': None,
            'error_text_source_images': 'error_text_from_source_images_table',
        },
        {
            'has_ava_url': False,
            'has_ava_base_url': False,
            'needs_forwarding': False,
            'error_text': None,
            'error_text_source_images': 'error_text_from_source_images_table',
        },
    ]


def _generate_image_data(
        url,
        has_ava_url,
        has_ava_base_url,
        client_name,
        needs_forwarding,
        error_text,
        error_text_source_images=None,
):
    md5_hash = hashlib.md5(url.encode()).hexdigest()
    return {
        'client_name': client_name,
        'base_url': url,
        'source_url': f'http://test/src/{url}',
        'ava_url': f'someprefix/{md5_hash}' if has_ava_url else None,
        'ava_base_url': 'somebase' if has_ava_base_url else None,
        'ava_hash': md5_hash if has_ava_url else None,
        'status': 'done' if has_ava_url else 'error',
        'error_text': f'{error_text}: {url}' if error_text else None,
        'error_text_source_images': error_text_source_images,
        'needs_forwarding': needs_forwarding,
    }


def _generate_image_data_with_invalid_url(
        url, client_name, needs_forwarding, error_text_source_images,
):
    return {
        'client_name': client_name,
        'base_url': url,
        'source_url': url,
        'ava_url': None,
        'ava_hash': None,
        'status': 'error',
        'error_text': f'error: {url}',
        'error_text_source_images': error_text_source_images,
        'needs_forwarding': needs_forwarding,
    }


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def _sql_add_clients(pg_cursor, image_data_with_id):
    pg_cursor.execute(
        """
        insert into eats_pics.clients(name)
        values(unnest(%s))
        returning name, id
        """,
        (list({i['client_name'] for i in image_data_with_id}),),
    )
    data = pg_cursor.fetchall()
    return {i['name']: i['id'] for i in data}


def _sql_add_ava_images(pg_cursor, image_data_with_id):
    data = []
    for i in image_data_with_id:
        if not i['ava_url']:
            continue
        pg_cursor.execute(
            """
            insert into eats_pics.ava_images(url, hash, base)
            values(%(ava_url)s,%(ava_hash)s, %(ava_base_url)s)
            returning hash, id
            """,
            i,
        )
        data += pg_cursor.fetchall()
    return {i['hash']: i['id'] for i in data}


def _sql_add_src_images(pg_cursor, image_data_with_id):
    data = []
    image_data_with_id_copy = image_data_with_id.copy()
    for i in image_data_with_id_copy:
        result = re.search(
            '(http|https)://(.+?)/(.+)', i['source_url'], re.IGNORECASE,
        )
        if result:
            i['host'] = result.group(2)
            i['path'] = result.group(3)
            i['is_https'] = result.group(1) == 'https'
        else:
            i['host'] = None
            i['path'] = None
            i['is_https'] = None
    for i in image_data_with_id_copy:
        pg_cursor.execute(
            """
            insert into eats_pics.source_images(
                url,
                host,
                path,
                is_https,
                ava_image_id,
                status,
                error_text)
            values(
                %(source_url)s,
                %(host)s,
                %(path)s,
                %(is_https)s,
                %(ava_id)s,
                %(status)s,
                %(error_text_source_images)s
            )
            returning url, id
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
    return {i['url']: i['id'] for i in data}


def _sql_add_client_images(pg_cursor, image_data_with_id):
    for i in image_data_with_id:
        pg_cursor.execute(
            """
            insert into eats_pics.client_images(
                client_id,
                source_image_id,
                needs_forwarding
            )
            values(%(client_id)s,%(src_id)s,%(needs_forwarding)s)
            """,
            i,
        )


def _sql_add_images(pg_cursor, image_data):
    image_data = copy.deepcopy(image_data)

    client_name_to_id = _sql_add_clients(pg_cursor, image_data)
    for i in image_data:
        i['client_id'] = client_name_to_id[i['client_name']]

    ava_hash_to_id = _sql_add_ava_images(pg_cursor, image_data)
    for i in image_data:
        i['ava_id'] = ava_hash_to_id[i['ava_hash']] if i['ava_hash'] else None

    src_url_to_id = _sql_add_src_images(pg_cursor, image_data)
    for i in image_data:
        i['src_id'] = src_url_to_id[i['source_url']]

    _sql_add_client_images(pg_cursor, image_data)

    return image_data


def _sql_get_forward_status(pg_cursor, image_data_with_id):
    data = {}
    for iii, vvv in enumerate(image_data_with_id):
        pg_cursor.execute(
            """
            select needs_forwarding
            from eats_pics.client_images
            where client_id = %(client_id)s and source_image_id = %(src_id)s
            """,
            vvv,
        )
        ret = pg_cursor.fetchone()
        data[iii] = ret['needs_forwarding']

    return data


def _sort_by_src_url(items):
    return sorted(items, key=lambda i: i['source_url'])
