# pylint: disable=no-else-return,too-many-lines,len-as-condition
import urllib.parse

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

DEFAULT_CARGO_REF_ID = 'order/9db1622e-582d-4091-b6fc-4cb2ffdc12c0'


def set_points_resolved(waybill: dict, point_indexes: list):
    for i in point_indexes:
        point = waybill['execution']['points'][i]
        point['visit_status'] = 'visited'
        point['is_resolved'] = True


def get_client_title(point_type: str, client_index: int):
    if point_type == 'source':
        return 'Отправитель ' + str(client_index)
    elif point_type == 'destination':
        return 'Получатель ' + str(client_index)
    else:
        return 'Возврат отправителю ' + str(client_index)


def get_exchange_parcels_title(point_type: str, number_of_parcels: int):
    plurals = ''
    if number_of_parcels == 1:
        plurals = 'посылку'
    elif number_of_parcels == 2:
        plurals = 'посылки'
    else:
        plurals = 'посылок'

    action = ''
    if point_type == 'source':
        action = 'Получить'
    elif point_type == 'destination':
        action = 'Вручить'
    else:
        action = 'Вернуть'

    return f'{action} {number_of_parcels} {plurals}'


def get_exchanged_parcel_title(point_type: str):
    if point_type == 'source':
        return 'Посылка получена'
    elif point_type == 'destination':
        return 'Посылка вручена'
    else:
        return 'Посылка возвращена'


def get_exchanged_parcels_title(point_type: str):
    if point_type == 'source':
        return 'Посылки получены'
    elif point_type == 'destination':
        return 'Посылки вручены'
    else:
        return 'Посылки возвращены'


def build_porch_floor_flat(address: dict):
    if (
            'porch' not in address
            and 'floor' not in address
            and 'flat' not in address
    ):
        return None

    pff = ''
    if 'porch' in address:
        pff = f"""{address['porch']} Подъезд"""
    if 'floor' in address:
        if pff != '':
            pff += ', '
        pff += f"""{address['floor']} Этаж"""
    if 'flat' in address:
        if pff != '':
            pff += ', '
        pff += f"""{address['flat']} Квартира"""
    return pff


def build_positions(positions: list):
    plurals = ''
    if len(positions) == 1:
        plurals = 'позиция'
    elif len(positions) == 2:
        plurals = 'позиции'
    else:
        plurals = 'позиций'

    return f'{len(positions)} {plurals}'


def build_point_parcel_info_payload(tag: str, point: dict, parcel: dict):
    payload = {
        'type': 'constructor',
        'title': 'Посылка',
        'tag': tag,
        'items': [],
    }  # type: dict

    if 'external_order_id' in parcel:
        parcel_number = {
            'type': 'default',
            'title': 'Номер посылки',
            'reverse': True,
            'horizontal_divider_type': 'bottom_bold_s',
        }
        parcel_number['subtitle'] = parcel['external_order_id']
        parcel_number['show_right_icon_background'] = True
        parcel_number['right_icon'] = 'copy_content'
        parcel_number['payload'] = {
            'type': 'action_copy',
            'notification': {'text': 'Номер посылки скопирован'},
            'text_to_copy': parcel['external_order_id'],
        }
        payload['items'].append(parcel_number)

    positions = {
        'type': 'detail',
        'title': build_positions(parcel['items']),
        'accent_title': True,
        'horizontal_divider_type': 'bottom_gap',
    }
    if 'external_order_cost' in parcel:
        positions['detail'] = parcel['external_order_cost']
    payload['items'].append(positions)

    for item in parcel['items']:
        payload['items'].append(
            {
                'type': 'detail',
                'title': item['title'],
                'detail': f"""{item['quantity']}""",
                'horizontal_divider_type': 'bottom_gap',
            },
        )

    payload['items'].append(
        {
            'type': 'multi_section',
            'orientation': 'horizontal',
            'horizontal_divider_type': 'none',
            'use_item_divider_type': False,
            'items': [
                {
                    'type': 'button_subtitle',
                    'subtitle': 'Поддержка',
                    'icon': {'icon_type': 'help'},
                    'payload': {'type': 'navigate_support_cargo'},
                },
            ],
        },
    )

    return payload


def build_point_parcel_list_payload(
        tag_prefix: str, point: dict, parcels: list,
):
    payload = {
        'type': 'constructor',
        'title': get_exchange_parcels_title(point['type'], len(parcels)),
        'tag': f'{tag_prefix}/parcel_list',
        'items': [],
    }

    for i, parcel in enumerate(parcels):
        parcel_number = {
            'type': 'tip_detail',
            'title': 'Посылка',
            'accent_title': True,
            'horizontal_divider_type': 'bottom_gap',
            'reverse': True,
            'left_tip': {
                'background_color': 'minor_bg',
                'text': f'{i + 1}',
                'text_color': 'main_text',
            },
        }
        if 'external_order_id' in parcel:
            parcel_number['subtitle'] = parcel['external_order_id']
        else:
            parcel_number['reverse'] = False

        positions = {
            'type': 'detail',
            'title': build_positions(parcel['items']),
            'payload': build_point_parcel_info_payload(
                f'{tag_prefix}/parcel_info', point, parcel,
            ),
            'right_icon': 'navigate',
            'horizontal_divider_type': 'none',
        }
        if 'external_order_cost' in parcel:
            positions['detail'] = parcel['external_order_cost']

        payload['items'].append(
            {
                'type': 'multi_section',
                'horizontal_divider_type': 'bottom_bold_s',
                'orientation': 'vertical',
                'use_item_divider_type': False,
                'items': [parcel_number, positions],
            },
        )

    return payload


