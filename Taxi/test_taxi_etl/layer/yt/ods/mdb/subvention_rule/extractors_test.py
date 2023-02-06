import pytest

from taxi_etl.layer.yt.ods.mdb.subvention_rule.loader import (
    list_has_items_extractor,
    tariff_zone_extractor,
    TariffZoneError
)


def test_list_has_items_extractor():
    extractor = list_has_items_extractor('list')

    assert extractor(doc={'list': []}) is False
    assert extractor(doc={'list': None}) is False
    assert extractor(doc={'list': ['a', 'b']}) is True
    assert extractor(doc={'list': ['']}) is True
    assert extractor(doc={'list': [None]}) is True


def test_tariff_zone_extractor():
    extractor = tariff_zone_extractor('tariffzone')

    assert 'unknown' == extractor(doc={'tariffzone': None})
    assert 'unknown' == extractor(doc={'tariffzone': []})
    assert 'msk' == extractor(doc={'tariffzone': ['msk']})

    id = 'record_id'
    with pytest.raises(TariffZoneError) as exc_info:
        extractor(doc={'_id': id, 'tariffzone': ['msk', 'msk']})
    assert TariffZoneError(id=id).args == exc_info.value.args
