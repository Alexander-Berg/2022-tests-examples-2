import pytest

from tests_driver_diagnostics import utils


SELF_EMPLOYED_PARK = {
    'id': 'park_id1',
    'login': 'some_login',
    'name': 'some_name',
    'is_active': True,
    'city_id': 'MSK',
    'locale': 'ru',
    'is_billing_enabled': True,
    'is_franchising_enabled': True,
    'country_id': 'rus',
    'driver_partner_source': 'selfemployed_fns',
    'fleet_type': 'taximeter',
    'provider_config': {'clid': 'park_id1', 'type': 'production'},
    'demo_mode': False,
    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
}

NOT_SELF_EMPLOYED_PARK = {
    'id': 'park_id1',
    'login': 'some_login',
    'name': 'some_name',
    'is_active': True,
    'city_id': 'MSK',
    'locale': 'ru',
    'is_billing_enabled': True,
    'is_franchising_enabled': True,
    'country_id': 'rus',
    'fleet_type': 'taximeter',
    'provider_config': {'clid': 'park_id1', 'type': 'production'},
    'demo_mode': False,
    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
}


@pytest.mark.experiments3(filename='diagnostics_message_action.json')
async def test_driver_ui_restrictions_message(
        taxi_driver_diagnostics, mock_fleet_parks_list, candidates, load_json,
):
    candidates.set_response_reasons({'some_filter': []}, {})

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json('ui_message_action.json')


@pytest.mark.parametrize(
    'filter_time,expected_time,expected_header',
    [
        (
            '2020-01-02T20:10:00.0+0000',
            '1 день',
            'Доступ приостановлен на 1 день',
        ),
        (
            '2020-01-02T19:00:00.0+0000',
            '1 день',
            'Доступ приостановлен на 1 день',
        ),
        (
            '2020-01-01T19:00:00.0+0000',
            'Вот-вот разблокируем',
            'Вот-вот разблокируем',
        ),
        (
            '2020-01-01T18:00:00.0+0000',
            'Вот-вот разблокируем',
            'Вот-вот разблокируем',
        ),
        (
            '2019-12-31T17:30:00.0+0000',
            'Вот-вот разблокируем',
            'Вот-вот разблокируем',
        ),
    ],
    ids=['full_time', 'only_days', 'soon', 'time_in_past', 'negative_minutes'],
)
@pytest.mark.now('2020-01-01T19:00:00.000Z')
@pytest.mark.experiments3(filename='diagnostics_time_block.json')
async def test_driver_ui_time_block(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        load_json,
        filter_time,
        expected_time,
        expected_header,
):
    candidates.set_response_reasons(
        {'efficiency/driver_weariness': [f'blocked till {filter_time}']}, {},
    )

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    expected_response = load_json('ui_time_block.json')
    expected_response['items'][2]['detail'] = expected_time
    expected_response['items'][0]['subtitle'] = expected_header
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'till,expected_response',
    [
        ('2020-01-02T20:10:00.000+0000', 'ui_activity.json'),
        ('2020-01-01T18:59:00.000+0000', 'ui_activity_less_than_minute.json'),
    ],
)
@pytest.mark.now('2020-01-01T19:00:00.000Z')
@pytest.mark.experiments3(filename='diagnostics_time_block.json')
async def test_driver_ui_time_reason(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        load_json,
        expected_response,
        till,
):
    candidates.set_response_reasons(
        {
            'efficiency/driver_metrics': [
                f'blocked until {till} UTC, ' 'reason: low_activity',
            ],
        },
        {},
    )

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    expected_response = load_json(expected_response)
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'candidates_details,expected_response',
    [
        (
            {'partners/fetch_license_experience_classes': ['experience']},
            'ui_license_experience.json',
        ),
        (
            {'some_filter': ['by reasons_list: reason1, reason2']},
            'ui_reasons_list.json',
        ),
    ],
    ids=['single_reason', 'reason_details'],
)
@pytest.mark.experiments3(filename='diagnostics_parsers.json')
async def test_driver_ui_parsers(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        load_json,
        candidates_details,
        expected_response,
):
    candidates.set_response_reasons(candidates_details, {})

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    expected_response = load_json(expected_response)
    assert response.json() == expected_response


