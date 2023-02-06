from ukrop.graphs.test_jupiter import test_jupiters_url_pool
from ukrop.graphs.run import run_graph


def init_subparser(parser):
    parser.add_argument("-j", '--custom-jupiter-states', nargs='+', help='Specify the list of jupiter states to compare (Format: state-0 [state-1 [...]])')
    parser.add_argument("-v", '--custom-validation-set', nargs='+', help='Array of custom sets. Format: [s-0 [s-1 [...]]]; s-0 is a tuple <validation_set_urls:name:jupiter_state>')
    return parser


def run(args):
    title = ''
    if args.custom_jupiter_states is not None:
        title += ', '.join(args.custom_jupiter_states)
    if args.custom_validation_set is not None:
        title += ', '.join(args.custom_validation_set)
    if len(title) == 0:
        title = 'All Jupiter States'

    run_graph(
        args,
        "Test Jupiter's results: %s" % title,
        [test_jupiters_url_pool(args)]
    )
