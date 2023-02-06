# -- coding: utf8 --

from __future__ import unicode_literals

import csv
import cStringIO as StringIO
from datetime import datetime

from django import test as django_test
import pytest

import taxi.config
import taxi.external.startrack
from taxi.core import async
from taxi.internal import audit


@pytest.mark.parametrize(
    'doc_before, doc_after, added',
    [
        (
            {'a': [1, 2], 'b': 5, 'c': 8},
            {'a': [1, 2, 3, {'d': 7}], 'b': 5, 'c': 6},
            {'a': [3, {'d': 7}], 'c': 6},
        ),
        (
            {'a': [1, 2], 'b': 5, 'c': 8},
            {'a': [1, 2, 3, {}], 'b': 5, 'c': 6},
            {'a': [3, {}], 'c': 6},
        ),
        (
            [{'a': 2, 'b': 2, 'c': 3}, {'a': 1}],
            [{'a': 1, 'b': 2, 'c': 3}, {'a': 1}],
            [{'a': 1}],
        ),
        (
            [{'a': 4, 'b': 5, 'c': 3}, {'a': 4, 'b': 6}],
            [{'a': 1, 'b': 2, 'c': 3}, {'a': 4, 'b': 5}],
            [{'a': 1, 'b': 2}, {'b': 5}],
        ),
        (
            [1, 2, 3, 4, 5],
            [2, 3, 4, 5, 6],
            [6],
        ),
        (
            [1, 2, 3],
            [1, 2, 3, 4],
            [4],
        ),
        (
            [1, 2, 3, 4],
            [2, 3, 4],
            {},
        ),
    ],
)
@pytest.mark.asyncenv('blocking')
def test_docs_diff(
    doc_before, doc_after, added,
):
    chk_added = audit._docs_diff(
        doc_before, doc_after,
    )

    assert chk_added == added


@pytest.mark.parametrize(
    'ticket, action, login, task_id, log_admin_id, subvention_rule_id, '
    'updated, expected_message',
    [
        (
            'TAXIRATE-999', 'set_tariff', 'test_login', None,
            '580a2198de29f9c9035f3a9c', None, None,
            'В рамках данного тикета кто:test_login '
            'создал(а)/измененил(а) тариф в 13:00:00 2017-09-10(MSK)\n'
            '\n'
            'Тестовая таблица\n'
        ),
        (
            'TAXIRATE-5', 'change_commission', 'test_login', None,
            '580a2198de29f9c9035f3a9c', None, None,
            'В рамках данного тикета кто:test_login '
            'изменил(а) комиссии в 13:00:00 2017-09-10(MSK)\n'
            '\n'
            'Тестовая таблица\n'
        ),
        (
            'TAXIRATE-1234', 'subventions', 'test_login', None, None,
            '587fad5639b479046a796552',
            datetime(
                year=2017,
                month=1,
                day=18,
                hour=18,
                minute=0,
                second=54,
                microsecond=727000,
            ),
            'В рамках данного тикета кто:test_login '
            'отредактировал(а) правила субсидий в 13:00:00 2017-09-10(MSK)\n'
            '\n'
            'Тестовая таблица\n'
        ),
        (
            'TAXIRATE-1234', 'subventions', 'test_login', None, None,
            '587fad5639b479046a796552', None,
            'В рамках данного тикета кто:test_login '
            'отредактировал(а) правила субсидий в 13:00:00 2017-09-10(MSK)\n'
            '\n'
            'Тестовая таблица\n'
        ),
        (
            'TAXIRATE-1234', 'subventions', 'test_login',
            'create_change_comment_1', None, None, None,
            'В рамках данного тикета кто:test_login '
            'отредактировал(а) правила субсидий в 13:00:00 2017-09-10(MSK)\n'
            '\n'
            'Тестовая таблица\n'
        ),
    ],
)
@pytest.mark.now('2017-09-10 10:00:00')
@pytest.mark.config(ADMIN_AUDIT_TICKET_ENABLE_COMMENT=True)
@pytest.mark.asyncenv('blocking')
def test_create_change_comment(
    monkeypatch, mock,
    ticket, action, login, task_id,
    log_admin_id,
    subvention_rule_id, updated,
    expected_message
):
    @mock
    def create_comment(
            ticket, message, summonees=None, profile=None, log_extra=None,
    ):
        pass

    @mock
    def create_change_comment(
        ticket, action,
        log_admin_id=None,
        subvention_rule_id=None,
        updated=None,
        login=None,
        task_id=task_id,
        log_extra=None,
    ):
        audit.startrack_change_comment(
            ticket, action, log_admin_id=log_admin_id, login=login,
            subvention_rule_id=subvention_rule_id, updated=updated,
            task_id=task_id, log_extra=log_extra,
        )

    @mock
    def make_table(
        ticket, log_entry=None,
        subvention_rule_id=None, updated=None
    ):
        return 'Тестовая таблица'

    monkeypatch.setattr(
        taxi.external.startrack,
        'create_comment',
        create_comment,
    )
    monkeypatch.setattr(
        taxi.internal.audit,
        'create_change_comment',
        create_change_comment,
    )
    monkeypatch.setattr(
        taxi.internal.audit,
        'make_table',
        make_table,
    )

    audit.create_change_comment(
        ticket=ticket,
        login=login,
        action=action,
        log_admin_id=log_admin_id,
        subvention_rule_id=subvention_rule_id,
        updated=updated,
    )

    assert create_comment.calls == [
        {
            'ticket': ticket,
            'message': expected_message,
            'summonees': None,
            'profile': None,
            'log_extra': None,
        },
    ]