@pytest.mark.experiments3(filename='diagnostics_nested_screens.json')
@pytest.mark.parametrize(
    'qc_cpp_response,candidates_response,fleet_parks_response,out_file',
    [
        (
            [
                {
                    'code': 'branding',
                    'modified': '2019-02-07T17:28:23.009000Z',
                    'present': {'sanctions': ['sticker_off']},
                },
            ],
            {'some_filter': []},
            None,
            'ui_nested_screens.json',
        ),
        (
            [
                {
                    'code': 'branding',
                    'modified': '2019-02-07T17:28:23.009000Z',
                    'present': {'sanctions': []},
                },
            ],
            {'some_filter': []},
            None,
            'ui_nested_screens_second_good.json',
        ),
        (
            [
                {
                    'code': 'branding',
                    'modified': '2019-02-07T17:28:23.009000Z',
                    'present': {},
                },
            ],
            {'some_filter': []},
            None,
            'ui_nested_screens_second_good.json',
        ),
        (
            [{'code': 'branding', 'modified': '2019-02-07T17:28:23.009000Z'}],
            {'some_filter': []},
            None,
            'ui_nested_screens_second_good.json',
        ),
        ([], {'some_filter': []}, None, 'ui_nested_screens_second_good.json'),
        (
            [
                {
                    'code': 'branding',
                    'modified': '2019-02-07T17:28:23.009000Z',
                    'present': {'sanctions': ['sticker_off']},
                },
            ],
            {},
            None,
            'ui_nested_screens_first_good.json',
        ),
        (
            [
                {
                    'code': 'branding',
                    'modified': '2019-02-07T17:28:23.009000Z',
                    'present': {'sanctions': []},
                },
            ],
            {},
            None,
            'ui_nested_screens_all_good.json',
        ),
        (
            [
                {
                    'code': 'branding',
                    'modified': '2019-02-07T17:28:23.009000Z',
                    'present': {'sanctions': ['sticker_off']},
                },
            ],
            {},
            SELF_EMPLOYED_PARK,
            'ui_nested_screens_first_good_2_warnings.json',
        ),
        (
            None,
            {},
            SELF_EMPLOYED_PARK,
            'ui_nested_screens_first_good_invalid_bankprops.json',
        ),
        (None, {}, NOT_SELF_EMPLOYED_PARK, 'ui_nested_screens_all_good.json'),
    ],
)
async def test_driver_ui_restrictions_nested_screens(
        taxi_driver_diagnostics,
        candidates,
        driver_profiles,
        mock_fleet_parks_list,
        load_json,
        qc_cpp,
        qc_cpp_response,
        candidates_response,
        fleet_parks_response,
        out_file,
):
    driver_profiles.set_contractor_data(
        utils.PARK_CONTRACTOR_PROFILE_ID, vehicle_id='12345',
    )
    auth_headers = utils.get_auth_headers().copy()
    if qc_cpp_response is not None:
        qc_cpp.set_exams(utils.PARK_ID + '_12345', qc_cpp_response)
    if fleet_parks_response is not None:
        mock_fleet_parks_list.set_parks([fleet_parks_response])
    else:
        mock_fleet_parks_list.set_parks([])
    candidates.set_response_reasons(candidates_response, {})

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=auth_headers,
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json(out_file)


@pytest.mark.experiments3(filename='diagnostics_nested_screens.json')
async def test_driver_ui_restrictions_empty_nested_screen(
        taxi_driver_diagnostics, candidates, mock_fleet_parks_list, load_json,
):
    candidates.set_response_reasons({'some_filter': []}, {})
    mock_fleet_parks_list.set_parks([])

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json('ui_empty_nested_screen.json')


