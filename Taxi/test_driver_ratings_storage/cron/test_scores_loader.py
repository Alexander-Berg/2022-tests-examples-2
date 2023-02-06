# pylint: disable=redefined-outer-name,duplicate-code,unused-variable
import typing as tp

import pytest

from driver_ratings_storage.generated.cron import run_cron

SCORES = {
    ('2021-05', 1620025200, 1620028800): [
        {
            'created_idx': 1620026784,
            'id': '9d8c03e1d4291896b6ddf8478657b295',
            'performer_db_id': 'park_id1',
            'performer_uuid': 'driver_id1',
            'feedback': {'rating': 5},
            'user_fraud': None,
        },
        {
            'created_idx': 1620027203,
            'id': '9b9e3d3d78213253a71950c53b203873',
            'performer_db_id': 'park_id1',
            'performer_uuid': 'driver_id1',
            'feedback': {'rating': 5},
            'user_fraud': False,
        },
        {
            'created_idx': 1620027557,
            'id': '142f23be32023b769f01335da0c68475',
            'performer_db_id': 'park_id1',
            'performer_uuid': 'driver_id_2',
            'feedback': {'rating': 5},
            'user_fraud': True,
        },
    ],
    ('2021-04', 1617260400, 1617264000): [
        {
            'created_idx': 1617263089,
            'id': '0581aeac3663116f95af318bc08cc05a',
            'performer_db_id': 'park_id1',
            'performer_uuid': 'driver_id3',
            'feedback': {'rating': 3},
            'user_fraud': False,
        },
        {
            'created_idx': 1617263190,
            'id': 'de17b77b8fd2308fbdd010bfbadc7c90',
            'performer_db_id': 'park_id1',
            'performer_uuid': 'driver_id3',
            'feedback': {'rating': 1},
            'user_fraud': True,
        },
        {
            'created_idx': 1617264291,
            'id': 'f4de569feba8c247b29b53205c455b55',
            'performer_db_id': 'park_id1',
            'performer_uuid': 'driver_id3',
            'feedback': {'rating': 2},
            'user_fraud': False,
        },
        {
            'created_idx': 1617264410,
            'id': 'c7c83c0fefd01fe9a359b9455f6bf4d6',
            'performer_db_id': 'park_id1',
            'performer_uuid': 'driver_id3',
            'feedback': {'rating': 1},
            'user_fraud': True,
        },
        {
            'created_idx': 1617264708,
            'id': 'a0a03df5ff242675b48d7c44dc4f915f',
            'performer_db_id': 'park_id1',
            'performer_uuid': 'driver_id3',
            'feedback': {'rating': 1},
            'user_fraud': None,
        },
    ],
}


def fetch_postfix(path):
    return path.split('/')[-1]


class MockedTable:
    def __init__(self, query):
        self.query = query

    def get_iterator(self):
        postfix = fetch_postfix(self.query)
        return SCORES[postfix]

    @property
    def column_names(self):
        return [
            'created_ts',
            'order_id',
            'park_id',
            'driver_profile_id',
            'udid',
            'score',
            'fraud',
        ]


class MockedResult:
    def __init__(self, query):
        self.query = query

    @property
    def status(self) -> str:
        return 'COMPLETED'

    @property
    def is_success(self) -> bool:
        return True

    @property
    def errors(self) -> tp.List[Exception]:
        return []

    def run(self):
        pass

    def get_results(self, *args, **kwargs):
        return self

    @property
    def share_url(self):
        return ''

    def __iter__(self):
        yield MockedTable(self.query)


@pytest.mark.now('2021-05-07T00:00:00')  # for testing [2021-04, 2021-05]
@pytest.mark.parametrize(
    'scores',
    (
        pytest.param(
            [score for scores in SCORES.values() for score in scores],
            id='init',
        ),
        pytest.param(
            [score for score in SCORES[('2021-05', 1620025200, 1620028800)]],
            marks=pytest.mark.pgsql(
                'driver_ratings_storage',
                queries=[
                    'INSERT INTO '
                    'common.events(task_id, name, created_at, details) '
                    'VALUES (\'3333333333\', \'scores_loader\', '
                    '\'2021-05-03 00:00:00\', '
                    '\'{"created_idx": 1620018000.0}\'::JSONB);',
                ],
            ),
            id='incremental',
        ),
    ),
)
async def test_cron(patch, pgsql, mock_unique_drivers, scores):
    @mock_unique_drivers('/v1/driver/uniques/retrieve_by_profiles')
    async def _v1_driver_new(request):
        profile_ids = request.json['profile_id_in_set']
        return {
            'uniques': [
                {
                    'park_driver_profile_id': park_driver_profile_id,
                    'data': {'unique_driver_id': 'some_unique'},
                }
                for park_driver_profile_id in profile_ids
            ],
        }

    plugin_path = (
        'driver_ratings_storage.generated.cron.'
        'yt_wrapper.plugin.AsyncYTClient'
    )

    @patch(plugin_path + '.read_table')
    async def yt_read(path, *args, **kwargs):
        postfix = fetch_postfix(str(path))
        time_range = path.attributes['ranges'][0]

        lower_limit = (
            time_range['lower_limit']['key'][0]
            if time_range.get('lower_limit')
            else None
        )
        upper_limit = (
            time_range['upper_limit']['key'][0]
            if time_range.get('upper_limit')
            else None
        )

        return SCORES.get((postfix, lower_limit, upper_limit), [])

    await run_cron.main(
        ['driver_ratings_storage.crontasks.scores_loader', '-t', '0'],
    )

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        for score in scores:
            cursor.execute(
                f"""
                SELECT
                    order_id,
                    park_id,
                    driver_profile_id,
                    score,
                    scored_at
                FROM driver_ratings_storage.driver_scores
                WHERE
                    order_id='{score['id']}'
                """,
            )
            rows = list(cursor)
            assert len(rows) == 1
            inserted = rows[0]
            assert inserted[0] == score['id']
            assert inserted[1] == score['performer_db_id']
            assert inserted[2] == score['performer_uuid']
            assert inserted[3] == score['feedback']['rating']
