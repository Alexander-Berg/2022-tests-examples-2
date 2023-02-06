from __future__ import unicode_literals

import json

import datetime
from django import test as django_test
import pytest

from taxi.internal import dbh

from taxiadmin import audit


@pytest.mark.parametrize('zone,code', [
    ('exists', 200),
    ('not_exists', 404)
])
@pytest.mark.now('2017-05-19 00:00:00.0')
@pytest.mark.asyncenv('blocking')
def test_get_for_zone(zone, code):
    response = django_test.Client().get(
        '/api/mph-thresholds/' + zone + '/active/'
    )
    assert response.status_code == code
    if code == 200:
        response = json.loads(response.content)
        assert response['nz'] == 'exists'
        assert response['start'] == '2017-05-09T00:00:00+0000'
        assert response['end'] == '9999-12-31T23:59:59+0000'
        assert len(response['thresholds']) == 1
        threshold = response['thresholds'][0]
        assert threshold['weekday'] == 1
        assert threshold['hour'] == 6
        assert threshold['value'] == 0.16


@pytest.fixture(autouse=True)
def no_audit_checks(monkeypatch):
    def fetch_ticket_from_url(value):
        return value

    def check_ticket(ticket, *args, **kwargs):
        if not ticket:
            raise audit.TicketError('Even a fake ticket is not present!')

    def log_action(*args, **kwargs):
        pass

    monkeypatch.setattr(audit, 'fetch_ticket_from_url', fetch_ticket_from_url)
    monkeypatch.setattr(audit, 'check_ticket', check_ticket)
    monkeypatch.setattr(audit, 'log_action', log_action)


@pytest.mark.now('2017-05-19 00:00:00.0')
@pytest.mark.asyncenv('blocking')
def test_update_existing_zone():
    data = {
        'thresholds': [
            {
                'weekday': 6,
                'hour': 18,
                'value': 4
            }
        ],
        'ticket': 'TAXIRATE-777',
    }
    response = django_test.Client().post(
        '/api/mph-thresholds/exists/update/', json.dumps(data),
        'applications/json'
    )
    assert response.status_code == 200
    old = dbh.mph_thresholds.Doc.find_one_or_not_found({'_id': 2})
    assert old.end == datetime.datetime.utcnow()
    new = dbh.mph_thresholds.Doc.find_active_for_date(
        'exists', datetime.datetime.utcnow()
    )
    assert new.start == datetime.datetime.utcnow()
    assert new._id != 2
    assert new.end == datetime.datetime(9999, 12, 31, 23, 59, 59, 999000)
    assert new.thresholds == {'6_18': 4}


@pytest.mark.now('2017-05-18 00:00:00.0')
@pytest.mark.asyncenv('blocking')
def test_update_with_time():
    data = {
        'start': '2017-05-20T10:00:00+03:00',
        'thresholds': [
            {
                'weekday': 6,
                'hour': 18,
                'value': 4
            }
        ],
        'ticket': 'TAXIRATE-777',
    }
    response = django_test.Client().post(
        '/api/mph-thresholds/exists/update/', json.dumps(data),
        'applications/json'
    )
    assert response.status_code == 200
    old = dbh.mph_thresholds.Doc.find_one_or_not_found({'_id': 2})
    assert old.end == datetime.datetime(2017, 5, 20, 7, 0, 0)
