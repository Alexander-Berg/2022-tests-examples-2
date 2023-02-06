import pytest


@pytest.mark.experiments3(filename='exp3_enabled.json')
async def test_getimage_no_args(taxi_inapp_communications):
    response = await taxi_inapp_communications.get('3.0/getimage', {})
    assert response.status_code == 400


@pytest.mark.experiments3(filename='exp3_enabled.json')
async def test_getimage_only_tag(taxi_inapp_communications):
    response = await taxi_inapp_communications.get('3.0/getimage?tag=tag', {})
    assert response.status_code == 400
    assert response.json()['message'] == 'Set size_hint param or width header'


@pytest.mark.experiments3(filename='exp3_enabled.json')
async def test_getimage_only_size_arg(taxi_inapp_communications):
    response = await taxi_inapp_communications.get('3.0/getimage?size_hint=1')
    assert response.status_code == 400


@pytest.mark.experiments3(filename='exp3_enabled.json')
async def test_getimage_only_width_header(taxi_inapp_communications):
    response = await taxi_inapp_communications.get(
        '3.0/getimage', headers={'width': '100'},
    )
    assert response.status_code == 400


@pytest.mark.experiments3(filename='exp3_enabled.json')
async def test_getimage_404_hint_arg(taxi_inapp_communications):
    response = await taxi_inapp_communications.get(
        '3.0/getimage?tag=unknown&size_hint=100',
    )
    assert response.status_code == 404
    assert response.headers['Cache-Control'] == 'no-store'


@pytest.mark.experiments3(filename='exp3_enabled.json')
async def test_getimage_bad_hint_arg(taxi_inapp_communications):
    response = await taxi_inapp_communications.get(
        '3.0/getimage?tag=unknown&size_hint=aaa',
    )
    assert response.status_code == 400


@pytest.mark.experiments3(filename='exp3_enabled.json')
async def test_getimage_bad_hint_header(taxi_inapp_communications):
    response = await taxi_inapp_communications.get(
        '3.0/getimage?tag=unknown', headers={'width': 'aaa'},
    )
    assert response.status_code == 400


