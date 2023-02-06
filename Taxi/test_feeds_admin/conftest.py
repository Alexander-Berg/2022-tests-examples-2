# pylint: disable=redefined-outer-name
import typing

import pytest

import feeds_admin.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301


pytest_plugins = ['feeds_admin.generated.service.pytest_plugins']


@pytest.fixture
def mock_publication_actions(patch):
    actions = ['create', 'update', 'remove']

    action_queue = {}

    @patch(
        'feeds_admin.views.publication_actions'
        '._testpoint_begin_publish_actions',
    )
    async def _testpoint_begin_publish_actions() -> None:
        for action in actions:
            action_queue[action] = []

    @patch('feeds_admin.views.publication_actions._testpoint_publish_actions')
    async def _testpoint_publish_actions(action_type, actions) -> None:
        nonlocal action_queue
        queue = action_queue[action_type.value]
        for action in actions:
            queue.append(
                {
                    'recipient_id': action.recipient_id,
                    'payload_params': action.payload_params,
                },
            )

    return action_queue


@pytest.fixture
def mock_yql(patch):
    """Set result of next YQL query"""

    def mock_next_query_result(*, columns, rows):
        @patch('yql.api.v1.client.YqlClient.query')
        def _query(*args, **kwargs):
            return _MockYqlRequestOperation(columns, rows)

    return mock_next_query_result


class _MockYqlResults:
    class result:  # pylint: disable=C0103
        status_code = 200
        text = 'OK'

    errors: typing.List[str] = []
    _rows = None

    def __init__(self, columns, rows):
        self._columns = columns
        self._rows = rows

    def __iter__(self):
        class _Table:
            rows = self._rows
            column_names = self._columns

            def get_iterator(self):
                return self.rows

        return iter([_Table()])


class _MockYqlRequestOperation:
    def __init__(self, columns, rows):
        self._columns = columns
        self._rows = rows

    def run(self):
        return _MockYqlRequestOperation(self._columns, self._rows)

    def get_results(self):
        return _MockYqlResults(self._columns, self._rows)

    @property
    def special(self):
        return """[
            <table>
                <tr>
                    <th>Id</th>
                    <th>Title</th>
                    <th>Content</th>
                    <th>Type</th>
                    <th>Files</th>
                    <th>Attributes</th>
                    <th>Parameters</th>
                    <th>ClusterType</th>
                    <th>QueryType</th>
                    <th>CreatedAt</th>
                    <th>UpdatedAt</th>
                    <th>Status</th>
                    <th>WorkerId</th>
                    <th>WorkerVersion</th>
                    <th>WorkerPid</th>
                    <th>WorkerHost</th>
                    <th>ExternalQueryIds</th>
                </tr>
                <tr>
                    <td>5dc3206e095c4ea674695614</td>
                    <td></td>
                    <td>SELECT * FROM '//home/recipients/'</td>
                    <td>SQL</td>
                    <td>[]</td>
                    <td>{'user_agent': 'Mozilla/5.0'}</td>
                    <td>{}</td>
                    <td>UNKNOWN</td>
                    <td>SQL</td>
                    <td>11-06 19:35:10</td>
                    <td>11-06 19:35:11</td>
                    <td>COMPLETED</td>
                    <td>b3217e9-bcfa8dab-6c5ad2c0-9dd69ca0</td>
                    <td>5884539</td>
                    <td>660104</td>
                    <td>yql-myt-prod01.search.yandex.net</td>
                    <td>[]</td>
                </tr>
            </table>
        ]"""
