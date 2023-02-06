import datetime

import pytest

from test_pro_profiles_removal import conftest


@pytest.mark.parametrize(
    'contractor_profile_id, http_code, error_message',
    [
        pytest.param(
            conftest.TEST_DRIVER_ID_1,
            400,
            'Заявка уже создана. Ожидайте решения',
            id='has_canceled_and_initialized',
        ),
        pytest.param(
            conftest.TEST_DRIVER_ID_2,
            400,
            'Заявка уже создана. Ожидайте решения',
            id='has_initialized_multiple',
        ),
        pytest.param(
            conftest.TEST_DRIVER_ID_3,
            400,
            'Заявка уже создана. Ожидайте решения',
            id='initialize_second_one',
        ),
        pytest.param(conftest.TEST_DRIVER_ID_4, 200, None, id='has_canceled'),
        pytest.param(
            conftest.TEST_DRIVER_ID_5, 200, None, id='first_removal_request',
        ),
    ],
)
async def test_profiles_removal_request_create(
        web_app_client,
        driver_profiles,
        contractor_profile_id,
        http_code,
        error_message,
):
    action = 'create'
    headers = conftest.TEST_HEADERS
    headers.update({'X-YaTaxi-Driver-Profile-Id': contractor_profile_id})
    response = await web_app_client.post(
        f'/driver/v1/profiles/removal_request/{action}', headers=headers,
    )
    assert response.status == http_code
    if error_message:
        content = await response.json()
        assert content == {'message': error_message}


async def test_removal_request_create_for_new_one(
        web_app_client, driver_profiles, web_context,
):
    action = 'create'
    headers = conftest.TEST_HEADERS
    headers.update({'X-YaTaxi-Driver-Profile-Id': conftest.TEST_DRIVER_ID_5})
    response = await web_app_client.post(
        f'/driver/v1/profiles/removal_request/{action}', headers=headers,
    )
    assert response.status == 200

    phone_pd_id = (
        f'{conftest.TEST_PARK_ID}_{conftest.TEST_DRIVER_ID_5}_phone_pd_id'
    )
    driver_profiles.add_profile(
        conftest.TEST_PARK_ID, conftest.TEST_DRIVER_ID_6, phone_pd_id,
    )

    headers.update({'X-YaTaxi-Driver-Profile-Id': conftest.TEST_DRIVER_ID_6})
    response = await web_app_client.post(
        f'/driver/v1/profiles/removal_request/{action}', headers=headers,
    )
    assert response.status == 200

    sql = """
        SELECT * FROM pro_profiles_removal.requests
        WHERE phone_pd_id = $1
    """
    records = await web_context.pg.main_master.fetch(sql, phone_pd_id)
    assert len(records) == 2


@pytest.mark.now(conftest.TEST_NOW)
@pytest.mark.config(
    PRO_PROFILES_REMOVAL_CANCELATION_FREEZING_TIME={'freezing_hours': 3},
    PRO_PROFILES_REMOVAL_TIME_BEFORE_REMOVING={'days': 27},
)
@pytest.mark.parametrize(
    'contractor_profile_id, http_code, error_message, forward_time',
    [
        pytest.param(
            conftest.TEST_DRIVER_ID_1,
            200,
            None,
            datetime.timedelta(hours=4),
            id='has_canceled_and_initialized',
        ),
        pytest.param(
            conftest.TEST_DRIVER_ID_1,
            400,
            'Отменить заявку можно через 3 дня с момента её создания',
            datetime.timedelta(hours=2),
            id='cancel_requested_too_early',
        ),
        pytest.param(
            conftest.TEST_DRIVER_ID_1,
            400,
            'Отменить заявку можно через 3 дня с момента её создания',
            datetime.timedelta(days=35),
            id='cancel_requested_too_late',
        ),
        pytest.param(
            conftest.TEST_DRIVER_ID_2,
            200,
            None,
            datetime.timedelta(hours=4),
            id='has_initialized_and_multiple_profiles',
        ),
        pytest.param(
            conftest.TEST_DRIVER_ID_3,
            200,
            None,
            datetime.timedelta(hours=4),
            id='has_initialized',
        ),
        pytest.param(
            conftest.TEST_DRIVER_ID_4,
            400,
            'Заявка на отмену удаления в работе либо нет заявок на удаление',
            datetime.timedelta(hours=4),
            id='already_requested',
        ),
        pytest.param(
            conftest.TEST_DRIVER_ID_5,
            400,
            'Заявка на отмену удаления в работе либо нет заявок на удаление',
            datetime.timedelta(hours=4),
            id='does_not_exist_in_db',
        ),
    ],
)
async def test_profiles_removal_request_cancel(
        taxi_pro_profiles_removal_web,
        driver_profiles,
        mocked_time,
        contractor_profile_id,
        http_code,
        error_message,
        forward_time,
):
    action = 'cancel'
    mocked_time.sleep(forward_time.total_seconds())
    headers = conftest.TEST_HEADERS
    headers.update({'X-YaTaxi-Driver-Profile-Id': contractor_profile_id})
    response = await taxi_pro_profiles_removal_web.post(
        f'/driver/v1/profiles/removal_request/{action}', headers=headers,
    )
    assert response.status == http_code
    if error_message:
        content = await response.json()
        assert content == {'message': error_message}


@pytest.mark.now(conftest.TEST_NOW)
@pytest.mark.config(
    PRO_PROFILES_REMOVAL_CANCELATION_FREEZING_TIME={'freezing_hours': 3},
)
async def test_cancel_new_one_does_not_cancel_all(
        taxi_pro_profiles_removal_web,
        driver_profiles,
        mocked_time,
        web_context,
):
    action = 'cancel'
    pg_main = web_context.pg.main_master
    phone_pd_id = (
        f'{conftest.TEST_PARK_ID}_{conftest.TEST_DRIVER_ID_3}_phone_pd_id'
    )

    driver_profiles.add_profile(
        conftest.TEST_PARK_ID, conftest.TEST_DRIVER_ID_6, phone_pd_id,
    )
    headers = conftest.TEST_HEADERS
    headers.update({'X-YaTaxi-Driver-Profile-Id': conftest.TEST_DRIVER_ID_6})

    mocked_time.sleep(datetime.timedelta(hours=4).total_seconds())
    response = await taxi_pro_profiles_removal_web.post(
        f'/driver/v1/profiles/removal_request/{action}', headers=headers,
    )
    assert response.status == 200

    sql = """
        SELECT
            state
        FROM pro_profiles_removal.profiles profiles
        JOIN pro_profiles_removal.requests requests
        ON profiles.request_id = requests.id
        WHERE phone_pd_id = $1
    """
    records = await pg_main.fetch(sql, phone_pd_id)
    assert len(records) == 2
    assert {r['state'] for r in records} == {'pending', 'cancel_requested'}
