# pylint: disable=redefined-outer-name
import typing

import pytest


class DriverIDs(typing.NamedTuple):
    unique_driver_id: str
    park_id: str
    driver_profile_id: str


BAD_ORDER = 'bad_order'
GOOD_ORDER = '8c83b49edb274ce0992f337061047375'
GOOD_HEADERS = {
    'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
    'X-Yandex-UID': '4003514353',
}

DRIVER_ADMIN_WITH_PORTRAIT = DriverIDs(
    '34256bf766d749fb905ff4d9', '3456', '4567',
)
NO_SUCH_DRIVER = DriverIDs('no_such_id', 'park_id1', 'uuid1')

DRIVER_TAXIMETER_WITH_PORTRAIT = DriverIDs(
    '34256bf766d749fb905ff442', '1112', '2221',
)


@pytest.fixture
async def check_response(taxi_udriver_photos, load_json):
    async def _check(
            order_id, empty=False, response_content=None, response_file=None,
    ):
        response = await taxi_udriver_photos.get(
            '/4.0/orderperformerinfo',
            params={'performer_tag': 'performer_tag1', 'order_id': order_id},
            headers=GOOD_HEADERS,
        )
        assert response.status == 200
        if empty:
            assert response.json() == {}
        elif response_content is not None:
            assert response.json() == response_content
        elif response_file is not None:
            assert response.json() == load_json(response_file)
        else:
            raise RuntimeError('no expected response')

    return _check


@pytest.mark.config(
    DRIVER_PHOTOS_USE_LOGIC_HIGH_CLASS=True,
    DRIVER_INFO_PREMIUM_TARIFFS=['vip', 'business', 'maybach'],
    DRIVER_INFO_DISPLAY_SETTINGS={
        'econom': {'return_profile_photo': True, 'status_title_source': {}},
    },
)
@pytest.mark.parametrize(
    'driver, tariffs, response_file',
    [
        (
            DRIVER_ADMIN_WITH_PORTRAIT,
            ['econom', 'comfort'],
            'with_portrait.json',
        ),
        (
            DRIVER_ADMIN_WITH_PORTRAIT,
            ['econom', 'maybach'],
            'with_portrait.json',
        ),
        (
            DRIVER_TAXIMETER_WITH_PORTRAIT,
            ['econom', 'maybach'],
            'empty_photos.json',
        ),
        (
            DRIVER_TAXIMETER_WITH_PORTRAIT,
            ['econom', 'comfort'],
            'with_portrait_taximeter.json',
        ),
    ],
    ids=[
        'no_premium_admin',
        'has_premium_admin',
        'has_premium_taximeter',
        'no_premium_taximeter',
    ],
)
async def test_premium_logic(
        mock_unique_drivers,
        mock_order_core,
        mock_candidates,
        check_response,
        driver,
        tariffs,
        response_file,
):
    mock_order_core(driver.park_id, driver.driver_profile_id, 'econom')
    mock_unique_drivers(driver.unique_driver_id)
    mock_candidates(driver.park_id, driver.driver_profile_id, tariffs)

    await check_response(GOOD_ORDER, response_file=response_file)


@pytest.mark.config(
    DRIVER_PHOTOS_USE_LOGIC_HIGH_CLASS=False,
    DRIVER_INFO_DISPLAY_SETTINGS={
        'econom': {'return_profile_photo': True, 'status_title_source': {}},
        'start': {'return_profile_photo': False, 'status_title_source': {}},
    },
)
@pytest.mark.parametrize(
    'tariff, response_file',
    [
        ('econom', 'with_portrait.json'),
        ('start', 'no_portrait.json'),
        ('cargo', 'no_portrait.json'),
    ],
    ids=['return_profile_true', 'return_profile_false', 'unknown_tariff'],
)
@pytest.mark.experiments3(
    filename='experiments3_order_show_driver_action_placeholder.json',
)
async def test_display_settings(
        mock_unique_drivers,
        mock_order_core,
        check_response,
        tariff,
        response_file,
):
    mock_order_core(
        DRIVER_ADMIN_WITH_PORTRAIT.park_id,
        DRIVER_ADMIN_WITH_PORTRAIT.driver_profile_id,
        tariff,
    )
    mock_unique_drivers(DRIVER_ADMIN_WITH_PORTRAIT.unique_driver_id)

    await check_response(GOOD_ORDER, response_file=response_file)


