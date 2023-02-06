import pytest


# TODO uncomment logistics after
#  https://st.yandex-team.ru/CARGODEV-8360#61bb2328ee8b8d148c4413ee
@pytest.mark.config(ENABLE_DYNAMIC_PARK_THRESHOLD=True)
@pytest.mark.now('2021-09-30T00:00:00.000+00:00')
async def test_active_logistic_park(taxi_parks_activation, park_sync_jobs):
    response = await taxi_parks_activation.post(
        'v1/parks/activation/updates', json={'last_known_revision': 0},
    )
    assert response.status_code == 200
    response_json = response.json()['parks_activation']
    for park in response_json:
        assert park['data']['deactivated']
        assert not park['data']['can_card']
        assert not park['data']['can_cash']
        # if park['park_id'] == 'park_id_1':
        #     assert not park['data']['logistic_deactivated']
        #     assert park['data']['logistic_can_card']
        #     assert park['data']['logistic_can_cash']
        # else:
        #     assert park['data']['logistic_deactivated']
        #     assert not park['data']['logistic_can_card']
        #     assert not park['data']['logistic_can_cash']
