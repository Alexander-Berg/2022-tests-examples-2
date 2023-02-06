# pylint: disable=too-many-lines
import datetime as dt
import hashlib
import io
import json
import math
import pathlib
import re

import pytest

Path = pathlib.Path

PERIODIC_NAME = 'eats-pics_images-update-periodic'
MOCK_AVATARNICA_PATH = '/avatars-mds/put-eda/'
# this path *is* whitelisted in config.json
MOCK_IMAGES_PATH = '/images/'
# this path *is not* whitelisted in config.json
MOCK_ZORA_IMAGES_PATH = '/zora_images/'
CLIENT_NAME = 'imaclient'


@pytest.mark.no_mds_avatarnica
async def test_upload_content(
        pg_cursor, taxi_eats_pics, testpoint, mockserver, mock_ext_image,
):
    mock_image_path = mock_ext_image.get_prefix()
    img_generator = mock_ext_image.generate_image_binary

    urls_to_request = ['url1', 'url2']
    image_data = [
        _generate_image_data(
            base_url=i,
            binary=img_generator(i),
            url=mockserver.url(f'{mock_image_path}/{i}'),
        )
        for i in urls_to_request
    ]

    def _mock_ava_interrupt(request):
        filename = request.path[len(MOCK_AVATARNICA_PATH) :]
        # filename is a md5 of a binary content
        image_matches = [i for i in image_data if i['md5'] == filename]
        assert len(image_matches) == 1

        image = image_matches[0]

        re_multipart = re.compile(r'^multipart/form-data; boundary=(.*)$')
        match = re_multipart.match(request.headers['content-type'])
        assert match is not None

        boundary = match.group(1)

        body = request.get_data()
        assert (
            _build_multipart_body(boundary, image['binary'], 'image/jpeg')
            == body
        )

    @mockserver.handler(MOCK_AVATARNICA_PATH, prefix=True)
    def _mock_ava(request):
        return _mock_avatarnica_impl(mockserver, request, _mock_ava_interrupt)

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        assert set(hashes) == {i['md5'] for i in image_data}

    _sql_add_source_images(pg_cursor, image_data)

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_hashes_to_upload.has_calls


async def test_hash_already_present(
        pg_cursor, taxi_eats_pics, testpoint, mockserver, mock_ext_image,
):
    """
    Scenario: image present in ava_images, but not linked with
    requested url in source_images.
    Expected result: this image should not be uploaded to ava.
    """

    mock_image_path = mock_ext_image.get_prefix()
    img_generator = mock_ext_image.generate_image_binary

    urls_to_test = ['url1']
    urls_normal = ['url2']
    urls_to_request = urls_to_test + urls_normal

    image_data = [
        _generate_image_data(
            base_url=i,
            binary=img_generator(i),
            url=mockserver.url(f'{mock_image_path}/{i}'),
            ava_url=f'01/0101/{i}',
        )
        for i in urls_to_request
    ]

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        assert set(hashes) == {
            i['md5'] for i in image_data if i['base_url'] in urls_normal
        }

    _sql_add_ava_images(
        pg_cursor, [i for i in image_data if i['base_url'] in urls_to_test],
    )

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_hashes_to_upload.has_calls

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    _verify_forward_status(forward_status, urls_to_request, [])


async def test_not_changed_on_refresh(
        pg_cursor, taxi_eats_pics, testpoint, mockserver, mock_ext_image,
):
    """
    Scenario: image present in ava_images and linked with
    requested url in source_images.
    Expected result: This image should not be uploaded to ava and
    should not be forwarded to client.
    """

    mock_image_path = mock_ext_image.get_prefix()
    img_generator = mock_ext_image.generate_image_binary

    urls_to_test = ['url1']
    urls_normal = ['url2']
    urls_to_request = urls_to_test + urls_normal

    image_data = [
        _generate_image_data(
            base_url=i,
            binary=img_generator(i),
            url=mockserver.url(f'{mock_image_path}/{i}'),
            ava_url=f'01/0101/{i}',
            status='done',
            # Force image refresh
            last_checked_at=dt.datetime.now() - dt.timedelta(days=365),
        )
        for i in urls_to_request
    ]

    @testpoint('eats-pics-processing_upload_images::urls-to-process')
    def task_urls_to_process(urls):
        # Verify that image refresh was triggered
        assert set(urls) == {
            i['url'] for i in image_data if i['base_url'] in urls_to_request
        }

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        assert set(hashes) == {
            i['md5'] for i in image_data if i['base_url'] in urls_normal
        }

    hash_to_ava_id = _sql_add_ava_images(
        pg_cursor, [i for i in image_data if i['base_url'] in urls_to_test],
    )
    for data in image_data:
        hash_value = data['md5']
        if hash_value in hash_to_ava_id:
            data['ava_id'] = hash_to_ava_id[hash_value]

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_urls_to_process.has_calls
    assert task_hashes_to_upload.has_calls

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    # no need to notify client if nothing has changed
    _verify_forward_status(forward_status, urls_normal, urls_to_test)