def build_multi_state_item(point: dict, is_multipoint_claim: bool):
    return {
        'type': 'multi_state',
        'horizontal_divider_type': 'none',
        'initial_state': 'exchange_init',
        'states': {
            'exchange_init': {
                'type': 'button',
                'title': (
                    get_exchanged_parcels_title(point['type'])
                    if is_multipoint_claim
                    else get_exchanged_parcel_title(point['type'])
                ),
                'accent': True,
                'horizontal_divider_type': 'none',
                'payload': {
                    'type': 'multi_state_select',
                    'target_state': 'exchange_confirm',
                },
            },
            'exchange_confirm': {
                'type': 'multi_section',
                'orientation': 'horizontal',
                'use_item_divider_type': False,
                'horizontal_divider_type': 'none',
                'items': [
                    {
                        'type': 'button',
                        'title': 'Назад',
                        'style': 'margin_top_bottom_start',
                        'accent': False,
                        'payload': {
                            'type': 'multi_state_select',
                            'target_state': 'exchange_init',
                        },
                    },
                    {
                        'type': 'button',
                        'title': 'Подтвердить',
                        'accent': True,
                        'payload': {
                            'type': 'cargo_package_exchange',
                            'point_id': point['claim_point_id'],
                        },
                    },
                ],
            },
        },
    }


def build_multi_exchange_items(point: dict, parcels: list, index: int):
    assert len(parcels) != 0

    if len(parcels) == 1:  # common claim
        parcel = parcels[0]
        multi_section = {
            'type': 'multi_section',
            'horizontal_divider_type': 'bottom_bold_s',
            'orientation': 'vertical',
            'use_item_divider_type': False,
            'items': [],
        }  # type: dict

        parcel_number = {
            'type': 'tip_detail',
            'accent_title': True,
            'horizontal_divider_type': 'bottom_gap',
            'reverse': False,
        }
        if 'external_order_id' in parcel:
            parcel_number['subtitle'] = parcel['external_order_id']
            parcel_number['reverse'] = True
        if point['is_resolved'] is True:
            parcel_number['title'] = get_exchanged_parcel_title(point['type'])
            parcel_number['left_tip'] = {
                'text': f'{index + 1}',
                'text_color': '#029154',
                'text_color_night': '#00CA50',
                'background_color': '#1400CA50',
                'background_color_night': '#3D00CA50',
                'icon': {
                    'icon_tip': {
                        'icon': {
                            'icon_type': 'check',
                            'tint_color': 'main_bg',
                        },
                        'background_color': '#00CA50',
                        'size': 'mu_1_5',
                    },
                },
            }
        else:
            parcel_number['title'] = 'Посылка'
            parcel_number['left_tip'] = {
                'text': f'{index + 1}',
                'text_color': 'main_text',
                'background_color': 'minor_bg',
            }
        multi_section['items'].append(parcel_number)

        positions = {
            'type': 'detail',
            'title': build_positions(parcel['items']),
            'payload': build_point_parcel_info_payload(
                'constructor/cargo/multi_order/parcel_info', point, parcel,
            ),
            'right_icon': 'navigate',
            'horizontal_divider_type': 'none',
        }
        if 'external_order_cost' in parcel:
            positions['detail'] = parcel['external_order_cost']
        multi_section['items'].append(positions)

        if point['is_resolved'] is False:
            multi_section['items'].append(
                build_multi_state_item(point, is_multipoint_claim=False),
            )

        return [multi_section]
    else:  # multipoint claim
        items = []

        expandable_section = {
            'type': 'expandable_section',
            'horizontal_divider_type': 'none',
            'expand_mode_has_divider': True,
            'is_expand': False,
            'header': {
                'type': 'detail',
                'title': f'{len(parcels)} посылки',
                'title_text_style': 'title_bold',
            },
            'header_expanded': {
                'type': 'detail',
                'title': f'{len(parcels)} посылки',
                'title_text_style': 'title_bold',
                'accent_title': True,
            },
            'items_background_color': 'main_bg',
            'items': [],
        }  # type: dict

        for i, parcel in enumerate(parcels):
            item = {
                'type': 'tip_detail',
                'payload': build_point_parcel_info_payload(
                    'constructor/cargo/multi_order/parcel_info', point, parcel,
                ),
                'right_icon': 'navigate',
                'horizontal_divider_type': 'bottom_gap',
            }
            if 'external_order_id' in parcel:
                item['subtitle'] = parcel['external_order_id']
            if 'external_order_cost' in parcel:
                item['detail'] = parcel['external_order_cost']
            if point['is_resolved'] is True:
                item['title'] = get_exchanged_parcel_title(point['type'])
                item['left_tip'] = {
                    'text': f'{index + i + 1}',
                    'text_color': '#029154',
                    'text_color_night': '#00CA50',
                    'background_color': '#1400CA50',
                    'background_color_night': '#3D00CA50',
                    'icon': {
                        'icon_tip': {
                            'icon': {
                                'icon_type': 'check',
                                'tint_color': 'main_bg',
                            },
                            'background_color': '#00CA50',
                            'size': 'mu_1_5',
                        },
                    },
                }
            else:
                item['title'] = 'Посылка'
                item['left_tip'] = {
                    'text': f'{index + i + 1}',
                    'text_color': 'main_text',
                    'background_color': 'minor_bg',
                }
            expandable_section['items'].append(item)
        items.append(expandable_section)

        if point['is_resolved'] is False:
            multi_state = build_multi_state_item(
                point, is_multipoint_claim=True,
            )
            multi_state['horizontal_divider_type'] = 'bottom_bold_s'
            items.append(multi_state)

        return items


