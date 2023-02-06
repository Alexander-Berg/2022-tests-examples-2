import pytest


DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_batch_skip_arrive_screen',
    consumers=['cargo-orders/taximeter-api'],
    clauses=[],
    default_value={
        'enable': True,
        'skip_arrive_screen': True,
        'pickup_label_tanker_key': 'actions.pickup.title',
        'sms_code_label_tanker_key': 'actions.pickup.sms_code.title',
    },
)
@pytest.mark.translations(
    cargo={
        'actions.photofixation.instructions_dialog.heading': {
            'ru': 'Заголовок экшена',
        },
        'actions.photofixation.instructions_dialog.details': {
            'ru': 'my_details',
        },
        'actions.photofixation.instructions_dialog.accept_button_title': {
            'ru': 'ins_accept_title',
        },
        'actions.photofixation.photo_dialog.title': {'ru': 'ins_title'},
        'actions.photofixation.confirmation_dialog.title': {
            'ru': 'conf_dialog',
        },
        'actions.photofixation.confirmation_dialog.confirm_button_title': {
            'ru': 'conf_but_title',
        },
        'actions.photofixation.confirmation_dialog.retake_button_title': {
            'ru': 'retake',
        },
    },
)
@pytest.mark.parametrize('enabled', [True, False])
async def test_photofixation_action_pickup_arrvied(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        waybill_state,
        mock_driver_tags_v1_match_profile,
        experiments3,
        enabled,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_photofixation_settings',
        consumers=['cargo-orders/photofixation-settings'],
        clauses=[],
        default_value={
            'take_picture_enabled': enabled,
            'preview_enabled': True,
        },
    )
    await taxi_cargo_orders.invalidate_caches()

    waybill_state.set_segment_status('pickup_arrived')

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    photofixation_action = {
        'confirmation_dialog': {
            'confirm_button_title': 'conf_but_title',
            'retake_button_title': 'retake',
            'title': 'conf_dialog',
        },
        'instructions_dialog': {
            'accept_button_title': 'ins_accept_title',
            'heading': 'Заголовок экшена',
        },
        'photo_dialog': {'title': 'ins_title'},
        'type': 'photofixation_take_picture',
    }
    if enabled:
        assert (
            photofixation_action in response.json()['current_point']['actions']
        )
    else:
        assert (
            photofixation_action
            not in response.json()['current_point']['actions']
        )


