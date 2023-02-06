import pytest

VGW_TALK_URL = '/vgw-api/v1/talk/'

VGW_TALK_RESPONSE = b'binary_data'

VGW_TALK_ERROR_404 = {
    'code': '404',
    'message': 'Talk not found',
    'error': {'code': 'TalkIdNotFound', 'message': 'Talk id not found'},
}

VGW_TALK_ERROR_500 = {
    'code': '500',
    'message': 'Internal server error',
    'error': {'code': 'UnknownError', 'message': 'Unknown error'},
}

EXPECTED_RESPONSE = b'binary_data'


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.parametrize("""content_type""", ['audio/wav', 'audio/mpeg'])
async def test_green_flow(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        content_type,
):
    @mockserver.json_handler(VGW_TALK_URL)
    def _mock_vgw_talk(request):
        return mockserver.make_response(
            status=200, response=VGW_TALK_RESPONSE, content_type=content_type,
        )

    response = await taxi_eats_support_misc_web.get(
        '/v1/get-talk',
        params={
            'gateway_id': 'mtt',
            'talk_id': 'B674108217FEC529CC37E6234D526B36',
        },
    )

    assert response.status == 200
    assert response.headers['Content-Type'] == content_type
    assert await response.content.read() == EXPECTED_RESPONSE


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.parametrize(
    """talk_code,talk_response""",
    [(404, VGW_TALK_ERROR_404), (500, VGW_TALK_ERROR_500)],
)
async def test_vgw_error(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        talk_code,
        talk_response,
):
    @mockserver.json_handler(VGW_TALK_URL)
    def _mock_vgw_talk(request):
        return mockserver.make_response(
            status=talk_code, content_type='audio/mpeg', json=talk_response,
        )

    response = await taxi_eats_support_misc_web.get(
        '/v1/get-talk',
        params={
            'gateway_id': 'mtt',
            'talk_id': 'B674108217FEC529CC37E6234D526B36',
        },
    )

    assert response.status == 404