async def test_error_on_refresh(
        pg_cursor, taxi_eats_pics, testpoint, mockserver, mock_ext_image,
):
    """
    Scenario: image present in ava_images and linked with
    requested url in source_images, and its refreshing failed
    Expected result: Field 'is_check_needed' will be changed to 'false' and
    error should not be forwarded to client
    """

    mock_image_path = mock_ext_image.get_prefix()
    img_generator = mock_ext_image.generate_image_binary

    urls_normal = ['url2']
    urls_to_fail = ['url3']
    urls_to_request = urls_normal + urls_to_fail

    image_data = [
        _generate_image_data(
            base_url=i,
            binary=img_generator(i),
            url=mockserver.url(f'{mock_image_path}/{i}'),
            ava_url=f'01/0101/{i}',
            status='done',
            # Force image refresh
            last_checked_at=dt.datetime.now() - dt.timedelta(days=365),
        )
        for i in urls_to_request
    ]

    @testpoint('eats-pics-processing_upload_images::urls-to-process')
    def task_urls_to_process(urls):
        # Verify that image refresh was triggered
        assert set(urls) == {
            i['url'] for i in image_data if i['base_url'] in urls_to_request
        }

    @mockserver.handler(MOCK_IMAGES_PATH, prefix=True)
    def _mock_images(request):
        url_suffix = request.path[len(MOCK_IMAGES_PATH) :].strip('/\\')

        if request.method in ['HEAD', 'GET']:
            # pylint: disable=no-else-return
            if url_suffix not in urls_to_fail:
                return mockserver.make_response(
                    img_generator(url_suffix), 200, content_type='image/jpeg',
                )
            else:
                return mockserver.make_response(
                    bytearray(b'Some error'), 404, content_type='image/jpeg',
                )
        return mockserver.make_response('Not found or invalid method', 404)

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        assert set(hashes) == {
            i['md5'] for i in image_data if i['base_url'] in urls_normal
        }

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_urls_to_process.has_calls
    assert task_hashes_to_upload.has_calls

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    # no need to notify client if nothing has changed
    _verify_forward_status(forward_status, urls_normal, urls_to_fail)
    is_check_needed_from_db = _sql_get_is_check_needed(pg_cursor)
    _add_base_url_to_statuses(is_check_needed_from_db, id_to_url)
    for status in is_check_needed_from_db:
        base_url = status['base_url']
        assert base_url in urls_to_request
        assert status['is_check_needed'] == (base_url not in urls_to_fail)


async def test_image_supported_content_type(
        pg_cursor, taxi_eats_pics, testpoint, mockserver,
):
    url_data = {'url1': 'jpeg', 'url2': 'png', 'url3': 'webp'}
    urls_to_request = list(url_data.keys())

    img_generator = _img_generator

    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_IMAGES_PATH}/{i}'),
            binary=img_generator(i),
        )
        for i in urls_to_request
    ]

    @mockserver.handler(MOCK_IMAGES_PATH, prefix=True)
    def _mock_images(request):
        url_suffix = request.path[len(MOCK_IMAGES_PATH) :].strip('/\\')
        assert url_suffix in urls_to_request

        if request.method in ['HEAD', 'GET']:
            # pylint: disable=no-else-return
            return mockserver.make_response(
                img_generator(url_suffix),
                200,
                content_type=f'image/{url_data[url_suffix]}',
            )
        return mockserver.make_response('Not found or invalid method', 404)

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        assert set(hashes) == {i['md5'] for i in image_data}

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_hashes_to_upload.has_calls

    images_status = _sql_get_source_image_status(pg_cursor)
    _add_base_url_to_statuses(images_status, id_to_url)
    _verify_source_image_status(images_status, urls_to_request, [], [])

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    _verify_forward_status(forward_status, urls_to_request, [])


async def test_image_wrong_content_type(
        pg_cursor, taxi_eats_pics, testpoint, mockserver,
):
    content_type = 'unknown/unknown'

    urls_to_fail = ['url1']
    urls_normal = ['url2']
    urls_to_request = urls_to_fail + urls_normal

    img_generator = _img_generator

    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_IMAGES_PATH}/{i}'),
            binary=img_generator(i),
        )
        for i in urls_to_request
    ]

    @mockserver.handler(MOCK_IMAGES_PATH, prefix=True)
    def _mock_images(request):
        url_suffix = request.path[len(MOCK_IMAGES_PATH) :].strip('/\\')

        if request.method in ['HEAD', 'GET']:
            # pylint: disable=no-else-return
            if url_suffix not in urls_to_fail:
                return mockserver.make_response(
                    img_generator(url_suffix), 200, content_type='image/jpeg',
                )
            else:
                return mockserver.make_response(
                    bytearray(b'I\'m not an image!'),
                    200,
                    content_type=content_type,
                )
        return mockserver.make_response('Not found or invalid method', 404)

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        assert set(hashes) == {
            i['md5'] for i in image_data if i['base_url'] in urls_normal
        }

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_hashes_to_upload.has_calls

    images_status = _sql_get_source_image_status(pg_cursor)
    _add_base_url_to_statuses(images_status, id_to_url)
    # wrong content type is a non-retryable error
    url_to_error_message = dict(
        {
            'url1': (
                'Source: download-direct, '
                'Error: unsupported `Content-Type`, '
                'Details: status_code: 200, '
                'message: Unsupported `Content-Type`: unknown/unknown'
            ),
        },
    )
    _verify_source_image_status(
        images_status, urls_normal, [], urls_to_fail, url_to_error_message,
    )

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    # non-retryable errors are forwarded immediately
    _verify_forward_status(forward_status, urls_to_request, [])


async def test_image_404(pg_cursor, taxi_eats_pics, testpoint, mockserver):
    urls_to_fail = ['url1']
    urls_normal = ['url2']
    urls_to_request = urls_to_fail + urls_normal

    img_generator = _img_generator

    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_IMAGES_PATH}/{i}'),
            binary=img_generator(i),
        )
        for i in urls_to_request
    ]

    @mockserver.handler(MOCK_IMAGES_PATH, prefix=True)
    def _mock_images(request):
        url_suffix = request.path[len(MOCK_IMAGES_PATH) :].strip('/\\')

        if request.method in ['HEAD', 'GET']:
            # pylint: disable=no-else-return
            if url_suffix not in urls_to_fail:
                return mockserver.make_response(
                    img_generator(url_suffix), 200, content_type='image/jpeg',
                )
            else:
                return mockserver.make_response(
                    bytearray(b'I\'m not an image!'),
                    404,
                    content_type='image/jpeg',
                )
        return mockserver.make_response('Not found or invalid method', 404)

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        assert set(hashes) == {
            i['md5'] for i in image_data if i['base_url'] in urls_normal
        }

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_hashes_to_upload.has_calls

    images_status = _sql_get_source_image_status(pg_cursor)
    _add_base_url_to_statuses(images_status, id_to_url)
    # 404 is a non-retryable error
    url_to_error_message = dict(
        {
            'url1': (
                'Source: download-direct, Error: 404: object not found, '
                'Details: status_code: 404, message: '
            ),
        },
    )
    _verify_source_image_status(
        images_status, urls_normal, [], urls_to_fail, url_to_error_message,
    )

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    # non-retryable errors are forwarded immediately
    _verify_forward_status(forward_status, urls_to_request, [])


