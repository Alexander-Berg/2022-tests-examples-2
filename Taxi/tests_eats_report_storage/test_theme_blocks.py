# flake8: noqa
# pylint: disable=redefined-outer-name, import-only-modules

from typing import Text
import pytest

from .conftest import (
    make_rating_response,
    make_ratings_response,
    make_place_rating,
    exp3_config_multi_places,
)

PARTNER_ID = 1
PLACE_ID = 1

THEME_BLOCK_RESPONSE = {
    'title': 'Рекомендации',
    'description': 'Этот блок поможет вам повысить качестов работы ресторана',
}

INSIDES_RESPONSE = {
    'title': '',
    'data': [
        {
            'icon_slug': 'info',
            'title': 'Повысьте качество',
            'description': 'Рекомендации ниже помогут вам повысить качестов работы ресторана',
        },
    ],
}

BENCHMARKS_RESPONSE = {
    'title': 'Показатели на сервисе',
    'description': 'И их сравнение со средними по Еде',
    'data': {
        'headers': {
            'metric': 'Показатель',
            'value': 'У вас',
            'reference': 'В среднем',
        },
        'rows': [
            {
                'metric': 'Рейтинг ресторана',
                'value': '4.1',
                'reference': '4',
                'is_bad': False,
            },
            {
                'metric': 'Упущенные заказы',
                'description': 'Процент отмененных заказов от общего',
                'value': '10 %',
                'reference': '2.5 %',
                'is_bad': True,
            },
        ],
    },
}

BENCHMARKS_REFERENCE_RESPONSE = {
    'title': 'Показатели на сервисе',
    'description': 'И их сравнение со средними по Еде',
    'data': {
        'headers': {
            'metric': 'Показатель',
            'value': 'У вас',
            'reference': 'В среднем',
        },
        'rows': [
            {
                'metric': 'Рейтинг ресторана',
                'value': '4.3',
                'reference': '4.5',
                'is_bad': True,
            },
        ],
    },
}

BENCHMARKS_MULTI_RESPONSE = {
    'title': 'Показатели на сервисе',
    'description': 'И их сравнение со средними по Еде',
    'data': {
        'headers': {
            'metric': 'Показатель',
            'value': 'У вас',
            'reference': 'В среднем',
        },
        'rows': [
            {
                'metric': 'Упущенные заказы',
                'description': 'Процент отмененных заказов от общего',
                'value': '10 %',
                'reference': '2.5 %',
                'is_bad': True,
            },
        ],
    },
}

SUGGESTS_RESPONSE = {
    'title': 'Советы для вас',
    'description': 'Мы обработали много данных',
    'data': [
        {
            'button': {'slug': 'goto_rating', 'text': 'Как поднять рейтинг'},
            'description': 'Это выделит его среди конкурентов и сделает более привлекательным для клиентов',
            'icon_slug': 'rating',
            'place_id': PLACE_ID,
            'title': 'Повысьте рейтинг ресторана',
        },
        {
            'button': {'slug': 'goto_rating', 'text': 'Как поднять рейтинг'},
            'description': 'Сократите количество отмен заказов. Внимательно проверяйте заказы прежде чем их принять — не стоит разочаровывать клиентов отменами',
            'icon_slug': 'cancels_rate',
            'place_id': PLACE_ID,
            'title': 'Снизить отмены',
        },
    ],
}

SUGGESTS_MULTI_RESPONSE = {
    'title': 'Советы для вас',
    'description': 'Мы обработали много данных',
    'data': [
        {
            'button': {'slug': 'goto_rating', 'text': 'Как поднять рейтинг'},
            'description': 'Это выделит его среди конкурентов и сделает более привлекательным для клиентов',
            'icon_slug': 'rating',
            'place_id': 1,
            'title': 'Повысьте рейтинг ресторана',
        },
        {
            'button': {'slug': 'goto_rating', 'text': 'Как поднять рейтинг'},
            'description': 'Сократите количество отмен заказов. Внимательно проверяйте заказы прежде чем их принять — не стоит разочаровывать клиентов отменами',
            'icon_slug': 'cancels_rate',
            'place_id': 1,
            'title': 'Снизить отмены',
        },
        {
            'button': {'slug': 'goto_rating', 'text': 'Как поднять рейтинг'},
            'description': 'Это выделит его среди конкурентов и сделает более привлекательным для клиентов',
            'icon_slug': 'rating',
            'place_id': 2,
            'title': 'Повысьте рейтинг ресторана',
        },
        {
            'button': {'slug': 'goto_rating', 'text': 'Как поднять рейтинг'},
            'description': 'Сократите количество отмен заказов. Внимательно проверяйте заказы прежде чем их принять — не стоит разочаровывать клиентов отменами',
            'icon_slug': 'cancels_rate',
            'place_id': 2,
            'title': 'Снизить отмены',
        },
    ],
}

