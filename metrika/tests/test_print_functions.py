from typing import List

import juggler_sdk
import pytest
from metrika.admin.python.scripts.juggler_downtimes_cleaner import lib


@pytest.mark.parametrize('selector, repr', [
    (juggler_sdk.DowntimeSelector(namespace='q', host='w'), 'host=w & namespace=q'),
    (juggler_sdk.DowntimeSelector(namespace='q', host=''), 'namespace=q'),
    (juggler_sdk.DowntimeSelector(namespace='q', host='w', tags=[1, 2]), 'host=w & namespace=q & (tag=1 | tag=2)')
])
def test_print_selector(selector: juggler_sdk.DowntimeSelector, repr: str):
    assert lib.print_selector(selector) == repr


class Downtime:
    def __init__(self, filters: List[juggler_sdk.DowntimeSelector]):
        self.filters = filters


@pytest.mark.parametrize('downtime, repr', [
    (
        Downtime(filters=[juggler_sdk.DowntimeSelector(namespace='q', host='w')]),
        'host=w & namespace=q'
    ),
    (
        Downtime(filters=[
            juggler_sdk.DowntimeSelector(namespace='q', host='w'),
            juggler_sdk.DowntimeSelector(namespace='qq', host='ww')
        ]),
        '(host=w & namespace=q) | (host=ww & namespace=qq)'
    ),
])
def test_print_downtime(downtime: Downtime, repr: str):
    assert lib.print_downtime(downtime) == repr