async def test_image_too_big(
        pg_cursor, taxi_eats_pics, taxi_config, testpoint, mockserver,
):
    max_image_size = 1000

    update_config = taxi_config.get('EATS_PICS_UPDATE_SETTINGS')
    update_config.update({'maximum_image_size_in_bytes': max_image_size})
    taxi_config.set(EATS_PICS_UPDATE_SETTINGS=update_config)

    url_normal = 'url1'
    url_too_big = 'url2'
    urls_to_request = [url_normal, url_too_big]

    img_generator = _img_generator

    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_IMAGES_PATH}/{i}'),
            binary=img_generator(i),
        )
        for i in urls_to_request
    ]

    for i in image_data:
        base_url = i['base_url']
        if base_url == url_normal:
            i['binary'] = i['binary'].zfill(max_image_size - 1)
        elif base_url == url_too_big:
            i['binary'] = i['binary'].zfill(max_image_size + 1)
        i['md5'] = hashlib.md5(i['binary']).hexdigest()

    @mockserver.handler(MOCK_IMAGES_PATH, prefix=True)
    def _mock_images(request):
        url_suffix = request.path[len(MOCK_IMAGES_PATH) :].strip('/\\')

        if request.method in ['HEAD', 'GET']:
            # pylint: disable=no-else-return
            if url_suffix == url_normal:
                return mockserver.make_response(
                    img_generator(url_suffix).zfill(max_image_size - 1),
                    200,
                    content_type='image/jpeg',
                )
            elif url_suffix == url_too_big:
                return mockserver.make_response(
                    img_generator(url_suffix).zfill(max_image_size + 1),
                    200,
                    content_type='image/jpeg',
                )
        return mockserver.make_response('Not found or invalid method', 404)

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        assert set(hashes) == {
            i['md5'] for i in image_data if i['base_url'] == url_normal
        }

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_hashes_to_upload.has_calls

    images_status = _sql_get_source_image_status(pg_cursor)
    _add_base_url_to_statuses(images_status, id_to_url)
    # `image size is too big` is a non-retryable error
    url_to_error_message = dict(
        {
            'url2': (
                'Source: download-direct, '
                'Error: image too big, '
                'Details: Image is too big: 1001 bytes'
            ),
        },
    )
    _verify_source_image_status(
        images_status, [url_normal], [], [url_too_big], url_to_error_message,
    )

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    _verify_forward_status(forward_status, [url_normal, url_too_big], [])


@pytest.mark.skip(reason='zora is disabled for now')
async def test_download_zora(
        pg_cursor, taxi_eats_pics, testpoint, mockserver, mock_ext_image,
):
    zora_http_urls = ['url1', 'url2']
    zora_https_urls = ['url3']
    zora_urls = zora_http_urls + zora_https_urls
    passthrough_urls = ['url4']
    all_urls = zora_urls + passthrough_urls

    img_generator = _img_generator
    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_ZORA_IMAGES_PATH}/{i}'),
            binary=img_generator(i),
        )
        for i in zora_http_urls
    ]
    image_data += [
        _generate_image_data(
            base_url=i,
            url='https://'
            + mockserver.url(f'{MOCK_ZORA_IMAGES_PATH}/{i}')[len('http://') :],
            binary=img_generator(i),
        )
        for i in zora_https_urls
    ]

    img_generator = mock_ext_image.generate_image_binary
    image_data += [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_IMAGES_PATH}/{i}'),
            binary=img_generator(i),
        )
        for i in passthrough_urls
    ]

    @testpoint('eats-pics-processing_upload_images::urls-to-download')
    def task_urls_to_download(urls):
        assert set(urls) == {i['url'] for i in image_data}

    @testpoint('eats-pics-processing_upload_images::set-dummy-zora-proxy')
    def task_set_dummy_zora_proxy(param):
        return {'should_substitute': True}

    @mockserver.handler(MOCK_ZORA_IMAGES_PATH, prefix=True)
    def _mock_images(request):
        url_suffix = request.path[len(MOCK_ZORA_IMAGES_PATH) :].strip('/\\')

        assert url_suffix in zora_urls

        if request.method in ['HEAD', 'GET']:
            return mockserver.make_response(
                img_generator(url_suffix), 200, content_type='image/jpeg',
            )
        return mockserver.make_response('Not found or invalid method', 404)

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        assert set(hashes) == {
            i['md5'] for i in image_data if i['base_url'] in all_urls
        }

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_urls_to_download.has_calls
    assert task_hashes_to_upload.has_calls
    assert task_set_dummy_zora_proxy.times_called >= len(zora_urls)

    images_status = _sql_get_source_image_status(pg_cursor)
    _add_base_url_to_statuses(images_status, id_to_url)
    _verify_source_image_status(images_status, all_urls, [], [])

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    _verify_forward_status(forward_status, all_urls, [])


