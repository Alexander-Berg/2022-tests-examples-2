import json

import yatest.common as yc

from sandbox.projects.autocheck.lib import native_builds


class DumpClient(object):
    def __init__(self):
        self.result = []

    def send_chunk(self, payload):
        self.result.extend(payload)

    def dump(self):
        return json.dumps(self.result)


def test_native_builds():
    params = json.dumps([
        {
            'path': 'path/to/project1',
            'toolchain': 'clang7-win-x86_64-relwithdebinfo',
            'targets': ['path/to/project1/sub1', 'path/to/project1/sub2', 'path/to/project1/sub3']
        },
        {
            'path': 'path/to/project2',
            'toolchain': 'clang7-win-x86_64-relwithdebinfo',
            'targets': ['path/to/project2/sub1', 'path/to/project2/sub2', 'path/to/project2/sub3']
        },
        {
            'path': 'path/to/project3',
            'toolchain': 'clang7-win-x86_64-relwithdebinfo',
            'targets': ['path/to/project3/sub1']
        },
    ])

    bin_results = ['path/to/project1/sub1:uid1', 'path/to/project1/sub3:uid3', 'path/to/project2/sub2:uid2']
    bin_results_path = yc.output_path('bin_results.json')
    with open(bin_results_path, 'w') as f:
        json.dump(bin_results, f)

    client = DumpClient()
    nb = native_builds.NativeBuilds(params)
    nb.set_bin_result_path(bin_results_path)
    nb.run_native_builds(client, 0, True)
    return client.dump()
