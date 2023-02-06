import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_tags.tags import tags_tools


_NOW = datetime.datetime(2019, 12, 27, 11, 22, 32, 0)
_MINUTE = datetime.timedelta(minutes=1)
_DAY = datetime.timedelta(days=1)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    TAGS_TOPICS_POLICY={
        '__default__': 'non_cached',
        'commissions': 'cached',
        'basic': 'cached',
    },
)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_tag_names(
            [
                tags_tools.TagName(2000, 'programmer'),
                tags_tools.TagName(2001, 'manager'),
                tags_tools.TagName(2002, 'engineer'),
            ],
        ),
        tags_tools.insert_topics(
            [
                tags_tools.Topic(4000, 'commissions', False),
                tags_tools.Topic(4001, 'tech', True),
                tags_tools.Topic(4002, 'basic', True),
            ],
        ),
        tags_tools.insert_relations(
            [tags_tools.Relation(2000, 4000), tags_tools.Relation(2001, 4001)],
        ),
    ],
)
@pytest.mark.parametrize(
    'topics, only_cached, excepted_code, excepted_json',
    [
        (['commissions', 'basic'], True, 200, {'commissions': ['programmer']}),
        (['commissions', 'tech'], None, 400, None),
        (['commissions', 'tech'], True, 400, None),
        (
            ['commissions', 'basic'],
            False,
            200,
            {'commissions': ['programmer']},
        ),
        (
            ['commissions', 'tech'],
            False,
            200,
            {'commissions': ['programmer'], 'tech': ['manager']},
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_topics_relations(
        taxi_tags,
        topics: List[str],
        only_cached: Optional[bool],
        excepted_code: int,
        excepted_json: Dict[str, List[str]],
):
    body: Dict[str, Any] = {'topics': topics}
    if only_cached is not None:
        body['only_cached'] = only_cached
    response = await taxi_tags.post('v1/topics_relations', body)
    assert response.status_code == excepted_code
    if excepted_json:
        response = response.json()
        for tags in response.values():
            tags.sort()
        assert response == excepted_json
