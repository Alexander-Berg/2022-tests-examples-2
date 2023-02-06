import json
import logging
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
                    "delay" : 0,
                    "allowedRestartIntervalSeconds" : 0,
                    "root": ".",
                    "path": "",
                    "log": false
                },
                {
                    "name": "exity",
                    "delay" : 0,
                    "allowedRestartIntervalSeconds" : 0,
                    "root": ".",
                    "path": "",
                    "log": false
                },
                {
                    "name": "aborty",
                    "delay" : 0,
                    "allowedRestartIntervalSeconds" : 0,
                    "root": ".",
                    "path": "",
                    "log": false
                },
                {
                    "name": "sleepy",
                    "delay" : 0,
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


def test_restart(tmpdir):
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
    json_cfg["nodes"][0]["tasks"][3]["arg"] = ["20"]

    launchjson_path = str(tmpdir.join("launch.json"))
    with open(launchjson_path, "w+") as cfg_file:
        cfg_file.write(json.dumps(json_cfg))
    logger.error(f"Tempdir: {str(tmpdir)}")
    b = yc.binary_path("smart_devices/tools/launcher2/test_apps/test_launcher/test_launcher")
    yc.execute([b, launchjson_path, "20"], shell=True, timeout=50)