CARGO_PHOTOFIXATION_TRANSLATIONS = {
    'actions.photofixation.instructions_dialog.heading': {
        'ru': 'Заголовок экшена',
    },
    'actions.photofixation.instructions_dialog.details': {
        'ru': 'Посылка: №%(number)s',
    },
    'actions.photofixation.instructions_dialog.accept_button_title': {
        'ru': 'ins_accept_title',
    },
    'actions.photofixation.photo_dialog.title': {'ru': 'ins_title'},
    'actions.photofixation.confirmation_dialog.title': {'ru': 'conf_dialog'},
    'actions.photofixation.confirmation_dialog.confirm_button_title': {
        'ru': 'conf_but_title',
    },
    'actions.photofixation.confirmation_dialog.retake_button_title': {
        'ru': 'retake',
    },
    'actions.photofixation.preview_dialog.heading': {'ru': 'preview_title'},
    'actions.photofixation.preview_dialog.details': {
        'ru': 'preview_dialog_details',
    },
    'actions.photofixation.preview_dialog.continue_button_title': {
        'ru': 'preview_dialog_continue_button_title',
    },
    'actions.photofixation.dialogs_order.template': {
        'ru': 'Шаг %(order)s из %(limit)s',
    },
}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_batch_skip_arrive_screen',
    consumers=['cargo-orders/taximeter-api'],
    clauses=[],
    default_value={
        'enable': True,
        'skip_arrive_screen': True,
        'pickup_label_tanker_key': 'actions.pickup.title',
        'sms_code_label_tanker_key': 'actions.pickup.sms_code.title',
    },
)
@pytest.mark.translations(cargo=CARGO_PHOTOFIXATION_TRANSLATIONS)
@pytest.mark.parametrize(
    'preview_enabled,delivery_photofixation_enabled',
    [[False, False], [True, False], [False, True], [True, True]],
)
async def test_photofixation_action_delivery_arrvied(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        waybill_state,
        mock_driver_tags_v1_match_profile,
        mockserver,
        preview_enabled,
        delivery_photofixation_enabled,
        experiments3,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_photofixation_settings',
        consumers=['cargo-orders/photofixation-settings'],
        clauses=[],
        default_value={
            'take_picture_enabled': delivery_photofixation_enabled,
            'preview_enabled': preview_enabled,
        },
    )
    await taxi_cargo_orders.invalidate_caches()
    photo_id = '123e4567-e89b-12d3-a456-426614174000'
    photo = {
        'id': photo_id,
        'claim_point_id': waybill_state.waybills['waybill-ref']['execution'][
            'points'
        ][0]['claim_point_id'],
        'status': 'uploaded',
        'url': (
            'http://cargo-photofixation.s3.mdst.yandex.net'
            + '/photos/'
            + photo_id
            + '_filename.jpeg'
        ),
    }

    @mockserver.json_handler('/cargo-photofixation/v1/order/photos')
    def _mock_photofixation_order_photos(request):
        return mockserver.make_response(
            status=200,
            json={'cargo_order_id': 'my_cargo_order_id', 'photos': [photo]},
        )

    waybill_state.set_segment_status('delivery_arrived')

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    photofixation_preview = {
        'preview_dialog': {
            'details': 'preview_dialog_details',
            'photo_url': photo['url'],
            'heading': 'preview_title',
            'continue_button_title': 'preview_dialog_continue_button_title',
        },
        'type': 'photofixation_preview',
    }
    photofixation = {
        'confirmation_dialog': {
            'confirm_button_title': 'conf_but_title',
            'retake_button_title': 'retake',
            'title': 'conf_dialog',
        },
        'instructions_dialog': {
            'accept_button_title': 'ins_accept_title',
            'heading': 'Заголовок экшена',
        },
        'photo_dialog': {'title': 'ins_title'},
        'type': 'photofixation_take_picture',
    }
    if preview_enabled and delivery_photofixation_enabled:
        photofixation_preview['preview_dialog']['title'] = 'Шаг 1 из 2'
        photofixation['instructions_dialog']['title'] = 'Шаг 2 из 2'
    if preview_enabled:
        assert (
            photofixation_preview
            in response.json()['current_point']['actions']
        )
    else:
        assert (
            photofixation_preview
            not in response.json()['current_point']['actions']
        )
    if delivery_photofixation_enabled:
        assert photofixation in response.json()['current_point']['actions']
    else:
        assert photofixation not in response.json()['current_point']['actions']


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_batch_skip_arrive_screen',
    consumers=['cargo-orders/taximeter-api'],
    clauses=[],
    default_value={
        'enable': True,
        'skip_arrive_screen': True,
        'pickup_label_tanker_key': 'actions.pickup.title',
        'sms_code_label_tanker_key': 'actions.pickup.sms_code.title',
    },
)
@pytest.mark.translations(cargo=CARGO_PHOTOFIXATION_TRANSLATIONS)
@pytest.mark.parametrize(
    'preview_enabled,delivery_photofixation_enabled',
    [[False, False], [True, False], [False, True], [True, True]],
)
async def test_photofixation_action_delivery_arrvied_with_external_order_id(
        taxi_cargo_orders,
        mock_waybill_info,
        default_order_id,
        waybill_state,
        mock_driver_tags_v1_match_profile,
        mockserver,
        preview_enabled,
        delivery_photofixation_enabled,
        experiments3,
        external_order_id='task1',
):
    waybill_state.waybills['waybill-ref']['execution']['points'][0][
        'external_order_id'
    ] = external_order_id
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_photofixation_settings',
        consumers=['cargo-orders/photofixation-settings'],
        clauses=[],
        default_value={
            'take_picture_enabled': delivery_photofixation_enabled,
            'preview_enabled': preview_enabled,
        },
    )
    await taxi_cargo_orders.invalidate_caches()
    photo_id = '123e4567-e89b-12d3-a456-426614174000'
    photo = {
        'id': photo_id,
        'claim_point_id': waybill_state.waybills['waybill-ref']['execution'][
            'points'
        ][0]['claim_point_id'],
        'status': 'uploaded',
        'url': (
            'http://cargo-photofixation.s3.mdst.yandex.net'
            + '/photos/'
            + photo_id
            + '_filename.jpeg'
        ),
    }

    @mockserver.json_handler('/cargo-photofixation/v1/order/photos')
    def _mock_photofixation_order_photos(request):
        return mockserver.make_response(
            status=200,
            json={'cargo_order_id': 'my_cargo_order_id', 'photos': [photo]},
        )

    waybill_state.set_segment_status('delivery_arrived')

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    photofixation_preview = {
        'preview_dialog': {
            'details': 'preview_dialog_details',
            'photo_url': photo['url'],
            'heading': 'preview_title',
            'continue_button_title': 'preview_dialog_continue_button_title',
        },
        'type': 'photofixation_preview',
    }
    photofixation = {
        'confirmation_dialog': {
            'confirm_button_title': 'conf_but_title',
            'retake_button_title': 'retake',
            'title': 'conf_dialog',
        },
        'instructions_dialog': {
            'accept_button_title': 'ins_accept_title',
            'details': 'Посылка: №' + external_order_id,
            'heading': 'Заголовок экшена',
        },
        'photo_dialog': {'title': 'ins_title'},
        'type': 'photofixation_take_picture',
    }
    if preview_enabled and delivery_photofixation_enabled:
        photofixation_preview['preview_dialog']['title'] = 'Шаг 1 из 2'
        photofixation['instructions_dialog']['title'] = 'Шаг 2 из 2'
    if preview_enabled:
        assert (
            photofixation_preview
            in response.json()['current_point']['actions']
        )
    else:
        assert (
            photofixation_preview
            not in response.json()['current_point']['actions']
        )
    if delivery_photofixation_enabled:
        assert photofixation in response.json()['current_point']['actions']
    else:
        assert photofixation not in response.json()['current_point']['actions']
