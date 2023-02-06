import typing

import pytest

from eats_analytics import eats_analytics

from eats_layout_constructor import communications
from eats_layout_constructor import configs
from eats_layout_constructor import experiments
from eats_layout_constructor import utils

LAYOUT_SLUG = 'banners_layout'


def banners_layout(with_adverts: bool):
    return pytest.mark.layout(
        slug=LAYOUT_SLUG,
        widgets=[
            utils.Widget(
                name='widget_1',
                type='banners',
                meta={'format': 'classic', 'advert': with_adverts, 'limit': 3},
                payload={},
                payload_schema={},
            ),
        ],
    )


@configs.keep_empty_layout()
@configs.layout_experiment_name(name='eats_layout_template')
@experiments.layout(
    layout_slug=LAYOUT_SLUG, experiment_name='eats_layout_template',
)
@pytest.mark.parametrize(
    'expected_banner_ids, advert_enabled',
    [
        pytest.param(
            [1, 2, 3],
            False,
            marks=(banners_layout(False)),
            id='advert disabled',
        ),
        pytest.param(
            [10, 11], True, marks=(banners_layout(True)), id='advert enabled',
        ),
    ],
)
async def test_advert_banners_simple(
        layout_constructor,
        eats_communications,
        expected_banner_ids: typing.List[int],
        advert_enabled: bool,
):
    formats = [communications.Format.Classic]
    eats_communications.add_banners(
        [
            communications.LayoutBanner(
                id=1,
                formats=formats,
                payload=communications.Banner(
                    id=1,
                    meta=communications.BannerMeta(
                        analytics=eats_analytics.encode(
                            eats_analytics.AnalyticsContext(item_id=str(1)),
                        ),
                    ),
                ),
            ),
            communications.LayoutBanner(
                id=2,
                formats=formats,
                payload=communications.Banner(
                    id=2,
                    meta=communications.BannerMeta(
                        analytics=eats_analytics.encode(
                            eats_analytics.AnalyticsContext(item_id=str(2)),
                        ),
                    ),
                ),
            ),
            communications.LayoutBanner(
                id=3,
                formats=formats,
                payload=communications.Banner(
                    id=3,
                    meta=communications.BannerMeta(
                        analytics=eats_analytics.encode(
                            eats_analytics.AnalyticsContext(item_id=str(3)),
                        ),
                    ),
                ),
            ),
        ],
    )

    eats_communications.add_block(
        communications.Block(
            block_id='advert_format_classic',
            type=communications.BlockType.Advert,
            payload=communications.AdvertBannersPayload(
                advert_banners=[
                    communications.Banner(
                        id=10,
                        meta=communications.BannerMeta(
                            analytics=eats_analytics.encode(
                                eats_analytics.AnalyticsContext(
                                    item_id=str(10),
                                ),
                            ),
                        ),
                    ),
                    communications.Banner(
                        id=11,
                        meta=communications.BannerMeta(
                            analytics=eats_analytics.encode(
                                eats_analytics.AnalyticsContext(
                                    item_id=str(11),
                                ),
                            ),
                        ),
                    ),
                ],
            ),
        ),
    )

    response = await layout_constructor.post()
    assert response.status_code == 200
    assert eats_communications.times_called == 1

    data = response.json()['data']
    banner_widgets = data['banners']
    assert len(banner_widgets) == 1

    banner_widget = banner_widgets.pop(0)
    assert 'banners' in banner_widget['payload']

    actual_banners = banner_widget['payload']['banners']
    assert len(expected_banner_ids) == len(actual_banners)
    i = 0
    for expected_banner_id, actual in zip(expected_banner_ids, actual_banners):
        assert expected_banner_id == actual['id']
        expected_analytics = eats_analytics.AnalyticsContext(
            item_id=str(expected_banner_id),
            widget_id='1_banners',
            widget_template_id='widget_1_template',
            item_position=eats_analytics.Position(column=i, row=0),
            banner_type=eats_analytics.BannerType.CLASSIC,
        )
        if advert_enabled:
            expected_analytics.is_ad = True
        i += 1
        assert (
            eats_analytics.decode(actual['meta']['analytics'])
            == expected_analytics
        )