@pytest.mark.parametrize('order_core_status', [404, 500])
async def test_order_core_error(
        order_core_status, check_response, mock_order_core,
):
    mock_order_core('park_id1', 'uuid1', return_code=order_core_status)
    await check_response(GOOD_ORDER, empty=True)


@pytest.mark.parametrize('unique_driver_status', [404, 500])
async def test_unique_driver_error(
        unique_driver_status,
        check_response,
        mock_order_core,
        mock_unique_drivers,
):
    mock_order_core('park_id1', 'uuid1')
    mock_unique_drivers('unique_driver_id1', return_code=unique_driver_status)
    await check_response(GOOD_ORDER, empty=True)


async def test_db_error(
        pgsql, mock_unique_drivers, mock_order_core, check_response,
):
    mock_order_core(
        DRIVER_ADMIN_WITH_PORTRAIT.park_id,
        DRIVER_ADMIN_WITH_PORTRAIT.driver_profile_id,
        'econom',
    )
    mock_unique_drivers(DRIVER_ADMIN_WITH_PORTRAIT.unique_driver_id)

    cursor = pgsql['driver_photos'].cursor()
    cursor.execute('ALTER TABLE driver_photos RENAME TO driver_photos_tmp')
    try:
        await check_response(GOOD_ORDER, empty=True)
    finally:
        cursor.execute('ALTER TABLE driver_photos_tmp RENAME TO driver_photos')


@pytest.mark.config(DRIVER_PHOTOS_USE_LOGIC_HIGH_CLASS=True)
@pytest.mark.parametrize(
    'return_code, is_network_error', [(200, True), (404, False), (500, False)],
)
async def test_candidates_error(
        mock_unique_drivers,
        mock_order_core,
        mock_candidates,
        check_response,
        return_code,
        is_network_error,
):
    driver = DRIVER_ADMIN_WITH_PORTRAIT
    mock_order_core(driver.park_id, driver.driver_profile_id, 'econom')
    mock_unique_drivers(driver.unique_driver_id)
    mock_candidates(
        driver.park_id,
        driver.driver_profile_id,
        [],
        return_code=return_code,
        is_network_error=is_network_error,
    )

    await check_response(GOOD_ORDER, empty=True)


@pytest.mark.pgsql('driver_photos', queries=['TRUNCATE driver_photos;'])
@pytest.mark.config(
    DRIVER_INFO_DISPLAY_SETTINGS={
        'econom': {'return_profile_photo': True, 'status_title_source': {}},
    },
)
@pytest.mark.parametrize(
    'placeholder_exp_value',
    [
        {
            'avatar': 'avatar_placeholder_url',
            'portrait': 'portrait_placeholder_url',
        },
        {},
    ],
)
async def test_placeholders(
        mock_unique_drivers,
        mock_order_core,
        check_response,
        experiments3,
        placeholder_exp_value,
):
    experiments3.add_experiment(
        clauses=[
            {'value': placeholder_exp_value, 'predicate': {'type': 'true'}},
        ],
        name='show_driver_action_placeholder',
        consumers=['udriver_photos'],
        match={'enabled': True, 'predicate': {'type': 'true'}},
    )
    mock_order_core(
        DRIVER_ADMIN_WITH_PORTRAIT.park_id,
        DRIVER_ADMIN_WITH_PORTRAIT.driver_profile_id,
        'econom',
    )
    mock_unique_drivers(DRIVER_ADMIN_WITH_PORTRAIT.unique_driver_id)

    if placeholder_exp_value:
        await check_response(GOOD_ORDER, response_file='placeholders.json')
    else:
        await check_response(GOOD_ORDER, response_content={'photos': {}})
