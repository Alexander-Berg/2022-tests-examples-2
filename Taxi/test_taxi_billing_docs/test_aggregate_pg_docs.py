import typing as tp

from dateutil import parser
from dateutil import tz
import pytest

from taxi_billing_docs.cron.tasks import aggregate_pg_docs as tasks
from test_taxi_billing_docs import conftest as tst


CONST_NOW = '2019-12-20T21:00:00'
CONST_NOW_OBJ = parser.parse(CONST_NOW).astimezone(tz.tzutc())

YT_DIR = '//home/taxi/unittests/services/taxi-billing-docs/'


class MockedTable:
    def __init__(
            self,
            data: tp.List[tp.List[tp.Any]],
            names: tp.Optional[tp.List[str]] = None,
            types: tp.Optional[tp.List[str]] = None,
    ):
        self._data: tp.List[tp.List[tp.Any]] = data
        self._names: tp.List[str] = names or []
        self._types: tp.List[str] = types or []

    def fetch_full_data(self):
        pass

    @property
    def rows(self) -> tp.List[tp.List[tp.Any]]:
        return self._data

    @property
    def column_names(self) -> tp.List[str]:
        return self._names

    @property
    def column_types(self) -> tp.List[str]:
        return self._types

    @property
    def is_good(self) -> bool:
        if len(self.column_names) != len(self.column_types):
            return False
        for row in self.rows:
            if len(row) != len(self.column_names):
                return False
        return True


class MockedDB:
    def __init__(self):
        self.reset()

    def reset(self):
        self._db: tp.Dict[str, MockedTable] = {
            YT_DIR
            + 'doc_chunks_pg': MockedTable(
                data=[],
                names=[
                    'created',
                    'shard_id',
                    'chunk_id',
                    'num',
                    'hash',
                    'last_seq_id',
                    'last_created',
                ],
                types=[
                    'Uint64',
                    'Uint64',
                    'Uint64',
                    'String',
                    'Uint64',
                    'Uint64',
                    'Uint64',
                ],
            ),
        }

    def write_table(
            self,
            path: str,
            data_iterator: tp.Iterable,
            column_names: tp.List[str],
            column_types: tp.List[str],
            append: bool = True,
            **kwargs,
    ):
        if path not in self._db or not append:
            self._db[path] = MockedTable(
                data=[], names=column_names, types=column_types,
            )
        print(f'append to {path}')
        for row in data_iterator:
            print(f'  {repr(row)}')
            self._db[path].rows.append(row)
        print('... done')
        assert self._db[path].is_good, f'inconsistent table: {path}'

    def read_table(self, path: str) -> MockedTable:
        assert path in self._db, f'path "{path}" not in {self._db.keys()}'
        print(f'--- {path} ---')
        for row in self._db[path].rows:
            print(f'  {repr(row)}')
        print('--- end of data ---')
        return self._db[path]


@pytest.fixture
def mocked_yt(patch) -> MockedDB:

    yt_base = MockedDB()

    # pylint: disable=unused-variable
    @patch('yql.api.v1.client.YqlClient.write_table')
    def write_table(
            path: str,
            data_iterator: tp.Iterable,
            column_names: tp.List[str],
            column_types: tp.List[str],
            append: bool = True,
            **kwargs,
    ):
        nonlocal yt_base
        yt_base.write_table(
            path, data_iterator, column_names, column_types, append, **kwargs,
        )

    return yt_base


@pytest.mark.pgsql(
    'billing_docs@0', files=('meta.sql', 'doc@0.sql', 'event@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('meta.sql', 'doc@1.sql', 'event@1.sql'),
)
@pytest.mark.config(
    BILLING_DOCS_PG_PREPARE_AUDIT_DATA_CHUNK_SIZE=10000,
    BILLING_DOCS_PG_PREPARE_AUDIT_DATA_ITER_COUNT=10,
    BILLING_DOCS_PG_PREPARE_AUDIT_DATA_WINDOW_SIZE=1000000,
    BILLING_DOCS_PG_PREPARE_AUDIT_DATA_WORK_DELAY=0,
    BILLING_DOCS_PREPARE_AUDIT_DATA_CHUNK_SIZE=10,
    BILLING_DOCS_PREPARE_AUDIT_DATA_LAG_HOURS=1,
)
@pytest.mark.now(CONST_NOW_OBJ.isoformat())
@pytest.mark.parametrize(
    'yt_responses, yt_expected_result',
    [
        pytest.param(
            [[]],
            [
                [
                    1576864800000000,
                    3,
                    10,
                    1,
                    12142702955,
                    10,
                    1536563272019582,
                ],
                [1576864800000000, 3, 20, 1, 8310300492, 20, 1536563272019582],
                [1576864800000000, 3, 30, 1, 5474354804, 30, 1536649672019582],
                [1576864800000000, 3, 40, 1, 4107100274, 40, 1536649672019582],
                [1576864800000000, 3, 50, 1, 6144583761, 50, 1536649672019582],
                [
                    1576864800000000,
                    3,
                    60,
                    1,
                    11354413426,
                    60,
                    1536649672019582,
                ],
                [1576864800000000, 4, 40, 1, 8801242093, 40, 1536563272019582],
                [1576864800000000, 4, 70, 1, 4648525705, 70, 1536563272019582],
                [1576864800000000, 4, 80, 1, 8009966169, 80, 1536563272019582],
            ],
            marks=pytest.mark.config(
                BILLING_DOCS_REPLICATE_NEW_DOCS_SINCE=(
                    '2099-01-01T00:00:00+00:00'
                ),
            ),
        ),
        pytest.param(
            [[[0, 10], [2, 20], [3, 50], [4, 70]]],
            [
                [
                    1576864800000000,
                    3,
                    60,
                    1,
                    11354413426,
                    60,
                    1536649672019582,
                ],
                [1576864800000000, 4, 80, 1, 8009966169, 80, 1536563272019582],
            ],
            marks=pytest.mark.config(
                BILLING_DOCS_REPLICATE_NEW_DOCS_SINCE=(
                    '2099-01-01T00:00:00+00:00'
                ),
            ),
        ),
        pytest.param(
            [[[0, 10], [2, 20], [3, 50], [4, 70]]],
            [
                [
                    1576864800000000,
                    3,
                    60,
                    1,
                    11354413426,
                    60,
                    1536649672019582,
                ],
                [1576864800000000, 4, 80, 1, 8009966169, 80, 1536563272019582],
                [
                    1576864800000000,
                    4,
                    90,
                    1,
                    10585596110,
                    90,
                    1536563272019582,
                ],
            ],
            marks=pytest.mark.config(
                BILLING_DOCS_REPLICATE_NEW_DOCS_SINCE=(
                    '2000-01-01T00:00:00+00:00'
                ),
            ),
        ),
    ],
)
async def test_cron_usage(
        docs_cron_app,
        yt_responses: tp.List,
        yt_expected_result,
        mocked_yql: tp.List,
        mocked_yt: MockedDB,  # pylint: disable=redefined-outer-name
        patch,
):
    @patch('random.shuffle')
    def _shuffle(array: tp.List):
        pass

    for response in yt_responses:
        mocked_yql.append(  # _get_last_ids_per_vshard
            tst.MockedRequest(
                tst.MockedResult(
                    tst.YT_STATUS_COMPLETED, [tst.MockedTable(response)],
                ),
            ),
        )
    task = tasks.AggregatePGDocs(context=docs_cron_app)
    await task.aggregate()
    actual = mocked_yt.read_table(YT_DIR + 'doc_chunks_pg').rows
    actual = sorted(actual, key=lambda row: row[1])
    assert actual == yt_expected_result
