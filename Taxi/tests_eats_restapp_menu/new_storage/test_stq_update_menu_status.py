import pytest

PARTNER_ID = '777'
PLACE_ID = '109151'
MENU_REVISION = 'Mi4y'
UPDATE_JOB_ID = '86fde2da-3c74-4408-909c-985a8b3c3bc1'


@pytest.mark.experiments3(filename='transitional_settings.json')
@pytest.mark.parametrize(
    (
        'core_menu_called',
        'disable_called',
        'db_statuses',
        'core_json',
        'disable_dt',
    ),
    [
        pytest.param(
            0,
            0,
            ['applied', 'applied'],
            'core_menu_autodisable.json',
            '2021-02-02T23:00:00+00:00',
            id='no autodisable',
        ),
        pytest.param(
            1,
            0,
            ['applied', 'applied', 'not_applicable'],
            'core_menu_autodisable.json',
            '2021-02-02T23:00:00+00:00',
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_MENU_AUTO_DISABLE_PLACES={
                        'enabled': True,
                        'active_items_threshold': 1,
                        'activation_shift': 60,
                    },
                ),
            ],
            id='threshold:1',
        ),
        pytest.param(
            1,
            1,
            ['applied', 'applied', 'not_applicable'],
            'core_menu_autodisable.json',
            '2021-02-02T23:00:00+00:00',
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_MENU_AUTO_DISABLE_PLACES={
                        'enabled': True,
                        'active_items_threshold': 2,
                        'activation_shift': 120,
                    },
                ),
            ],
            id='threshold:2, shift:120',
        ),
        pytest.param(
            1,
            1,
            ['applied', 'applied', 'not_applicable'],
            'core_menu_autodisable_cat.json',
            '2021-02-01T01:15:00+00:00',
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_MENU_AUTO_DISABLE_PLACES={
                        'enabled': True,
                        'active_items_threshold': 2,
                        'activation_shift': 15,
                    },
                ),
            ],
            id='threshold:2, shift:15, category',
        ),
        pytest.param(
            1,
            1,
            ['applied', 'applied', 'not_applicable'],
            'core_menu_autodisable_cat2.json',
            '2021-03-11T01:15:00+00:00',
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_MENU_AUTO_DISABLE_PLACES={
                        'enabled': True,
                        'active_items_threshold': 2,
                        'activation_shift': 15,
                    },
                ),
            ],
            id='threshold:2, shift:15, category, two',
        ),
    ],
)
@pytest.mark.now('2021-01-01T12:00:00Z')
async def test_ns_stq_update_menu_status_success_autodisable(
        stq_runner,
        mockserver,
        stq,
        pg_get_menus,
        load_json,
        core_menu_called,
        disable_called,
        db_statuses,
        core_json,
        disable_dt,
):
    @mockserver.json_handler(
        f'/eats-core-restapp/v1/place-menu/{UPDATE_JOB_ID}/status',
    )
    def core_menu_update_status(request):
        return {'is_success': True, 'status': 'success', 'errors': []}

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu',
    )
    def core_menu_get(request):
        return load_json(core_json)

    @mockserver.json_handler('/eats-core-restapp/v1/places/disable')
    def core_places_disable(request):
        req_json = request.json
        assert req_json['disable_details']['reactivated_at'] == disable_dt
        assert req_json['place_ids'] == [int(PLACE_ID)]
        return {'payload': {'disabled_places': [int(PLACE_ID)], 'errors': []}}

    await stq_runner.eats_restapp_menu_update_menu_status.call(
        task_id=MENU_REVISION,
        kwargs={
            'place_id': int(PLACE_ID),
            'revision': MENU_REVISION,
            'job_id': UPDATE_JOB_ID,
            'auto_disable': True,
        },
        expect_fail=False,
    )

    assert [it['status'] for it in pg_get_menus()] == db_statuses

    assert core_menu_update_status.times_called == 1
    assert core_menu_get.times_called == core_menu_called
    assert core_places_disable.times_called == disable_called
    assert stq.eats_restapp_menu_update_menu_status.times_called == 0
