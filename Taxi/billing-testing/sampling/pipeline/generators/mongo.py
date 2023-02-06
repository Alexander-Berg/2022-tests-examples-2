from typing import Any

import bson

from . import generator


class Oid(generator.Generator):
    def fetch(self) -> Any:
        return {'$oid': str(bson.objectid.ObjectId())}
