import pytest

from promotions.logic import yql
from promotions.models import promo
from promotions.repositories import storage as repo_storage
from promotions.stq import get_yql_data


class _MockYqlResults:
    def __init__(self, has_data=True):
        self.has_data = has_data

    class result:  # pylint: disable=C0103
        status_code = 200
        text = 'OK'

    def __iter__(self):
        return iter([_MockYqlTable(has_data=self.has_data)])


class _MockYqlRequestOperation:
    def __init__(self, has_data=True):
        self.has_data = has_data

    def run(self):
        return _MockYqlRequestOperation()

    @property
    def special(self):
        return """
            <table>\n<tr><th>Id</th><th>Title</th><th>Content</th>
            <th>Type</th><th>Files</th><th>Attributes</th>
            <th>Parameters</th><th>ClusterType</th><th>QueryType</th>
            <th>CreatedAt</th><th>UpdatedAt</th><th>Status</th>
            <th>WorkerId</th><th style="text-align: right;">WorkerVersion</th>
            <th style="text-align: right;">WorkerPid</th>
            <th>WorkerHost</th></tr>\n<tr>
            <td>5dc9212b9dee76fca7ec0158</td><td></td>
            <td>SELECT * FROM some_table;</td>
            <td>SQLv1</td><td>[]</td><td>{}</td><td>{}</td>
            <td>UNKNOWN</td><td>SQLv1</td><td>11-11 08:51:55</td>
            <td>11-11 08:51:57</td><td>COMPLETED</td>
            <td>b3217e9-bcfa8dab-6c5ad2c0-9dd69ca0</td>
            <td style="text-align: right;">5884539</td>
            <td style="text-align: right;">383434</td>
            <td>yql-myt-prod01.search.yandex.net</td></tr>\n</table>
        """

    def get_results(self):
        return _MockYqlResults(has_data=self.has_data)


class _MockYqlTable:
    def __init__(self, has_data=True):
        self.has_data = has_data

    def get_iterator(self):
        if self.has_data:
            return self.rows
        return []

    column_names = [
        'yandex_uid',
        'user_id',
        'phone_id',
        'param1',
        'param2',
        'param3',
    ]
    rows = [
        [
            'test_yandex_uid1',
            'test_user_id1',
            'test_phone_id1',
            'value1',
            'value2',
            'value3',
        ],
        [
            'test_yandex_uid2',
            'test_user_id2',
            'test_phone_id2',
            'value11',
            'value22',
            'value33',
        ],
        [
            'test_yandex_uid3',
            None,
            'test_phone_id3',
            'value21',
            'value22',
            'value23',
        ],
        [
            None,
            'test_user_id4',
            'test_phone_id4',
            'value31',
            'value32',
            'value33',
        ],
        [
            'test_yandex_uid5',
            'test_user_id5',
            None,
            'value31',
            'value32',
            'value33',
        ],
        [None, None, None, 'value41', 'value42', 'value43'],
    ]


@pytest.mark.pgsql('promotions', files=['pg_promotions_yql.sql'])
async def test_task(patch, stq3_context, load_json):
    @patch('yql.api.v1.client.YqlClient.query')
    def _query(*args, **kwargs):
        return _MockYqlRequestOperation()

    promotion_id = '6b2ee5529f5b4ffc8fea7008e6913ca7'
    await get_yql_data.task(context=stq3_context, promotion_id=promotion_id)

    storage = repo_storage.from_context(stq3_context)
    result = await storage.yql_cache.get_by_promotion_id(promotion_id)
    result = [item.serialize() for item in result]
    assert result == load_json('test_task_ok_result.json')


@pytest.mark.pgsql('promotions', files=['pg_promotions_yql.sql'])
@pytest.mark.parametrize(
    'exception_type',
    [
        pytest.param(yql.YTUnavailable, id='YTUnavailable error'),
        pytest.param(yql.BaseError, id='unknown error'),
    ],
)
async def test_retries(patch, stq3_context, exception_type):
    @patch('yql.api.v1.client.YqlClient.query')
    def _query(*args, **kwargs):
        raise exception_type

    promotion_id = '6b2ee5529f5b4ffc8fea7008e6913ca7'
    await get_yql_data.task(context=stq3_context, promotion_id=promotion_id)

    storage = repo_storage.from_context(stq3_context)
    result = await storage.promotions.get_by_id(promotion_id)
    assert result.yql_data.retries == 1


@pytest.mark.pgsql('promotions', files=['pg_promotions_yql.sql'])
async def test_retries_limit_reached(patch, stq3_context):
    @patch('yql.api.v1.client.YqlClient.query')
    def _query(*args, **kwargs):
        raise yql.YTUnavailable

    promotion_id = 'e8917b72eb694b6ca94bdfabf7a14caa'
    await get_yql_data.task(context=stq3_context, promotion_id=promotion_id)

    storage = repo_storage.from_context(stq3_context)
    result = await storage.promotions.get_by_id(promotion_id)
    assert result.yql_data.retries == 3
    assert promo.Status(result.status) == promo.Status.CRASHED


@pytest.mark.pgsql('promotions', files=['pg_promotions_yql.sql'])
async def test_empty_yt_response(patch, stq3_context, load_json):
    @patch('yql.api.v1.client.YqlClient.query')
    def _query(*args, **kwargs):
        return _MockYqlRequestOperation(has_data=False)

    promotion_id = '6b2ee5529f5b4ffc8fea7008e6913ca7'
    await get_yql_data.task(context=stq3_context, promotion_id=promotion_id)

    storage = repo_storage.from_context(stq3_context)
    result = await storage.yql_cache.get_by_promotion_id(promotion_id)
    result = [item.serialize() for item in result]
    assert result == []

    promo_object = await storage.promotions.get_by_id(promotion_id)
    assert promo_object.status == 'crashed'
