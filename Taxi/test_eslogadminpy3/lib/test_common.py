import datetime

import pytest

from eslogadminpy3.lib import common


@pytest.mark.parametrize(
    'base, concrete, expected',
    [
        (None, datetime.datetime(2019, 10, 12), 'yandex-taxi-*2019.10.12.00'),
        (
            None,
            datetime.datetime(2019, 10, 12, 10),
            'yandex-taxi-*2019.10.12.10',
        ),
        (
            'yandex-taxi-api',
            datetime.datetime(2019, 10, 12),
            'yandex-taxi-api-2019.10.12.00',
        ),
        (None, None, 'yandex-taxi-*'),
        ('yandex-taxi-api', None, 'yandex-taxi-api*'),
        ('yandex-taxi-api-', None, 'yandex-taxi-api-*'),
    ],
)
def test_index_builder(base, concrete, expected):
    assert expected == common.build_es_index(base, concrete)