LINKS_RESPONSE = {
    'title': 'Полезные ссылки',
    'data': [
        {'slug': 'goto_rating', 'text': 'Как поднять рейтинг?'},
        {'slug': 'goto_cancels', 'text': 'Как снизить отмены?'},
    ],
}

COMMON_METRICS_WITH_REFERENCE = {
    'metrics': [
        {
            'data_key': 'rating_average',
            'granularity': ['hour', 'day', 'week', 'month'],
            'metric_id': 'rating_average',
            'name': 'rating_average',
            'periods': ['week', 'month', 'year', 'custom'],
            'permissions': ['other_permission'],
            'simbols_after_comma': 1,
            'reference_value': {
                'bad_template': '',
                'good_template': '',
                'value': 4.5,
            },
        },
    ],
}


def make_theme_block_response(topic, *blocks):
    resp = THEME_BLOCK_RESPONSE.copy()
    resp['topic'] = topic
    if 'insides' in blocks:
        resp['insides'] = INSIDES_RESPONSE.copy()
    if 'benchmarks' in blocks:
        resp['benchmarks'] = BENCHMARKS_RESPONSE.copy()
    if 'benchmarks_multi' in blocks:
        resp['benchmarks'] = BENCHMARKS_MULTI_RESPONSE.copy()
    if 'benchmarks_reference' in blocks:
        resp['benchmarks'] = BENCHMARKS_REFERENCE_RESPONSE.copy()
    if 'suggests' in blocks:
        resp['suggests'] = SUGGESTS_RESPONSE.copy()
    if 'suggests_multi' in blocks:
        resp['suggests'] = SUGGESTS_MULTI_RESPONSE.copy()
    if 'links' in blocks:
        resp['links'] = LINKS_RESPONSE.copy()
    return resp


class MissingPermissions:
    def __init__(self):
        self.data = []

    def set(self, data):
        self.data = data


@pytest.fixture
def missing_permissions_resp():
    return MissingPermissions()


@pytest.fixture
def mock_authorizer_no_perm(mockserver, request, missing_permissions_resp):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=403,
            json={
                'code': '403',
                'message': 'Error',
                'details': {
                    'permissions': missing_permissions_resp.data,
                    'place_ids': [],
                },
            },
        )


async def test_theme_blocks_400_on_unknown_topic(taxi_eats_report_storage):
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-suggests/theme-block'
        '?place_ids={place_id}&topic=unknown'.format(place_id=PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )
    assert response.status_code == 400


async def test_theme_blocks_403_on_unavailable_places(
        taxi_eats_report_storage, mock_authorizer_403,
):
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-suggests/theme-block'
        '?place_ids={place_id}&topic=quality'.format(place_id=PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )
    assert response.status_code == 403


async def test_theme_blocks_403_on_no_block_permissions(
        taxi_eats_report_storage,
        mock_authorizer_no_perm,
        missing_permissions_resp,
):
    missing_permissions_resp.set(['block_quality_permissions'])
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-suggests/theme-block'
        '?place_ids={place_id}&topic=quality'.format(place_id=PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )
    assert response.status_code == 403


@pytest.mark.now('2021-12-09T12:00:00+0000')
@pytest.mark.pgsql(
    'eats_report_storage', files=['insert_data_theme_blocks.sql'],
)
@pytest.mark.parametrize(
    'missing_permissions, response_blocks',
    [
        pytest.param(
            ['benchmarks_permission'],
            ['insides', 'suggests', 'links'],
            id='skip_benchmarks_block_without_permission',
        ),
        pytest.param(
            ['suggests_permission'],
            ['insides', 'benchmarks', 'links'],
            id='skip_suggests_block_without_permission',
        ),
        pytest.param(
            ['some_permission'],
            ['insides', 'benchmarks', 'suggests', 'links'],
            id='skip_no_block_on_irrelevant_permission',
        ),
    ],
)
async def test_theme_blocks_without_subblock_permissions(
        taxi_eats_report_storage,
        mock_authorizer_no_perm,
        missing_permissions_resp,
        mock_eats_place_rating,
        rating_response,
        missing_permissions,
        response_blocks,
):
    missing_permissions_resp.set(missing_permissions)
    rating_response.set_data(make_rating_response(show_rating=True))
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-suggests/theme-block'
        '?place_ids={place_id}&topic=quality'.format(place_id=PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )
    assert response.status_code == 200
    assert response.json()['payload'] == [
        make_theme_block_response('quality', *response_blocks),
    ]


