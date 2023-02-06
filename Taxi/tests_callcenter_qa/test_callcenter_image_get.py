import pytest

GET_IMAGE_URL = '/cc/v1/callcenter-qa/v1/image'


@pytest.mark.parametrize(
    ['request_body', 'expected_status', 'response_body'],
    (
        pytest.param(
            {'image_link': 'images/image_link_1'},
            200,
            b'image_body',
            id='simple_request',
        ),
        pytest.param({'image_link': 'bad_link'}, 400, b'', id='invalid_link'),
        pytest.param(
            {'image_link': 'images/bad_link'}, 404, b'', id='not_found',
        ),
    ),
)
async def test_base(
        taxi_callcenter_qa,
        request_body,
        expected_status,
        response_body,
        mockserver,
):
    @mockserver.handler('/mds-s3-internal', prefix=True)
    def _mock_s3(request):
        if request.path.startswith('/mds-s3-internal/images/image_link'):
            return mockserver.make_response('image_body', 200)
        return mockserver.make_response('Not found', 404)

    response = await taxi_callcenter_qa.post(GET_IMAGE_URL, request_body)
    assert response.status_code == expected_status
    assert response.content == response_body