@configs.keep_empty_layout()
@configs.layout_experiment_name(name='eats_layout_template')
@experiments.layout(
    layout_slug=LAYOUT_SLUG, experiment_name='eats_layout_template',
)
@pytest.mark.layout(
    slug=LAYOUT_SLUG,
    widgets=[
        utils.Widget(
            name='widget_1',
            type='banners',
            meta={'format': 'classic', 'advert': True, 'limit': 3},
            payload={},
            payload_schema={},
        ),
        utils.Widget(
            name='widget_2',
            type='banners',
            meta={'format': 'classic', 'advert': True, 'limit': 3},
            payload={},
            payload_schema={},
        ),
        # NOTE(udalovmax): этот виджет не попадет в ответ, т.к. в блоке
        # для него кончатся баннеры.
        utils.Widget(
            name='widget_3',
            type='banners',
            meta={'format': 'classic', 'advert': True},
            payload={},
            payload_schema={},
        ),
    ],
)
async def test_advert_banners_sinlge_block_for_multiple_widgets(
        layout_constructor, eats_communications,
):
    # NOTE(udalovmax): добавляем блок, баннеры которого должны попасть в
    # виджет.
    formats = [communications.Format.Classic]
    first_advert_banners = [
        communications.Banner(
            id=10,
            meta=communications.BannerMeta(
                analytics=eats_analytics.encode(
                    eats_analytics.AnalyticsContext(item_id=str(10)),
                ),
            ),
        ),
        communications.Banner(
            id=11,
            meta=communications.BannerMeta(
                analytics=eats_analytics.encode(
                    eats_analytics.AnalyticsContext(item_id=str(11)),
                ),
            ),
        ),
        communications.Banner(
            id=12,
            meta=communications.BannerMeta(
                analytics=eats_analytics.encode(
                    eats_analytics.AnalyticsContext(item_id=str(12)),
                ),
            ),
        ),
    ]
    second_advert_banners = [
        communications.Banner(
            id=13,
            meta=communications.BannerMeta(
                analytics=eats_analytics.encode(
                    eats_analytics.AnalyticsContext(item_id=str(13)),
                ),
            ),
        ),
        communications.Banner(
            id=14,
            meta=communications.BannerMeta(
                analytics=eats_analytics.encode(
                    eats_analytics.AnalyticsContext(item_id=str(14)),
                ),
            ),
        ),
    ]
    eats_communications.add_block(
        communications.Block(
            block_id='advert_format_classic',
            type=communications.BlockType.Advert,
            payload=communications.AdvertBannersPayload(
                advert_banners=first_advert_banners + second_advert_banners,
            ),
        ),
    )

    response = await layout_constructor.post()
    assert response.status_code == 200
    assert eats_communications.times_called == 1

    data = response.json()['data']
    banner_widgets = data['banners']
    assert len(banner_widgets) == 2

    i = 0
    first_widget = banner_widgets.pop(0)
    banners = first_widget['payload']['banners']
    assert len(first_advert_banners) == len(banners)
    for expected, actual in zip(first_advert_banners, banners):
        assert expected.id == actual['id']
        expected_analytics = eats_analytics.AnalyticsContext(
            item_id=str(expected.id),
            widget_id='1_banners',
            widget_template_id='widget_1_template',
            item_position=eats_analytics.Position(column=i, row=0),
            banner_type=eats_analytics.BannerType.CLASSIC,
            is_ad=True,
        )
        i += 1
        assert (
            eats_analytics.decode(actual['meta']['analytics'])
            == expected_analytics
        )

    i = 0
    second_widget = banner_widgets.pop(0)
    banners = second_widget['payload']['banners']
    assert len(second_advert_banners) == len(banners)
    for expected, actual in zip(second_advert_banners, banners):
        assert expected.id == actual['id']
        expected_analytics = eats_analytics.AnalyticsContext(
            item_id=str(expected.id),
            widget_id='2_banners',
            widget_template_id='widget_2_template',
            item_position=eats_analytics.Position(column=i, row=0),
            banner_type=eats_analytics.BannerType.CLASSIC,
            is_ad=True,
        )
        i += 1
        assert (
            eats_analytics.decode(actual['meta']['analytics'])
            == expected_analytics
        )


@configs.keep_empty_layout()
@configs.layout_experiment_name(name='eats_layout_template')
@experiments.layout(
    layout_slug=LAYOUT_SLUG, experiment_name='eats_layout_template',
)
@pytest.mark.layout(
    slug=LAYOUT_SLUG,
    widgets=[
        utils.Widget(
            name='widget_1',
            type='banners',
            meta={'format': 'classic', 'advert': True, 'limit': 3},
            payload={},
            payload_schema={},
        ),
    ],
)
async def test_advert_banners_pass_yabs_headers(
        layout_constructor, eats_communications,
):
    app_metrica_device_id = 'testsuite-app-metrica-device-id'
    app_metrica_uuid = 'testsuite-app-metrica-uuid'
    mobile_ifa = 'testsuite-mobile-ifa'

    @eats_communications.request_assertion
    def _assertion(request):
        assert 'x-appmetrica-deviceid' in request.headers
        assert (
            request.headers['x-appmetrica-deviceid'] == app_metrica_device_id
        )

        assert 'x-appmetrica-uuid' in request.headers
        assert request.headers['x-appmetrica-uuid'] == app_metrica_uuid

        assert 'x-mobile-ifa' in request.headers
        assert request.headers['x-mobile-ifa'] == mobile_ifa

    response = await layout_constructor.post(
        headers={
            'x-appmetrica-deviceid': app_metrica_device_id,
            'x-appmetrica-uuid': app_metrica_uuid,
            'x-mobile-ifa': mobile_ifa,
        },
    )
    assert response.status_code == 200
    assert eats_communications.times_called == 1
