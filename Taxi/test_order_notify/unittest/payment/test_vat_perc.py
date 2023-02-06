import datetime

import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.order_info import OrderData
from order_notify.repositories.payment import vat_perc as vat_p


@pytest.fixture(name='mock_functions')
def mock_country_vat_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_country_doc_by_city_id = Counter()
            self.get_country_vat_by_date = Counter()

    counters = Counters()

    @patch(
        'order_notify.repositories.territories.' 'get_country_doc_by_city_id',
    )
    async def _get_country_doc_by_city_id(
            context: stq_context.Context, zone: str,
    ) -> dict:
        counters.get_country_doc_by_city_id.call()
        assert zone == 'moscow'
        return {'_id': 'rus'}

    @patch(
        'order_notify.repositories.payment.vat_perc.'
        'get_country_vat_by_date',
    )
    def _get_country_vat_by_date(
            context: stq_context.Context,
            country: dict,
            request_due: datetime.datetime,
    ) -> float:
        counters.get_country_vat_by_date.call()
        assert country == {'_id': 'rus'}
        assert request_due == datetime.datetime.fromisoformat(
            '2018-12-31 21:00:00',
        )
        return 12000

    return counters


@pytest.mark.parametrize(
    'payment_tech, expected_vat, expected_call',
    [
        pytest.param({}, 12000, 1, id='no_country_vat_in_payment'),
        pytest.param(
            {'country_vat': 'f'}, 12000, 1, id='country_vat_not_number',
        ),
        pytest.param(
            {'country_vat': 11000}, 11000, 0, id='country_vat_number',
        ),
    ],
)
async def test_get_vat_coeff(
        stq3_context: stq_context.Context,
        mock_functions,
        payment_tech,
        expected_vat,
        expected_call,
):
    vat = await vat_p.get_vat_coeff(
        context=stq3_context,
        order_data=OrderData(
            brand='',
            country='',
            order={'payment_tech': payment_tech, 'nz': 'moscow'},
            order_proc={
                'order': {
                    'request': {
                        'due': datetime.datetime.fromisoformat(
                            '2018-12-31 21:00:00',
                        ),
                    },
                },
            },
        ),
    )
    assert vat == expected_vat
    assert (
        mock_functions.get_country_doc_by_city_id.times_called == expected_call
    )
    assert mock_functions.get_country_vat_by_date.times_called == expected_call


@pytest.mark.parametrize(
    'country_code, request_due, expected_vat',
    [
        pytest.param('blr', '2018-12-31 21:00:00', 11000, id='not_in_config'),
        pytest.param('rus', '1969-12-31 23:59:59', 11000, id='min_due'),
        pytest.param('rus', '1970-01-01 00:00:00', 11800, id='in_first_due'),
        pytest.param('rus', '2018-12-31 21:00:00', 12000, id='in_second_due'),
        pytest.param('rus', '2999-12-31 00:00:01', 11000, id='max_due'),
    ],
)
@pytest.mark.config(
    COUNTRY_CORP_VAT_BY_DATE={
        'rus': [
            {
                'end': '2018-12-31 21:00:00',
                'start': '1970-01-01 00:00:00',
                'value': 11800,
            },
            {
                'end': '2999-12-31 00:00:00',
                'start': '2018-12-31 21:00:00',
                'value': 12000,
            },
        ],
    },
)
def test_get_country_vat_by_date(
        stq3_context: stq_context.Context,
        country_code,
        request_due,
        expected_vat,
):
    vat = vat_p.get_country_vat_by_date(
        context=stq3_context,
        country={'_id': country_code, 'vat': 11000},
        request_due=datetime.datetime.fromisoformat(request_due),
    )
    assert vat == expected_vat


@pytest.mark.config(COUNTRY_CORP_VAT_BY_DATE={'rus': []})
def test_get_country_vat_by_date_raise_unknown_vat(
        stq3_context: stq_context.Context,
):
    with pytest.raises(vat_p.UnknownVatError):
        vat_p.get_country_vat_by_date(
            context=stq3_context,
            country={'_id': 'f'},
            request_due=datetime.datetime.fromisoformat('2018-12-31 21:00:00'),
        )
