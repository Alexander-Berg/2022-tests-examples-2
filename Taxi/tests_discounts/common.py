import pytest

# Generated via `tvmknife unittest service -s 123 -d 123321`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIexC5wwc:Q9I_85'
    'oQtOPXLu9Ds2xuQNWKPxksLjXJ4AqHbvuCulWBk5N'
    'O2CXoV4FoNn-5uN4gjYLAgq19i3AV5_hfSdGYfTph'
    'Ibm6wzagYf8nMoSTWW_7aBoY2VPHmmhJF9zDcN2Au'
    'MnuEXa5CTym5hyAM3g8lq-BfvL16ZAg7iTGOxipklY'
)
DEFAULT_DISCOUNTS_HEADER = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}


@pytest.fixture(autouse=True)
def select_rules_request(mockserver):
    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _rules_select(request):
        return {
            'subventions': [
                {
                    'tariff_zones': ['moscow'],
                    'status': 'enabled',
                    'start': '2009-01-01T00:00:00Z',
                    'end': '9999-12-31T23:59:59Z',
                    'type': 'discount_payback',
                    'is_personal': False,
                    'taxirate': '',
                    'subvention_rule_id': '__moscow__',
                    'cursor': '',
                    'tags': [],
                    'time_zone': {'id': '', 'offset': ''},
                    'updated': '2019-01-01T00:00:00Z',
                    'currency': 'rub',
                    'visible_to_driver': False,
                    'week_days': [],
                    'hours': [],
                    'log': [],
                    'tariff_classes': [],
                },
            ],
        }
