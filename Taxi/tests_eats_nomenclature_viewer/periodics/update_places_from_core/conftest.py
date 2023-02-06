from typing import List

import pytest

from tests_eats_nomenclature_viewer.periodics.update_places_from_core import (
    constants,
)
from tests_eats_nomenclature_viewer import models


@pytest.fixture(autouse=True)
def testpoint_periodic_ok(testpoint):
    @testpoint(
        f'eats-nomenclature-viewer_{constants.PERIODIC_NAME}::finished-ok',  # noqa: E501 pylint: disable=line-too-long
    )
    def impl(request):
        pass

    return impl


class CoreHandlerCtx:
    def __init__(self):
        self.mock_handler = None
        self.mock_data = {}

    def set_places_to_mock_data(self, places: List[models.Place], cursor=None):
        self.mock_data = CoreHandlerCtx.generate_mock_data(places, cursor)

    @staticmethod
    def generate_mock_data(places: List[models.Place], cursor=None):
        return {
            'places': [
                {
                    'id': str(i.place_id),
                    'slug': i.slug,
                    'enabled': i.is_enabled,
                    'stock_reset_limit': i.stock_reset_limit,
                    'parser_enabled': True,
                }
                for i in places
            ],
            'meta': {'limit': len(places)},
            'cursor': cursor,
        }


@pytest.fixture(autouse=True)
def mock_core_handler(mockserver):
    ctx = CoreHandlerCtx()

    @mockserver.json_handler(constants.CORE_PLACES_HANDLER)
    def impl(_):
        return ctx.mock_data

    ctx.mock_handler = impl

    return ctx