@pytest.mark.config(
    APPLICATION_MAP_IMAGES={
        'yango_android': 'android',
        'yango_iphone': 'iphone',
        'uber_iphone': 'iphone',
        'uber_by_iphone': 'iphone',
        'uber_android': 'android',
    },
)
@pytest.mark.parametrize(
    'user_agent, tag, size_hint, status_code, path, is_tintable',
    [
        (None, 'unknown', 100, 404, None, False),
        (None, 'tag1', 50, 200, '/static/images/image1', False),
        (None, 'tag1', 100, 200, '/static/images/image1', False),
        (None, 'tag2', 101, 200, '/static/images/image2', False),
        (None, 'tag2', 201, 200, '/static/images/image2', False),
        (
            'yandex-taxi/3.129.0.110856 Android/9 (samsung; SM-A705FN)',
            'tag3',
            50,
            200,
            '/static/images/image3',
            False,
        ),
        (
            'ru.yandex.ytaxi/3.22.2896 (iPhone; iPhone6,2; iOS 8.3; Darwin)',
            'tag4:rev1',
            340,
            200,
            '/static/images/image4_rev1',
            True,
        ),
        (
            'yandex-uber/3.86.2.121338 Android/6.0 (HUAWEI; EVA-L19)',
            'tag3:rev1',
            340,
            200,
            '/static/images/image3',
            False,
        ),
        (
            (
                'ru.yandex.uber/5.37.53957 '
                '(iPhone; iPhone10,6; iOS 13.5.1; Darwin)'
            ),
            'tag4:rev1',
            340,
            200,
            '/static/images/image4_rev1',
            True,
        ),
        (
            (
                'ru.yandex.yango/550.5.0.63835 '
                '(iPhone; iPhone10,6; iOS 13.5.1; Darwin)'
            ),
            'tag4:rev1',
            340,
            200,
            '/static/images/image4_rev1',
            True,
        ),
        (
            (
                'ru.yandex.uber-by/4.80.30925 '
                '(iPhone; iPhone12,1; iOS 13.5.1; Darwin)'
            ),
            'tag4:rev1',
            340,
            200,
            '/static/images/image4_rev1',
            True,
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_enabled.json')
async def test_getimage(
        taxi_inapp_communications,
        mockserver,
        load_json,
        user_agent,
        tag,
        size_hint,
        status_code,
        path,
        is_tintable,
):
    @mockserver.json_handler('/admin-images/internal/list')
    def _mock_internal_list(request):
        return load_json('admin_images_list.json')

    await taxi_inapp_communications.invalidate_caches()

    custom_headers = {}
    if user_agent is not None:
        custom_headers = {'User-Agent': user_agent}

    response = await taxi_inapp_communications.get(
        f'3.0/getimage?tag={tag}&size_hint={size_hint}',
        headers=custom_headers,
    )
    assert response.status_code == status_code
    if status_code == 200:
        assert response.headers['X-Accel-Redirect'] == path
        assert (
            response.headers['Cache-Control']
            == 'public,max-age=31536000,immutable'
        )
        assert 'X-Is-Tintable' in response.headers
        expected_tint = 'true' if is_tintable else 'false'
        assert response.headers['X-Is-Tintable'] == expected_tint

    if status_code == 404:
        assert response.headers['Cache-Control'] == 'no-store'


@pytest.mark.parametrize(
    'tag, theme, path',
    [
        pytest.param(
            'tag0',
            'light',
            '/static/images/image0',
            id='default_light_theme_in_cache',
        ),
        pytest.param(
            'tag1', None, '/static/images/image1', id='no_theme_specified',
        ),
        pytest.param(
            'tag1', 'light', '/static/images/image1', id='light_theme',
        ),
        pytest.param('tag1', 'dark', '/static/images/image2', id='dark_theme'),
        pytest.param(
            'tag2',
            'dark',
            '/static/images/image3',
            id='dark_theme_not_found_fallback_to_light',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_enabled.json')
async def test_getimage_with_theme(
        taxi_inapp_communications, mockserver, load_json, tag, theme, path,
):
    @mockserver.json_handler('/admin-images/internal/list')
    def _mock_internal_list(request):
        return load_json('admin_images_with_themes.json')

    await taxi_inapp_communications.invalidate_caches()

    parameters = {'tag': tag, 'size_hint': '100'}
    if theme:
        parameters['theme'] = theme
    response = await taxi_inapp_communications.get(
        f'3.0/getimage', params=parameters,
    )
    assert response.status_code == 200
    assert response.headers['X-Accel-Redirect'] == path


@pytest.mark.parametrize(
    'tag, size_hint, status_code, path, file_format, is_tintable',
    [
        ('tag1', 50, 200, '/static/images/image_no_ff_rev2', None, True),
        ('tag1', 50, 200, '/static/images/image_no_ff_rev2', 'unknown', True),
        ('tag1', 50, 200, '/static/images/image_avif_rev2', 'avif', True),
        # No last revision for heif
        ('tag1', 50, 200, '/static/images/image_no_ff_rev2', 'heif', True),
        # No appropriate size for avif but appropriate for default
        ('tag1', 100, 200, '/static/images/image_no_ff_rev2', 'avif', True),
        ('tag1:rev1', 50, 200, '/static/images/image_heif_rev1', 'heif', True),
        ('tag1:rev1', 50, 200, '/static/images/image_avif_rev1', 'avif', True),
        ('tag1:rev2', 50, 200, '/static/images/image_avif_rev2', 'avif', True),
        ('tag1:rev1', 50, 200, '/static/images/image_no_ff_rev1', None, True),
        ('tag1:rev2', 50, 200, '/static/images/image_no_ff_rev2', None, True),
        ('tag2', 50, 200, '/static/images/image_no_ff2_rev1', None, False),
        ('tag2', 50, 200, '/static/images/image_heif2_rev1', 'heif', False),
    ],
)
@pytest.mark.experiments3(filename='exp3_enabled.json')
async def test_getimage_with_file_format(
        taxi_inapp_communications,
        mockserver,
        load_json,
        tag,
        size_hint,
        status_code,
        path,
        file_format,
        is_tintable,
):
    @mockserver.json_handler('/admin-images/internal/list')
    def _mock_internal_list(request):
        return load_json('admin_images_file_formats.json')

    await taxi_inapp_communications.invalidate_caches()

    url = f'3.0/getimage?tag={tag}&size_hint={size_hint}'
    if file_format is not None:
        url += f'&file_format={file_format}'
    response = await taxi_inapp_communications.get(url)
    assert response.status_code == status_code
    if status_code == 200:
        assert response.headers['X-Accel-Redirect'] == path
        assert (
            response.headers['Cache-Control']
            == 'public,max-age=31536000,immutable'
        )
        assert 'X-Is-Tintable' in response.headers
        expected_tint = 'true' if is_tintable else 'false'
        assert response.headers['X-Is-Tintable'] == expected_tint

    if status_code == 404:
        assert response.headers['Cache-Control'] == 'no-store'


@pytest.mark.parametrize(
    'tag, size_hint, status_code, path, file_format, is_tintable',
    [
        ('tag1', 50, 200, '/static/images/image_no_ff_rev2', None, True),
        ('tag1', 50, 200, '/static/images/image_no_ff_rev2', 'unknown', True),
        ('tag1', 50, 200, '/static/images/image_no_ff_rev2', 'avif', True),
        ('tag1', 50, 200, '/static/images/image_no_ff_rev2', 'heif', True),
        ('tag2', 50, 200, '/static/images/image_no_ff2_rev1', 'heif', False),
        ('tag2', 50, 200, '/static/images/image_avif2_rev1', 'avif', False),
    ],
)
@pytest.mark.experiments3(filename='exp3_disabled_tag1_and_tag2_heif.json')
async def test_getimage_with_file_format_and_exp(
        taxi_inapp_communications,
        mockserver,
        load_json,
        tag,
        size_hint,
        status_code,
        path,
        file_format,
        is_tintable,
):
    @mockserver.json_handler('/admin-images/internal/list')
    def _mock_internal_list(request):
        return load_json('admin_images_file_formats.json')

    await taxi_inapp_communications.invalidate_caches()

    url = f'3.0/getimage?tag={tag}&size_hint={size_hint}'
    if file_format is not None:
        url += f'&file_format={file_format}'
    response = await taxi_inapp_communications.get(url)
    assert response.status_code == status_code
    if status_code == 200:
        assert response.headers['X-Accel-Redirect'] == path
        assert (
            response.headers['Cache-Control']
            == 'public,max-age=31536000,immutable'
        )
        assert 'X-Is-Tintable' in response.headers
        expected_tint = 'true' if is_tintable else 'false'
        assert response.headers['X-Is-Tintable'] == expected_tint

    if status_code == 404:
        assert response.headers['Cache-Control'] == 'no-store'
