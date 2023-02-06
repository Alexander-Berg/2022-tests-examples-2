# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import pytest

from corp_orders.stq import corp_offer_accept_by_order


ORDER_ID = '1234567'


@pytest.mark.parametrize(
    ('clid', 'sf_calls', 'method'),
    (
        pytest.param('643753730232', 0, 'zapier'),
        pytest.param('643753730233', 0, 'zapier'),
        pytest.param('643753730232', 0, 'sf-data-load'),
        pytest.param('643753730233', 1, 'sf-data-load'),
    ),
)
async def test_offer_accept_by_order(
        stq3_context,
        mock_parks_activation,
        mock_sf_data_load,
        clid,
        sf_calls,
        method,
):
    stq3_context.config.CORP_PARKS_OFFER_ACCEPT_SETTINGS = {
        'enabled': True,
        'method': method,
    }

    await corp_offer_accept_by_order.task(stq3_context, ORDER_ID, clid)
    assert mock_sf_data_load._offer_accept_parks.times_called == sf_calls