@pytest.mark.experiments3(filename='diagnostics_empty_ok.json')
async def test_driver_ui_restrictions_empty_ok(
        taxi_driver_diagnostics, mock_fleet_parks_list, load_json,
):
    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json('ui_empty.json')


@pytest.mark.experiments3(filename='diagnostics_empty_ok.json')
@pytest.mark.config(DRIVER_DIAGNOSTICS_CHECK_PROVIDERS=True)
async def test_driver_ui_restrictions_unsupported_provider(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        driver_profiles,
        load_json,
):
    driver_profiles.set_contractor_data(
        utils.PARK_CONTRACTOR_PROFILE_ID, providers=[],
    )
    candidates.set_response_reasons(
        {},
        {'partners/fetch_exams_classes': ['econom by exams: exam1, exam2']},
    )

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json('ui_unsupported_provider.json')


@pytest.mark.parametrize(
    'park_categories,expected_response,reasons,details',
    [
        (
            ['econom', 'comfortplus', 'business', 'ultimate'],
            'ui_class_block.json',
            {'infra/fetch_profile_classes': []},
            {
                'partners/fetch_exams_classes': [
                    'econom by exams: exam1, exam2',
                ],
                'efficiency/fetch_tags_classes': [
                    'econom by tags: tag1, tag2, hidden_reason_tag',
                ],
                'infra/fetch_profile_classes': [
                    'econom by grade',
                    'comfortplus by requirements: req1, req2',
                    'business by requirements: req1',
                ],
                'infra/fetch_final_classes': ['econom by final result'],
            },
        ),
        (
            ['econom'],
            'ui_single_available_class_blocked.json',
            {},
            {'partners/fetch_exams_classes': ['econom by exams: exam1']},
        ),
    ],
)
@pytest.mark.experiments3(filename='diagnostics_classes_block.json')
async def test_driver_ui_restrictions_class_block(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        driver_categories_api,
        load_json,
        expected_response,
        reasons,
        details,
        park_categories,
):
    candidates.set_response_reasons(reasons, details)
    driver_categories_api.set_categories(park_categories)

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.parametrize(
    'park_categories,expected_response,reasons,details',
    [
        (
            ['econom', 'business', 'comfortplus', 'maybach', 'minivan'],
            'ui_geozone_classes_blocked.json',
            {'some_filter': []},
            {
                'partners/fetch_exams_classes': ['econom by exams: exam1'],
                'infra/fetch_profile_classes': [
                    'comfortplus by requirements: req1',
                ],
                'infra/fetch_final_classes': ['econom by final result'],
            },
        ),
        (
            ['econom', 'maybach'],
            'ui_all_classes_blocked_geozone.json',
            {},
            {'partners/fetch_exams_classes': ['econom by exams: exam1']},
        ),
    ],
)
@pytest.mark.experiments3(filename='diagnostics_classes_block.json')
async def test_driver_ui_restrictions_zone_categories(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        driver_categories_api,
        load_json,
        expected_response,
        reasons,
        details,
        park_categories,
):
    candidates.set_response_reasons(reasons, details)
    driver_categories_api.set_categories(park_categories)

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.experiments3(
    filename='diagnostics_classes_block_tariffs_redirect.json',
)
async def test_driver_ui_restrictions_class_block_tariffs_redirect(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        driver_categories_api,
        load_json,
):
    candidates.set_response_reasons(
        {},
        {
            'efficiency/fetch_tags_classes': [
                'econom by tags: hidden_reason_tag',
            ],
            'infra/fetch_profile_classes': [
                'econom by grade',
                'comfortplus by requirements: req1, req2',
            ],
        },
    )
    driver_categories_api.set_categories(['econom', 'comfortplus'])

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'ui_all_classes_block_tariffs_redirect.json',
    )


