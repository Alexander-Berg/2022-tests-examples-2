from context.settings import settings
from core.yt_connection import YTConnection

sample = [
    {"timestamp": "2018-07-04T10:45:37.206019Z", "id": 1635798718, "event_type": "job_started"},
    {"timestamp": "2018-07-04T10:45:41.936127Z", "id": 1199727417, "event_type": "xxx"},
    {"timestamp": "2018-07-04T10:45:37.204844Z", "id": 3526028446, "event_type": "job_started"},
    {"timestamp": "2018-07-04T10:45:36.692502Z", "id": 3566952852, "event_type": "job_completed"},
    {"timestamp": "2018-07-04T10:45:39.884958Z", "id": 4258882432, "event_type": "job_completed"},
    {"timestamp": "2018-07-04T10:45:41.416617Z", "id": 2499187136, "event_type": "job_started"},
    {"timestamp": "2018-07-04T10:45:45.321227Z", "id": 2657551809, "event_type": "job_started"},
    {"timestamp": "2018-07-04T10:45:45.244115Z", "id": 3117603837, "event_type": "job_completed"}
]

yt_conn = YTConnection(
    cluster_name=settings('YT.CLUSTER_NAME'),
    chyt_alias=settings('YT.CHYT_ALIAS'),
    logger_extra={}
)


def write_table_test_flow(data, attributes):
    yt_client = yt_conn.yt_client
    with yt_client.TempTable(attributes=attributes) as tmp_table:
        yt_conn.write(data, tmp_table)
        res = yt_client.read_table(tmp_table)
        assert list(res) == data


def test_write_plain_table():
    attributes = {
        'dynamic': False,
        'schema': [
            {'name': 'id', 'type': 'int64'},
            {'name': 'timestamp', 'type': 'string'},
            {'name': 'event_type', 'type': 'string'},
        ]
    }

    write_table_test_flow(data=sample, attributes=attributes)


def test_write_sorted_table():
    attributes = {
        'dynamic': False,
        'schema': [
            {'name': 'id', 'type': 'int64', 'sort_order': 'ascending'},
            {'name': 'timestamp', 'type': 'string', 'sort_order': 'ascending'},
            {'name': 'event_type', 'type': 'string'},
        ]
    }
    data = sorted(sample, key=lambda item: (item['id'], item['timestamp']))
    yt_conn.create_table('/home/taxi-dwh-dev/')
    write_table_test_flow(data=data, attributes=attributes)


def test_write_dynamic_table():
    attributes = {
        'dynamic': True,
        'schema': [
            {'name': 'id', 'type': 'int64', 'sort_order': 'ascending'},
            {'name': 'timestamp', 'type': 'string', 'sort_order': 'ascending'},
            {'name': 'event_type', 'type': 'string'},
        ]
    }
    write_table_test_flow(data=sample, attributes=attributes)


def test_chyt_query():
    query = '''
        SELECT 1 as column
    '''

    res = yt_conn.execute_and_fetch(query, engine='chyt')
    assert next(res)['column'] == 1


def test_yql_query():
    query = '''
        SELECT 2 as column
    '''
    res = yt_conn.execute_and_fetch(query, engine='yql')
    assert next(res)['column'] == 2
