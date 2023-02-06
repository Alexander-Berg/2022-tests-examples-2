from __future__ import absolute_import

import sys

import pytest

from sandbox import sdk2


@pytest.mark.usefixtures("project_types")
def test__resource_nesting():
    for cls in sdk2.Resource:
        mod = sys.modules[cls.__module__]
        assert getattr(mod, cls.__name__, None) is cls, (
            "Resource class has to be located on module level, but {}.{} is nested".format(cls.__module__, cls.__name__)
        )


@pytest.mark.usefixtures("project_types")
def test__resource_serialization():
    from sandbox.yasandbox.database import mapping
    for resource in sdk2.Resource:
        mapping.ResourceMeta(resource_meta=mapping.ResourceMeta.Meta(**resource.__getstate__()[0])).validate()
