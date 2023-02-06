import typing

import pytest

from generated.clients import taxi_tariffs
from generated.models import taxi_tariffs as taxi_tariffs_models


@pytest.fixture(name='mock_get_cashed_zones')
def mock_get_cashed_zones(patch):
    @patch('order_notify.repositories.tariffs._get_cashed_zones')
    async def _get_cashed_zones(
            client_tariffs: taxi_tariffs.TaxiTariffsClient, zone: str,
    ) -> typing.Dict[str, taxi_tariffs_models.TariffZonesItem]:
        return {
            'riga': taxi_tariffs_models.TariffZonesItem(
                country='lva', name='riga', time_zone='Europe/Riga',
            ),
            'moscow': taxi_tariffs_models.TariffZonesItem(
                country='rus', name='moscow', time_zone='Europe/Moscow',
            ),
            'paris': taxi_tariffs_models.TariffZonesItem(
                country='fr', name='paris', time_zone='Europe/Paris',
            ),
        }

    return _get_cashed_zones
