import datetime
from ukrop.graphs.test_set import create_test_set
from ukrop.graphs.run import run_graph


def init_subparser(parser):
    parser.add_argument("-r", "--random-urls-count", type=int, help="Random urls count", required=True, dest='random_urls_count')
    parser.add_argument("--tmp-dir", type=str, default='//tmp', dest='tmp_dir')
    parser.add_argument("--test-table", type=str, default='//home/robot-quality/selection_rank/test/current', dest='test_table')
    parser.add_argument("--jupiter-test-table", type=str, default='//home/robot-quality/selection_rank/test/current_to_jupiter', dest='jupiter_test_table')
    parser.add_argument("--metrics-secret", type=str, default='robot_metrics_musca_metrics_token')
    return parser


def run(args):
    run_graph(
        args,
        'Create Test Set %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        create_test_set(args)
    )
