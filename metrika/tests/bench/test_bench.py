import json
import os
import subprocess
import yatest.common


def test_parser(mtmobproxy_simple_directories, metrics):
    os.environ["LOG_PATH"] = str(yatest.common.build_path("metrika/admin/python/logpusher/tests/data/mtmobproxy.log"))
    os.environ["LOGPUSHER_CONFIG"] = str(yatest.common.build_path("metrika/admin/python/logpusher/tests/data/mtmobproxy_simple.yaml"))
    os.environ["LOGPUSHER_LOG_FILE"] = os.path.join(mtmobproxy_simple_directories.out_root, "bench.log")
    yappi_path = os.path.join(mtmobproxy_simple_directories.out_root, "callgrind")
    os.makedirs(yappi_path)
    os.environ["YAPPI_PATH"] = yappi_path

    bench = yatest.common.binary_path("metrika/admin/python/logpusher/bin/bench/parser/logpusher-parser-bench")
    py_spy = yatest.common.binary_path("metrika/admin/py-spy/py-spy")

    bench_proc = subprocess.Popen((bench, "-f", "json"), stdout=subprocess.PIPE)
    py_spy_proc = subprocess.Popen(
        (
            py_spy, "record",
            "-p", str(bench_proc.pid),
            "-o", os.path.join(mtmobproxy_simple_directories.report_dir, "flamegraph.xml"),
        ),
    )

    stdout, _ = bench_proc.communicate()
    # py_spy_proc.terminate()
    py_spy_proc.communicate(timeout=10)
    retcode = bench_proc.returncode
    if retcode != 0:
        raise Exception("bench failed with exit code %d and stdout %s", retcode, stdout)

    print(stdout)

    metrics.set_benchmark(json.loads(stdout))
