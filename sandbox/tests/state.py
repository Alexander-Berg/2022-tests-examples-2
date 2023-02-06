import copy
import mock
import datetime

from sandbox.yasandbox import controller
from sandbox.yasandbox.database import mapping


class TestCpuBalancer(object):
    def recursive_dict_check(self, d1, d2):
        assert type(d1) == type(d2)

        if isinstance(d1, dict):
            assert len(d1) == len(d2)
            for k, v in d1.iteritems():
                assert k in d2
                self.recursive_dict_check(v, d2[k])
        elif isinstance(d1, list):
            assert len(d1) == len(d2)
            for i in range(len(d1)):
                assert self.recursive_dict_check(d1[i], d2[i])
        else:
            assert d1 == d2

    def test__construct_map(self, state_controller):
        controller.Statistics.db_shards_status = mock.MagicMock()
        test_map = copy.deepcopy(TEST_MAP)
        controller.Statistics.db_shards_status.return_value = test_map
        state_controller.update_state_infromation()
        group_map = controller.State.group_mongo_map(test_map)

        servers = list(mapping.State.objects())
        assert len(servers) == len(group_map)
        now = datetime.datetime.utcnow()

        for server in servers:
            assert server.name in group_map
            assert server.updated > now - datetime.timedelta(minutes=2)
            assert server.api_enabled

            for shard in server.shards_info:
                assert shard.name in group_map[server.name]["shards"]
                assert shard.updated > now - datetime.timedelta(minutes=2)
                self.recursive_dict_check(
                    shard.info, group_map[server.name]["shards"][shard.name]
                )

    def test__remove_unused_servers(self, state_controller):
        controller.Statistics.db_shards_status = mock.MagicMock()
        test_map = copy.deepcopy(TEST_MAP)
        controller.Statistics.db_shards_status.return_value = test_map
        state_controller.update_state_infromation()

        dead_client = state_controller.get("sandbox-server01")
        old_date = datetime.datetime.utcnow() - datetime.timedelta(
            days=state_controller.SERVER_TRESHOLD, minutes=5
        )
        dead_client.updated = old_date
        dead_client.save()
        dead_shards = []
        client_with_dead_shards = state_controller.get("sandbox-server02")
        client_with_dead_shards.shards_info[0].updated = old_date
        client_with_dead_shards.shards_info[3].updated = old_date
        client_with_dead_shards.save()
        dead_shards.append(client_with_dead_shards.shards_info[0].name)
        dead_shards.append(client_with_dead_shards.shards_info[3].name)

        servers = state_controller.remove_unused_servers()
        assert dead_client.name not in servers
        assert client_with_dead_shards.name in servers

        for shard in servers[client_with_dead_shards.name].shards_info:
            assert shard.name not in dead_shards


