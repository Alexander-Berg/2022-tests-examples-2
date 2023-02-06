import pytest

from generated.models import tinkoff_secured as tinkoff_models


@pytest.fixture(autouse=True)
def tinkoff_service(mockserver_ssl):
    card_spend_limits = dict()
    card_spend_remains = dict()
    card_cash_limits = dict()

    @mockserver_ssl.json_handler(
        r'/tinkoff-secured/api/v1/card/(?P<cid>\d+)/limits', regex=True,
    )
    # pylint: disable=W0612
    def get_card_limits(request, cid):
        cid = int(cid)

        if cid not in card_spend_limits or cid not in card_cash_limits:
            return mockserver_ssl.make_response(status=404)

        return tinkoff_models.Limits(
            ucid=cid,
            spend_limit=tinkoff_models.LimitDescriptor(
                limit_period='IRREGULAR',
                limit_value=card_spend_limits[cid],
                limit_remain=card_spend_remains[cid],
            ),
            cash_limit=tinkoff_models.LimitDescriptor(
                limit_period='IRREGULAR', limit_value=0, limit_remain=0,
            ),
        ).serialize()

    @mockserver_ssl.json_handler(
        r'/tinkoff-secured/api/v1/card/(?P<cid>\d+)/spend-limit', regex=True,
    )
    # pylint: disable=W0612
    def set_spend_limit(request, cid):
        cid = int(cid)

        data = tinkoff_models.SpendLimitRequest.deserialize(request.json)
        assert data.limit_period == 'IRREGULAR'

        card_spend_limits[cid] = data.limit_value
        card_spend_remains[cid] = data.limit_value

        return mockserver_ssl.make_response()

    @mockserver_ssl.json_handler(
        r'/tinkoff-secured/api/v1/card/(?P<cid>\d+)/cash-limit', regex=True,
    )
    # pylint: disable=W0612
    def set_cash_limit(request, cid):
        cid = int(cid)

        data = tinkoff_models.CashLimitRequest.deserialize(request.json)
        assert data.limit_period == 'IRREGULAR'
        assert data.limit_value == 0

        card_cash_limits[cid] = 0

        return mockserver_ssl.make_response()

    def _decrease_limit_remains(cid, amount):
        cid = int(cid)

        card_spend_remains[cid] -= amount

    return {'_decrease_limit_remains': _decrease_limit_remains}
