import pytest

from taxi import memstorage

from order_notify.generated.stq3 import stq_context
from order_notify.repositories import territories


@pytest.fixture(autouse=True, name='mock_territories')
def mock_territories_fixture(mockserver):
    memstorage.invalidate()

    @mockserver.json_handler('/territories/v1/countries/list')
    async def _countries(request):
        return {'countries': [{'_id': 'rus', 'vat': 12000}]}

    return _countries


async def test_get_country_doc_by_city_id(
        stq3_context: stq_context.Context,
        mock_get_cashed_zones,
        mock_territories,
):
    country_doc = await territories.get_country_doc_by_city_id(
        context=stq3_context, zone='moscow',
    )
    assert country_doc == {'_id': 'rus', 'vat': 12000}
    assert mock_territories.times_called == 1


async def test_get_country_doc_by_city_id_raise_not_found(
        stq3_context: stq_context.Context,
        mock_get_cashed_zones,
        mock_territories,
):
    with pytest.raises(territories.NotFoundError):
        await territories.get_country_doc_by_city_id(
            context=stq3_context, zone='riga',
        )
    assert mock_territories.times_called == 1
