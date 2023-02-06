import datetime
import json

from django import test as django_test
import pytest

from taxi.internal import dbh
from taxi.util import versioned_field


_NOW = datetime.datetime(2017, 11, 20)


@pytest.mark.parametrize(
    'zone,expected_start,expected_end,expected_value', [
        ('moscow', '2017-11-15T21:00:00Z', None, 86400 * 7),
        ('unknown', None, None, 0),
    ]
)
@pytest.mark.filldb(
    holded_subventions_config='for_test_get_holded_subventions_config'
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.asyncenv('blocking')
def test_get_holded_subventions_config(zone, expected_start,
                                       expected_end, expected_value):
    response = django_test.Client().get(
        '/api/holded_subventions_config/%s/' % zone,
    )
    assert response.status_code == 200
    expected_result = {
        'version': 1,
        'hold_delays': [
            {
                'start': expected_start,
                'end': expected_end,
                'value': expected_value,
            }
        ]
    }
    assert json.loads(response.content) == expected_result


@pytest.mark.filldb(
    holded_subventions_config='for_test_set_holded_subventions_config',
    tariff_settings='for_test_set_holded_subventions_config'
)
@pytest.mark.parametrize('zone_name,value,start,version', [
    ('moscow', 86400, datetime.datetime(2018, 1, 1), 1),
    ('obninsk', 7200, datetime.datetime(2018, 1, 2), 1),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_set_holded_subventions(zone_name, value, start, version):
    ST_TICKET = 'TAXIRATE-1234'
    try:
        old_doc = yield dbh.holded_subventions_config.Doc.find_by_home_zone(
            zone_name
        )
    except dbh.holded_subventions_config.NotFound:
        pass
    else:
        assert _get_value_at(old_doc, start) != value
    url = '/api/holded_subventions_config/{}'.format(zone_name)
    data = {
        'value': value,
        'start': start.isoformat(),
        'version': version,
        'ticket': ST_TICKET,
    }
    response = django_test.Client().post(
        url, json.dumps(data),
        content_type='application/json',
    )
    assert response.status_code == 200
    new_doc = yield dbh.holded_subventions_config.Doc.find_by_home_zone(
        zone_name
    )
    assert new_doc.version == version + 1
    assert _get_value_at(new_doc, start) == value


def _get_value_at(doc, timestamp):
    """
    :type doc: taxi.internal.dbh.holded_subventions.Doc
    :type timestamp: datetime.datetime
    :rtype: int
    """
    return versioned_field.get_value(
        doc=doc,
        field=dbh.holded_subventions_config.Doc.hold_delays,
        old_field=None,
        timestamp=timestamp,
    )