async def test_download_direct_external(
        pg_cursor,
        taxi_eats_pics,
        taxi_config,
        testpoint,
        mockserver,
        mock_ext_image,
):
    parallel_downloads_limit = 3
    updated_config = taxi_config.get('EATS_PICS_UPDATE_SETTINGS')
    updated_config.update(
        {'parallel_downloads_limit': parallel_downloads_limit},
    )
    taxi_config.set(EATS_PICS_UPDATE_SETTINGS=updated_config)

    external_http_urls = ['url1', 'url2']
    external_https_urls = ['url3']
    external_urls = external_http_urls + external_https_urls
    passthrough_urls = ['url4']
    all_urls = external_urls + passthrough_urls

    img_generator = _img_generator
    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_ZORA_IMAGES_PATH}/{i}'),
            binary=img_generator(i),
        )
        for i in external_http_urls
    ]
    image_data += [
        _generate_image_data(
            base_url=i,
            url='https://'
            + mockserver.url(f'{MOCK_ZORA_IMAGES_PATH}/{i}')[len('http://') :],
            binary=img_generator(i),
        )
        for i in external_https_urls
    ]

    img_generator = mock_ext_image.generate_image_binary
    image_data += [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_IMAGES_PATH}/{i}'),
            binary=img_generator(i),
        )
        for i in passthrough_urls
    ]

    @testpoint('eats-pics-processing_upload_images::urls-to-download')
    def task_urls_to_download(urls):
        assert set(urls) == {i['url'] for i in image_data}

    @testpoint('eats-pics-processing_upload_images::use-http-for-external')
    def task_use_http_for_external(param):
        return {'should_substitute': True}

    @testpoint('eats-pics-processing_upload_images::check-async-tasks-number')
    def check_async_tasks_number(number):
        assert number == parallel_downloads_limit

    @testpoint(
        'eats-pics-processing_upload_images::check-remaining-async-tasks-number',  # noqa: E501
    )
    def check_remaining_tasks_number(number):
        assert number == len(all_urls) % parallel_downloads_limit

    @mockserver.handler(MOCK_ZORA_IMAGES_PATH, prefix=True)
    def _mock_images(request):
        url_suffix = request.path[len(MOCK_ZORA_IMAGES_PATH) :].strip('/\\')

        assert url_suffix in external_urls

        if request.method in ['HEAD', 'GET']:
            return mockserver.make_response(
                img_generator(url_suffix), 200, content_type='image/jpeg',
            )
        return mockserver.make_response('Not found or invalid method', 404)

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        assert set(hashes) == {
            i['md5'] for i in image_data if i['base_url'] in all_urls
        }

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_urls_to_download.has_calls
    assert task_hashes_to_upload.has_calls
    assert task_use_http_for_external.times_called >= len(external_urls)
    assert check_async_tasks_number.has_calls
    assert check_remaining_tasks_number.has_calls

    images_status = _sql_get_source_image_status(pg_cursor)
    _add_base_url_to_statuses(images_status, id_to_url)
    _verify_source_image_status(images_status, all_urls, [], [])

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    _verify_forward_status(forward_status, all_urls, [])


async def test_download_error_direct(
        pg_cursor, taxi_eats_pics, testpoint, mockserver,
):
    urls_to_fail = ['url1']
    urls_normal = ['url2']
    urls_to_request = urls_to_fail + urls_normal

    img_generator = _img_generator

    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_IMAGES_PATH}/{i}'),
            binary=img_generator(i),
        )
        for i in urls_to_request
    ]

    @mockserver.handler(MOCK_IMAGES_PATH, prefix=True)
    def _mock_images(request):
        url_suffix = request.path[len(MOCK_IMAGES_PATH) :].strip('/\\')

        if request.method in ['HEAD', 'GET']:
            # pylint: disable=no-else-return
            if url_suffix not in urls_to_fail:
                return mockserver.make_response(
                    img_generator(url_suffix), 200, content_type='image/jpeg',
                )
            else:
                return mockserver.make_response(
                    'Have a free serving of errors!', 401,
                )
        return mockserver.make_response('Not found or invalid method', 404)

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        assert set(hashes) == {
            i['md5'] for i in image_data if i['base_url'] in urls_normal
        }

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_hashes_to_upload.has_calls

    images_status = _sql_get_source_image_status(pg_cursor)
    _add_base_url_to_statuses(images_status, id_to_url)
    url_to_error_message = dict(
        {
            'url1': (
                'Source: download-direct, '
                'Error: response validation failed, '
                'Details: status_code: 401, '
                'message: Raise for status exception, code = 401'
            ),
        },
    )
    _verify_source_image_status(
        images_status, urls_normal, urls_to_fail, [], url_to_error_message,
    )

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    _verify_forward_status(forward_status, urls_normal, urls_to_fail)


@pytest.mark.skip(reason='zora is disabled for now')
# Remove `test_download_error_direct_external` below
# after reenabling this test
async def test_download_error_zora(
        pg_cursor, taxi_eats_pics, testpoint, mockserver, mock_ext_image,
):
    urls_to_fail = ['url1']
    urls_normal = ['url2']
    urls_to_request = urls_to_fail + urls_normal

    img_generator = _img_generator

    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_ZORA_IMAGES_PATH}/{i}'),
            binary=img_generator(i),
        )
        for i in urls_to_request
    ]

    @testpoint('eats-pics-processing_upload_images::set-dummy-zora-proxy')
    def task_set_dummy_zora_proxy(param):
        return {'should_substitute': True}

    @mockserver.handler(MOCK_ZORA_IMAGES_PATH, prefix=True)
    def _mock_images(request):
        url_suffix = request.path[len(MOCK_ZORA_IMAGES_PATH) :].strip('/\\')

        if request.method in ['HEAD', 'GET']:
            # pylint: disable=no-else-return
            if url_suffix not in urls_to_fail:
                return mockserver.make_response(
                    img_generator(url_suffix), 200, content_type='image/jpeg',
                )
            else:
                return mockserver.make_response(
                    'Have a free serving of errors!', 401,
                )
        return mockserver.make_response('Not found or invalid method', 404)

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        assert set(hashes) == {
            i['md5'] for i in image_data if i['base_url'] in urls_normal
        }

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_hashes_to_upload.has_calls
    assert task_set_dummy_zora_proxy.has_calls

    images_status = _sql_get_source_image_status(pg_cursor)
    _add_base_url_to_statuses(images_status, id_to_url)
    _verify_source_image_status(images_status, urls_normal, urls_to_fail, [])

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    _verify_forward_status(forward_status, urls_normal, urls_to_fail)


