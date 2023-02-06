from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink
from nile.api.v1 import Record

from projects.common.nile import test_utils
from projects.support.data_context.collect_data import (
    parse_history,
    process_chatterbox,
)


def test_parse_history(load_json):
    history = test_utils.to_bytes(load_json('autoreply_with_support.json'))
    history_data = parse_history(history)

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
    process_chatterbox(input_table).label('output')

    input_records = list(iter_records(load_json('chatterbox_table.json')))

    output = []
    job.local_run(
        sources={'input': StreamSource(input_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 3

    assert output[0]['autoreply_collect_data'] is False
    assert output[0]['support_comments_count_collect_data'] == 3
    assert output[0]['support_admin_collect_data'] == b'maksatat'
    assert output[0]['first_macro_id_collect_data'] == 87044

    assert output[1]['autoreply_collect_data'] is False
    assert output[1]['support_comments_count_collect_data'] == 1
    assert output[1]['support_admin_collect_data'] == b'natinatalia'

    assert output[2]['autoreply_collect_data'] is True
    assert output[2]['support_comments_count_collect_data'] == 0
    assert output[2]['support_admin_collect_data'] == b'superuser'
