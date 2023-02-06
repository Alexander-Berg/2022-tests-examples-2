import datetime

import pytest

from taxi.internal.yt_replication import utils


@pytest.mark.parametrize('clusters_info,expected', [
    (
        [{'last_updated': datetime.datetime(2017, 1, 2)}],
        datetime.datetime(2017, 1, 2),
    ),
    (
        [
            {'last_updated': datetime.datetime(2017, 3, 4)},
            {'last_updated': datetime.datetime(2017, 2, 3)},
        ],
        datetime.datetime(2017, 2, 3),
    ),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_get_min_last_updated(clusters_info, expected):
    result = utils.get_min_last_updated_or_raise(clusters_info)
    assert result == expected


@pytest.mark.parametrize('clusters_info', [
    # empty
    [],
    # one is None
    [{'last_updated': datetime.datetime.utcnow()}, {'last_updated': None}],
    # one is missing
    [{'last_updated': datetime.datetime.utcnow()}, {}],
    # all is None
    [{'last_updated': None}, {'last_updated': None}],
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_get_min_last_updated_failure(clusters_info):
    with pytest.raises(utils.UnknownLastUpdated):
        utils.get_min_last_updated_or_raise(clusters_info)
