import pytest

from taxi.eda.eda_analytics.lib.context import decode
from taxi.eda.eda_analytics.lib.context import model


@pytest.mark.parametrize(
    'input, parsed',
    [
        pytest.param(
            'CgUIBhoBMQoECAUgAwoECA5AAQoNCAIaCTFfYmFubmVycwoUCAMaEGJhbm5lcnNfdGVtcGxhdGUKJQgEGiHQl9Cw0LPQvtC70L7QstC+0Log0LLQuNC00LbQtdGC0LAKBAgNOAMKBggKEgIAAA==',
            model.AnalyticsContext(
                item_id='1',
                item_type=model.ItemType.BANNER,
                item_position=model.Position(column=0, row=0),
                banner_type=model.BannerType.CLASSIC,
                banner_width=model.BannerWidth.SINGLE,
                widget_id='1_banners',
                widget_template_id='banners_template',
                widget_title='Заголовок виджета',
            ),
        ),
        pytest.param(
            'CgQIBSABCgUIBhoBMwosCAgaKNCi0LXRgdGC0L7QstC+0LUg0LfQsNCy0LXQtNC10L3QuNC1IDEyOTMKCAgHGgRvcGVuCgYIEhICGSMKBAgPKAE=',
            model.AnalyticsContext(
                item_id='3',
                item_name='Тестовое заведение 1293',
                item_type=model.ItemType.PLACE,
                place_business=model.Business.RESTAURANT,
                item_slug='open',
                place_eta=model.DeliveryEta(min=25, max=35),
            ),
        ),
        pytest.param('hello', None, id='proto unmarhsal error'),
        pytest.param('', None, id='empty string'),
    ],
)
def test_analytics_context(input, parsed):
    assert parsed == decode.decode(input)


@pytest.mark.parametrize(
    'input, parsed',
    [
        pytest.param(
            'CgQIF0gBChIIGBoOTXkgU2VhcmNoIFRleHQKDggZGgpyZXF1ZXN0X2lkCgcIGhoDYWxsCgUIGxIBCgoFCBwSAQoKMggdUg0KBAgeIAEKBQggEgEKUh8KBAgeIAIKEAgfGgzQotC+0LLQsNGA0YsKBQggEgEK',
            model.AnalyticsContext(
                search_item_type=model.SearchItemType.REQUEST,
                search_query='My Search Text',
                search_request_id='request_id',
                search_selector='all',
                search_places_found=10,
                search_places_available=10,
                search_blocks=[
                    model.SearchBlock(
                        type=model.SearchBlockType.PLACES,
                        title=None,
                        items_count=10,
                    ),
                    model.SearchBlock(
                        type=model.SearchBlockType.ITEMS,
                        title='Товары',
                        items_count=10,
                    ),
                ],
            ),
        ),
        pytest.param(
            'CgQIDygBCgUIExIBAAoICBQaBHNsdWcKFAgVGhDQoNC10YHRgtC+0YDQsNC9CgUIFhIBAQoECBdIAgoFCCESAQEKBQgiEgEFChcIHxoT0KfQsNGB0YLQviDQuNGJ0YPRgg==',
            model.AnalyticsContext(
                search_item_type=model.SearchItemType.PLACE,
                place_slug='slug',
                place_name='Ресторан',
                place_business=model.Business.RESTAURANT,
                place_available=True,
                is_ad=False,
                search_place_position=1,
                search_place_items_count=5,
                search_place_block_title='Часто ищут',
            ),
        ),
    ],
)
def test_search_analytics_context(input, parsed):
    assert parsed == decode.decode(input)