# TODO: remove once zora is reenabled
async def test_download_error_direct_external(
        pg_cursor, taxi_eats_pics, testpoint, mockserver, mock_ext_image,
):
    urls_to_fail = ['url1']
    urls_normal = ['url2']
    urls_to_request = urls_to_fail + urls_normal

    img_generator = _img_generator

    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_ZORA_IMAGES_PATH}/{i}'),
            binary=img_generator(i),
        )
        for i in urls_to_request
    ]

    @mockserver.handler(MOCK_ZORA_IMAGES_PATH, prefix=True)
    def _mock_images(request):
        url_suffix = request.path[len(MOCK_ZORA_IMAGES_PATH) :].strip('/\\')

        if request.method in ['HEAD', 'GET']:
            # pylint: disable=no-else-return
            if url_suffix not in urls_to_fail:
                return mockserver.make_response(
                    img_generator(url_suffix), 200, content_type='image/jpeg',
                )
            else:
                return mockserver.make_response(
                    'Have a free serving of errors!', 401,
                )
        return mockserver.make_response('Not found or invalid method', 404)

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        assert set(hashes) == {
            i['md5'] for i in image_data if i['base_url'] in urls_normal
        }

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_hashes_to_upload.has_calls

    images_status = _sql_get_source_image_status(pg_cursor)
    _add_base_url_to_statuses(images_status, id_to_url)
    url_to_error_message = dict(
        {
            'url1': (
                'Source: download-external, '
                'Error: response validation failed, '
                'Details: status_code: 401, '
                'message: Raise for status exception, code = 401'
            ),
        },
    )
    _verify_source_image_status(
        images_status, urls_normal, urls_to_fail, [], url_to_error_message,
    )

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    _verify_forward_status(forward_status, urls_normal, urls_to_fail)


async def test_ava_url_passthrough(
        pg_cursor, component_config, taxi_eats_pics, testpoint, mock_ext_image,
):
    ava_base_url = component_config.get(
        'pics-service-settings', 'ava_base_url',
    )
    additional_ava_base_urls = component_config.get(
        'pics-service-settings', 'additional_ava_base_urls',
    )
    ava_base_urls = [ava_base_url, *additional_ava_base_urls]
    assert ava_base_urls

    http_urls = [
        f'{hashlib.md5(str(i).encode()).hexdigest()}'
        for i, v in enumerate(ava_base_urls)
    ]
    https_urls = [
        f'{hashlib.md5(str(i).encode()).hexdigest()}'
        for i, v in enumerate(ava_base_urls, start=len(http_urls))
    ]
    urls_to_request = http_urls + https_urls

    image_data = [
        _generate_image_data(
            base_url=v, url=f'http://{ava_base_urls[i]}/get-eda/{i}/{v}/orig',
        )
        for i, v in enumerate(http_urls)
    ]
    image_data += [
        _generate_image_data(
            base_url=v,
            url=f'https://{ava_base_urls[i]}/get-eda/'
            + f'{i + len(http_urls)}/{v}/orig',
        )
        for i, v in enumerate(https_urls)
    ]

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        pass

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    # urls with proper ava base should not be uploaded
    assert not task_hashes_to_upload.has_calls

    images_status = _sql_get_source_image_status(pg_cursor)
    _add_base_url_to_statuses(images_status, id_to_url)
    _verify_source_image_status(images_status, urls_to_request, [], [])

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    _verify_forward_status(forward_status, urls_to_request, [])
    hash_to_ava_base_urls = _sql_get_hash_to_ava_base_urls_from_db(pg_cursor)
    for image in image_data:
        image_hash = image['base_url']
        if image['host'] == ava_base_url:
            assert hash_to_ava_base_urls[image_hash] is None
        else:
            assert (
                hash_to_ava_base_urls[image_hash] in additional_ava_base_urls
            )


async def test_ava_url_wrong_naming_reupload(
        pg_cursor, component_config, taxi_eats_pics, testpoint, mock_ext_image,
):
    ava_base_urls = (
        [component_config.get('pics-service-settings', 'ava_base_url')]
        + component_config.get(
            'pics-service-settings', 'additional_ava_base_urls',
        )
    )

    urls_to_request = [f'url{i}' for i, v in enumerate(ava_base_urls)]

    image_data = [
        _generate_image_data(
            base_url=v,
            url=f'http://{ava_base_urls[i]}/get-bucket/{i}/{i}/{v}',
        )
        for i, v in enumerate(urls_to_request)
    ]

    @testpoint('eats-pics-processing_upload_images::urls-to-download')
    def task_urls_to_download(urls):
        assert set(urls) == {i['url'] for i in image_data}

    @testpoint('eats-pics-processing_upload_images::download-abort')
    def task_download_abort(param):
        # Have to abort here to avoid forced service crash
        # caused by the unsupported mock url prefix
        return {'inject_failure': True}

    _sql_add_source_images(pg_cursor, image_data)

    try:
        await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
        assert False, 'Periodic task should\'ve failed'
    except taxi_eats_pics.PeriodicTaskFailed:
        # urls with correct ava base,
        # but wrong naming scheme should be reuploaded
        assert task_urls_to_download.has_calls
        assert task_download_abort.has_calls


async def test_url_whitelist_regexp(
        pg_cursor,
        taxi_eats_pics,
        testpoint,
        mockserver,
        mock_ext_image,
        taxi_config,
):
    custom_prefix = 'my_custom_prefix'
    base_url_no_schema = mockserver.base_url[len('http://') :].strip('/\\')
    full_prefix = f'{base_url_no_schema}/{custom_prefix}'

    taxi_config.set(
        EATS_PICS_UPDATE_SETTINGS={
            'url_whitelist': [
                {'str': f'.*/+{custom_prefix}/+.*', 'is_regexp': True},
            ],
            'supported_image_types': ['image/png', 'image/jpeg', 'image/webp'],
        },
    )

    img_generator = _img_generator

    http_urls = ['url1', 'url2']
    https_urls = ['url3', 'url4']
    urls_to_request = http_urls + https_urls

    image_data = [
        _generate_image_data(base_url=v, url=f'http://{full_prefix}/{i}')
        for i, v in enumerate(http_urls)
    ]
    image_data += [
        _generate_image_data(base_url=v, url=f'https://{full_prefix}/{i}')
        for i, v in enumerate(https_urls, start=len(image_data))
    ]

    @mockserver.handler(custom_prefix, prefix=True)
    def _mock_images(request):
        url_suffix = request.path[len(custom_prefix) :].strip('/\\')

        if request.method in ['HEAD', 'GET']:
            return mockserver.make_response(
                img_generator(url_suffix), 200, content_type='image/jpeg',
            )
        return mockserver.make_response('Not found or invalid method', 404)

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        pass

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_hashes_to_upload.has_calls

    images_status = _sql_get_source_image_status(pg_cursor)
    _add_base_url_to_statuses(images_status, id_to_url)
    _verify_source_image_status(images_status, urls_to_request, [], [])

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    _verify_forward_status(forward_status, urls_to_request, [])


