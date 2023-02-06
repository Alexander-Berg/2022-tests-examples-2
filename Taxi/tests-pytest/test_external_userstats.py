import json
import pytest

from taxi.core import arequests
from taxi.external import userstats


BRAND_YATAXI = 'yataxi'


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_userstats_bad_status(areq_request):
    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == arequests.METHOD_POST
        return areq_request.response(400, body='super content')

    with pytest.raises(userstats.UserstatsRequestError):
        yield userstats.request(['tariffs.econom'], BRAND_YATAXI, phone_ids=['12345'])


@pytest.mark.parametrize(
    'phone_id, tariff, content, expected_value, expected_exception',
    [
        (
            'somephone 1',
            'econom',
            {
                'phone_id': [
                    {
                        'id': 'somephone',
                        'counters': []
                    }
                ]
            },
            None,
            userstats.UserstatsResponseError
        ),
        (
            'somephone 2',
            'vip',
            {
                'phone_id': [
                    {
                        'id': 'somephone',
                        'counters': [{'tariffs.vip': 10}]
                    }
                ]
            },
            10,
            None
        ),
        (
            'somephone 3',
            'econom',
            {
                'phone_id': []
            },
            0,
            None
        )
    ]
)
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_userstats_get(areq_request, phone_id, tariff, content, expected_value,
                       expected_exception):

    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == arequests.METHOD_POST
        data = kwargs.pop('json', None)
        assert data.get('brand') == BRAND_YATAXI
        assert data.get('counters') == ['tariffs.' + tariff]
        assert 'bulk_ids' in data
        assert data['bulk_ids']['phone_id'] == [phone_id]
        return areq_request.response(200, body=json.dumps(content))

    if expected_exception:
        with pytest.raises(expected_exception):
            yield userstats.get_user_tariff_counter(phone_id, tariff, BRAND_YATAXI)
    else:
        value = yield userstats.get_user_tariff_counter(phone_id, tariff, BRAND_YATAXI)
        assert value == expected_value
