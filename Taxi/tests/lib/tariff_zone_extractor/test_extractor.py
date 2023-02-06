from unittest import mock

from lib.tariff_zone_extractor.extractor import extract_tariff_zone_from_coordinates
from lib.tariff_zone_extractor.geoareas import GeoareasHandbook
from lib.tariff_zone_extractor.tariffs import TariffsHandbook



MOSCOW_LON_LAT = (37.618, 55.751)
NONEXISTENT_LON_LAT = (90, 90)

MOSCOW_GEOAREA = [
    {
        '_id': 'db9d1fa0efd64c18a2e01eff73958c81',
        'name': 'moscow_activation',
        'geometry': {
            'type': 'Polygon',
            'coordinates': [[[37.24590749190489, 55.388258710286024], [38.21630630887042, 55.388258710286024],
                            [37.24590749190489, 55.913889384939836], [38.21630630887042, 55.913889384939836]]]
        }
    },
    {
        '_id': '1f121111472a45e9bcbb7c72200c6340',
        'name': 'moscow',
        'geometry': {
            'type': 'Polygon',
            'coordinates': [[[37.1946401739712, 55.478983901730004], [37.1946401739712, 55.99950389279226],
                            [38.07767013102269, 55.478983901730004], [38.07767013102269, 55.99950389279226]]]
        },
    }
]

MOSCOW_TARIFF = [{
    '_id': '5e25852b22f2053024bff68b',
    'activation_zone': 'moscow_activation',
    'home_zone': 'moscow',
    'categories': [
        {'name': 'express'},
        {'name': 'child_tariff'},
        {'name': 'vip'},
        {'name': 'minivan'},
        {'name': 'comfortplus'},
        {'name': 'econom'},
    ]
}]


class TestExtractor:
    def test_extract_from_coordinates(self):
        geoareas_handbook = GeoareasHandbook(MOSCOW_GEOAREA)
        tariffs_handbook = TariffsHandbook(MOSCOW_TARIFF)

        res = extract_tariff_zone_from_coordinates(*MOSCOW_LON_LAT, geoareas_handbook, tariffs_handbook)
        assert res.home_zone == 'moscow'

        res = extract_tariff_zone_from_coordinates(*NONEXISTENT_LON_LAT, geoareas_handbook, tariffs_handbook)
        assert res is None
