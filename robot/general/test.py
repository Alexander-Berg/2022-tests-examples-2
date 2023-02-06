from collections import OrderedDict
from robot.cmpy.library.config import NonOverridableConfig, add_cmpy_modules_with_local_configs
from robot.kwyt.cm.configuration import update_config


def create_config():
    cfg = NonOverridableConfig()
    cfg.Modules = OrderedDict()

    update_config(cfg)

    add_cmpy_modules_with_local_configs("robot.kwyt.cm", cfg,
                                        [
                                            ("delivery", "delivery.cm"),
                                            ("scheduler", "scheduler.cm")
                                        ])

    return cfg
