#!/usr/bin/python3

import argparse
import json

# pylint: disable=import-error
import graphviz as gv


WIRE_TYPE_COLOR = {'data': 'blue', 'bounds': 'green', 'state': 'red'}
ENTRY_SHAPE = 'house'
OUT_SHAPE = 'invtriangle'


def parse_args():
    parser = argparse.ArgumentParser(
        description='View circuit schema as graph',
    )
    parser.add_argument('--filename', type=str, help='json schema filename')
    parser.add_argument(
        '--legend',
        dest='legend',
        action='store_true',
        help='add legend to image (default)',
    )
    parser.add_argument(
        '--no-legend',
        dest='legend',
        action='store_false',
        help='do not add legend to image',
    )
    parser.set_defaults(legend=True)

    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.filename, 'r') as graph:
        schema = json.load(graph)

    graph = gv.Digraph(
        name=args.filename, format='png', body=[f'label="{args.filename}"'],
    )

    graph.attr('node', shape=ENTRY_SHAPE)

    for node in schema['entry_points']:
        graph.node(node['id'])

    graph.attr('node', shape=OUT_SHAPE)

    for node in schema['out_points']:
        graph.node(node['id'])

    graph.attr('node', shape='ellipse')

    for node in schema['blocks']:
        graph.node(node['id'])

    for wire in schema['wires']:
        graph.edge(
            wire['from'], wire['to'], color=WIRE_TYPE_COLOR[wire['type']],
        )

    if args.legend:
        with graph.subgraph(
                name='clusterlegend', body=['label="Legend"'],
        ) as legend:
            # pylint: disable=no-member
            legend.node('entry', shape=ENTRY_SHAPE)
            # pylint: disable=no-member
            legend.node('out', shape=OUT_SHAPE)
            for wire_type in WIRE_TYPE_COLOR:
                # pylint: disable=no-member
                legend.edge(
                    'entry',
                    'out',
                    label=wire_type,
                    color=WIRE_TYPE_COLOR[wire_type],
                )

    graph.view()


if __name__ == '__main__':
    main()
