import pydantic
import pytest

from ipv4mgr.interface.pool import Net4Info, Net4Type


class TestNet4Info:
    def test_required_portrange_step_at_stateless_portrange_type(self):
        with pytest.raises(pydantic.ValidationError):
            Net4Info.parse_obj(
                {"net4": "192.2.2.2", "type": Net4Type.STATELESS_PORTRANGE.value}
            )

    def test_invalid_type(self):
        with pytest.raises(pydantic.ValidationError):
            Net4Info.parse_obj({"net4": "192.2.2.2", "type": "bad type"})
