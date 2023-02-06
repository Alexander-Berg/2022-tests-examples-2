import pytest

ENDPOINT = '/driver/v1/deptrans-status/v1/profile/info'


def _get_headers(park_id, driver_id):
    return {
        'Accept-Language': 'ru',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_id,
        'X-Request-Application-Version': '9.60 (1234)',
    }


def _get_response(
        deptrans_profile,
        park_id,
        driver_id,
        request_for_temp,
        is_outdated,
        date_until_valid,
        button_disabled,
        accepted_agreement,
        pending_info,
):
    profile = deptrans_profile.get(park_id, driver_id)
    items = []
    if profile.checking_deptrans_id:
        items.append(
            'Сейчас на проверке введенное Вами значение: '
            + profile.checking_deptrans_id,
        )
    if is_outdated is True:
        items.append('Временный профиль действовал до ' + date_until_valid)
    elif is_outdated is False:
        items.append('Временный профиль действует до ' + date_until_valid)

    if request_for_temp:
        title = 'title_temp_key_localized'
        items += ['item_temp_key_1_localized', 'item_temp_key_2_localized']
        agreement = 'personal_data_agreement_link'

        if profile.license_pd_id != 'unknown':
            profile_id = {
                'value': profile.deptrans_id,
                'is_approved': profile.status == 'approved',
                'is_temp': profile.status == 'temporary',
                'input_mask': '[0-9]{1,10}',
                'input_label': 'input_label_localized',
            }
        else:
            profile_id = None
    else:
        title = 'title_full_key_localized'
        items += ['item_full_key_1_localized', 'item_full_key_2_localized']
        agreement = 'deptrans_id_agreement_link'

        profile_id = {
            'value': profile.deptrans_id if not is_outdated else '',
            'is_approved': profile.status == 'approved',
            'is_temp': profile.status == 'temporary',
            'input_mask': '[0-9]{1,10}',
            'input_label': 'input_label_localized',
        }

    if (
            not request_for_temp
            and not pending_info
            and profile_id
            and (profile_id['is_temp'] or is_outdated)
    ):
        items.append('temp_profile_info_localized')

    if button_disabled:
        button = {
            'text': 'pending_button_localized',
            'action': 'skip',
            'state': 'disabled',
        }
    else:
        button = {
            'text': 'button_localized',
            'action': 'bind',
            'state': 'enabled',
        }

    if pending_info:
        items.append('pending_info_localized')

    response = {
        'title': title,
        'items': items,
        'button': button,
        'user_agreement': {
            'link': agreement,
            'is_accepted': accepted_agreement,
            'text': 'agreement_text_localized',
        },
    }
    if request_for_temp and not button_disabled:
        response['help_button'] = {
            'text': 'help_button_localized',
            'action': {'type': 'webview', 'value': 'help_link'},
        }
    if profile_id:
        response['profile_id'] = profile_id
    return response


@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_AGREEMENTS={
        'deptrans_id_agreement': 'deptrans_id_agreement_link',
        'personal_data_agreement': 'personal_data_agreement_link',
    },
    DEPTRANS_DRIVER_STATUS_TEMP_ACCOUNT_DAYS_TTL=5,
)
@pytest.mark.experiments3(filename='deptrans_driver_profile_info.json')
@pytest.mark.pgsql('deptrans_driver_status', files=['deptrans_profiles.sql'])
@pytest.mark.parametrize(
    (
        'park_id',
        'driver_id',
        'request_for_temp',
        'is_outdated',
        'date_until_valid',
        'button_disabled',
        'accepted_agreement',
        'pending_info',
        'personal_handler',
    ),
    [
        pytest.param(
            'park2',
            'driver2',
            False,
            None,
            None,
            False,
            False,
            False,
            None,
            id='Explicit full',
        ),
        pytest.param(
            'park2',
            'driver2',
            None,
            None,
            None,
            False,
            False,
            False,
            None,
            id='Implicit full',
        ),
        pytest.param(
            'park2',
            'driver2',
            True,
            None,
            None,
            False,
            False,
            False,
            None,
            id='Request temp',
        ),
        pytest.param(
            'park1',
            'driver1',
            None,
            None,
            None,
            True,
            False,
            False,
            'retrieve',
            id='Approved profile',
        ),
        pytest.param(
            'park1',
            'driver1',
            None,
            None,
            None,
            True,
            True,
            False,
            'retrieve',
            id='With accepted agreement',
            marks=pytest.mark.pgsql(
                'deptrans_driver_status', files=['agreements.sql'],
            ),
        ),
        pytest.param(
            'park1',
            'driver2',
            None,
            None,
            None,
            True,
            False,
            True,
            'bulk_retrieve',
            id='Approving profile',
        ),
        pytest.param(
            'park2',
            'driver1',
            None,
            False,
            '04.01.2021',
            False,
            False,
            False,
            'retrieve',
            id='Temp profile without import_date',
        ),
        pytest.param(
            'park3',
            'driver1',
            None,
            False,
            '03.01.2021',
            False,
            False,
            False,
            'retrieve',
            id='Temp profile with import_date',
        ),
        pytest.param(
            'park3',
            'driver3',
            None,
            True,
            '03.01.2020',
            False,
            False,
            False,
            'retrieve',
            id='Temp_outdated profile with import_date',
        ),
        pytest.param(
            'park3',
            'driver5',
            None,
            True,
            '04.01.2021',
            False,
            False,
            False,
            'retrieve',
            id='Temp_outdated profile without import_date',
        ),
        pytest.param(
            'park3',
            'driver4',
            None,
            None,
            None,
            True,
            False,
            True,
            'bulk_retrieve',
            id='Temp profile pending permanent',
        ),
        pytest.param(
            'park2',
            'driver1',
            True,
            None,
            None,
            True,
            False,
            False,
            'retrieve',
            id='Show temp',
        ),
    ],
)
@pytest.mark.now('2021-01-01T12:00:00+00:00')
async def test_get_deptrans_profile_info(
        taxi_deptrans_driver_status,
        personal,
        deptrans_profile,
        park_id,
        driver_id,
        request_for_temp,
        is_outdated,
        date_until_valid,
        button_disabled,
        accepted_agreement,
        pending_info,
        personal_handler,
):
    params = {}
    if request_for_temp is not None:
        params['try_temporary_id'] = request_for_temp

    response = await taxi_deptrans_driver_status.get(
        ENDPOINT, params=params, headers=_get_headers(park_id, driver_id),
    )
    assert response.status_code == 200
    if personal_handler:
        assert personal[personal_handler].times_called == 1

    assert response.json() == _get_response(
        deptrans_profile,
        park_id,
        driver_id,
        request_for_temp,
        is_outdated,
        date_until_valid,
        button_disabled,
        accepted_agreement,
        pending_info,
    )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='deptrans_driver_profile_info',
    consumers=['deptrans_driver_status_extended'],
    default_value={
        'agreement': {'text': 'agreement_text'},
        'button': {'action': 'bind', 'state': 'enabled', 'text': 'button'},
        'id': {'label': 'input_label', 'mask': '[0-9]{1,10}'},
        'items': ['item_extended'],
        'title': 'title_full_key',
    },
    is_config=True,
)
@pytest.mark.pgsql('deptrans_driver_status', files=['deptrans_profiles.sql'])
async def test_get_localization_with_args(
        taxi_deptrans_driver_status, personal,
):
    response = await taxi_deptrans_driver_status.get(
        ENDPOINT, headers=_get_headers('park2', 'driver1'),
    )
    assert response.status_code == 200
    assert response.json()['items'] == [
        'Ваш идентификатор 3 действителен до 29.01.2021',
    ]
