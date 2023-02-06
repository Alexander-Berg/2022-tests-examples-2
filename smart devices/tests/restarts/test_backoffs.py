import datetime
import json
import logging
import re
import yatest.common as yc

logger = logging.getLogger(__name__)


config = """{
    "nodes": [
        {
            "name": "main",
            "root": ".",
            "tasks": [
                {
                    "name": "heapy",
                    "allowedRestartIntervalSeconds" : 0,
                    "root": ".",
                    "path": "",
                    "log": false
                },
                {
                    "name": "exity",
                    "allowedRestartIntervalSeconds" : 0,
                    "root": ".",
                    "path": "",
                    "log": false
                },
                {
                    "name": "aborty",
                    "allowedRestartIntervalSeconds" : 0,
                    "root": ".",
                    "path": "",
                    "log": false
                },
                {
                    "name": "sleepy",
                    "allowedRestartIntervalSeconds" : 0,
                    "root": ".",
                    "path": "",
                    "log": false
                }
            ]
        }
    ]
}
"""


BACKOFF_MULTIPLIER = 2.5
JITTER_SHARE = 0.02
BASE_DELAY = 1


def calculate_restart_delay_interval(restart_number):

    delay = min(BASE_DELAY * (BACKOFF_MULTIPLIER ** (max(restart_number, 1) - 1)), 600)
    return int(delay * (1 - JITTER_SHARE)), int(delay * (1 + JITTER_SHARE))


def test_restart_backing_off(tmpdir):
    json_cfg = json.loads(config)
    json_cfg["nodes"][0]["tasks"][0]["path"] = str(
        yc.binary_path("smart_devices/tools/launcher2/test_apps/heapy/heapy")
    )
    json_cfg["nodes"][0]["tasks"][1]["path"] = str(
        yc.binary_path("smart_devices/tools/launcher2/test_apps/exity/exity")
    )
    json_cfg["nodes"][0]["tasks"][2]["path"] = str(
        yc.binary_path("smart_devices/tools/launcher2/test_apps/aborty/aborty")
    )
    json_cfg["nodes"][0]["tasks"][3]["path"] = str(
        yc.binary_path("smart_devices/tools/launcher2/test_apps/sleepy/sleepy")
    )
    json_cfg["nodes"][0]["tasks"][3]["arg"] = ["30"]

    for task in json_cfg["nodes"][0]["tasks"]:
        task['delay'] = BASE_DELAY

    launchjson_path = str(tmpdir.join("launch.json"))
    with open(launchjson_path, "w+") as cfg_file:
        cfg_file.write(json.dumps(json_cfg))
    logger.error(f"Tempdir: {str(tmpdir)}")
    b = yc.binary_path("smart_devices/tools/launcher2/test_apps/test_launcher/test_launcher")
    try:
        execution = yc.execute([b, launchjson_path, "30"], shell=True, timeout=40)
    except TimeoutError:
        pass  # Sometimes due to overloading on the host launcher is not able to terminate at the proper time, this should not fail the test

    with open(yc.work_path("launcher2.log"), "r") as f:
        lines = f.readlines()

    logs = list(filter(lambda s: 'Started' in s, lines))
    starts = {}
    for line in logs:
        m = re.search("\[.*\] \[(.*)\] \[.*\] Started new process of (\w+)", line)
        date = datetime.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S.%f")
        process = m.group(2)
        if process not in starts:
            starts[process] = []
        starts[process].append(date)

    for _, dates in starts.items():
        dates.sort()

    assert len(starts["sleepy"]) == 1  # Does not crash, so should only be started once

    for name in ["heapy", "exity", "aborty"]:
        dates = starts[name]
        restart_delays = list(dates)
        for i in range(len(restart_delays)):
            print(restart_delays[i])
            for j in range(i + 1, len(restart_delays)):
                restart_delays[j] = restart_delays[j] - restart_delays[i]

        # We should have at least 3 starts during test
        assert len(restart_delays) > 3

        for i, delay in enumerate(restart_delays[1:]):  # Skipping first message since it is not a restart
            min_delay, _ = calculate_restart_delay_interval(i + 1)
            assert delay >= datetime.timedelta(seconds=min_delay)
