import datetime
from ukrop.graphs.callisto_test import create_test_set
from ukrop.graphs.run import run_graph


def init_subparser(parser):
    parser.add_argument("-r", "--random-urls-count", type=int, help="Random urls count", required=True, dest='random_urls_count')
    parser.add_argument("--test-table", type=str, default='//home/ukropdata/selection_rank/test/current', dest='test_table')
    parser.add_argument('--tmp-dir', type=str, default='//tmp')
    return parser


def run(args):
    run_graph(
        args,
        'Create Callisto Test Set %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        create_test_set(args)
    )
