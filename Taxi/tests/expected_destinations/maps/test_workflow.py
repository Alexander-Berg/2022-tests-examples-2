from projects.expected_destinations.maps import workflow

from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink
from nile.api.v1 import Record

from mock import patch, Mock

from projects.common.nile.ml_yt_path import MlPath
from projects.common.nile.test_utils import to_bytes


INPUT = [
    {
        'created': '2019-05-15 12:35:41',
        'destination': {
            'country': 'Россия',
            'exact': False,
            'full_text': 'Россия, Москва, Саринский проезд, 13с2',
            'lat': 55.72961,
            'lon': 37.657476,
            'type': 'address',
        },
        'id': '0eb8ad09c42b492db6588887b444e24b',
        'route_type': 'transport',
        'source': {
            'country': 'Россия',
            'exact': False,
            'full_text': 'Россия, Москва, Дубнинская улица, 48к2',
            'lat': 55.89338833,
            'lon': 37.56028,
            'type': 'address',
        },
    },
    {
        'created': '2019-05-15 13:42:45',
        'destination': {
            'country': 'Россия',
            'exact': False,
            'full_text': 'Россия, Москва, Саринский проезд, 13с2',
            'lat': 55.72961,
            'lon': 37.657476,
            'type': 'address',
        },
        'id': '0eb8ad09c42b492db6588887b444e24b',
        'route_type': 'transport',
        'source': {
            'country': 'Россия',
            'exact': False,
            'full_text': 'Россия, Москва, Северо-Восточный административный округ, \
                    район Отрадное',
            'lat': 55.86541333,
            'lon': 37.57364333,
            'type': 'address',
        },
    },
    {
        'created': '2019-05-15 06:41:19',
        'destination': {
            'country': 'Турция',
            'exact': False,
            'full_text': 'Türkiye, İstanbul, Dr. Eyüp Aksoy Cad.',
            'lat': 40.999411,
            'lon': 29.029464,
            'type': 'address',
        },
        'id': '0eb8b86fa2e1e525b99d3caff227c623',
        'route_type': 'car',
        'source': {
            'country': 'Турция',
            'exact': False,
            'full_text': 'Türkiye, İstanbul, Avcılar, E-5 Londra Asfaltı Cad.',
            'lat': 40.9850783,
            'lon': 28.7232317,
            'type': 'address',
        },
    },
]


@patch('projects.expected_destinations.maps.workflow.args')
@patch('projects.expected_destinations.maps.workflow.get_config')
def test_workflow(mock_get_config, mock_args, load_json):
    mock_args.return_value = Mock(quantity_suffix='', exp_id='')
    mock_get_config.return_value = load_json('config.json')

    job = clusters.MockCluster().job()
    ml_dev_path = MlPath('maps_suggest', experiment='nevermind')

    workflow.collect_user_history(job, ml_dev_path)
    collect_user_history_output = []
    job.local_run(
        sources={
            'source': StreamSource(
                [Record(Trip=to_bytes(trip)) for trip in INPUT],
            ),
        },
        sinks={'routes_history': ListSink(collect_user_history_output)},
    )
    assert len(collect_user_history_output) == 2

    compile_data_output = []
    workflow.compile_data(job, ml_dev_path)
    job.local_run(
        sources={
            'routes_history': StreamSource(
                to_bytes(collect_user_history_output),
            ),
        },
        sinks={'data': ListSink(compile_data_output)},
    )
    assert len(compile_data_output) == 3

    history_size_distribution_output = []
    workflow.history_size_distribution(job, ml_dev_path)
    job.local_run(
        sources={'data': StreamSource(to_bytes(compile_data_output))},
        sinks={
            'history_size_distribution': ListSink(
                history_size_distribution_output,
            ),
        },
    )
    assert len(history_size_distribution_output) == 1

    eval_max_quality_output = []
    workflow.eval_max_quality(job, ml_dev_path)
    job.local_run(
        sources={'data': StreamSource(to_bytes(compile_data_output))},
        sinks={'quality_max': ListSink(eval_max_quality_output)},
    )
    assert len(eval_max_quality_output) == len(workflow.DROPPED_MINUTES)

    eval_heuristic_quality_output = []
    workflow.eval_heuristic_quality(job, ml_dev_path)
    job.local_run(
        sources={'data': StreamSource(to_bytes(compile_data_output))},
        sinks={'quality_heuristic': ListSink(eval_heuristic_quality_output)},
    )
    assert len(eval_heuristic_quality_output) == 20

    train_test_split_train_output = []
    train_test_split_test_output = []
    workflow.train_test_split(job, ml_dev_path)
    job.local_run(
        sources={'data': StreamSource(to_bytes(compile_data_output))},
        sinks={
            'data_train': ListSink(train_test_split_train_output),
            'data_test': ListSink(train_test_split_test_output),
        },
    )
    assert len(train_test_split_train_output) == 3
    assert len(train_test_split_test_output) == 0

    prepare_nirvana_train_output = []
    workflow.prepare_nirvana_train(job, ml_dev_path)
    job.local_run(
        sources={
            'data_train': StreamSource(
                to_bytes(train_test_split_train_output),
            ),
        },
        sinks={'data_nirvana_train': ListSink(prepare_nirvana_train_output)},
    )
    assert len(prepare_nirvana_train_output) == 7
    for rec in prepare_nirvana_train_output:
        assert len(rec['value'].split('\t')) == 383

    eval_cand_quality_output = []
    workflow.eval_cand_quality(job, ml_dev_path)
    job.local_run(
        sources={'data': StreamSource(to_bytes(compile_data_output))},
        sinks={'quality_cand': ListSink(eval_cand_quality_output)},
    )
    assert len(eval_heuristic_quality_output) == 20
