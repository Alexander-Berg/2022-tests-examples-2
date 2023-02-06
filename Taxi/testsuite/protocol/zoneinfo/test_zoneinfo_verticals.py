from typing import List

import pytest

TEST_USER_ID = 'a01d0000000000000000000000000000'


def insert_image_to_db(db, tag, image_id):
    db.images.insert(
        {
            '_id': image_id,
            'image_id': image_id,
            'size_hint': {'android': 100},
            'tags': [tag],
        },
    )


@pytest.mark.translations(
    client_messages={
        'tanker.delivery_title': {'ru': 'Delivery'},
        'tanker.ultima_title': {'ru': 'Ultima Black'},
        'tanker.minivan_name': {'ru': 'MiniVan'},
        'tanker.business_description': {'ru': 'Elite cars'},
    },
)
@pytest.mark.config(
    ZONEINFO_VERTICALS={
        'moscow': [
            {
                'type': 'group',
                'id': 'delivery',
                'title': 'tanker.delivery_title',
                'default_tariff': 'courier',
                'tariffs': [
                    {'class': 'courier', 'name': 'tanker.courier_name'},
                    {'class': 'minivan', 'name': 'tanker.minivan_name'},
                ],
            },
            {
                'type': 'group',
                'id': 'ultima',
                'title': 'tanker.ultima_title',
                'mode': 'ultima',
                'can_make_order_from_summary': True,
                'default_tariff': 'comfortplus',
                'tariffs': [
                    {
                        'class': 'business',
                        'description': 'tanker.business_description',
                        'use_tariff_title_on_vertical_name': True,
                    },
                    {'class': 'comfortplus'},
                ],
            },
        ],
    },
)
@pytest.mark.parametrize(
    'verticals_enabled, supported_vertical_types, expected_verticals',
    [
        (False, ['group', 'tariff'], []),
        (True, [], []),
        (True, ['tariff'], []),
        (
            True,
            ['group', 'tariff'],
            [
                {'class': 'econom', 'type': 'tariff'},
                {
                    'can_make_order_from_summary': True,
                    'default_tariff': 'comfortplus',
                    'id': 'ultima',
                    'tariffs': [
                        {
                            'class': 'business',
                            'mode': 'ultima',
                            'description': 'Elite cars',
                            'use_tariff_title_on_vertical_name': True,
                        },
                        {'class': 'comfortplus', 'mode': 'ultima'},
                    ],
                    'title': 'Ultima Black',
                    'title_summary': 'Ultima Black: $TARIFF$',
                    'type': 'group',
                },
                {'class': 'vip', 'type': 'tariff'},
                {
                    'can_make_order_from_summary': False,
                    'default_tariff': 'minivan',
                    'id': 'delivery',
                    'tariffs': [{'class': 'minivan', 'name': 'MiniVan'}],
                    'title': 'Delivery',
                    'type': 'group',
                },
            ],
        ),
    ],
)
def test_zoneinfo_verticals(
        taxi_protocol,
        experiments3,
        verticals_enabled,
        supported_vertical_types,
        expected_verticals,
):
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='zoneinfo_verticals_support',
        consumers=['protocol/zoneinfo'],
        clauses=[
            {
                'value': {'enabled': verticals_enabled},
                'predicate': {'type': 'true'},
            },
        ],
    )
    taxi_protocol.invalidate_caches()

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'options': True,
            'supported_vertical_types': supported_vertical_types,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    assert expected_verticals == response.json().get('verticals', [])


