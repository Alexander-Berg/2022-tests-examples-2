import json
import yatest.common

generate_tracks_bin = yatest.common.binary_path("taxi/graph/tools/generate-graph-tracks/taxi-generate-graph-tracks")

graph_data = yatest.common.binary_path("taxi/graph/data/graph3/")

GEN_COUNT = 5


def test_generate():
    generated_filename = 'generated'
    with open(generated_filename, 'w+') as f:
        yatest.common.execute([generate_tracks_bin, '--graph-dir', graph_data,
                               '--count', str(GEN_COUNT)],
                              stdout=f)

    # Re-open file
    with open(generated_filename) as f:
        res = json.load(f)
        assert len(res) == GEN_COUNT
        for elem in res:
            assert 'track' in elem
            track = elem['track']
            assert len(track) > 0
            pos = track[0]
            assert 'lat' in pos
            float(pos['lat'])
            assert 'lon' in pos
            float(pos['lon'])
            assert 'timestamp' in pos
            int(pos['timestamp'])
