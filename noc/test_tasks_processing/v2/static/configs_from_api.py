from copy import deepcopy

from balancer_agent.operations.balancer_configs.config_containers import BalancerConfigL3States

TEST_SERVICE_FQDN = "l3.tt.yandex-team.ru"


class ConfigListGenerator:
    ACTIVE = "ACTIVE"
    REMOVED = "REMOVED"

    @classmethod
    def get(cls, *states):
        _id = 0
        result = []

        for state in states:
            _id += 1

            result.append(
                {
                    "id": _id,
                    "target": state,
                    "revision": _id,
                    "locked": None,
                    "state": BalancerConfigL3States.UNKNOWN.name,
                    "service": "fake",
                }
            )

        return result


CONFIG_GENERATOR_SETTINGS = {
    "config_target": "ACTIVE",
    "vs_group_settings": {"num": 2, "min_up": (1, 2), "num_vss": (1, 2)},
}

CONFIG_GENERATOR_SETTINGS_ONE_VS_GROUP_ONE_VS = {
    "config_target": "ACTIVE",
    "vs_group_settings": {"num": 1, "min_up": (1,), "num_vss": (1,)},
}


class ConfigGenerator:
    ACTIVE = "ACTIVE"
    REMOVED = "REMOVED"

    SCHEDULER = {
        "type": "wrr",
        "options": {
            "mh_port": False,
            "mh_fallback": False,
            "ops": False,
        },
    }

    DYNAMICWEIGHT = {"enabled": False, "options": {"ratio": 30, "allow_zero": False, "in_header": False}}

    START_VS_ID = 1069928

    @classmethod
    def vs(cls, port, scheduler, dynamicweight, _id):
        return deepcopy(
            {
                "id": _id,
                # optional
                # "fwmark": 12345
                "port": port,
                "protocol": "TCP",
                "config": {
                    "method": "TUN",
                    "announce": {
                        "enabled": True,
                        "quorum": 1,
                        "hysteresis": 0,
                    },
                    "scheduler": scheduler,
                    "check": {
                        "type": "SSL_GET",
                        "connect_params": {"ip": "", "port": 443, "timeout": 1},
                        "retry_params": {"count": 1, "delay": 1},
                        "delay_loop": 10,
                        "options": {
                            "http_protocol": None,
                            "host": TEST_SERVICE_FQDN,
                            "check_url": "/ping",
                            "digest": "",
                            "status_code": 204,
                        },
                    },
                    "dynamicweight": dynamicweight,
                    "inhibit_on_failure": False,
                    "persistence_timeout": 0,
                },
                "rss": {
                    "2a02:6b8:0:1482::115": {"id": 1554, "fwmark": 1650, "config": {"weight": 1}},
                    "2a02:6b8:b010:31::233": {"id": 1555, "fwmark": 1651, "config": {"weight": 1}},
                },
            }
        )

    @classmethod
    def vs_group(cls, ip, min_up, vss):
        return {ip: {"target_state": "DEPLOYED", "weight": 300, "min_vs_up": min_up, "vss": vss}}

    @classmethod
    def config(cls):
        return deepcopy(
            {"id": 1, "locked": 1635430178, "target": "ACTIVE", "service": TEST_SERVICE_FQDN, "vs_group": {}}
        )

    @classmethod
    def vs_ip(cls, last_segment):
        return "2a02:6b8:0:3400::" + str(last_segment)

    @classmethod
    def port(cls, add_num):
        return int("80" + str(add_num)) if add_num else 80

    @classmethod
    def vs_id(cls):
        current = cls.START_VS_ID

        cls.START_VS_ID += 1

        return current

    @classmethod
    def reset_vs_id(cls):
        cls.START_VS_ID = 1069928

    @classmethod
    def get(cls, settings):
        config = cls.config()
        config["target"] = settings["config_target"]

        for i in range(settings["vs_group_settings"]["num"]):
            vss = []

            for j in range(settings["vs_group_settings"]["num_vss"][i]):
                vss.append(
                    cls.vs(
                        cls.port(j),
                        settings.get("scheduler") or cls.SCHEDULER,
                        settings.get("dynamicweight") or cls.DYNAMICWEIGHT,
                        cls.vs_id(),
                    )
                )

            min_up = settings["vs_group_settings"]["min_up"][i]
            config["vs_group"] = {**cls.vs_group(cls.vs_ip(i), min_up, vss), **config.get("vs_group", {})}

        cls.reset_vs_id()
        return config
