import pytest


def test_getimage_no_args(taxi_protocol):
    response = taxi_protocol.get('3.0/getimage', {})
    assert response.status_code == 400


def test_getimage_only_tag(taxi_protocol):
    response = taxi_protocol.get('3.0/getimage?tag=tag', {})
    assert response.status_code == 400


def test_getimage_only_size_arg(taxi_protocol):
    response = taxi_protocol.get('3.0/getimage?size_hint=1', {})
    assert response.status_code == 400


def test_getimage_only_width_header(taxi_protocol):
    response = taxi_protocol.get('3.0/getimage', headers={'width': '100'})
    assert response.status_code == 400


def test_getimage_404_hint_arg(taxi_protocol):
    response = taxi_protocol.get('3.0/getimage?tag=unknown&size_hint=100', {})
    assert response.status_code == 404
    assert response.headers['Cache-Control'] == 'no-store'


def test_getimage_bad_hint_arg(taxi_protocol):
    response = taxi_protocol.get('3.0/getimage?tag=unknown&size_hint=aaa', {})
    assert response.status_code == 400


def test_getimage_bad_hint_header(taxi_protocol):
    response = taxi_protocol.get(
        '3.0/getimage?tag=unknown', headers={'width': 'aaa'},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'user_agent,tag,size_hint,status_code,url',
    [
        (None, 'unknown', 100, 404, None),
        (None, 'test_image', 100, 200, '/static/images/image1'),
        (None, 'test_image', 101, 200, '/static/images/image2'),
        (None, 'test_image', 201, 200, '/static/images/image2'),
        (None, 'test_image', 50, 200, '/static/images/image1'),
        (
            'ru.yandex.ytaxi/3.22.2896 (iPhone; iPhone6,2; iOS 8.3; Darwin)',
            'test_image',
            50,
            200,
            '/static/images/image0',
        ),
    ],
)
def test_getimage(taxi_protocol, user_agent, tag, size_hint, status_code, url):
    custom_headers = {}
    if user_agent is not None:
        custom_headers = {'User-Agent': user_agent}

    response = taxi_protocol.get(
        '3.0/getimage?tag=%s&size_hint=%d' % (tag, size_hint),
        headers=custom_headers,
    )
    assert response.status_code == status_code
    if status_code == 200:
        assert response.headers['X-Accel-Redirect'] == url

    if status_code == 404:
        assert response.headers['Cache-Control'] == 'no-store'
    else:
        assert 'Cache-Control' not in response.headers