@pytest.mark.driver_tags_match(
    dbid='park_id1', uuid='driver_id1', tags=['tag1'],
)
@pytest.mark.config(
    DRIVER_DIAGNOSTICS_TAGS_SETTINGS={
        '__default__': {},
        'moscow': {'tag1': {'details': ['some_text']}},
    },
)
@pytest.mark.experiments3(filename='diagnostics_tags_provider.json')
async def test_driver_ui_restrictions_tags_provider(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        driver_tags_mocks,
        load_json,
):
    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert driver_tags_mocks.has_calls()
    assert response.json() == load_json('ui_tags_provider.json')


@pytest.mark.experiments3(filename='diagnostics_deptrans_provider.json')
@pytest.mark.parametrize(
    'skipped',
    [
        pytest.param(
            True,
            id='Supported zones empty',
            marks=[
                pytest.mark.config(
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
                        'supported_categories': ['econom'],
                    },
                ),
                pytest.mark.driver_tags_match(
                    dbid='park_id1',
                    uuid='driver_id1',
                    tags=['deptrans_driver_status_integration_enabled'],
                ),
            ],
        ),
        pytest.param(
            True,
            id='Supported categories empty',
            marks=[
                pytest.mark.config(
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={
                        'supported_zones': ['moscow'],
                    },
                ),
                pytest.mark.driver_tags_match(
                    dbid='park_id1',
                    uuid='driver_id1',
                    tags=['deptrans_driver_status_integration_enabled'],
                ),
            ],
        ),
        pytest.param(
            True,
            id='Skip by category',
            marks=[
                pytest.mark.config(
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
                        'supported_categories': ['courier'],
                    },
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={
                        'supported_zones': ['moscow'],
                    },
                ),
            ],
        ),
        pytest.param(
            True,
            id='Skip by zone',
            marks=[
                pytest.mark.config(
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
                        'supported_categories': ['econom'],
                    },
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={
                        'supported_zones': ['night_city'],
                    },
                ),
            ],
        ),
        pytest.param(
            True,
            id='Skip by tag',
            marks=[
                pytest.mark.config(
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
                        'supported_categories': ['econom'],
                    },
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={
                        'supported_zones': ['moscow'],
                    },
                ),
                pytest.mark.driver_tags_match(
                    dbid='park_id1',
                    uuid='driver_id1',
                    tags=['deptrans_driver_status_integration_enabled'],
                ),
            ],
        ),
        pytest.param(
            False,
            id='Gotcha!',
            marks=[
                pytest.mark.config(
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
                        'supported_categories': ['econom'],
                    },
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={
                        'supported_zones': ['moscow'],
                    },
                ),
            ],
        ),
    ],
)
async def test_driver_ui_restrictions_deptrans_provider(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        driver_categories_api,
        driver_tags_mocks,
        load_json,
        skipped,
):
    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert driver_tags_mocks.has_calls()
    assert driver_categories_api.has_calls()
    if skipped:
        assert response.json() == {
            'items': [],
            'bottom_items': [],
            'meta': {'reasons': []},
        }
    else:
        assert response.json() == load_json('ui_deptrans_provider.json')


@pytest.mark.experiments3(filename='diagnostics_absolute_block.json')
async def test_driver_ui_absolute_block_fullscreen(
        taxi_driver_diagnostics, mock_fleet_parks_list, candidates, load_json,
):
    candidates.set_response_reasons({'infra/deactivated_park_v2': []}, {})

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json('ui_absolute_block_fullscreen.json')


@pytest.mark.experiments3(filename='diagnostics_required_provider.json')
async def test_driver_ui_restrictions_required_provider_failed(
        taxi_driver_diagnostics, mock_fleet_parks_list, candidates, load_json,
):
    candidates.set_error()

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }


@pytest.mark.experiments3(filename='diagnostics_message_action.json')
async def test_driver_ui_zone_not_found(
        taxi_driver_diagnostics, mock_fleet_parks_list, load_json,
):
    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json={'position': {'lon': 10, 'lat': 20}, 'client_reasons': []},
    )
    assert response.status_code == 200
    assert response.json() == load_json('ui_zone_not_found.json')