TEST_MAP = [
    {
        "date": "2019-08-20 09:35:08.077000",
        "ok": 1.0,
        "replicaset": "sandbox1",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512947,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:1234",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:06.234000",
                "configVersion": 34,
                "lastHeartbeat": "2019-08-20 09:35:07.883000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 75373,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:1234",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.919000",
                "configVersion": 34,
                "lastHeartbeat": "2019-08-20 09:35:06.767000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162737,
                "configVersion": 34,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,37)"
                },
                "name": "sandbox-server11.search.yandex.net:1234",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133885,4045)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "electionDate": "2019-07-26 09:38:05",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2134,
                "configVersion": 34,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,10008)"
                },
                "name": "sandbox-server01.search.yandex.net:1234",
                "syncSourceHost": "sandbox-server11.search.yandex.net:1234",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 11,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,10008)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.759000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "lastHeartbeat": "2019-08-20 09:35:06.795000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 5732,
                "configVersion": 34,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3284)"
                },
                "name": "sandbox-server06.search.yandex.net:1234",
                "syncSourceHost": "sandbox-server11.search.yandex.net:1234",
                "pingMs": 18,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 11,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3284)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.470000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:06.370000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.176000",
        "ok": 1.0,
        "replicaset": "sandbox2",
        "members": [
            {
                "uptime": 2159756,
                "configVersion": 31,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,2090)"
                },
                "name": "sandbox-server01.search.yandex.net:1236",
                "syncSourceHost": "sandbox-server11.search.yandex.net:1236",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 11,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,2090)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.237000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 1,
                "lastHeartbeat": "2019-08-20 09:35:07.574000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 473260,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:1236",
                "syncSourceHost": "",
                "pingMs": 4,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:06.861000",
                "configVersion": 31,
                "lastHeartbeat": "2019-08-20 09:35:07.736000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68048,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:1236",
                "syncSourceHost": "",
                "pingMs": 2,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:06.419000",
                "configVersion": 31,
                "lastHeartbeat": "2019-08-20 09:35:06.207000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162723,
                "configVersion": 31,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,109)"
                },
                "name": "sandbox-server11.search.yandex.net:1236",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133885,4061)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "electionDate": "2019-07-26 09:38:05",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161049,
                "configVersion": 31,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,6059)"
                },
                "name": "sandbox-server06.search.yandex.net:1236",
                "syncSourceHost": "sandbox-server11.search.yandex.net:1236",
                "pingMs": 17,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 11,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,6059)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.067000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "lastHeartbeat": "2019-08-20 09:35:07.969000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.190000",
        "ok": 1.0,
        "replicaset": "sandbox3",
        "members": [
            {
                "uptime": 2159746,
                "configVersion": 31,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3307)"
                },
                "name": "sandbox-server01.search.yandex.net:1239",
                "syncSourceHost": "sandbox-server11.search.yandex.net:1239",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 11,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3307)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.685000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 1,
                "lastHeartbeat": "2019-08-20 09:35:06.388000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512947,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:1239",
                "syncSourceHost": "",
                "pingMs": 4,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:06.968000",
                "configVersion": 31,
                "lastHeartbeat": "2019-08-20 09:35:07.148000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68047,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:1239",
                "syncSourceHost": "",
                "pingMs": 2,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.827000",
                "configVersion": 31,
                "lastHeartbeat": "2019-08-20 09:35:07.640000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162714,
                "configVersion": 31,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,109)"
                },
                "name": "sandbox-server11.search.yandex.net:1239",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133885,4064)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "electionDate": "2019-07-26 09:38:05",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 473220,
                "configVersion": 31,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1567)"
                },
                "name": "sandbox-server06.search.yandex.net:1239",
                "syncSourceHost": "sandbox-server11.search.yandex.net:1239",
                "pingMs": 20,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 11,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1567)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.249000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "lastHeartbeat": "2019-08-20 09:35:07.408000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.197000",
        "ok": 1.0,
        "replicaset": "sandbox4",
        "members": [
            {
                "uptime": 2159736,
                "configVersion": 31,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,2903)"
                },
                "name": "sandbox-server01.search.yandex.net:12222",
                "syncSourceHost": "sandbox-server06.search.yandex.net:12222",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,2903)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.570000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 1,
                "lastHeartbeat": "2019-08-20 09:35:07.725000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512947,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:12222",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.321000",
                "configVersion": 31,
                "lastHeartbeat": "2019-08-20 09:35:06.490000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68047,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:12222",
                "syncSourceHost": "",
                "pingMs": 4,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.906000",
                "configVersion": 31,
                "lastHeartbeat": "2019-08-20 09:35:06.532000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162705,
                "configVersion": 31,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,109)"
                },
                "name": "sandbox-server11.search.yandex.net:12222",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133886,1)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "electionDate": "2019-07-26 09:38:06",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 1159350,
                "configVersion": 31,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,2263)"
                },
                "name": "sandbox-server06.search.yandex.net:12222",
                "syncSourceHost": "sandbox-server11.search.yandex.net:12222",
                "pingMs": 15,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 11,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,2263)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.765000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "lastHeartbeat": "2019-08-20 09:35:06.192000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.206000",
        "ok": 1.0,
        "replicaset": "sandbox5",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512947,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37005",
                "syncSourceHost": "",
                "pingMs": 4,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:06.855000",
                "configVersion": 32,
                "lastHeartbeat": "2019-08-20 09:35:08.169000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68047,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37005",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.219000",
                "configVersion": 32,
                "lastHeartbeat": "2019-08-20 09:35:06.323000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2159758,
                "configVersion": 32,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,7576)"
                },
                "name": "sandbox-server02.search.yandex.net:1234",
                "syncSourceHost": "sandbox-server12.search.yandex.net:1234",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,7576)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.588000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:06.703000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162742,
                "configVersion": 32,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,64)"
                },
                "name": "sandbox-server12.search.yandex.net:1234",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133886,8)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-07-26 09:38:06",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161063,
                "configVersion": 32,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1997)"
                },
                "name": "sandbox-server07.search.yandex.net:1234",
                "syncSourceHost": "sandbox-server12.search.yandex.net:1234",
                "pingMs": 17,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1997)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.702000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:07.529000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.214000",
        "ok": 1.0,
        "replicaset": "sandbox6",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512947,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37006",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:08.018000",
                "configVersion": 34,
                "lastHeartbeat": "2019-08-20 09:35:07.441000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68047,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37006",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.433000",
                "configVersion": 34,
                "lastHeartbeat": "2019-08-20 09:35:07.959000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2159750,
                "configVersion": 34,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,7660)"
                },
                "name": "sandbox-server02.search.yandex.net:1236",
                "syncSourceHost": "sandbox-server12.search.yandex.net:1236",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,7660)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:08.206000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:06.715000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162732,
                "configVersion": 34,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,109)"
                },
                "name": "sandbox-server12.search.yandex.net:1236",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133886,9)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-07-26 09:38:06",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161054,
                "configVersion": 34,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3310)"
                },
                "name": "sandbox-server07.search.yandex.net:1236",
                "syncSourceHost": "sandbox-server02.search.yandex.net:1236",
                "pingMs": 16,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 11,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3310)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.429000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:06.458000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.222000",
        "ok": 1.0,
        "replicaset": "sandbox7",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512946,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37007",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.246000",
                "configVersion": 34,
                "lastHeartbeat": "2019-08-20 09:35:06.949000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68047,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37007",
                "syncSourceHost": "",
                "pingMs": 2,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:06.250000",
                "configVersion": 34,
                "lastHeartbeat": "2019-08-20 09:35:07.469000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2159741,
                "configVersion": 34,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1539)"
                },
                "name": "sandbox-server02.search.yandex.net:1239",
                "syncSourceHost": "sandbox-server12.search.yandex.net:1239",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1539)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.527000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:07.281000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162724,
                "configVersion": 34,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,116)"
                },
                "name": "sandbox-server12.search.yandex.net:1239",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133887,1)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-07-26 09:38:07",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161042,
                "configVersion": 34,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3309)"
                },
                "name": "sandbox-server07.search.yandex.net:1239",
                "syncSourceHost": "sandbox-server12.search.yandex.net:1239",
                "pingMs": 16,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3309)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.609000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:06.422000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.234000",
        "ok": 1.0,
        "replicaset": "sandbox8",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512947,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37008",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:06.799000",
                "configVersion": 34,
                "lastHeartbeat": "2019-08-20 09:35:07.254000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68047,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37008",
                "syncSourceHost": "",
                "pingMs": 2,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:06.615000",
                "configVersion": 34,
                "lastHeartbeat": "2019-08-20 09:35:06.636000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2159733,
                "configVersion": 34,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3240)"
                },
                "name": "sandbox-server02.search.yandex.net:12222",
                "syncSourceHost": "sandbox-server12.search.yandex.net:12222",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3240)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.861000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:06.262000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162717,
                "configVersion": 34,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,224)"
                },
                "name": "sandbox-server12.search.yandex.net:12222",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133887,5)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-07-26 09:38:07",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161032,
                "configVersion": 34,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,4)"
                },
                "name": "sandbox-server07.search.yandex.net:12222",
                "syncSourceHost": "sandbox-server12.search.yandex.net:12222",
                "pingMs": 18,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,6081)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.962000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:08.062000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.244000",
        "ok": 1.0,
        "replicaset": "sandbox9",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512947,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37009",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.217000",
                "configVersion": 36,
                "lastHeartbeat": "2019-08-20 09:35:07.593000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68047,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37009",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.599000",
                "configVersion": 36,
                "lastHeartbeat": "2019-08-20 09:35:06.702000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2159768,
                "configVersion": 36,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1578)"
                },
                "name": "sandbox-server03.search.yandex.net:1234",
                "syncSourceHost": "sandbox-server13.search.yandex.net:1234",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1578)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.025000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:07.546000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162741,
                "configVersion": 36,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,219)"
                },
                "name": "sandbox-server13.search.yandex.net:1234",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133887,1244)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-07-26 09:38:07",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161063,
                "configVersion": 36,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1541)"
                },
                "name": "sandbox-server08.search.yandex.net:1234",
                "syncSourceHost": "sandbox-server13.search.yandex.net:1234",
                "pingMs": 17,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1541)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.842000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:07.325000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.086000",
        "ok": 1.0,
        "replicaset": "sandbox10",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512946,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37010",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:06.309000",
                "configVersion": 36,
                "lastHeartbeat": "2019-08-20 09:35:07.907000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68047,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37010",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.567000",
                "configVersion": 36,
                "lastHeartbeat": "2019-08-20 09:35:08.033000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2159749,
                "configVersion": 36,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3278)"
                },
                "name": "sandbox-server03.search.yandex.net:1236",
                "syncSourceHost": "sandbox-server08.search.yandex.net:1236",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 13,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3278)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.627000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:06.365000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162733,
                "configVersion": 36,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,39)"
                },
                "name": "sandbox-server13.search.yandex.net:1236",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133888,37)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-07-26 09:38:08",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161054,
                "configVersion": 36,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293705,2934)"
                },
                "name": "sandbox-server08.search.yandex.net:1236",
                "syncSourceHost": "sandbox-server13.search.yandex.net:1236",
                "pingMs": 21,
                "optimeDate": "2019-08-20 09:35:05",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293705,2934)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.375000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:06.130000",
                "optimeDurableDate": "2019-08-20 09:35:05",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.093000",
        "ok": 1.0,
        "replicaset": "sandbox11",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 414310,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37011",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:06.666000",
                "configVersion": 96752,
                "lastHeartbeat": "2019-08-20 09:35:06.302000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68047,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37011",
                "syncSourceHost": "",
                "pingMs": 4,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.847000",
                "configVersion": 96752,
                "lastHeartbeat": "2019-08-20 09:35:06.633000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 414310,
                "configVersion": 96752,
                "optime": {
                    "t": 4,
                    "ts": "Timestamp(1566293706,10194)"
                },
                "name": "sandbox-server03.search.yandex.net:1239",
                "syncSourceHost": "sandbox-server13.search.yandex.net:1239",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 4,
                    "ts": "Timestamp(1566293706,10194)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.392000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:06.814000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162725,
                "configVersion": 96752,
                "optime": {
                    "t": 4,
                    "ts": "Timestamp(1566293708,37)"
                },
                "name": "sandbox-server13.search.yandex.net:1239",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1565890443,3925)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-08-15 17:34:03",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161044,
                "configVersion": 96752,
                "optime": {
                    "t": 4,
                    "ts": "Timestamp(1566293707,1493)"
                },
                "name": "sandbox-server08.search.yandex.net:1239",
                "syncSourceHost": "sandbox-server03.search.yandex.net:1239",
                "pingMs": 17,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 11,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 4,
                    "ts": "Timestamp(1566293707,1493)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.744000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:07.211000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.102000",
        "ok": 1.0,
        "replicaset": "sandbox12",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512947,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37012",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:08.095000",
                "configVersion": 139019,
                "lastHeartbeat": "2019-08-20 09:35:07.811000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68047,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37012",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:06.420000",
                "configVersion": 139019,
                "lastHeartbeat": "2019-08-20 09:35:06.508000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2159732,
                "configVersion": 139019,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,10854)"
                },
                "name": "sandbox-server03.search.yandex.net:12222",
                "syncSourceHost": "sandbox-server13.search.yandex.net:12222",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,10854)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.993000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:06.843000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162715,
                "configVersion": 139019,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,25)"
                },
                "name": "sandbox-server13.search.yandex.net:12222",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133889,9524)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-07-26 09:38:09",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161034,
                "configVersion": 139019,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3286)"
                },
                "name": "sandbox-server08.search.yandex.net:12222",
                "syncSourceHost": "sandbox-server13.search.yandex.net:12222",
                "pingMs": 18,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3286)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.246000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:06.377000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.111000",
        "ok": 1.0,
        "replicaset": "sandbox13",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512947,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37013",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:08.019000",
                "configVersion": 111396,
                "lastHeartbeat": "2019-08-20 09:35:06.201000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68046,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37013",
                "syncSourceHost": "",
                "pingMs": 2,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:06.636000",
                "configVersion": 111396,
                "lastHeartbeat": "2019-08-20 09:35:06.654000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2159764,
                "configVersion": 111396,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,5644)"
                },
                "name": "sandbox-server04.search.yandex.net:1234",
                "syncSourceHost": "sandbox-server14.search.yandex.net:1234",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,5644)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.323000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:06.576000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162738,
                "configVersion": 111396,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,44)"
                },
                "name": "sandbox-server14.search.yandex.net:1234",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133888,3255)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-07-26 09:38:08",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161060,
                "configVersion": 111396,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,6546)"
                },
                "name": "sandbox-server09.search.yandex.net:1234",
                "syncSourceHost": "sandbox-server14.search.yandex.net:1234",
                "pingMs": 18,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,6546)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.671000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:06.620000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.120000",
        "ok": 1.0,
        "replicaset": "sandbox14",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512946,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37014",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.042000",
                "configVersion": 133889,
                "lastHeartbeat": "2019-08-20 09:35:07.825000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68046,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37014",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:06.372000",
                "configVersion": 133889,
                "lastHeartbeat": "2019-08-20 09:35:06.871000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2159756,
                "configVersion": 133889,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1577)"
                },
                "name": "sandbox-server04.search.yandex.net:1236",
                "syncSourceHost": "sandbox-server09.search.yandex.net:1236",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 13,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1577)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.725000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:07.421000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162730,
                "configVersion": 133889,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,50)"
                },
                "name": "sandbox-server14.search.yandex.net:1236",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133888,3316)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-07-26 09:38:08",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161047,
                "configVersion": 133889,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,10459)"
                },
                "name": "sandbox-server09.search.yandex.net:1236",
                "syncSourceHost": "sandbox-server14.search.yandex.net:1236",
                "pingMs": 19,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,10459)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.237000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:06.874000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.129000",
        "ok": 1.0,
        "replicaset": "sandbox15",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512947,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37015",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.690000",
                "configVersion": 163831,
                "lastHeartbeat": "2019-08-20 09:35:07.738000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68046,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37015",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.842000",
                "configVersion": 163831,
                "lastHeartbeat": "2019-08-20 09:35:07.858000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2159746,
                "configVersion": 163831,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3329)"
                },
                "name": "sandbox-server04.search.yandex.net:1239",
                "syncSourceHost": "sandbox-server14.search.yandex.net:1239",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3329)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.112000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:06.428000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162718,
                "configVersion": 163831,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,35)"
                },
                "name": "sandbox-server14.search.yandex.net:1239",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133888,3345)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-07-26 09:38:08",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161040,
                "configVersion": 163831,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1526)"
                },
                "name": "sandbox-server09.search.yandex.net:1239",
                "syncSourceHost": "sandbox-server14.search.yandex.net:1239",
                "pingMs": 19,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1526)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.116000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:07.301000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.139000",
        "ok": 1.0,
        "replicaset": "sandbox16",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512947,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37016",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.255000",
                "configVersion": 98123,
                "lastHeartbeat": "2019-08-20 09:35:07.195000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68046,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37016",
                "syncSourceHost": "",
                "pingMs": 2,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.901000",
                "configVersion": 98123,
                "lastHeartbeat": "2019-08-20 09:35:07.899000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2159738,
                "configVersion": 98123,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,13)",
                    "votes": 2,
                    "priority": 2.0
                },
                "name": "sandbox-server04.search.yandex.net:12222",
                "syncSourceHost": "sandbox-server14.search.yandex.net:12222",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,13)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.025000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:08.048000",
                "optimeDurableDate": "2019-08-20 09:35:08",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162710,
                "configVersion": 98123,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,68)"
                },
                "name": "sandbox-server14.search.yandex.net:12222",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133889,202)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-07-26 09:38:09",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161031,
                "configVersion": 98123,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3334)"
                },
                "name": "sandbox-server09.search.yandex.net:12222",
                "syncSourceHost": "sandbox-server14.search.yandex.net:12222",
                "pingMs": 18,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,3334)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.181000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:06.469000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.152000",
        "ok": 1.0,
        "replicaset": "sandbox17",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512947,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37017",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.972000",
                "configVersion": 44014,
                "lastHeartbeat": "2019-08-20 09:35:06.338000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68047,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37017",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:08.077000",
                "configVersion": 44014,
                "lastHeartbeat": "2019-08-20 09:35:08.009000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2159761,
                "configVersion": 44014,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,6085)"
                },
                "name": "sandbox-server05.search.yandex.net:1234",
                "syncSourceHost": "sandbox-server15.search.yandex.net:1234",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1997)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.594000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:08.029000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162737,
                "configVersion": 44014,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,58)"
                },
                "name": "sandbox-server15.search.yandex.net:1234",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133889,9022)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-07-26 09:38:09",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161056,
                "configVersion": 44014,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,2244)"
                },
                "name": "sandbox-server10.search.yandex.net:1234",
                "syncSourceHost": "sandbox-server15.search.yandex.net:1234",
                "pingMs": 17,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,2244)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.743000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:06.148000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.161000",
        "ok": 1.0,
        "replicaset": "sandbox18",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512947,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37018",
                "syncSourceHost": "",
                "pingMs": 4,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.627000",
                "configVersion": 207401,
                "lastHeartbeat": "2019-08-20 09:35:06.987000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68047,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37018",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:06.628000",
                "configVersion": 207401,
                "lastHeartbeat": "2019-08-20 09:35:07.200000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2159752,
                "configVersion": 207401,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1537)"
                },
                "name": "sandbox-server05.search.yandex.net:1236",
                "syncSourceHost": "sandbox-server15.search.yandex.net:1236",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1537)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.747000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:07.306000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162729,
                "configVersion": 207401,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,32)"
                },
                "name": "sandbox-server15.search.yandex.net:1236",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133889,9509)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-07-26 09:38:09",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161049,
                "configVersion": 207401,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,2396)"
                },
                "name": "sandbox-server10.search.yandex.net:1236",
                "syncSourceHost": "sandbox-server15.search.yandex.net:1236",
                "pingMs": 20,
                "optimeDate": "2019-08-20 09:35:06",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293706,2396)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.851000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:06.284000",
                "optimeDurableDate": "2019-08-20 09:35:06",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.170000",
        "ok": 1.0,
        "replicaset": "sandbox19",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512947,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37019",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:06.761000",
                "configVersion": 111213,
                "lastHeartbeat": "2019-08-20 09:35:06.856000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68047,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37019",
                "syncSourceHost": "",
                "pingMs": 4,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.735000",
                "configVersion": 111213,
                "lastHeartbeat": "2019-08-20 09:35:07.341000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2159741,
                "configVersion": 111213,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1589)"
                },
                "name": "sandbox-server05.search.yandex.net:1239",
                "syncSourceHost": "sandbox-server15.search.yandex.net:1239",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1572)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.957000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:07.429000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162719,
                "configVersion": 111213,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,36)"
                },
                "name": "sandbox-server15.search.yandex.net:1239",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133889,9531)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-07-26 09:38:09",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161040,
                "configVersion": 111213,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,2903)"
                },
                "name": "sandbox-server10.search.yandex.net:1239",
                "syncSourceHost": "sandbox-server15.search.yandex.net:1239",
                "pingMs": 17,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,2903)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:06.600000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:07.728000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            }
        ]
    },
    {
        "date": "2019-08-20 09:35:08.185000",
        "ok": 1.0,
        "replicaset": "sandbox20",
        "members": [
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 512947,
                "_id": 9,
                "name": "sandbox-storage12.search.yandex.net:37020",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.860000",
                "configVersion": 52268,
                "lastHeartbeat": "2019-08-20 09:35:08.066000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "infoMessage": "",
                "lastHeartbeatMessage": "",
                "uptime": 68046,
                "_id": 10,
                "name": "sandbox-storage13.search.yandex.net:37020",
                "syncSourceHost": "",
                "pingMs": 3,
                "syncSourceId": -1,
                "state": 7,
                "health": 1.0,
                "stateStr": "ARBITER",
                "lastHeartbeatRecv": "2019-08-20 09:35:07.192000",
                "configVersion": 52268,
                "lastHeartbeat": "2019-08-20 09:35:07.567000",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2159732,
                "configVersion": 52268,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1495)"
                },
                "name": "sandbox-server05.search.yandex.net:12222",
                "syncSourceHost": "sandbox-server15.search.yandex.net:12222",
                "pingMs": 3,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,1495)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.263000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 11,
                "lastHeartbeat": "2019-08-20 09:35:07.203000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2162712,
                "configVersion": 52268,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293708,115)"
                },
                "name": "sandbox-server15.search.yandex.net:12222",
                "syncSourceHost": "",
                "self": True,
                "optimeDate": "2019-08-20 09:35:08",
                "state": 1,
                "electionTime": "Timestamp(1564133890,8)",
                "syncSourceId": -1,
                "infoMessage": "",
                "health": 1.0,
                "stateStr": "PRIMARY",
                "lastHeartbeatMessage": "",
                "_id": 12,
                "electionDate": "2019-07-26 09:38:10",
                "votes": 2,
                "priority": 2.0
            },
            {
                "uptime": 2161031,
                "configVersion": 52268,
                "optime": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,2905)"
                },
                "name": "sandbox-server10.search.yandex.net:12222",
                "syncSourceHost": "sandbox-server15.search.yandex.net:12222",
                "pingMs": 21,
                "optimeDate": "2019-08-20 09:35:07",
                "state": 2,
                "syncSourceId": 12,
                "infoMessage": "",
                "health": 1.0,
                "optimeDurable": {
                    "t": 2,
                    "ts": "Timestamp(1566293707,2905)"
                },
                "lastHeartbeatRecv": "2019-08-20 09:35:07.865000",
                "stateStr": "SECONDARY",
                "lastHeartbeatMessage": "",
                "_id": 13,
                "lastHeartbeat": "2019-08-20 09:35:07.737000",
                "optimeDurableDate": "2019-08-20 09:35:07",
                "votes": 2,
                "priority": 2.0
            }
        ]
    }
]
