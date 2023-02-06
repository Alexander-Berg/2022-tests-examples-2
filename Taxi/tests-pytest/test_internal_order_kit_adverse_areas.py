import pytest

from taxi import config
from taxi.internal.order_kit import adverse_areas


SOURCE_AREA = 'spb'
MURINO_AREA = 'murino'


@pytest.mark.parametrize(
    'zones_cfg,source_zone,destination_zone,expected_to_find',
    [
        ({
            SOURCE_AREA: {
                MURINO_AREA: {
                    'show_destination': True,
                    'skip_fields': ''
                }
            }
        }, SOURCE_AREA, MURINO_AREA, True),
        ({
            SOURCE_AREA: {
                MURINO_AREA: {
                    'show_destination': True,
                    'skip_fields': 'skipfeld'
                }
            }
        }, 'not_source_area', MURINO_AREA, False),
        ({
            SOURCE_AREA: {
                MURINO_AREA: {
                    'show_destination': True,
                    'skip_fields': ''
                }
            }
        }, SOURCE_AREA, None, False),
        ({
            SOURCE_AREA: {
                MURINO_AREA: {
                    'show_destination': True,
                    'skip_fields': 'abcrw'
                }
            }
        }, None, None, False),
        ({}, SOURCE_AREA, MURINO_AREA, False),
    ]
)
@pytest.inline_callbacks
def test_get_zones_for(zones_cfg, source_zone, destination_zone,
                       expected_to_find):
    yield config.save('ADVERSE_ZONES', zones_cfg)
    areas_found = yield adverse_areas._get_adverse_settings_dict_for(
        source_zone, destination_zone
    )
    if expected_to_find:
        assert areas_found
    else:
        assert areas_found == {}


@pytest.mark.parametrize(
    'cfg_show_b,source_zone,adverse_destination,expected',
    [
        (True, SOURCE_AREA, MURINO_AREA, True),
        (False, SOURCE_AREA, MURINO_AREA, False),
        (True, SOURCE_AREA, None, False),
        (False, SOURCE_AREA, None, False),
        (True, SOURCE_AREA, 'not_murino', False),
        (False, SOURCE_AREA, 'not_murino', False),
    ]
)
@pytest.inline_callbacks
def test_need_show_dest_for_driver(cfg_show_b, source_zone,
                                   adverse_destination, expected):
    yield config.save('ADVERSE_ZONES', {
        SOURCE_AREA: {
            MURINO_AREA: {
                'show_destination': cfg_show_b,
                'skip_fields': 'abc'
            },
            'non_existing': {
                'show_destination': True,
                'skip_fields': ''
            }
        }
    })

    result = yield adverse_areas.need_show_destination_for_driver(
        source_zone, adverse_destination
    )
    assert expected == result
