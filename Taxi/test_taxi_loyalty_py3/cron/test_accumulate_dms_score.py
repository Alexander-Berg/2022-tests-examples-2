import pytest
from yql import config as yql_config

from taxi_loyalty_py3.generated.cron import run_cron


class _MockYqlRequestResults:
    is_success = True
    errors = None
    empty = False

    @property
    def dataframe(self):
        return self

    @property
    def full_dataframe(self):
        return self

    def to_dict(self, *args, **kwargs):
        return {}


class _MockYqlRequestOperation:
    share_url = ''

    def run(self, parameters):
        assert parameters == {
            '$wallet_table': (
                '{"Data": "//home/taxi/unittests/'
                'features/loyalty/dms_wallet/2020-05"}'
            ),
            '$udids_table': (
                '{"Data": "home/taxi/unittests/'
                'replica/postgres/dm_storage/common_udids"}'
            ),
            '$data_table': (
                '{"Data": "home/taxi/unittests/'
                'replica/postgres/dm_storage/data_logs/2020-05"}'
            ),
            '$tmp_folder': (
                '{"Data": "//home/taxi/unittests/'
                'features/loyalty/dms_wallet/tmp"}'
            ),
            '$last_datetime': '{"Data": "1590958800"}',
            '$prev_data_table': (
                '{"Data": "home/taxi/unittests/replica/'
                'postgres/dm_storage/data_logs/2020-04"}'
            ),
            '$start_datetime': '{"Data": "1588280400"}',
        }

    def subscribe(self, *args, **kwargs):
        pass

    def get_results(self, *args, **kwargs):
        return _MockYqlRequestResults()


@pytest.mark.now('2020-05-10 00:00:00')
@pytest.mark.config(
    LOYALTY_JOBS_SETTINGS={
        '__default__': {},
        'accumulate_dms_score': {
            'enabled': True,
            'hours_to_next_month_start': 32 * 24,
            'hours_to_next_month_end': 0,
        },
    },
)
async def test_accumulate_dms_score(patch):
    yt_wrapper = 'taxi_loyalty_py3.generated.cron.yt_wrapper.plugin.'

    @patch(yt_wrapper + 'AsyncYTClient.create')
    async def _create(*args, **kwargs):
        return kwargs['path']

    @patch(yt_wrapper + 'AsyncYTClient.exists')
    async def _exists(*args, **kwargs):
        return False

    @patch('yql.api.v1.client.YqlClient.query')
    def _query(query_str, **kwargs):
        assert yql_config.config.db == 'hahn'
        return _MockYqlRequestOperation()

    await run_cron.main(
        ['taxi_loyalty_py3.crontasks.accumulate_dms_score', '-t', '0'],
    )
