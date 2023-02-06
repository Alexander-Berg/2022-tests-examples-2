import json

import sandbox.client
from sandbox.client import pinger


CLIENT_STATE = (
    """{"e41071c7c6e24c1a950fbb51f41e0a02": {"__state": {"task_id": 68397033, "kill_timeout": 10800,"""
    """"args": {"ramdrive": null, "vault_key": "z0UJirq31yI8H/ITaIoVvE3DxGQSwUZfWqfhX/3bFTc=","""
    """"dns64": true, "iteration": 0, "task_id": 68397033}, "iteration": 0, "timestamp_start": 1472485318.095777,"""
    """"platform": {"__state": {"_container": {"__state": ["149289071", 0, null, null, null, 149289071],"""
    """"__cls": "Container"}}, "__cls": "LXCPlatform"}, "token": "e41071c7c6e24c1a950fbb51f41e0a02","""
    """"tasks_rid": 157956378, "killed_by_timeout": false, "arch": "linux_ubuntu_14.04_trusty","""
    """"id": 5969, "liner": {"__state": {"liner": "1bb1409e"},"__cls": "TaskLiner"}}, "__cls": "ExecuteTaskCommand"}}"""
)

COMMAND_DICT = {
    "task_id": 68397033,
    "iteration": 0,
    "args": {
        "dns64": True,
        "vault_key": "z0UJirq31yI8H/ITaIoVvE3DxGQSwUZfWqfhX/3bFTc=",
        "iteration": 0,
        "task_id": 68397033,
        "task_token": "e41071c7c6e24c1a950fbb51f41e0a02",
        "ramdrive": None
    },
    "kill_timeout": 10800,
    "killed_by_timeout": False,
    "timestamp_start": 1472485318.095777,
    "arch": "linux_ubuntu_14.04_trusty",
    "id": 5969
}


class TestClient(object):
    def test__unpickle_client_state(self):
        assert pinger.PingSandboxServerThread.instance is None

        pt = pinger.PingSandboxServerThread()
        pt.load_state(json.loads(CLIENT_STATE))

        assert pinger.PingSandboxServerThread.instance is not None

        command = sandbox.client.commands.Command.registry.itervalues().next()
        assert command.token == COMMAND_DICT["args"].pop("task_token")
        assert isinstance(command, sandbox.client.commands.ExecuteTaskCommand)
        for k, v in COMMAND_DICT.iteritems():
            assert k in command.__dict__
            assert getattr(command, k) == v
        liner = command.liner
        assert isinstance(liner, sandbox.client.system.TaskLiner)
        platform = command.platform
        assert isinstance(platform, sandbox.client.platforms.LinuxPlatform)
        assert platform._cmd is command
