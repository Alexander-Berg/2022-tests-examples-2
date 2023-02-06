import pytest


DISABLE_UMLAAS = pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': False},
)

ENABLE_ANALYTICS = pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ANALYTICS={'enable': True},
)


def rest_availability_settings(
        enable: bool = True,
        index: str = 'menu_item_production',
        erms_batch_size: int = 1000,
):
    return pytest.mark.config(
        EATS_FULL_TEXT_SEARCH_RESTAURANT_AVAILABILITY_SETTINGS={
            'enable': enable,
            'index': index,
            'erms_batch_size': erms_batch_size,
        },
    )
