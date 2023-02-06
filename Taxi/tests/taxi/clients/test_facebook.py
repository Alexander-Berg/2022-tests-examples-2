import pytest

from taxi.clients import facebook


@pytest.fixture(name='test_fb_app')
def fb_test_app(test_taxi_app):
    test_taxi_app.facebook = facebook.FacebookApiClient(
        session=test_taxi_app.session, settings=test_taxi_app.settings,
    )
    return test_taxi_app


@pytest.mark.parametrize(
    'error_code, error_subcode, bad_error',
    [(100, 33, True), (100, 2018218, True), (100, 0, False), (0, 33, False)],
)
async def test_raise_exception_on_bad_errors(
        test_fb_app,
        patch_aiohttp_session,
        response_mock,
        error_code,
        error_subcode,
        bad_error,
):
    @patch_aiohttp_session('https://graph.facebook.com/', 'GET')
    def _facebook_api(*args, **kwargs):
        return response_mock(
            json={
                'error': {'code': error_code, 'error_subcode': error_subcode},
            },
            status=400,
        )

    if bad_error:
        with pytest.raises(facebook.BadUserError):
            await test_fb_app.facebook.user_info('user_id', [], 'page_token')
    else:
        with pytest.raises(facebook.BaseError):
            await test_fb_app.facebook.user_info('user_id', [], 'page_token')