async def test_url_whitelist_prefix(
        pg_cursor,
        load_yaml,
        testsuite_build_dir,
        taxi_eats_pics,
        testpoint,
        mockserver,
        mock_ext_image,
        taxi_config,
):
    short_prefix = 'my_custom_prefix'
    base_url_no_schema = mockserver.base_url[len('http://') :].strip('/\\')
    full_prefix = f'{base_url_no_schema}/{short_prefix}'

    taxi_config.set(
        EATS_PICS_UPDATE_SETTINGS={
            'url_whitelist': [{'str': f'{full_prefix}', 'is_regexp': False}],
            'supported_image_types': ['image/png', 'image/jpeg', 'image/webp'],
        },
    )

    img_generator = _img_generator

    http_urls = ['url1', 'url2']
    https_urls = ['url3', 'url4']
    urls_to_request = http_urls + https_urls

    image_data = [
        _generate_image_data(base_url=v, url=f'http://{full_prefix}/{i}')
        for i, v in enumerate(http_urls)
    ]
    image_data += [
        _generate_image_data(base_url=v, url=f'https://{full_prefix}/{i}')
        for i, v in enumerate(https_urls, start=len(image_data))
    ]

    @mockserver.handler(short_prefix, prefix=True)
    def _mock_images(request):
        url_suffix = request.path[len(short_prefix) :].strip('/\\')

        if request.method in ['HEAD', 'GET']:
            return mockserver.make_response(
                img_generator(url_suffix), 200, content_type='image/jpeg',
            )
        return mockserver.make_response('Not found or invalid method', 404)

    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(hashes):
        pass

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)
    assert task_hashes_to_upload.has_calls

    images_status = _sql_get_source_image_status(pg_cursor)
    _add_base_url_to_statuses(images_status, id_to_url)
    _verify_source_image_status(images_status, urls_to_request, [], [])

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    _verify_forward_status(forward_status, urls_to_request, [])


@pytest.mark.no_mds_avatarnica
async def test_upload_fail(
        pg_cursor, taxi_eats_pics, mockserver, mock_ext_image,
):
    img_generator = mock_ext_image.generate_image_binary

    urls_to_fail = ['url1']
    urls_normal = ['url2']
    urls_to_request = urls_to_fail + urls_normal

    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_IMAGES_PATH}/{i}'),
            binary=img_generator(i),
        )
        for i in urls_to_request
    ]

    def _mock_ava_interrupt(request):
        filename = request.path[len(MOCK_AVATARNICA_PATH) :]
        # filename is a md5 of a binary content
        image_matches = [i for i in image_data if i['md5'] == filename]
        assert len(image_matches) == 1

        image = image_matches[0]

        # pylint: disable=no-else-return
        if image['base_url'] in urls_to_fail:
            return mockserver.make_response(
                'Have a free serving of errors!', 401,
            )
        else:
            return None

    @mockserver.handler(MOCK_AVATARNICA_PATH, prefix=True)
    def _mock_ava(request):
        return _mock_avatarnica_impl(mockserver, request, _mock_ava_interrupt)

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)

    images_status = _sql_get_source_image_status(pg_cursor)
    _add_base_url_to_statuses(images_status, id_to_url)
    url_to_error_message = dict(
        {
            'url1': (
                'Source: upload, '
                'Error: upload to avatarnica failed, '
                'Details: Error in \'POST /put-namespace/imagename\': '
                'Parse error at pos 0, path \'\': Invalid value.'
            ),
        },
    )
    _verify_source_image_status(
        images_status, urls_normal, urls_to_fail, [], url_to_error_message,
    )

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    _verify_forward_status(forward_status, urls_normal, urls_to_fail)


async def test_upload_exists_in_ava(
        pg_cursor, taxi_eats_pics, mockserver, mock_ext_image,
):
    img_generator = mock_ext_image.generate_image_binary

    urls_to_exist = ['url1']
    urls_normal = ['url2']
    urls_to_request = urls_to_exist + urls_normal

    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_IMAGES_PATH}/{i}'),
            binary=img_generator(i),
        )
        for i in urls_to_request
    ]

    def _mock_ava_interrupt(request):
        filename = request.path[len(MOCK_AVATARNICA_PATH) :]

        # filename is a md5 of a binary content
        image_matches = [i for i in image_data if i['md5'] == filename]
        assert len(image_matches) == 1

        image = image_matches[0]

        # remove extension from filename
        image_id = str(Path(filename).stem)
        group_id = ord(image['md5'][0]) * 10 + ord(image['md5'][1])

        # pylint: disable=no-else-return
        if image['base_url'] in urls_to_exist:
            error_response = {
                'attrs': {'group-id': group_id, 'imagename': image_id},
                'description': 'update is prohibited',
                'status': 'error',
            }
            return mockserver.make_response(json=error_response, status=403)
        else:
            return None

    @mockserver.handler(MOCK_AVATARNICA_PATH, prefix=True)
    def _mock_ava(request):
        return _mock_avatarnica_impl(mockserver, request, _mock_ava_interrupt)

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)

    images_status = _sql_get_source_image_status(pg_cursor)
    _add_base_url_to_statuses(images_status, id_to_url)
    _verify_source_image_status(images_status, urls_to_request, [], [])

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    _verify_forward_status(forward_status, urls_to_request, [])


