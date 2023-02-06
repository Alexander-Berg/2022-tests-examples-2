import pytest

import sandbox.web.response
from sandbox.yasandbox.api.json import registry


class TestRegistry:
    def test_registered_json(self):
        _register = registry.REGISTERED_JSON[:]
        for _ in xrange(len(registry.REGISTERED_JSON)):
            del registry.REGISTERED_JSON[0]
        path = '/test/path'
        marker = object()
        registry.registered_json(path)(marker)
        assert registry.REGISTERED_JSON[0][1] == marker
        assert registry.REGISTERED_JSON[0][1] is marker
        registry.REGISTERED_JSON.pop(0)
        registry.REGISTERED_JSON.extend(_register)

    def test_api_docs(self):
        assert registry.api_docs('None') is None
        with pytest.raises(sandbox.web.response.HttpResponse):
            registry.api_docs(registry.DOCS_ROOT)