def build_point_info_payload(
        point: dict,
        parcels: list,
        client_index: int,
        instructions_deeplink=None,
):
    payload = {
        'type': 'constructor',
        'title': get_client_title(point['type'], client_index),
        'tag': 'constructor/cargo/tracking/info',
        'items': [
            {
                'type': 'default',
                'title': 'Адрес',
                'subtitle': point['address']['shortname'],
                'payload': {
                    'type': 'action_copy',
                    'notification': {'text': 'Адрес скопирован'},
                    'text_to_copy': point['address']['shortname'],
                },
                'right_icon': 'copy_content',
                'show_right_icon_background': True,
                'horizontal_divider_type': 'top',
                'reverse': True,
            },
        ],
    }

    porch_floor_flat = build_porch_floor_flat(point['address'])
    if porch_floor_flat is not None:
        payload['items'].append(
            {
                'type': 'default',
                'title': build_porch_floor_flat(point['address']),
                'horizontal_divider_type': 'top_gap',
            },
        )

    payload['items'].append(
        {
            'type': 'default',
            'title': get_client_title(point['type'], client_index),
            'subtitle': (
                point['client_name'] if 'client_name' in point else ''
            ),
            'payload': {
                'type': 'action_call_cargo',
                'point_id': f"""{point['claim_point_id']}""",
                'is_deaf': False,
                'phone_options': point['phones'],
            },
            'right_icon': 'call_right',
            'show_right_icon_background': True,
            'horizontal_divider_type': 'top_gap',
            'reverse': True,
        },
    )
    if 'comment' in point['address']:
        payload['items'].append(
            {
                'background': {'type': 'balloon'},
                'horizontal_divider_type': 'none',
                'primary_text_size': 'caption_1',
                'title': point['address']['comment'],
                'type': 'default',
            },
        )

    payload['items'].append(
        {
            'horizontal_divider_type': 'top_gap',
            'right_icon': 'navigate',
            'title': get_exchange_parcels_title(point['type'], len(parcels)),
            'payload': build_point_parcel_list_payload(
                'constructor/cargo/tracking', point, parcels,
            ),
            'type': 'default',
        },
    )

    if instructions_deeplink is not None:
        payload['items'].append(
            {
                'horizontal_divider_type': 'top_gap',
                'orientation': 'horizontal',
                'type': 'multi_section',
                'use_item_divider_type': False,
                'item_divider_type': 'regular',
                'items': [
                    {
                        'type': 'button_subtitle',
                        'subtitle': 'Инструкция',
                        'icon': {'icon_type': 'help'},
                        'payload': {
                            'type': 'deeplink',
                            'url': instructions_deeplink,
                        },
                    },
                ],
            },
        )

    return payload


def build_point_deeplink_payload(point: dict):
    params = urllib.parse.urlencode(
        {
            'cargo_ref_id': DEFAULT_CARGO_REF_ID,
            'claim_point_id': point['claim_point_id'],
        },
    )
    url = (
        f'/driver/v1/cargo-claims/v1/cargo/point-constructor-payload?{params}'
    )
    return {
        'type': 'deeplink',
        'url': (
            'taximeter://screen/server_constructor?constructor_url='
            f'{urllib.parse.quote_plus(url)}'
            '&body={"cargo_ref_id":"' + DEFAULT_CARGO_REF_ID + '"}'
        ),
        'title': 'Загрузка',
        'message': 'Подождите немного',
    }


