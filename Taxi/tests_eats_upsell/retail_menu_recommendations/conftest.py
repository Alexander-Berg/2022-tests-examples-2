from typing import Optional

import pytest

from . import types


@pytest.fixture(name='retail_recommendations')
def retail_recommendations(taxi_eats_upsell):
    """
    Фикстура для запросов в ручку рекомендаций товаров для карточки товара в
    ритейле.
    """

    url_path: str = '/internal/eats-upsell/retail/v1/menu/recommendations'

    class Context:
        async def send_request(
                self,
                item: types.RequestItem,
                place_slug: str,
                headers: dict = None,
                location: Optional[types.Location] = None,
                shipping_type: Optional[types.RequestShippingType] = None,
        ):
            request_headers: dict = {}
            if headers:
                request_headers.update(headers)

            body: dict = {'item': item, 'place_slug': place_slug}
            if location:
                body['location'] = location
            if shipping_type:
                body['shipping_type'] = shipping_type

            return await taxi_eats_upsell.post(
                url_path, headers=request_headers, json=body,
            )

    return Context()
