from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink
from nile.api.v1 import Record

from projects.common.nile import test_utils
from projects.autoreply.client_suport import dwh


def test_parse_history(load_json):
    history = test_utils.to_bytes(load_json('autoreply_with_support.json'))
    history_data = dwh.parse_history(history)
    assert history_data.autoreply is True
    assert history_data.first_macro_id == 124899
    assert history_data.support_comments_count == 1


def iter_records(data):
    for elem in data:
        params = {k: test_utils.to_bytes(v) for k, v in elem.items()}
        yield Record(**params)


def test_preprocess_chatterbox(load_json):
    job = clusters.MockCluster().job()

    input_table = job.table('//input').label('input')
    dwh.process_chatterbox(input_table).label('output')

    input_records = list(iter_records(load_json('chatterbox_table.json')))

    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 3

    assert output[0]['autoreply'] is False
    assert output[0]['csat'] is None
    assert output[0]['support_comments_count'] == 3
    assert output[0]['support_admin'] == b'maksatat'
    assert output[0]['line'] == b'corp_email_rus'
    assert output[0]['first_macro_id'] == 87044

    assert output[1]['autoreply'] is False
    assert output[1]['csat'] is None
    assert output[1]['support_comments_count'] == 1
    assert output[1]['support_admin'] == b'natinatalia'
    assert output[1]['line'] == b'driver_fin'

    assert output[2]['autoreply'] is True
    assert output[2]['csat'] == 5
    assert output[2]['support_comments_count'] == 0
    assert output[2]['support_admin'] == b'superuser'
    assert output[2]['line'] == b'first_center'