def build_progress_item(
        point: dict,
        point_index: int,
        current_point_index: int,
        parcels: list,
        client_index: int,
        instructions_deeplink=None,
        is_deeplink_payload=False,
):
    progress_item = {
        'content': {
            'type': 'default',
            'reverse': True,
            'right_icon': 'navigate',
            'title': get_client_title(point['type'], client_index),
            'subtitle': point['address']['shortname'],
            'horizontal_divider_type': 'bottom',
            'payload': (
                build_point_deeplink_payload(point)
                if is_deeplink_payload
                else build_point_info_payload(
                    point, parcels, client_index, instructions_deeplink,
                )
            ),
        },
        'progress': {
            'tip': {
                'icon': {'icon_size': 'mu_3'},
                'size': 'mu_5',
                'type': 'tip_info',
            },
            'type': 'vertical_progress_icon',
        },
        'type': 'progress_item',
    }  # type: dict

    if point['type'] == 'source':
        progress_item['progress']['tip']['icon']['icon_type'] = 'cargo_pickup'
    elif point['type'] == 'destination':
        progress_item['progress']['tip']['icon']['icon_type'] = 'client'
    else:
        progress_item['progress']['tip']['icon']['icon_type'] = 'cargo_return'

    if point_index < current_point_index:
        progress_item['progress']['tip']['icon']['tint_color'] = 'minor_text'
    elif point_index == current_point_index:
        progress_item['progress']['tip']['icon']['tint_color'] = '#000000'
    else:
        progress_item['progress']['tip']['icon']['tint_color'] = 'main_icon'

    if point_index == current_point_index:
        progress_item['progress']['tip']['background_color'] = '#FCE000'
    else:
        progress_item['progress']['tip']['background_color'] = 'minor_bg'

    if len(parcels) > 1:
        progress_item['progress']['tip']['icon']['icon_tip'] = {
            'background_color': 'main_icon',
            'size': 'mu_2',
            'text': f'{len(parcels)}',
            'text_color': 'main_bg',
        }
    return progress_item


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'cargo_tracking_ui': '8.00'}},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_enable_cargo_taximeter_tracking_ui',
    consumers=['cargo-orders/taximeter-constructor'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
    default_value={'enabled': False},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_instructions_deeplink',
    consumers=['cargo-orders/instructions-deeplink'],
    clauses=[],
    default_value={'deeplink': 'http://test/link'},
)
async def test_cargo_constructor_ui_for_batches(
        taxi_cargo_orders,
        mock_waybill_info,
        my_triple_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
        set_segments_place_id,
        instructions_deeplink='http://test/link',
):
    # Make first 2 source points same
    set_segments_place_id(my_triple_batch_waybill_info, [0, 1], 1234)

    # Add return point
    my_triple_batch_waybill_info['execution']['points'][3][
        'is_return_required'
    ] = True

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': DEFAULT_CARGO_REF_ID},
    )
    assert response.status_code == 200
    assert response.json()['tracking_ui'] == {
        'items': [
            {
                'type': 'vertical_progress',
                'display_dividers': True,
                'line_color_day': '#F1F0ED',
                'line_color_night': '#302F2D',
                'line_width': 'mu_0_5',
                'progress_width': 'mu_7',
                'horizontal_divider_type': 'none',
                'items': [
                    build_progress_item(
                        point=my_triple_batch_waybill_info['execution'][
                            'points'
                        ][0],
                        point_index=0,
                        current_point_index=0,
                        parcels=[
                            # Second point items first cause it's destination
                            # point is visited earlier.
                            {'items': [{'title': 'Хлеб', 'quantity': 1}]},
                            {
                                'external_order_id': '111111-222222',
                                'external_order_cost': '672 ₽',
                                'items': [
                                    {'title': 'Молоко', 'quantity': 2},
                                    {'title': 'Творог', 'quantity': 3},
                                ],
                            },
                        ],
                        client_index=1,
                        instructions_deeplink=instructions_deeplink,
                    ),
                    build_progress_item(
                        point=my_triple_batch_waybill_info['execution'][
                            'points'
                        ][2],
                        point_index=1,
                        current_point_index=0,
                        parcels=[
                            {
                                'external_order_id': '444444-555555',
                                'external_order_cost': '157 ₽',
                                'items': [
                                    {'title': 'Картошка', 'quantity': 4},
                                    {'title': 'Лук', 'quantity': 1},
                                ],
                            },
                        ],
                        client_index=2,
                        instructions_deeplink=instructions_deeplink,
                    ),
                    build_progress_item(
                        point=my_triple_batch_waybill_info['execution'][
                            'points'
                        ][3],
                        point_index=2,
                        current_point_index=0,
                        parcels=[
                            {
                                'external_order_id': '444444-555555',
                                'external_order_cost': '157 ₽',
                                'items': [
                                    {'title': 'Картошка', 'quantity': 4},
                                    {'title': 'Лук', 'quantity': 1},
                                ],
                            },
                        ],
                        client_index=1,
                        instructions_deeplink=instructions_deeplink,
                    ),
                    build_progress_item(
                        point=my_triple_batch_waybill_info['execution'][
                            'points'
                        ][4],
                        point_index=3,
                        current_point_index=0,
                        parcels=[
                            {'items': [{'title': 'Хлеб', 'quantity': 1}]},
                        ],
                        client_index=2,
                        instructions_deeplink=instructions_deeplink,
                    ),
                    build_progress_item(
                        point=my_triple_batch_waybill_info['execution'][
                            'points'
                        ][5],
                        point_index=4,
                        current_point_index=0,
                        parcels=[
                            {
                                'external_order_id': '111111-222222',
                                'external_order_cost': '672 ₽',
                                'items': [
                                    {'title': 'Молоко', 'quantity': 2},
                                    {'title': 'Творог', 'quantity': 3},
                                ],
                            },
                        ],
                        client_index=3,
                        instructions_deeplink=instructions_deeplink,
                    ),
                    build_progress_item(
                        point=my_triple_batch_waybill_info['execution'][
                            'points'
                        ][8],
                        point_index=5,
                        current_point_index=0,
                        parcels=[
                            {
                                'external_order_id': '444444-555555',
                                'external_order_cost': '157 ₽',
                                'items': [
                                    {'title': 'Картошка', 'quantity': 4},
                                    {'title': 'Лук', 'quantity': 1},
                                ],
                            },
                        ],
                        client_index=1,
                        instructions_deeplink=instructions_deeplink,
                    ),
                ],
            },
        ],
        'tag': 'constructor/cargo/tracking',
        'title': 'Весь маршрут',
        'tracking_widget': {
            'current_index': 0,
            'items': [
                {'icon': 'cargo_pickup', 'count': 2},
                {'icon': 'cargo_pickup'},
                {'icon': 'client'},
                {'icon': 'client'},
                {'icon': 'client'},
                {'icon': 'cargo_return'},
            ],
        },
    }


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'cargo_tracking_ui': '8.00'}},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_enable_cargo_taximeter_tracking_ui',
    consumers=['cargo-orders/taximeter-constructor'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
    default_value={'enabled': False},
)
async def test_cargo_constructor_ui_for_batches_with_skipped_segments(
        taxi_cargo_orders,
        mock_waybill_info,
        my_triple_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
        set_segments_points_skipped,
        set_segments_place_id,
        set_current_point,
):
    set_current_point(my_triple_batch_waybill_info, 0)
    set_segments_place_id(my_triple_batch_waybill_info, [1, 2], 1234)
    # Skip one standalone point and one from same ones
    set_segments_points_skipped(
        my_triple_batch_waybill_info, segment_ids=['seg_1', 'seg_2'],
    )

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': DEFAULT_CARGO_REF_ID},
    )
    assert response.status_code == 200
    assert response.json()['tracking_ui']['items'][0]['items'] == [
        build_progress_item(
            point=my_triple_batch_waybill_info['execution']['points'][1],
            point_index=0,
            current_point_index=0,
            parcels=[
                {
                    'external_order_id': '444444-555555',
                    'external_order_cost': '157 ₽',
                    'items': [
                        {'title': 'Картошка', 'quantity': 4},
                        {'title': 'Лук', 'quantity': 1},
                    ],
                },
            ],
            client_index=1,
        ),
        build_progress_item(
            point=my_triple_batch_waybill_info['execution']['points'][3],
            point_index=1,
            current_point_index=0,
            parcels=[
                {
                    'external_order_id': '444444-555555',
                    'external_order_cost': '157 ₽',
                    'items': [
                        {'title': 'Картошка', 'quantity': 4},
                        {'title': 'Лук', 'quantity': 1},
                    ],
                },
            ],
            client_index=1,
        ),
    ]

    assert response.json()['tracking_ui']['tracking_widget'] == {
        'current_index': 0,
        'items': [{'icon': 'cargo_pickup'}, {'icon': 'client'}],
    }


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'cargo_tracking_ui': '8.00'}},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_enable_cargo_taximeter_tracking_ui',
    consumers=['cargo-orders/taximeter-constructor'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
    default_value={'enabled': False},
)
async def test_cargo_constructor_ui_for_multipoints(
        taxi_cargo_orders,
        mock_waybill_info,
        my_multipoints_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': DEFAULT_CARGO_REF_ID},
    )
    assert response.status_code == 200
    assert response.json()['tracking_ui']['items'][0]['items'] == [
        build_progress_item(
            point=my_multipoints_waybill_info['execution']['points'][0],
            point_index=0,
            current_point_index=0,
            parcels=[
                {
                    'external_order_id': '1',
                    'items': [{'title': 'some_title', 'quantity': 1}],
                },
                {
                    'external_order_id': '2',
                    'items': [{'title': 'some_title_2', 'quantity': 1}],
                },
            ],
            client_index=1,
        ),
        build_progress_item(
            point=my_multipoints_waybill_info['execution']['points'][1],
            point_index=1,
            current_point_index=0,
            parcels=[
                {
                    'external_order_id': '1',
                    'items': [{'title': 'some_title', 'quantity': 1}],
                },
            ],
            client_index=1,
        ),
        build_progress_item(
            point=my_multipoints_waybill_info['execution']['points'][2],
            point_index=2,
            current_point_index=0,
            parcels=[
                {
                    'external_order_id': '2',
                    'items': [{'title': 'some_title_2', 'quantity': 1}],
                },
            ],
            client_index=2,
        ),
    ]

    assert response.json()['tracking_ui']['tracking_widget'] == {
        'current_index': 0,
        'items': [
            {'icon': 'cargo_pickup', 'count': 2},
            {'icon': 'client'},
            {'icon': 'client'},
        ],
    }


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'cargo_tracking_ui': '8.00'}},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_enable_cargo_taximeter_tracking_ui',
    consumers=['cargo-orders/taximeter-constructor'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
    default_value={'enabled': False},
)
async def test_tracking_widget_for_batch_with_multipoints(
        taxi_cargo_orders,
        mock_waybill_info,
        my_batch_with_multipoints_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': DEFAULT_CARGO_REF_ID},
    )
    assert response.status_code == 200
    assert response.json()['tracking_ui']['tracking_widget'] == {
        'current_index': 1,
        'items': [
            {'icon': 'cargo_pickup', 'count': 2},
            {'icon': 'cargo_pickup'},
            {'icon': 'client'},
            {'icon': 'client'},
            {'icon': 'client'},
        ],
    }


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'cargo_tracking_ui': '8.00'}},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_enable_cargo_taximeter_tracking_ui',
    consumers=['cargo-orders/taximeter-constructor'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_tracking_ui_enable_deeplink_payload_for_not_current_points',  # noqa: E501
    consumers=['cargo-orders/taximeter-constructor'],
    clauses=[],
    default_value={'enable_deeplink_payload': True},
)
async def test_deeplink_for_not_current_points(
        taxi_cargo_orders,
        mock_waybill_info,
        my_triple_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
        set_segments_place_id,
):
    set_segments_place_id(my_triple_batch_waybill_info, [1, 2], 1234)

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': DEFAULT_CARGO_REF_ID},
    )
    assert response.status_code == 200
    assert response.json()['tracking_ui']['items'][0]['items'] == [
        build_progress_item(
            point=my_triple_batch_waybill_info['execution']['points'][0],
            point_index=0,
            current_point_index=1,
            parcels=[
                {
                    'external_order_id': '111111-222222',
                    'external_order_cost': '672 ₽',
                    'items': [
                        {'title': 'Молоко', 'quantity': 2},
                        {'title': 'Творог', 'quantity': 3},
                    ],
                },
            ],
            client_index=1,
            is_deeplink_payload=True,
        ),
        build_progress_item(
            point=my_triple_batch_waybill_info['execution']['points'][1],
            point_index=1,
            current_point_index=1,
            parcels=[
                {
                    'external_order_id': '444444-555555',
                    'external_order_cost': '157 ₽',
                    'items': [
                        {'title': 'Картошка', 'quantity': 4},
                        {'title': 'Лук', 'quantity': 1},
                    ],
                },
                {'items': [{'title': 'Хлеб', 'quantity': 1}]},
            ],
            client_index=2,
            is_deeplink_payload=False,
        ),
        build_progress_item(
            point=my_triple_batch_waybill_info['execution']['points'][3],
            point_index=2,
            current_point_index=1,
            parcels=[
                {
                    'external_order_id': '444444-555555',
                    'external_order_cost': '157 ₽',
                    'items': [
                        {'title': 'Картошка', 'quantity': 4},
                        {'title': 'Лук', 'quantity': 1},
                    ],
                },
            ],
            client_index=1,
            is_deeplink_payload=True,
        ),
        build_progress_item(
            point=my_triple_batch_waybill_info['execution']['points'][4],
            point_index=3,
            current_point_index=1,
            parcels=[{'items': [{'title': 'Хлеб', 'quantity': 1}]}],
            client_index=2,
            is_deeplink_payload=True,
        ),
        build_progress_item(
            point=my_triple_batch_waybill_info['execution']['points'][5],
            point_index=4,
            current_point_index=1,
            parcels=[
                {
                    'external_order_id': '111111-222222',
                    'external_order_cost': '672 ₽',
                    'items': [
                        {'title': 'Молоко', 'quantity': 2},
                        {'title': 'Творог', 'quantity': 3},
                    ],
                },
            ],
            client_index=3,
            is_deeplink_payload=True,
        ),
    ]


