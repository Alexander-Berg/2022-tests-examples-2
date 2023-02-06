import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.driver import car_vars
from order_notify.repositories.order_info import OrderData


@pytest.fixture(name='mock_functions')
def mock_car_vars_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_car_data = Counter()

    counters = Counters()

    @patch('order_notify.repositories.driver.car_vars.get_car_data')
    def _get_car_data(
            context: stq_context.Context, order_data: OrderData,
    ) -> dict:
        counters.get_car_data.call()
        assert order_data == OrderData(
            brand='', country='', order={}, order_proc={},
        )
        return {
            '_id': 'car_number',
            'display_model': 'display_model',
            'color_code': 'FAFBFB',
        }

    return counters


@pytest.mark.translations(color={'FAFBFB': {'ru': 'белый'}})
def test_get_car_vars(stq3_context: stq_context.Context, mock_functions):
    expected_vars = {
        'car_number': 'car_number',
        'car_model': 'display_model',
        'car_color': 'белый',
    }
    c_vars = car_vars.get_car_vars(
        context=stq3_context,
        order_data=OrderData(brand='', country='', order={}, order_proc={}),
        locale='ru',
    )
    assert c_vars == expected_vars
    assert mock_functions.get_car_data.times_called == 1


@pytest.mark.parametrize(
    'chosen_candidate, expected_id, expected_display_model, '
    'expected_color_code',
    [
        pytest.param({}, '', '', None, id='empty'),
        pytest.param(
            {'car_number': '1', 'car_color_code': 'FAFBFB'},
            '1',
            '',
            'FAFBFB',
            id='no_car_model',
        ),
        pytest.param(
            {'car_number': '1', 'car_model': 'Lamba'},
            '1',
            'Lamba',
            None,
            id='car_model_not_in_config',
        ),
        pytest.param(
            {'car_number': '1', 'car_model': 'Hyundai Equus'},
            '1',
            'Equus',
            None,
            id='car_model_in_config',
        ),
    ],
)
@pytest.mark.config(CAR_MARK_DISPLAY_RULES={'Hyundai Equus': 'Equus'})
def test_get_car_data(
        stq3_context: stq_context.Context,
        chosen_candidate,
        expected_id,
        expected_display_model,
        expected_color_code,
):
    expected_car_doc = {
        '_id': expected_id,
        'display_model': expected_display_model,
        'color_code': expected_color_code,
    }
    car_doc = car_vars.get_car_data(
        context=stq3_context,
        order_data=OrderData(
            brand='',
            country='',
            order={},
            order_proc={
                'candidates': [chosen_candidate],
                'performer': {'candidate_index': 0},
            },
        ),
    )
    assert car_doc == expected_car_doc