async def test_try_to_upload_ava_image(
        pg_cursor,
        taxi_eats_pics,
        mockserver,
        component_config,
        testpoint,
        mock_ext_image,
):
    @testpoint('eats-pics-processing_upload_images::hashes-to-upload')
    def task_hashes_to_upload(arg):
        pass

    @testpoint('force_leave_single_ava_base_url')
    def leave_single_ava_base_url(arg):  # pylint: disable=unused-variable
        return {'leave_single_ava_base_url': True}

    ava_base_urls = [
        component_config.get('pics-service-settings', 'ava_base_url'),
    ]
    http_urls = [
        f'{hashlib.md5(str(i).encode()).hexdigest()}'
        for i, v in enumerate(ava_base_urls)
    ]
    image_data = [
        _generate_image_data(
            base_url=i, url=f'http://{ava_base_urls[i]}/get-eda/{i}/{v}/orig',
        )
        for i, v in enumerate(http_urls)
    ]

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)

    assert task_hashes_to_upload.times_called == 0


async def test_retry_on_error(
        pg_cursor, taxi_eats_pics, testpoint, mockserver, taxi_config,
):
    retry_initial_delay = 10
    retry_delay_factor = 3
    retry_max_delay = 100
    retry_rand_interval_percent = 50

    update_config = taxi_config.get('EATS_PICS_UPDATE_SETTINGS')
    update_config.update(
        {
            'error_retry_initial_delay_in_seconds': retry_initial_delay,
            'error_retry_delay_factor': retry_delay_factor,
            'error_retry_max_delay_in_seconds': retry_max_delay,
            'error_retry_random_interval_in_percent': (
                retry_rand_interval_percent
            ),
        },
    )
    taxi_config.set(EATS_PICS_UPDATE_SETTINGS=update_config)

    url_initial_retry = 'url1'
    url_second_retry = 'url2'
    url_exceeded_retry = 'url3'
    url_no_retry_after_error = 'url4'
    url_no_retry_after_new = 'url5'

    urls = [
        url_initial_retry,
        url_second_retry,
        url_exceeded_retry,
        url_no_retry_after_error,
        url_no_retry_after_new,
    ]

    img_generator = _img_generator

    image_data = [
        _generate_image_data(
            base_url=i,
            url=mockserver.url(f'{MOCK_IMAGES_PATH}/{i}'),
            binary=img_generator(i),
        )
        for i in urls
    ]

    for i in image_data:
        base_url = i['base_url']
        if base_url == url_initial_retry:
            i['status'] = 'new'
        elif base_url == url_second_retry:
            i['status'] = 'error'
            i['error_text'] = 'error'
            i['retry_delay'] = f'\'{retry_initial_delay} seconds\''
            i['retry_at'] = dt.datetime.now() - dt.timedelta(seconds=30)
        elif base_url == url_exceeded_retry:
            i['status'] = 'error'
            i['error_text'] = 'error'
            delay = math.floor(retry_max_delay / (0.66 * retry_delay_factor))
            i['retry_delay'] = f'\'{delay} seconds\''
            i['retry_at'] = dt.datetime.now() - dt.timedelta(seconds=30)
        elif base_url == url_no_retry_after_error:
            i['status'] = 'error'
            i['error_text'] = 'error'
            i['retry_delay'] = f'\'{retry_initial_delay} seconds\''
            i['retry_at'] = dt.datetime.now() - dt.timedelta(seconds=30)
        elif base_url == url_no_retry_after_new:
            i['status'] = 'new'

    @mockserver.handler(MOCK_IMAGES_PATH, prefix=True)
    def _mock_images(request):
        url_suffix = request.path[len(MOCK_IMAGES_PATH) :].strip('/\\')

        if request.method in ['HEAD', 'GET']:
            # pylint: disable=no-else-return
            if url_suffix in [
                    url_no_retry_after_error,
                    url_no_retry_after_new,
            ]:
                # invalid content-type is a non-retryable error
                return mockserver.make_response(
                    img_generator(url_suffix),
                    200,
                    content_type='invalid/content_type',
                )
            else:
                return mockserver.make_response(
                    'Have a free serving of errors!', 401,
                )
        return mockserver.make_response('Not found or invalid method', 404)

    def validate_retry_delay(delay_to_verify, expected_delay_base):
        new_delay_adjust_value = expected_delay_base * (
            retry_rand_interval_percent / 100.0
        )
        assert (
            expected_delay_base - new_delay_adjust_value
            <= delay_to_verify
            <= expected_delay_base + new_delay_adjust_value
        )

    def validate_retry_at(retry_at_to_vetify, expected_delay_base):
        new_delay_adjust_value = expected_delay_base * (
            retry_rand_interval_percent / 100.0
        )
        assert (
            dt.datetime.now() + expected_delay_base - new_delay_adjust_value
            <= retry_at_to_vetify
            <= dt.datetime.now() + expected_delay_base + new_delay_adjust_value
        )

    client_id = _sql_add_client(pg_cursor, CLIENT_NAME)
    id_to_url = _sql_add_source_images(pg_cursor, image_data)
    _sql_add_client_images(pg_cursor, client_id, list(id_to_url.keys()))

    await taxi_eats_pics.run_periodic_task(PERIODIC_NAME)

    images_status = _sql_get_source_image_status(pg_cursor)
    _add_base_url_to_statuses(images_status, id_to_url)
    for status in images_status:
        base_url = status['base_url']
        assert status['status'] == 'error'
        assert status['error_text']
        if base_url == url_initial_retry:
            new_delay = dt.timedelta(seconds=retry_initial_delay)
            validate_retry_delay(status['retry_delay'], new_delay)
            validate_retry_at(status['retry_at'], new_delay)
        elif base_url == url_second_retry:
            new_delay = dt.timedelta(
                seconds=retry_initial_delay * retry_delay_factor,
            )
            validate_retry_delay(status['retry_delay'], new_delay)
            validate_retry_at(status['retry_at'], new_delay)
        elif base_url in [
            url_exceeded_retry,
            url_no_retry_after_error,
            url_no_retry_after_new,
        ]:
            assert status['retry_delay'] is None
            assert status['retry_at'] is None

    forward_status = _sql_get_forward_status(
        pg_cursor, client_id, list(id_to_url.keys()),
    )
    _add_base_url_to_fwd_statuses(forward_status, id_to_url)
    # retryable errors should not be forwarded
    _verify_forward_status(
        forward_status,
        [url_exceeded_retry, url_no_retry_after_error, url_no_retry_after_new],
        [url_initial_retry, url_second_retry],
    )