async def test_point_constructor_payload(
        taxi_cargo_orders,
        mock_waybill_info,
        my_triple_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    params = urllib.parse.urlencode(
        {'cargo_ref_id': DEFAULT_CARGO_REF_ID, 'claim_point_id': '1'},
    )
    response = await taxi_cargo_orders.post(
        f'/driver/v1/cargo-claims/v1/cargo/point-constructor-payload?{params}',
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'payload': build_point_info_payload(
            point=my_triple_batch_waybill_info['execution']['points'][0],
            parcels=[
                {
                    'external_order_id': '111111-222222',
                    'external_order_cost': '672 ₽',
                    'items': [
                        {'title': 'Молоко', 'quantity': 2},
                        {'title': 'Творог', 'quantity': 3},
                    ],
                },
            ],
            client_index=1,
        ),
    }


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'cargo_multi_exchange': '8.00'}},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_multi_exchange_settings',
    consumers=['cargo-orders/multi-exchange-settings'],
    clauses=[],
    default_value={'is_enabled': True},
)
async def test_multi_exchange_action_for_batches_with_active_points(
        taxi_cargo_orders,
        mock_waybill_info,
        my_triple_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
        set_segments_place_id,
        set_segment_status,
        set_current_point,
        find_action,
):
    set_segments_place_id(my_triple_batch_waybill_info, [0, 1], 1234)
    set_segment_status(my_triple_batch_waybill_info, 0, 'pickup_arrived')
    set_current_point(my_triple_batch_waybill_info, 0)

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': DEFAULT_CARGO_REF_ID},
    )
    assert response.status_code == 200

    multi_exchange_action = find_action(response.json(), 'multi_exchange')
    items = [
        {
            'type': 'header',
            'subtitle': 'Получить 2 посылки',
            'horizontal_divider_type': 'bottom_bold_s',
            'gravity': 'left',
            'style': 'padding_bottom_compact',
        },
    ]
    items += build_multi_exchange_items(
        point=my_triple_batch_waybill_info['execution']['points'][1],
        parcels=[{'items': [{'title': 'Хлеб', 'quantity': 1}]}],
        index=0,
    )
    items += build_multi_exchange_items(
        point=my_triple_batch_waybill_info['execution']['points'][0],
        parcels=[
            {
                'external_order_id': '111111-222222',
                'external_order_cost': '672 ₽',
                'items': [
                    {'title': 'Молоко', 'quantity': 2},
                    {'title': 'Творог', 'quantity': 3},
                ],
            },
        ],
        index=1,
    )
    assert multi_exchange_action == {
        'type': 'multi_exchange',
        'tag': 'constructor/cargo/multi_order',
        'title': 'Получить',
        'ui': {'items': items},
    }


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'cargo_multi_exchange': '8.00'}},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_multi_exchange_settings',
    consumers=['cargo-orders/multi-exchange-settings'],
    clauses=[],
    default_value={'is_enabled': True},
)
async def test_multi_exchange_action_for_batches_with_resolved_points(
        taxi_cargo_orders,
        mock_waybill_info,
        my_triple_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
        set_segments_place_id,
        set_segment_status,
        find_action,
):
    set_segments_place_id(my_triple_batch_waybill_info, [0, 1, 2], 1234)
    set_segment_status(my_triple_batch_waybill_info, 1, 'pickup_arrived')
    set_points_resolved(my_triple_batch_waybill_info, [0, 2])

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': DEFAULT_CARGO_REF_ID},
    )
    assert response.status_code == 200

    multi_exchange_action = find_action(response.json(), 'multi_exchange')
    items = [
        {
            'type': 'header',
            'subtitle': 'Получить 3 посылки',
            'horizontal_divider_type': 'bottom_bold_s',
            'gravity': 'left',
            'style': 'padding_bottom_compact',
        },
    ]
    items += build_multi_exchange_items(
        point=my_triple_batch_waybill_info['execution']['points'][1],
        parcels=[{'items': [{'title': 'Хлеб', 'quantity': 1}]}],
        index=1,
    )
    items += build_multi_exchange_items(
        point=my_triple_batch_waybill_info['execution']['points'][2],
        parcels=[
            {
                'external_order_id': '444444-555555',
                'external_order_cost': '157 ₽',
                'items': [
                    {'title': 'Картошка', 'quantity': 4},
                    {'title': 'Лук', 'quantity': 1},
                ],
            },
        ],
        index=0,
    )
    items += build_multi_exchange_items(
        point=my_triple_batch_waybill_info['execution']['points'][0],
        parcels=[
            {
                'external_order_id': '111111-222222',
                'external_order_cost': '672 ₽',
                'items': [
                    {'title': 'Молоко', 'quantity': 2},
                    {'title': 'Творог', 'quantity': 3},
                ],
            },
        ],
        index=2,
    )
    assert multi_exchange_action == {
        'type': 'multi_exchange',
        'tag': 'constructor/cargo/multi_order',
        'title': 'Получить',
        'ui': {'items': items},
    }


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'cargo_multi_exchange': '8.00'}},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_multi_exchange_settings',
    consumers=['cargo-orders/multi-exchange-settings'],
    clauses=[],
    default_value={'is_enabled': True},
)
async def test_multi_exchange_action_for_multipoints_with_active_points(
        taxi_cargo_orders,
        mock_waybill_info,
        my_batch_with_multipoints_waybill_info,
        mock_driver_tags_v1_match_profile,
        set_segments_place_id,
        set_segment_status,
        set_current_point,
        find_action,
):
    set_segments_place_id(my_batch_with_multipoints_waybill_info, [0, 1], 1234)
    set_segment_status(
        my_batch_with_multipoints_waybill_info, 0, 'pickup_arrived',
    )
    set_current_point(my_batch_with_multipoints_waybill_info, 0)

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': DEFAULT_CARGO_REF_ID},
    )
    assert response.status_code == 200

    multi_exchange_action = find_action(response.json(), 'multi_exchange')
    items = [
        {
            'type': 'header',
            'subtitle': 'Получить 3 посылки',
            'horizontal_divider_type': 'bottom_bold_s',
            'gravity': 'left',
            'style': 'padding_bottom_compact',
        },
    ]
    items += build_multi_exchange_items(
        point=my_batch_with_multipoints_waybill_info['execution']['points'][1],
        parcels=[{'items': [{'title': 'Хлеб', 'quantity': 1}]}],
        index=0,
    )
    items += build_multi_exchange_items(
        point=my_batch_with_multipoints_waybill_info['execution']['points'][0],
        parcels=[
            {
                'external_order_id': '444444-555555',
                'external_order_cost': '157 ₽',
                'items': [
                    {'title': 'Пирожное', 'quantity': 2},
                    {'title': 'Масло', 'quantity': 1},
                ],
            },
            {
                'external_order_id': '111111-222222',
                'external_order_cost': '672 ₽',
                'items': [
                    {'title': 'Молоко', 'quantity': 2},
                    {'title': 'Творог', 'quantity': 3},
                ],
            },
        ],
        index=1,
    )
    assert multi_exchange_action == {
        'type': 'multi_exchange',
        'tag': 'constructor/cargo/multi_order',
        'title': 'Получить',
        'ui': {'items': items},
    }


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'cargo_multi_exchange': '8.00'}},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_multi_exchange_settings',
    consumers=['cargo-orders/multi-exchange-settings'],
    clauses=[],
    default_value={'is_enabled': True},
)
async def test_multi_exchange_action_for_multipoints_with_resolved_points(
        taxi_cargo_orders,
        mock_waybill_info,
        my_batch_with_multipoints_waybill_info,
        mock_driver_tags_v1_match_profile,
        set_segments_place_id,
        set_segment_status,
        set_current_point,
        find_action,
):
    set_segments_place_id(my_batch_with_multipoints_waybill_info, [0, 1], 1234)
    set_segment_status(
        my_batch_with_multipoints_waybill_info, 1, 'pickup_arrived',
    )
    set_current_point(my_batch_with_multipoints_waybill_info, 0)
    set_points_resolved(my_batch_with_multipoints_waybill_info, [0])

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': DEFAULT_CARGO_REF_ID},
    )
    assert response.status_code == 200

    multi_exchange_action = find_action(response.json(), 'multi_exchange')
    assert len(multi_exchange_action['ui']['items']) == 3
    assert (
        multi_exchange_action['ui']['items'][2]
        == build_multi_exchange_items(
            point=my_batch_with_multipoints_waybill_info['execution'][
                'points'
            ][0],
            parcels=[
                {
                    'external_order_id': '444444-555555',
                    'external_order_cost': '157 ₽',
                    'items': [
                        {'title': 'Пирожное', 'quantity': 2},
                        {'title': 'Масло', 'quantity': 1},
                    ],
                },
                {
                    'external_order_id': '111111-222222',
                    'external_order_cost': '672 ₽',
                    'items': [
                        {'title': 'Молоко', 'quantity': 2},
                        {'title': 'Творог', 'quantity': 3},
                    ],
                },
            ],
            index=1,
        )[0]
    )


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'cargo_multi_exchange': '8.00'}},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_multi_exchange_settings',
    consumers=['cargo-orders/multi-exchange-settings'],
    clauses=[],
    default_value={'is_enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_show_3_dots_menu_button_in_exchange_init_button',
    consumers=['cargo-orders/show-3-dots-menu-button-in-exchange-init-button'],
    clauses=[],
    default_value={'should_show': True},
)
@pytest.mark.experiments3(filename='exp3_action_checks.json')
async def test_3_dots_menu_with_several_active_segments(
        taxi_cargo_orders,
        mock_waybill_info,
        my_batch_with_multipoints_waybill_info,
        mock_driver_tags_v1_match_profile,
        set_segments_place_id,
        set_segment_status,
        set_current_point,
        find_action,
):
    set_segments_place_id(my_batch_with_multipoints_waybill_info, [0, 1], 1234)
    set_segment_status(
        my_batch_with_multipoints_waybill_info, 0, 'pickup_arrived',
    )
    set_current_point(my_batch_with_multipoints_waybill_info, 0)

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': DEFAULT_CARGO_REF_ID},
    )
    assert response.status_code == 200

    multi_exchange_action = find_action(response.json(), 'multi_exchange')
    assert multi_exchange_action is not None
    # common claim point
    assert (
        multi_exchange_action['ui']['items'][1]['items'][2]['states'][
            'exchange_init'
        ]
        == {
            'type': 'button_with_options',
            'button_primary': {
                'type': 'button',
                'title': 'Посылка получена',
                'accent': True,
                'horizontal_divider_type': 'none',
                'payload': {
                    'type': 'multi_state_select',
                    'target_state': 'exchange_confirm',
                },
            },
            'short_button': {
                'type': 'icon_button',
                'icon': {'icon_type': 'vertical_dots'},
                'accent': False,
                'payload': {
                    'type': 'modal',
                    'modal_type': 'bottom',
                    'fullscreen': False,
                    'items': [
                        {
                            'type': 'tip_detail',
                            'title': 'Посылка',
                            'accent_title': True,
                            'horizontal_divider_type': 'bottom_gap',
                            'left_tip': {
                                'text': '1',
                                'text_color': 'main_text',
                                'background_color': 'minor_bg',
                            },
                        },
                        {
                            'type': 'default',
                            'title': 'Отменить получение',
                            'right_icon': 'cancel',
                            'element_color': 'main_text',
                            'show_right_icon_background': True,
                            'horizontal_divider_type': 'none',
                            'payload': {
                                'type': 'cargo_skip_point',
                                'point_id': 3,
                                'free_conditions': [
                                    {
                                        'type': 'time_after',
                                        'value': '2020-06-17T19:39:50.000000Z',
                                    },
                                    {'type': 'min_call_count', 'value': '3'},
                                ],
                                'force_allowed': False,
                                'force_punishments': [],
                                'query_for_reasons_menu_info': True,
                            },
                        },
                        {
                            'type': 'button',
                            'title': 'Назад',
                            'accent': False,
                            'horizontal_divider_type': 'none',
                            'payload': {
                                'type': 'action',
                                'action_type': 'pop',
                            },
                        },
                    ],
                },
            },
        }
    )

    # multipoint claim point
    assert (
        multi_exchange_action['ui']['items'][3]['states']['exchange_init'][
            'short_button'
        ]['payload']['items'][0]
        == {
            'type': 'tip_detail',
            'title': '2 посылки',
            'accent_title': True,
            'horizontal_divider_type': 'bottom_gap',
        }
    )

    assert find_action(response.json(), 'skip_source_point') is None


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'cargo_multi_exchange': '8.00'}},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_multi_exchange_settings',
    consumers=['cargo-orders/multi-exchange-settings'],
    clauses=[],
    default_value={'is_enabled': True},
)
async def test_current_point_parcels(
        taxi_cargo_orders,
        mock_waybill_info,
        my_triple_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
        set_segments_place_id,
):
    set_segments_place_id(my_triple_batch_waybill_info, [0, 1], 1234)

    # Get parcels for second point and expect two parcels
    claim_point_id = 3
    response = await taxi_cargo_orders.get(
        '/driver/v1/cargo-claims/v1/cargo/items'
        f'?cargo_ref_id={DEFAULT_CARGO_REF_ID}&point_id={claim_point_id}',
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': build_point_parcel_list_payload(
            tag_prefix='constructor/cargo/package',
            point=my_triple_batch_waybill_info['execution']['points'][0],
            parcels=[
                {'items': [{'title': 'Хлеб', 'quantity': 1}]},
                {
                    'external_order_id': '111111-222222',
                    'external_order_cost': '672 ₽',
                    'items': [
                        {'title': 'Молоко', 'quantity': 2},
                        {'title': 'Творог', 'quantity': 3},
                    ],
                },
            ],
        )['items'],
    }
