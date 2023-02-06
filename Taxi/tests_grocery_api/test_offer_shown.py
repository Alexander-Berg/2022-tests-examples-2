from dateutil import parser
import pytest
import pytz


@pytest.mark.now('2021-07-21T12:00:00+03:00')
async def test_offer_shown_log(taxi_grocery_api, testpoint, now):
    """ /lavka/v1/api/v1/offer-shown adds offer_id and
    offer shown time to shown_offers logs """

    offer_id = 'some-offer-id'

    @testpoint('yt_offer_shown')
    def yt_offer_shown(shown_offers):
        assert shown_offers['offer_id'] == offer_id
        timestamp = parser.parse(shown_offers['timestamp'])
        assert timestamp == now.replace(tzinfo=pytz.utc)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/offer-shown', json={'offer_id': offer_id},
    )
    assert response.status_code == 200
    assert yt_offer_shown.times_called == 1
