import uuid

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from grocery_products_plugins import *  # noqa: F403 F401


class CatalogItem:
    def __init__(self, *, item_id, url_template):
        self.item_id = item_id
        self.url_template = url_template


class DataUri:
    def __init__(self, *, item: CatalogItem, data_uri):
        self.item = item
        self.data_uri = data_uri


@pytest.fixture(name='grocery_pics')
def mock_grocery_pics(mockserver):
    images = []

    @mockserver.json_handler('/grocery-pics/v1/images/bulk-retrieve')
    def _mock_grocery_pics(request):
        return {'images': images}

    class Context:
        def add_picture(self, *, item: CatalogItem, width=100, height=200):
            data_uri = str(uuid.uuid4())
            images.append(
                {
                    'data_uri': data_uri,
                    'url_template': item.url_template,
                    'dimensions': {'width': width, 'height': height},
                },
            )

            return DataUri(item=item, data_uri=data_uri)

        def times_called(self):
            return _mock_grocery_pics.times_called

        def flush(self):
            _mock_grocery_pics.flush()

    context = Context()
    return context