@pytest.mark.now('2021-12-09T12:00:00+0000')
@pytest.mark.pgsql(
    'eats_report_storage', files=['insert_data_theme_blocks.sql'],
)
@pytest.mark.parametrize(
    'topic, response_blocks',
    [
        pytest.param('quality_empty', [], id='theme_block_without_subblocks'),
        pytest.param(
            'quality_insides', ['insides'], id='theme_block_with_insides',
        ),
        pytest.param(
            'quality_benchmarks',
            ['benchmarks'],
            id='theme_block_with_benchmarks',
        ),
        pytest.param(
            'quality_suggests', ['suggests'], id='theme_block_with_suggests',
        ),
        pytest.param('quality_links', ['links'], id='theme_block_with_links'),
        pytest.param(
            'quality',
            ['insides', 'benchmarks', 'suggests', 'links'],
            id='theme_block_with_all',
        ),
    ],
)
async def test_theme_blocks_with_different_subblocks_in_config(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_eats_place_rating,
        rating_response,
        topic,
        response_blocks,
):
    rating_response.set_data(make_rating_response(show_rating=True))
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-suggests/theme-block'
        '?place_ids={place_id}&topic={topic}'.format(
            place_id=PLACE_ID, topic=topic,
        ),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )
    assert response.status_code == 200
    assert response.json()['payload'] == [
        make_theme_block_response(topic, *response_blocks),
    ]


@pytest.mark.now('2021-12-09T12:00:00+0000')
@pytest.mark.pgsql(
    'eats_report_storage', files=['insert_data_theme_blocks.sql'],
)
async def test_theme_blocks_skip_subblocks_on_empty_data(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_eats_place_rating,
        rating_response,
):
    rating_response.set_data({'places_rating_info': []})
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-suggests/theme-block'
        '?place_ids={place_id}&topic={topic}'.format(
            place_id=3, topic='quality',
        ),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )
    assert response.status_code == 200
    assert response.json()['payload'] == [
        make_theme_block_response('quality', 'insides', 'links'),
    ]


@pytest.mark.now('2021-12-09T12:00:00+0000')
@pytest.mark.pgsql(
    'eats_report_storage', files=['insert_data_theme_blocks.sql'],
)
async def test_theme_blocks_multi_places(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_eats_place_rating,
        rating_response,
):
    rating_response.set_data(
        make_ratings_response(
            [make_place_rating(1, 4.0, 3.4), make_place_rating(2, 4.1, 2.2)],
        ),
    )
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-suggests/theme-block'
        '?place_ids={place_id}&topic={topic}'.format(
            place_id='1,2', topic='quality',
        ),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )
    assert response.status_code == 200
    assert response.json()['payload'] == [
        make_theme_block_response(
            'quality',
            'benchmarks_multi',
            'suggests_multi',
            'insides',
            'links',
        ),
    ]


@pytest.mark.now('2021-12-09T12:00:00+0000')
@pytest.mark.pgsql(
    'eats_report_storage', files=['insert_data_theme_blocks.sql'],
)
@pytest.mark.parametrize(
    'blocks',
    [
        pytest.param(['suggests_multi'], id='config_off'),
        pytest.param(
            ['suggests_multi'],
            id='config_disable_false',
            marks=[exp3_config_multi_places()],
        ),
        pytest.param(
            ['suggests_multi'],
            id='config_disable_true_only_sg',
            marks=[
                exp3_config_multi_places(
                    disable_in_suggests=True, disable_in_theme_blocks=False,
                ),
            ],
        ),
        pytest.param(
            [],
            id='config_disable_true_only_tb',
            marks=[
                exp3_config_multi_places(
                    disable_in_suggests=False, disable_in_theme_blocks=True,
                ),
            ],
        ),
        pytest.param(
            [],
            id='config_disable_true',
            marks=[exp3_config_multi_places(True, True)],
        ),
    ],
)
async def test_theme_blocks_for_multi_places_suggests(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_eats_place_rating,
        rating_response,
        blocks,
):
    rating_response.set_data({'places_rating_info': []})
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-suggests/theme-block'
        '?place_ids={place_id}&topic={topic}'.format(
            place_id='1,2', topic='quality_suggests',
        ),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )
    assert response.status_code == 200
    assert response.json()['payload'] == [
        make_theme_block_response('quality_suggests', *blocks),
    ]


@pytest.mark.now('2021-12-09T12:00:00+0000')
@pytest.mark.pgsql(
    'eats_report_storage', files=['insert_data_theme_blocks.sql'],
)
@pytest.mark.config(
    EATS_REPORT_STORAGE_COMMON_METRICS=COMMON_METRICS_WITH_REFERENCE,
)
async def test_theme_blocks_with_reference(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_eats_place_rating,
        rating_response,
):
    rating_response.set_data(
        make_ratings_response([make_place_rating(1, 4.3, 3.4)]),
    )
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-suggests/theme-block'
        '?place_ids={place_id}&topic=quality'.format(place_id=PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )
    assert response.status_code == 200
    assert response.json()['payload'] == [
        make_theme_block_response(
            'quality', 'benchmarks_reference', 'suggests', 'insides', 'links',
        ),
    ]
