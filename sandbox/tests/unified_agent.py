from sandbox.deploy.unified_agent import UnifiedAgent


class TestUnifiedAgent(object):
    def test__basic(self):
        ua = UnifiedAgent(1, "", True, False, [UnifiedAgent.LEGACY_WEBSERVER_METRIC, UnifiedAgent.ZOOKEEPER_METRIC])
        cfg = ua.get_config("~/PATH_TO_SECRET")
        assert cfg
        assert cfg["status"]
        assert cfg["routes"]
        assert cfg["pipes"]
        assert cfg["storages"]

        print(cfg)

    def test__zookeeper(self):
        ua = UnifiedAgent(1, "", True, False, [UnifiedAgent.LEGACY_WEBSERVER_METRIC, UnifiedAgent.ZOOKEEPER_METRIC])
        cfg = ua.get_config("~/PATH_TO_SECRET")
        route_zookeeper = next(
            r for r in cfg["routes"] if r.get("input", {}).get("config", {}).get("service") == "zookeeper"
        )
        assert route_zookeeper
        assert route_zookeeper["channel"]
        assert len(route_zookeeper["channel"]["pipe"]) == 3

        filter_assign = route_zookeeper["channel"]["pipe"][2]["filter"]
        assert filter_assign
        assert isinstance(filter_assign["config"]["session"], list)
        assert route_zookeeper["channel"]["output"]

        storage_ref = route_zookeeper["channel"]["pipe"][1]["storage_ref"]
        storage_name = storage_ref["name"]
        assert [s for s in cfg["storages"] if s["name"] == storage_name]

        print(cfg)