@pytest.mark.experiments3(filename='diagnostics_coordinates_not_found.json')
async def test_driver_ui_coordinates_not_found(
        taxi_driver_diagnostics, mock_fleet_parks_list, load_json,
):
    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(position=None),
    )
    assert response.status_code == 200
    assert response.json() == load_json('ui_coordinates_not_found.json')


@pytest.mark.experiments3(filename='diagnostics_driver_no_car.json')
async def test_driver_ui_restrictions_driver_no_car(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        driver_profiles,
        load_json,
):
    driver_profiles.set_contractor_data(
        utils.PARK_CONTRACTOR_PROFILE_ID, vehicle_id=None,
    )
    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json('ui_driver_no_car.json')


@pytest.mark.parametrize(
    'dp_blocklists,expected_response',
    [
        (
            {
                'DriverCarBlacklistedTemp': {
                    'message': (
                        'Машина временно отключена от заказов. Причина:'
                        ' car block. Блокировка снимется через 3 дней'
                    ),
                    'till': '2020-01-02T20:10:00.0+0000',
                    'title': 'Доступ приостановлен',
                },
            },
            'ui_time_blocklist.json',
        ),
        (
            {
                'DriverLicenseBlacklisted': {
                    'message': (
                        'Ваша лицензия в чёрном списке. Обратитесь '
                        'в службу поддержки.'
                    ),
                    'title': 'Доступ запрещен',
                },
            },
            'ui_blocklist_fullscreen.json',
        ),
    ],
)
@pytest.mark.now('2020-01-01T19:00:00.000Z')
@pytest.mark.experiments3(filename='diagnostics_absolute_block.json')
async def test_driver_ui_old_blocklists(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        driver_protocol,
        load_json,
        expected_response,
        dp_blocklists,
):
    driver_protocol.set_driver_blocks({}, dp_blocklists)

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.parametrize(
    'details, expected_response',
    [
        ({'partners/blocklist': ['blocklist: 111, 333']}, 'ui_blocklist.json'),
        ({'partners/blocklist': ['blocklist: 222']}, 'ui_blocklist_temp.json'),
        ({'partners/blocklist': ['blocklist: 333']}, 'ui_empty.json'),
        ({'partners/blocklist': ['block: 111, 222']}, 'ui_empty.json'),
    ],
)
@pytest.mark.now('2020-01-01T19:00:00.000Z')
@pytest.mark.experiments3(filename='diagnostics_absolute_block.json')
async def test_driver_ui_blocklist(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        blocklist,
        candidates,
        load_json,
        details,
        expected_response,
):
    blocklist.set_block(
        '111', {'text': 'Причина блокировки', 'mechanics': 'old_blocklist'},
    )
    blocklist.set_block(
        '222',
        {
            'text': 'Причина временной блокировки',
            'mechanics': 'old_blocklist',
            'till': '2020-01-01T19:00:10.0+0000',
        },
    )
    candidates.set_response_reasons({}, details)

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.experiments3(filename='diagnostics_dkb_childchairs.json')
async def test_driver_ui_restrictions_invisible(
        taxi_driver_diagnostics, mock_fleet_parks_list, candidates, load_json,
):
    candidates.set_response_reasons({'infra/meta_status_searchable': []}, {})

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json('ui_nested_screens_all_good.json')


@pytest.mark.experiments3(filename='diagnostics_kis_art_provider.json')
@pytest.mark.parametrize(
    'park_id, right_response_json',
    [
        ('park_enabled', 'ui_kis_art_enabled.json'),
        ('park_disabled', 'ui_kis_art_disabled.json'),
    ],
)
async def test_driver_ui_restictions_driver_kis_art_check(
        taxi_driver_diagnostics, park_id, load_json, right_response_json,
):
    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(park_id=park_id),
        json=utils.get_default_body(position=None),
    )
    assert response.status_code == 200
    assert response.json() == load_json(right_response_json)
