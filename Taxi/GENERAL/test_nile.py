import argparse
import sys

from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1 import files as nfl
from nile.api.v1 import with_hints

from cprojects import graph
from projects.common.nile import environment

DM_ORDER_PATH = '//home/taxi-dwh/summary/dm_order/2020-01'
LATEST_GRAPH_PATH = '//home/maps/graph/latest'
SMALL_GRAPH_PATH = (
    '//home/maps/graph/tmp/19.09.25-0~immartynov.cis2.development'
)
ROAD_GRAPH_FILENAME = 'road_graph.fb'
RTREE_FILENAME = 'rtree.fb'
DETECT_GATES_RADIUS = 1000


def get_cluster():
    return environment.configure_environment(
        clusters.yt.YT(proxy=args.yt_proxy),
        add_cxx_bindings=True,
        nfl_files=[nfl.DevelopPackage('/home/tilgasergey/ml/junk')],
    )


def get_mapper(max_distance, graph_path):
    @with_hints(
        files=[
            nfl.RemoteFile(f'{graph_path}/{ROAD_GRAPH_FILENAME}'),
            nfl.RemoteFile(f'{graph_path}/{RTREE_FILENAME}'),
        ],
    )
    def mapper(records):
        print('loading graph...', file=sys.stderr)
        road_graph = graph.create_road_graph(
            road_graph_filename=ROAD_GRAPH_FILENAME,
            rtree_filename=RTREE_FILENAME,
        )
        print('loaded!', file=sys.stderr)
        for r in records:
            source_point = [r.order_source_lon, r.order_source_lat]
            position = road_graph.getNearestEdgePoint(
                r.order_source_lon, r.order_source_lat, max_distance,
            )
            if position is None:
                yield Record(source_point=source_point)
                continue
            coords = road_graph.getCoords(position)
            reversed_edge_id = road_graph.getReverseEdgeId(position.edgeId)
            detect_gates_stats = graph.detect_gates(
                road_graph, position, DETECT_GATES_RADIUS,
            )
            yield Record(
                source_point=source_point,
                edge_id=position.edgeId,
                reversed_edge_id=reversed_edge_id,
                edge_position=position.position,
                edge_point=[coords.lon, coords.lat],
                detect_gates_stats={
                    'exitGatesCount': detect_gates_stats.exitGatesCount,
                    'looseEndsCount': detect_gates_stats.looseEndsCount,
                    'edgesVisited': detect_gates_stats.edgesVisited,
                },
            )

    return mapper


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--graph-path', type=str, default=LATEST_GRAPH_PATH)
    parser.add_argument('--output-path', type=str, required=True)
    parser.add_argument('--max-distance', type=float, default=100)
    parser.add_argument('--memory-limit', type=int, default=None)
    parser.add_argument(
        '--yt-proxy', type=str, default=environment.DEFAULT_CLUSTER,
    )
    args = parser.parse_args()

    job = get_cluster().job()
    job.table(DM_ORDER_PATH).map(
        get_mapper(args.max_distance, args.graph_path),
        memory_limit=args.memory_limit,
    ).put(args.output_path)
    job.run()
