from typing import Optional

import pydantic
import pytest

from ipv4mgr.interface.mapping import CreateMappingRequest


class TestCreateMappingRequest:
    @pytest.mark.parametrize("client_port_begin", (0, 1023))
    def test_client_port_begin_low_range(self, client_port_begin: int) -> None:
        with pytest.raises(pydantic.ValidationError) as exc_info:
            CreateMappingRequest.parse_obj({"client_port_begin": client_port_begin})
        (error,) = exc_info.value.errors()
        (error_loc,) = error["loc"]
        assert error_loc == "client_port_begin"

    @pytest.mark.parametrize("client_port_begin", (None, 1024))
    def test_client_port_begin_success(self, client_port_begin: Optional[int]) -> None:
        request = CreateMappingRequest.parse_obj(
            {"client_port_begin": client_port_begin}
        )
        assert request.client_port_begin == client_port_begin

    def test_client_port_begin_not_power_of_2(self):
        with pytest.raises(pydantic.ValidationError):
            CreateMappingRequest.parse_obj({"client_port_begin": 1025})
