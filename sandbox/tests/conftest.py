import py
import pytest
import logging

from sandbox.agentr import db
from sandbox.agentr import session
from sandbox.agentr import deblock
import sandbox.common.os as common_os
import sandbox.common.config as common_config
import sandbox.common.platform as common_platform


@pytest.fixture
def tasks_registry():
    logger = logging.getLogger(__name__)

    config = common_config.Registry()
    db_deblock = deblock.Deblock(logger=logger)
    database = db_deblock.make_proxy(_db_factory(config, logger))
    ini, fw, bw = _load_migrations_scripts()
    database.migrate(ini, fw, bw)

    tasks_registry = session.Registry(database, logger, config, None, common_os.User.service_users.unprivileged)
    assert tasks_registry is not None, tasks_registry
    return tasks_registry


def _load_migrations_scripts():
    ini, fw, bw = {}, {}, {}

    for _ in sorted(py.path.local(__file__).join("..", "..", "share", "db").listdir()):
        if _.ext in (".sql", ".py"):
            t, no = _.basename.split("_", 2)[:2]
            (fw if t == "fw" else (bw if t == "bw" else ini)).setdefault(int(no), []).append(_)

    return ini, fw, bw


def _db_factory(config, logger):
    database = db.Database(
        config.agentr.daemon.db.path,
        logger,
        mmap=15728640,
        temp=config.agentr.daemon.db.temp,
    )
    database.set_debug()
    database.open(force=common_platform.on_osx() or common_platform.on_wsl(), lite=False)
    return database
