# pylint: disable=redefined-outer-name, import-error
import json

from pricing_extended import mocking_base
import pytest


class ComboContractorsContext(mocking_base.BasicMock):
    def __init__(self):
        super().__init__()

        self.response = {
            'tariff_classes': {
                'ubernight': {
                    'combo_inner': {'discount_function': 'default_formula'},
                    'combo_outer': {'discount_function': 'default_formula'},
                },
            },
        }

    def add_tariff(self, tariff):
        new_tariff = {
            tariff: {
                'combo_inner': {'discount_function': 'default_formula'},
                'combo_outer': {'discount_function': 'default_formula'},
            },
        }

        self.response['tariff_classes'].update(new_tariff)

    def set_saved_supply_minutes(self, alternative_type, saved_supply_minutes):
        params = next(
            (
                alt
                for alt in self.response['alternatives']
                if alt['alternative_type'] == alternative_type
            ),
            None,
        )
        if params is None:
            params = {
                'alternative_type': alternative_type,
                'saved_supply_minutes': saved_supply_minutes,
            }
            self.response['alternatives'] = self.response['alternatives'] + [
                params,
            ]
        else:
            params['saved_supply_minutes'] = saved_supply_minutes

    def clear(self):
        self.response = {'alternatives': []}

    def check_request(self, request):
        data = json.loads(request.get_data())
        assert 'alternatives' in data
        assert 'user_id' in data
        assert 'user_phone_id' in data
        assert 'tariff_zone' in data
        assert 'tariff_classes' in data
        assert 'route' in data


@pytest.fixture
def combo_contractors():
    return ComboContractorsContext()


@pytest.fixture
def mock_combo_contractors(mockserver, combo_contractors):
    @mockserver.json_handler('/combo-contractors/v1/pricing-info')
    def pricing_info_handler(request):
        combo_contractors.check_request(request)
        return combo_contractors.process(mockserver)

    return pricing_info_handler
