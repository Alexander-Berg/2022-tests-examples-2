# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
import pytest

from taxi_billing_subventions import config
from taxi_billing_subventions.personal_uploads import actions


class Upload:
    pass


class YtClient:
    pass


class TerritoriesApiClient:
    pass


class UniqueDriversApiClient:
    # pylint: disable=invalid-name
    def __init__(self, response_list: list = None):
        self._response_list = response_list or []

    def set_responses(self, response_list):
        self._response_list = response_list

    async def get_driver_profile_ids_from_data(self, uids_list):
        return self._response_list.pop(0)


@pytest.fixture
def upload_action(db):
    return actions._UploadAction(
        database=db,
        upload=Upload(),
        yt_client=YtClient(),
        territories_client=TerritoriesApiClient(),
        unique_drivers_client=UniqueDriversApiClient(),
        config=config.Config(),
        log_extra=None,
    )


@pytest.mark.filldb(
    dbdrivers='for_test_personal_upload_action',
    dbparks='for_test_personal_upload_action',
)
@pytest.mark.parametrize(
    'group_json, driver_finder_json', [('group.json', 'driver_finder.json')],
)
async def test_make_driver_finder_by_uuid(
        upload_action: actions._UploadAction,
        group_json,
        load_py_json_dir,
        driver_finder_json,
):
    group = load_py_json_dir('test_make_driver_finder_by_uuid', group_json)
    expected_driver_finder = load_py_json_dir(
        'test_make_driver_finder_by_uuid', driver_finder_json,
    )
    driver_finder = await upload_action._make_driver_finder(group)
    assert driver_finder._driver_by_properties == expected_driver_finder


@pytest.mark.filldb(
    dbdrivers='for_test_personal_upload_action',
    dbparks='for_test_personal_upload_action',
)
@pytest.mark.parametrize(
    'group_json, driver_finder_json, unique_drivers_response_json',
    [
        (
            'group.json',
            'driver_finder.json',
            'unique_drivers_get_driver_profile_by_uid.json',
        ),
    ],
)
async def test_make_driver_finder_by_uid(
        upload_action: actions._UploadAction,
        group_json,
        load_py_json_dir,
        driver_finder_json,
        unique_drivers_response_json,
):
    group = load_py_json_dir('test_make_driver_finder_by_uid', group_json)
    expected_driver_finder = load_py_json_dir(
        'test_make_driver_finder_by_uid', driver_finder_json,
    )
    unique_drivers_response = load_py_json_dir(
        'test_make_driver_finder_by_uid', unique_drivers_response_json,
    )
    upload_action._unique_drivers_client.set_responses(  # type: ignore
        unique_drivers_response,
    )
    driver_finder = await upload_action._make_driver_finder_from_udi(group)
    assert driver_finder._driver_by_properties == expected_driver_finder


@pytest.mark.filldb(
    dbdrivers='for_test_personal_upload_action',
    dbparks='for_test_personal_upload_action',
)
@pytest.mark.parametrize(
    'group_json, driver_finder_json, unique_drivers_response_json',
    [('group.json', 'driver_finder.json', 'unique_drivers_reduced.json')],
)
async def test_make_driver_finder_by_uid_absent(
        upload_action: actions._UploadAction,
        group_json,
        load_py_json_dir,
        driver_finder_json,
        unique_drivers_response_json,
):
    group = load_py_json_dir('test_make_driver_finder_by_uid', group_json)
    expected_driver_finder = load_py_json_dir(
        'test_make_driver_finder_by_uid', driver_finder_json,
    )
    unique_drivers_response = load_py_json_dir(
        'test_make_driver_finder_by_uid', unique_drivers_response_json,
    )
    upload_action._unique_drivers_client.set_responses(  # type: ignore
        unique_drivers_response,
    )
    driver_finder = await upload_action._make_driver_finder_from_udi(group)
    assert driver_finder._driver_by_properties
    assert set(driver_finder._driver_by_properties).issubset(
        set(expected_driver_finder),
    )
