import allure
import unittest

from io import StringIO
import logging
import sys

import pytest
import requests
import ticket_parser2 as tp2
import ticket_parser2.exceptions as tp2e


TVMTOOL_PORT_FILE = "tvmtool.port"
TVMTOOL_AUTHTOKEN_FILE = "tvmtool.authtoken"


SRV_TICKET_INV = (
    "3:serv:CBAQ__________9_IgYIexCUkQY:GioCM49Ob6_f80y6FY0XBVN4hLXuMlFeyMvIMiDuQnZkbkLpRp"
    "QOuQo5YjWoBjM0Vf-XqOm8B7xtrvxSYHDD7Q4OatN2l-Iwg7i71lE3scUeD36x47st3nd0OThvtjrFx_D8mw_"
    "c0GT5KcniZlqq1SjhLyAk1b_zJsx8viRAhCU"
)

SRV_TICKET = (
    "3:serv:CBAQ__________9_IgQIexAq:CeYHbo4MJQajoJluQVkCs8KPZGh454Xqdk8wBylfa_2xmQ2euarOV"
    "OGIg4q9OULydSXghWWcbhCMfJiNkp3ALeFVA0HctTjowNqbi5Kg8LesNQbbLeEn4DBX2psrxn9Ifu_ZHFAErj"
    "548jWB6ajicWsNNLXSF7RNH1I6kg98_WM"
)


log_stream = StringIO()
l = logging.getLogger('TVM')
handler = logging.StreamHandler(stream=log_stream)
handler.setLevel(logging.DEBUG)
l.addHandler(handler)


def _get_tvmtool_params():
    port = int(open(TVMTOOL_PORT_FILE).read())
    authtoken = open(TVMTOOL_AUTHTOKEN_FILE).read()

    r = requests.get("http://localhost:%d/tvm/ping" % port)
    assert r.status_code == 200

    return port, authtoken


@allure.story('Запуск клиента к изолированому tvmtool')
class ClientTests(unittest.TestCase):
    def test_client(self):
        """Базовые сценарии"""

        port, authtoken = _get_tvmtool_params()

        log_stream.truncate(0)
        c = None
        try:
            s = tp2.TvmToolClientSettings(
                self_alias='me',
                auth_token=authtoken,
                port=port,
            )

            c = tp2.TvmClient(s)

            assert c.status == tp2.TvmClientStatus.Ok
            with pytest.raises(tp2e.BrokenTvmClientSettings):
                c.get_service_ticket_for('bbox')

            assert c.check_service_ticket(SRV_TICKET)
            with pytest.raises(tp2e.TicketParsingException):
                assert c.check_service_ticket(SRV_TICKET_INV)

            c.stop()

            acctual = log_stream.getvalue()
            assert ("Meta info fetched from localhost:%d\n" % port) in acctual
            assert "Meta: self_tvm_id=42, bb_env=Test, idm_slug=<NULL>, dsts=[" in acctual
            assert "Thread-worker started\n" in acctual
        except:
            print(log_stream.getvalue(), file=sys.stderr)
            raise
        finally:
            print('==test_full_client: 1', file=sys.stderr)
            if c is not None:
                c.stop()
            print('==test_full_client: 2', file=sys.stderr)
