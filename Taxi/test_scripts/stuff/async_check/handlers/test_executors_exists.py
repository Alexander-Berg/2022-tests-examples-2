import asyncio
import os

import scripts.app
from scripts.lib import executable_schemas
from scripts.stuff.async_check import handlers


_SCHEMAS = executable_schemas.Schemas(
    os.path.join(scripts.app.BASE_DIR, 'executor_schemas'),
)
asyncio.run(_SCHEMAS.load())


def test_known_handlers_has_executor_type():
    handler_keys = handlers.HANDLERS_BY_TYPE.keys()
    assert not handler_keys - _SCHEMAS.default.keys()
