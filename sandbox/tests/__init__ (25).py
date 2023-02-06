# coding: utf-8

import pytest

from sandbox.common import tvm


class FakeTickets(object):
    UID = 1120000000026416  # robot-sandbox

    # `ya tool tvmknife unittest user -e prod_yateam -u 1120000000026416`
    USER_VALID = (
        "3:user:CAwQ__________9_GhwKCQiwzpmRpdT-ARCwzpmRpdT-ASDShdjMBCgC:SPXqiTyvOrszwTcMX-ZnrGdwfv1O14X"
        "nvzWSw_Cl71WVD2LwaXMKBrUCD-7gezEYOwzaQ-Ro0C7YT5nQ31lcwQd7CfvlJmFA-Oyv3FcbejAR7nu2J_ufu_5cOoP2zEI"
        "BxsDkZ247QhF81Efd4zY4bG1HO7Bh40eBtoNnC0KGo6o"
    )

    # Intentionally wrong blackbox environment
    # `ya tool tvmknife unittest user -e test -u 1120000000026416`
    USER_INVALID = (
        "3:user:CA0Q__________9_GhwKCQiwzpmRpdT-ARCwzpmRpdT-ASDShdjMBCgB:Bfz6mc-Wzp5p2WVt0fIJNjJ6mo5BoH"
        "ruepIGk8_w4-u8EAJke7nmCqg07ADWlVIYK3qk6HA7UFmNE074BScHjNhfM-IRZudvbwcwfRkfqfHFpUkITQp6yQekOoP6Q"
        "mLm6RY7DWgphVYFhz7DdqZ4tk2ioqtDnc902IBB7O1kWbY"
    )

    # From `sandbox production` to `yav`
    # `ya tool tvmknife unittest service -s 2002826 -d 2001357`
    SERVICE = (
        "3:serv:CBAQ__________9_IggIip96EM2Teg:UMftiEhCKaRF2kEIYARvsJr6J2QhVQv9gMYniZdn_g_ymsJn3jIQbIOHN_"
        "GPYHE-xO5a1PzSaRRWU4hap5RnDOjR5UwInoJsir6WSao56GLLrskqtM59ORvYT8PlFTzlvXabXlEjhxfkoGDBgYXRUTvmYqA"
        "u_mX3iuaVnljeVqQ"
    )


@pytest.mark.usefixtures("tvmtool")
class TestTVMTool(object):

    def test__check_user_ticket(self):
        r = tvm.TVM.check_user_ticket(FakeTickets.USER_VALID)
        assert r["default_uid"] == FakeTickets.UID

        with pytest.raises(tvm.TVM.Error):
            tvm.TVM.check_user_ticket(FakeTickets.USER_INVALID)

    def test__check_service_ticket(self):
        tvm.TVM.check_service_ticket(FakeTickets.SERVICE, dst="yav")

        with pytest.raises(tvm.TVM.Error):
            # Intentionally wrong destination
            tvm.TVM.check_service_ticket(FakeTickets.SERVICE, dst="sandbox")

    def test__get_service_ticket(self):

        with pytest.raises(tvm.TVM.Error):
            tvm.TVM.get_service_ticket(["yav", "invalid-service"])

        tickets = tvm.TVM.get_service_ticket(["yav", "blackbox"])
        assert set(tickets) == {"yav", "blackbox"}
        tvm.TVM.check_service_ticket(tickets["yav"], "yav")