def _build_multipart_body(boundary, content, content_type):
    fp = io.BytesIO()
    fp.write(bytes(f'--{boundary}\r\n', 'ascii'))
    fp.write(
        b'Content-Disposition: form-data; name="file"; '
        b'filename="image"\r\n'
        b'Content-Type: %b\r\n\r\n' % content_type.encode('utf8'),
    )
    fp.write(content)
    fp.write(bytes(f'\r\n--{boundary}\r\n', 'ascii'))
    return fp.getvalue()


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
        is_check_needed=True,
        last_checked_at=None,
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
        'is_check_needed': is_check_needed,
        'last_checked_at': last_checked_at or dt.datetime.now(),
        'binary': binary,
        'md5': hashlib.md5(binary).hexdigest(),
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
                last_checked_at,
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
                %(last_checked_at)s,
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


def _sql_get_is_check_needed(pg_cursor):
    pg_cursor.execute(
        """
        select id, is_check_needed
        from eats_pics.source_images""",
    )
    return [
        {'id': i['id'], 'is_check_needed': i['is_check_needed']}
        for i in pg_cursor.fetchall()
    ]


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


def _sql_add_client_images(pg_cursor, client_id, source_image_ids):
    pg_cursor.execute(
        """
        insert into eats_pics.client_images(client_id, source_image_id)
        values (%s, unnest(%s))
        """,
        (client_id, source_image_ids),
    )


def _mock_avatarnica_impl(mockserver, request, interrupt_fn):
    # copied from plugins/mock_avatarnica.py

    if request.method != 'POST':
        return mockserver.make_response('Not found or invalid method', 404)

    interrupt_response = interrupt_fn(request)
    if interrupt_response is not None:
        return interrupt_response

    md5 = hashlib.md5(request.get_data()).hexdigest()
    # remove extension from filename
    image_id = str(Path(request.path[len(MOCK_AVATARNICA_PATH) :]).stem)

    group_id = ord(md5[0]) * 10 + ord(md5[1])

    response = {
        'imagename': image_id,
        'group-id': group_id,
        'meta': {'orig-format': 'JPEG'},
        'sizes': {
            'orig': {
                'height': 640,
                'path': f'/get-eda/{group_id}/{image_id}/orig',
                'width': 1024,
            },
            'sizename': {
                'height': 200,
                'path': f'/get-eda/{group_id}/{image_id}/sizename',
                'width': 200,
            },
        },
    }

    return mockserver.make_response(json.dumps(response), 200)


def _add_base_url_to_statuses(images_status, id_to_base_url):
    for status in images_status:
        status['base_url'] = id_to_base_url[status['id']]


def _verify_source_image_status(
        images_status,
        urls_to_succeed,
        urls_to_retryable_fail,
        urls_to_nonretryable_fail,
        urls_to_error_message=None,
):
    assert (
        len(urls_to_retryable_fail) + len(urls_to_nonretryable_fail) == 0
    ) or (urls_to_error_message is not None)
    assert len(images_status) == (
        len(urls_to_succeed)
        + len(urls_to_retryable_fail)
        + len(urls_to_nonretryable_fail)
    )
    for status in images_status:
        base_url = status['base_url']
        assert (
            base_url
            in urls_to_succeed
            + urls_to_retryable_fail
            + urls_to_nonretryable_fail
        )
        if base_url in urls_to_retryable_fail + urls_to_nonretryable_fail:
            assert status['status'] == 'error'
            if (
                    urls_to_error_message is not None
                    and base_url in urls_to_error_message
            ):
                assert status['error_text'] == urls_to_error_message[base_url]
            if base_url in urls_to_nonretryable_fail:
                assert status['retry_delay'] is None
                assert status['retry_at'] is None
            else:
                assert status['retry_delay'] is not None
                assert status['retry_at'] is not None
        else:
            assert_text = (
                status['error_text'] if status['error_text'] else '<none>'
            )
            assert status['status'] == 'done', f'error_text: {assert_text}'

            assert not status['error_text']


def _sql_get_forward_status(pg_cursor, client_id, src_image_ids):
    pg_cursor.execute(
        """
        select source_image_id, needs_forwarding
        from eats_pics.client_images
        where client_id=%s and source_image_id = any(%s)
        """,
        (client_id, src_image_ids),
    )
    return [
        {
            'source_image_id': i['source_image_id'],
            'needs_forwarding': i['needs_forwarding'],
        }
        for i in pg_cursor.fetchall()
    ]


def _sql_get_hash_to_ava_base_urls_from_db(pg_cursor):
    pg_cursor.execute(
        """
        select hash, base
        from eats_pics.ava_images
        """,
    )
    return {i['hash']: i['base'] for i in pg_cursor.fetchall()}


def _add_base_url_to_fwd_statuses(fwd_status, id_to_base_url):
    for status in fwd_status:
        status['base_url'] = id_to_base_url[status['source_image_id']]


def _verify_forward_status(fwd_status, urls_to_fwd, urls_to_not_fwd):
    assert len(fwd_status) == (len(urls_to_fwd) + len(urls_to_not_fwd))
    for status in fwd_status:
        base_url = status['base_url']
        assert base_url in urls_to_fwd + urls_to_not_fwd
        if base_url in urls_to_fwd:
            assert status['needs_forwarding']
        elif base_url in urls_to_not_fwd:
            assert not status['needs_forwarding']


def _img_generator(url):
    return bytearray(b'I\'m an image! My url is %a' % url)
