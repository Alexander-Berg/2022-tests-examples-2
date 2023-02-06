import pytest

from pro_profiles_removal.entities import contractor
from test_pro_profiles_removal import conftest


@pytest.mark.parametrize(
    'profiles, expected_result_count',
    [
        (
            [
                contractor.Profile(
                    conftest.TEST_PARK_ID, conftest.TEST_DRIVER_ID_1,
                ),
            ],
            1,
        ),
        (
            [
                contractor.Profile(
                    conftest.TEST_PARK_ID, conftest.TEST_DRIVER_ID_1,
                ),
                contractor.Profile(
                    conftest.TEST_PARK_ID, conftest.TEST_DRIVER_ID_2,
                ),
            ],
            2,
        ),
        (
            [
                contractor.Profile(
                    conftest.TEST_PARK_ID, conftest.TEST_DRIVER_ID_1,
                ),
                contractor.Profile(
                    conftest.TEST_PARK_ID, conftest.TEST_DRIVER_ID_6,
                ),
            ],
            1,
        ),
    ],
)
async def test_get_license_by_profiles(
        web_context, driver_profiles, profiles, expected_result_count,
):
    srv = web_context.services.profiles
    result = await srv.get_license_by_profiles(profiles)
    assert len(result) == expected_result_count