@pytest.mark.timeout(100)
@pytest.mark.asyncenv('blocking')
def test_show_changes():
    response = django_test.Client().get('/changes/TAXIRATE-4104')
    assert response.status_code == 200


@pytest.mark.timeout(100)
@pytest.mark.asyncenv('blocking')
def test_show_changes_ignores_not_approved_rules():
    response = django_test.Client().get('/changes/TAXIRATE-4105')
    changes_csv = StringIO.StringIO(response.content)
    csv_reader = csv.reader(changes_csv, delimiter=b';')
    header = next(csv_reader)
    records = list(csv_reader)
    assert response.status_code == 200
    assert header
    assert not records


@pytest.mark.parametrize('params, expected', [
    (
        {
            'ticket': 'TAXIRATE-20',
            'action': 'add_user_discounts',
            'log_admin_id': '5bd10e35bfa9294d98035255'
        },
        'expected_comment_1.txt'
    ),
    (
        {
            'ticket': 'TAXIRATE-20',
            'action': 'update_user_discounts',
            'log_admin_id': '5bd10aa8bfa9294d97748892'
        },
        'expected_comment_2.txt'
    ),
    (
        {
            'ticket': 'TAXIRATE-20',
            'action': 'delete_user_discounts',
            'log_admin_id': '5bd11027bfa9294d998ca635'
        },
        'expected_comment_3.txt'
    ),
    (
        {
            'ticket': 'TAXIRATE-1',
            'action': 'set_tariff',
            'log_admin_id': '5bf556d091090a00014fe9f5'
        },
        'expected_comment_4.txt'
    ),
    (
        {
            'ticket': 'TAXIRATE-33',
            'action': 'set_tariff',
            'log_admin_id': '5bf556d010e2e300013e2623'
        },
        'expected_comment_5.txt'
    ),
    (
        {
            'ticket': 'TAXIRATE-666',
            'action': 'set_tariff',
            'log_admin_id': '5bf556d07321630001c61fe8'
        },
        'expected_comment_6.txt'
    )
])
@pytest.mark.config(ADMIN_AUDIT_TICKET_ENABLE_COMMENT=True)
@pytest.mark.asyncenv('blocking')
def test_create_comment_updates(params, expected, load, patch):
    @patch('taxi.external.startrack.create_comment')
    @async.inline_callbacks
    def create_ticket(
            ticket, body, summonees=None, profile=None, log_extra=None,
    ):
        assert ticket == params['ticket']
        assert body == load(expected).decode('utf-8')
        yield

    audit.startrack_change_comment(**params)

    assert create_ticket.call
