# -*- coding: utf-8 -*-
from passport.backend.takeout.common.conf import db
import pytest


@pytest.fixture
def db_hosts():
    hosts = [
        'vla-1',
        'vla-2',
        'man-1',
        'man-2',
    ]
    return hosts


def test_order_by_dc_unknown_dc(db_hosts):
    ordered_hosts = db.order_db_hosts_by_dc(
        db_hosts=db_hosts,
        current_dc='sas',
    )
    assert db_hosts == ordered_hosts


def test_order_by_dc_known_dc(db_hosts):
    ordered_hosts = db.order_db_hosts_by_dc(
        db_hosts=db_hosts,
        current_dc='man',
    )
    assert ordered_hosts == ['man-1', 'man-2', 'vla-1', 'vla-2']
