import pytest


@pytest.mark.parametrize('bad_step', ['exit', 'foobar'])
async def test_get_mocks_bad_step(
        taxi_selfemployed_fns_profiles, prepare_get_rq, bad_step,
):
    request = prepare_get_rq(step=bad_step, passport_uid='puid1')
    response = await taxi_selfemployed_fns_profiles.get(**request)
    assert response.status_code == 400