@pytest.mark.translations(client_messages={'ultima_title': {'ru': 'Ultima'}})
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='zoneinfo_verticals_support',
    consumers=['protocol/zoneinfo'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.parametrize(
    'tariffs_use_config_order, cfg_tariffs, resp_tariffs',
    [
        (
            None,
            ['comfortplus', 'business', 'vip'],
            ['business', 'comfortplus', 'vip'],
        ),
        (
            None,
            ['business', 'vip', 'comfortplus'],
            ['business', 'comfortplus', 'vip'],
        ),
        (
            False,
            ['comfortplus', 'vip', 'business'],
            ['business', 'comfortplus', 'vip'],
        ),
        (
            False,
            ['vip', 'business', 'comfortplus'],
            ['business', 'comfortplus', 'vip'],
        ),
        (
            True,
            ['comfortplus', 'vip', 'business'],
            ['comfortplus', 'vip', 'business'],
        ),
        (
            True,
            ['vip', 'business', 'comfortplus'],
            ['vip', 'business', 'comfortplus'],
        ),
        (
            True,
            [
                'fake_tariff_1',
                'vip',
                'fake_tariff_2',
                'comfortplus',
                'fake_tariff_3',
            ],
            ['vip', 'comfortplus'],
        ),
    ],
)
def test_zoneinfo_verticals_tariffs_order(
        taxi_protocol,
        taxi_config,
        tariffs_use_config_order,
        cfg_tariffs,
        resp_tariffs,
):
    def tariffs_to_obj(tt):
        return list(map(lambda t: {'class': t}, tt))

    ultima_vertical_cfg = {
        'type': 'group',
        'id': 'ultima',
        'title': 'ultima_title',
        'default_tariff': 'comfortplus',
        'tariffs': tariffs_to_obj(cfg_tariffs),
    }

    if tariffs_use_config_order is not None:
        ultima_vertical_cfg[
            'tariffs_use_config_order'
        ] = tariffs_use_config_order

    taxi_config.set_values(
        {'ZONEINFO_VERTICALS': {'moscow': [ultima_vertical_cfg]}},
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'options': True,
            'supported_vertical_types': ['group', 'tariff'],
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    verticals = response.json().get('verticals', [])
    verticals = [
        x for x in verticals if x.get('id', '') == ultima_vertical_cfg['id']
    ]
    assert 1 == len(verticals)
    assert tariffs_to_obj(resp_tariffs) == verticals[0]['tariffs']


@pytest.mark.translations(
    client_messages={
        'delivery_title': {'ru': 'Delivery'},
        'ultima_title': {'ru': 'Ultima Black'},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='zoneinfo_verticals_support',
    consumers=['protocol/zoneinfo'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.config(
    ZONEINFO_VERTICALS={
        'moscow': [
            {
                'type': 'group',
                'id': 'delivery',
                'title': 'delivery_title',
                'tariffs': [{'class': 'courier'}, {'class': 'minivan'}],
            },
            {
                'type': 'group',
                'id': 'ultima',
                'title': 'ultima_title',
                'mode': 'ultima',
                'tariffs': [{'class': 'business'}, {'class': 'comfortplus'}],
            },
        ],
    },
)
def test_zoneinfo_verticals_images(taxi_protocol, db, mockserver):
    delivery_image_tag = 'vertical_delivery_image'
    delivery_image_id = 'delivery_vert_image'
    insert_image_to_db(db, delivery_image_tag, delivery_image_id)

    delivery_header_icon_tag = 'vertical_delivery_header_icon'
    delivery_header_icon_id = 'delivery_vert_header_icon'
    insert_image_to_db(db, delivery_header_icon_tag, delivery_header_icon_id)

    ultima_icon_tag = 'vertical_ultima_icon'
    ultima_icon_id = 'ultima_vert_icon'
    insert_image_to_db(db, ultima_icon_tag, ultima_icon_id)

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 100,
            'options': True,
            'supported_vertical_types': ['group'],
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    verticals = response.json().get('verticals', [])

    delivery_vertical = [
        item for item in verticals if item.get('id', '') == 'delivery'
    ]
    assert len(delivery_vertical) == 1
    assert delivery_vertical == [
        {
            'can_make_order_from_summary': False,
            'default_tariff': 'minivan',
            'header_icon': {
                'size_hint': 100,
                'image_tag': 'vertical_delivery_header_icon',
                'url': mockserver.url(
                    'static/images/' + delivery_header_icon_id,
                ),
                'url_parts': {
                    'key': 'TC',
                    'path': '/static/test-images/' + delivery_header_icon_id,
                },
            },
            'id': 'delivery',
            'image': {
                'size_hint': 100,
                'image_tag': 'vertical_delivery_image',
                'url': mockserver.url('static/images/' + delivery_image_id),
                'url_parts': {
                    'key': 'TC',
                    'path': '/static/test-images/' + delivery_image_id,
                },
            },
            'tariffs': [{'class': 'minivan'}],
            'title': 'Delivery',
            'type': 'group',
        },
    ]

    ultima_vertical = [
        item for item in verticals if item.get('id', '') == 'ultima'
    ]
    assert len(ultima_vertical) == 1
    assert ultima_vertical == [
        {
            'can_make_order_from_summary': False,
            'default_tariff': 'business',
            'icon': {
                'size_hint': 100,
                'image_tag': 'vertical_ultima_icon',
                'url': mockserver.url('static/images/' + ultima_icon_id),
                'url_parts': {
                    'key': 'TC',
                    'path': '/static/test-images/' + ultima_icon_id,
                },
            },
            'id': 'ultima',
            'tariffs': [
                {'class': 'business', 'mode': 'ultima'},
                {'class': 'comfortplus', 'mode': 'ultima'},
            ],
            'title': 'Ultima Black',
            'type': 'group',
        },
    ]


@pytest.mark.translations(
    client_messages={'tanker.delivery_title': {'ru': 'Delivery'}},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='zoneinfo_verticals_support',
    consumers=['protocol/zoneinfo'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.config(
    ZONEINFO_VERTICALS={
        'moscow': [
            {
                'experiment_name': 'delivery_vertical',
                'type': 'group',
                'id': 'delivery',
                'title': 'tanker.delivery_title',
                'tariffs': [
                    {'class': 'courier'},
                    {'class': 'minivan'},
                    {'class': 'vip'},
                ],
            },
        ],
    },
)
@pytest.mark.parametrize(
    'expected_verticals, verticals_customization',
    [
        ([], {'enabled': False}),
        (
            [
                {'class': 'econom', 'type': 'tariff'},
                {'class': 'business', 'type': 'tariff'},
                {'class': 'comfortplus', 'type': 'tariff'},
                {'class': 'vip', 'type': 'tariff'},
                {'class': 'minivan', 'type': 'tariff'},
            ],
            {
                'enabled': True,
                'tariffs': [{'class': 'courier'}, {'class': 'express'}],
            },
        ),
        (
            [
                {'class': 'econom', 'type': 'tariff'},
                {'class': 'business', 'type': 'tariff'},
                {'class': 'comfortplus', 'type': 'tariff'},
                {'class': 'vip', 'type': 'tariff'},
                {
                    'can_make_order_from_summary': False,
                    'default_tariff': 'minivan',
                    'id': 'delivery',
                    'tariffs': [{'class': 'minivan'}],
                    'title': 'Delivery',
                    'type': 'group',
                },
            ],
            {'enabled': True, 'tariffs': [{'class': 'minivan'}]},
        ),
        (
            [
                {'class': 'econom', 'type': 'tariff'},
                {'class': 'business', 'type': 'tariff'},
                {'class': 'comfortplus', 'type': 'tariff'},
                {'class': 'vip', 'type': 'tariff'},
                {
                    'can_make_order_from_summary': False,
                    'default_tariff': 'minivan',
                    'id': 'delivery',
                    'tariffs': [{'class': 'minivan'}],
                    'title': 'Delivery',
                    'type': 'group',
                },
                {'class': 'minivan', 'type': 'tariff'},
            ],
            {
                'enabled': True,
                'tariffs': [{'class': 'minivan'}],
                'show_on_summary': ['minivan'],
            },
        ),
        (
            [
                {'class': 'econom', 'type': 'tariff'},
                {'class': 'business', 'type': 'tariff'},
                {'class': 'comfortplus', 'type': 'tariff'},
                {'class': 'vip', 'type': 'tariff'},
                {
                    'can_make_order_from_summary': False,
                    'default_tariff': 'minivan',
                    'id': 'delivery',
                    'tariffs': [{'class': 'minivan'}],
                    'title': 'Delivery',
                    'type': 'group',
                },
            ],
            {
                'enabled': True,
                'tariffs': [{'class': 'minivan'}, {'class': 'business'}],
                'show_on_summary': ['business'],
            },
        ),
        (
            [
                {'class': 'econom', 'type': 'tariff'},
                {'class': 'business', 'type': 'tariff'},
                {'class': 'comfortplus', 'type': 'tariff'},
                {
                    'can_make_order_from_summary': False,
                    'default_tariff': 'vip',
                    'id': 'delivery',
                    'tariffs': [{'class': 'vip', 'mode': 'ultima'}],
                    'title': 'Delivery',
                    'type': 'group',
                },
                {'class': 'minivan', 'type': 'tariff'},
            ],
            {'enabled': True, 'tariffs': [{'class': 'vip'}], 'mode': 'ultima'},
        ),
    ],
)
def test_zoneinfo_vertical_by_experiment(
        taxi_protocol,
        experiments3,
        expected_verticals,
        verticals_customization,
):
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='delivery_vertical',
        consumers=['protocol/zoneinfo'],
        clauses=[
            {'value': verticals_customization, 'predicate': {'type': 'true'}},
        ],
    )
    taxi_protocol.invalidate_caches()

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'options': True,
            'supported_vertical_types': ['group'],
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    assert expected_verticals == response.json().get('verticals', [])


VERTICAL = 'vertical'


def _create_vert_ans(names: List[str]) -> List[dict]:
    verticals = []
    for name in names:
        if name == VERTICAL:
            verticals.append(
                {
                    'id': 'delivery',
                    'can_make_order_from_summary': False,
                    'default_tariff': 'vip',
                    'title': 'Delivery',
                    'tariffs': [{'class': 'econom'}, {'class': 'vip'}],
                    'type': 'group',
                },
            )

        else:
            verticals.append({'class': name, 'type': 'tariff'})

    return verticals


@pytest.mark.translations(
    client_messages={'tanker.delivery_title': {'ru': 'Delivery'}},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='zoneinfo_verticals_support',
    consumers=['protocol/zoneinfo'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.config(
    ZONEINFO_VERTICALS={
        'moscow': [
            {
                'experiment_name': 'delivery_vertical',
                'type': 'group',
                'id': 'delivery',
                'title': 'tanker.delivery_title',
                'default_tariff': 'vip',
                'tariffs': [{'class': 'vip'}, {'class': 'econom'}],
            },
        ],
    },
)
@pytest.mark.parametrize(
    ('verticals_names', 'verticals_customization'),
    (
        pytest.param(
            ['business', 'comfortplus', VERTICAL, 'minivan'],
            {
                'enabled': True,
                'tariffs': [{'class': 'econom'}, {'class': 'vip'}],
            },
            id='vert_position',
        ),
        pytest.param(
            ['business', 'comfortplus', VERTICAL, 'vip', 'minivan'],
            {
                'enabled': True,
                'tariffs': [{'class': 'econom'}, {'class': 'vip'}],
                'show_on_summary': ['vip'],
            },
            id='default_class_position',
        ),
        pytest.param(
            ['econom', 'business', 'comfortplus', VERTICAL, 'minivan'],
            {
                'enabled': True,
                'tariffs': [{'class': 'econom'}, {'class': 'vip'}],
                'show_on_summary': ['econom'],
            },
            id='summary_class_position',
        ),
    ),
)
def test_zoneinfo_vertical_order(
        taxi_protocol, experiments3, verticals_names, verticals_customization,
):
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='delivery_vertical',
        consumers=['protocol/zoneinfo'],
        clauses=[
            {'value': verticals_customization, 'predicate': {'type': 'true'}},
        ],
    )
    taxi_protocol.invalidate_caches()

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'options': True,
            'supported_vertical_types': ['group'],
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    assert _create_vert_ans(verticals_names) == response.json()['verticals']


@pytest.mark.translations(
    client_messages={
        'zoneinfo.verticals.delivery.title': {'ru': 'Delivery'},
        'zoneinfo.verticals.child.title': {'ru': 'Child'},
        'zoneinfo.verticals.ultima.title': {'ru': 'Ultima Black'},
        'zoneinfo.verticals.taxi.title': {'ru': 'Taxi'},
        'zoneinfo.verticals.rest_tariffs.title': {'ru': 'Other traiffs'},
        'zoneinfo.verticals.maas.title': {'ru': 'Subscription'},
        'zoneinfo.verticals.maas.econom.name': {'ru': 'MultiTransport'},
        'zoneinfo.verticals.requirement.childchair_v2.unset_order_button': {
            'ru': 'Choose seat',
        },
        'multiclass.min_selected_count.text': {
            'ru': 'Выберите %(min_count)s и более классов',
        },
    },
    tariff={
        'routestats.multiclass.name': {'ru': 'Самый быстрый'},
        'routestats.multiclass.details.order_button.text': {
            'ru': 'Выберите минимум два тарифа',
        },
        'routestats.multiclass.search_screen.title': {'ru': 'Поиск'},
        'routestats.multiclass.search_screen.subtitle': {
            'ru': 'в нескольких тарифах',
        },
        'routestats.multiclass.details.description.title': {
            'ru': 'Несколько тарифов',
        },
        'routestats.multiclass.details.description.subtitle': {
            'ru': 'Назначим ближайшую к вам машину',
        },
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='zoneinfo_verticals_support',
    consumers=['protocol/zoneinfo'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='verticals_multiclass_support',
    consumers=['protocol/zoneinfo'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.experiments3(filename='verticals_selector_exp.json')
def test_verticals_selector(taxi_protocol, db, load_json, mockserver):
    delivery_selector_icon_image_tag = 'delivery_multiclass_selector_icon'
    delivery_selector_icon_image_id = 'delivery_multiclass_selector_icon_image'
    insert_image_to_db(
        db, delivery_selector_icon_image_tag, delivery_selector_icon_image_id,
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'options': True,
            'supported_vertical_types': ['group'],
            'supported': ['verticals_selector'],
            'size_hint': 640,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200

    response_body = response.json()
    assert 'verticals_selector' in response_body['verticals_modes']

    expected_response = load_json('verticals_selector_response.json')
    for vertical in expected_response:
        if (
                'multiclass' in vertical
                and 'selector_icon' in vertical['multiclass']
        ):
            vertical['multiclass']['selector_icon']['url'] = mockserver.url(
                'static/images/' + delivery_selector_icon_image_id,
            )

    assert expected_response == response_body['verticals']


@pytest.mark.translations(
    client_messages={
        'zoneinfo.verticals.delivery.title': {'ru': 'Delivery'},
        'zoneinfo.verticals.child.title': {'ru': 'Child'},
        'zoneinfo.verticals.ultima.title': {'ru': 'Ultima Black'},
        'zoneinfo.verticals.taxi.title': {'ru': 'Taxi'},
        'zoneinfo.verticals.rest_tariffs.title': {'ru': 'Other traiffs'},
        'zoneinfo.verticals.maas.title': {'ru': 'Subscription'},
        'zoneinfo.verticals.maas.econom.name': {'ru': 'MultiTransport'},
        'zoneinfo.verticals.requirement.childchair_v2.unset_order_button': {
            'ru': 'Choose seat',
        },
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='zoneinfo_verticals_support',
    consumers=['protocol/zoneinfo'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.experiments3(filename='verticals_selector_exp.json')
def test_verticals_selector_no_full_multiclass(
        taxi_protocol, db, load_json, mockserver,
):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'options': True,
            'supported_vertical_types': ['group'],
            'supported': ['verticals_selector'],
            'size_hint': 640,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200

    response_body = response.json()
    assert 'verticals_selector' in response_body['verticals_modes']

    expected_response = load_json(
        'verticals_selector_no_full_multiclass_response.json',
    )
    assert expected_response == response_body['verticals']


@pytest.mark.translations(
    client_messages={
        'zoneinfo.verticals.delivery.title': {'ru': 'Delivery'},
        'zoneinfo.verticals.ultima.title': {'ru': 'Ultima Black'},
        'zoneinfo.verticals.taxi.title': {'ru': 'Taxi'},
        'zoneinfo.verticals.rest_tariffs.title': {'ru': 'Other traiffs'},
    },
)
@pytest.mark.config(
    ZONEINFO_VERTICALS={
        'moscow': [
            {
                'type': 'group',
                'id': 'delivery',
                'title': 'zoneinfo.verticals.delivery.title',
                'default_tariff': 'vip',
                'tariffs': [{'class': 'vip'}, {'class': 'econom'}],
            },
        ],
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='zoneinfo_verticals_support',
    consumers=['protocol/zoneinfo'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.parametrize(
    ('field_name', 'experiment_value'),
    [
        pytest.param('rest_tariffs', None, id='no_rest_tariffs_info'),
        pytest.param('rest_tariffs', {}, id='empty_rest_tariffs_info'),
        pytest.param(
            'rest_tariffs',
            {
                'id': 'rest_tariffs',
                'title': 'zoneinfo.verticals.rest_tariffs.title',
                'type': 'group',
                'tariffs': [{'class': 'econom'}],
            },
            id='rest_tariffs_with_tariff',
        ),
        pytest.param('verticals', None, id='no_verticals'),
        pytest.param('verticals', [], id='empty_verticals'),
    ],
)
def test_verticals_selector_fallback_to_verticals(
        taxi_protocol, load_json, experiments3, field_name, experiment_value,
):
    selector_exp = load_json('verticals_selector_exp.json')
    if experiment_value is None:
        selector_exp['experiments'][0]['clauses'][0]['value'].pop(field_name)
    else:
        selector_exp['experiments'][0]['clauses'][0]['value'][
            field_name
        ] = experiment_value
    experiments3.add_experiments_json(selector_exp)
    taxi_protocol.invalidate_caches()

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'options': True,
            'supported_vertical_types': ['group'],
            'supported': ['verticals_selector'],
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200

    response_body = response.json()
    assert 'verticals_modes' not in response_body
    assert 'verticals' in response_body
    tariff_vertical_count = 0
    for vert in response_body['verticals']:
        if vert['type'] == 'tariff':
            tariff_vertical_count += 1
    assert tariff_vertical_count > 0


@pytest.mark.translations(
    client_messages={
        'tanker.delivery_title': {'ru': 'Delivery'},
        'tanker.minivan_name': {'ru': 'MiniVan'},
    },
)
@pytest.mark.config(
    ZONEINFO_VERTICALS={
        'moscow': [
            {
                'type': 'group',
                'id': 'delivery',
                'title': 'tanker.delivery_title',
                'default_tariff': 'minivan',
                'tariffs': [
                    {'class': 'minivan', 'name': 'tanker.minivan_name'},
                ],
            },
        ],
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='zoneinfo_verticals_support',
    consumers=['protocol/zoneinfo'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='set_detailed_delivery_vertical_title',
    consumers=['protocol/zoneinfo'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
def test_zoneinfo_delivery_vertical_title_summary(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'options': True,
            'supported_vertical_types': ['group', 'tariff'],
        },
    )

    assert response.status_code == 200

    verticals_response = response.json()['verticals']
    delivery_vertical = [
        x for x in verticals_response if ('id' in x and x['id'] == 'delivery')
    ]
    assert len(delivery_vertical) == 1
    assert delivery_vertical[0]['title_summary'] == 'Delivery: $TARIFF$'
