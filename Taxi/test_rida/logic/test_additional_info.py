from typing import Any
from typing import Dict

import pytest

from rida.generated.service.swagger.models import api as api_models
from rida.utils import additional_info as additional_info_utils


@pytest.fixture(name='rida_translations')
def rida_translations_fixture(web_app):
    return web_app['context'].rida_translations


@pytest.mark.translations(
    rida={
        'simple_key': {'en': 'simple value'},
        'key_param_1': {'en': 'pr1 {param_1}'},
        'key_param_2': {'en': 'pr2 {param_2}'},
    },
)
@pytest.mark.parametrize(
    ['unit_template', 'expected_unit'],
    [
        pytest.param(
            api_models.ControlUnit(type=100, color='#000000'),
            {'type': 100, 'data': {'color': '#000000'}},
            id='separator_unit',
        ),
        pytest.param(
            api_models.ControlUnit(type=101),
            {'type': 101, 'data': {}},
            id='spacer_unit',
        ),
        pytest.param(
            api_models.TextUnit(tanker_key='key_param_1', color='#121212'),
            {'type': 1, 'data': {'text': 'pr1 value_1', 'color': '#121212'}},
            id='text_unit',
        ),
        pytest.param(
            api_models.KeyValueUnit(
                key=api_models.Text(tanker_key='simple_key', color='#121212'),
                value=api_models.Text(tanker_key='key_param_1'),
            ),
            {
                'type': 2,
                'data': {
                    'key': {'text': 'simple value', 'color': '#121212'},
                    'value': {'text': 'pr1 value_1', 'color': '#000000'},
                },
            },
            id='key_value_unit',
        ),
        pytest.param(
            api_models.BubbleUnit(
                tanker_key='key_param_1',
                color='#121212',
                background_color='#232323',
            ),
            {
                'type': 3,
                'data': {
                    'text': 'pr1 value_1',
                    'text_color': '#121212',
                    'background_color': '#232323',
                },
            },
            id='bubble_unit',
        ),
        pytest.param(
            api_models.NamedBubbleListUnit(
                text_tk='simple_key',
                text_color='#000005',
                text_size=10,
                text_style='normal',
                bubbles=[
                    api_models.Bubble(
                        text_tk='key_param_1',
                        text_color='#000001',
                        background_color='#000002',
                        radius=2,
                    ),
                    api_models.Bubble(
                        text_tk='key_param_2',
                        text_color='#000003',
                        background_color='#000004',
                        radius=4,
                    ),
                ],
            ),
            {
                'type': 4,
                'data': {
                    'text': 'simple value',
                    'text_color': '#000005',
                    'text_size': 10,
                    'text_style': 'normal',
                    'bubbles': [
                        {
                            'text': 'pr1 value_1',
                            'text_color': '#000001',
                            'background_color': '#000002',
                            'radius': 2,
                        },
                        {
                            'text': 'pr2 value_2',
                            'text_color': '#000003',
                            'background_color': '#000004',
                            'radius': 4,
                        },
                    ],
                },
            },
            id='named_bubble_list_unit',
        ),
        pytest.param(
            api_models.KeyValueComboBubblesUnit(
                kv_combo_bubbles=[
                    api_models.KeyValueComboBubble(
                        bg_color='#ffe9e8',
                        kv_bubbles=[
                            api_models.KeyValueBubble(
                                key_tk='simple_key',
                                value_tk='key_param_1',
                                key_color='#000001',
                                value_color='#000002',
                            ),
                            api_models.KeyValueBubble(
                                key_tk='simple_key',
                                value_tk='key_param_2',
                                key_color='#000003',
                                value_color='#000004',
                                key_font_style='bold',
                                value_font_style='normal',
                            ),
                        ],
                    ),
                    api_models.KeyValueComboBubble(
                        bg_color='#f0f2f7',
                        kv_bubbles=[
                            api_models.KeyValueBubble(
                                key_tk='simple_key',
                                value_tk='key_param_1',
                                key_color='#000005',
                                value_color='#000006',
                            ),
                        ],
                    ),
                ],
            ),
            {
                'type': 5,
                'data': {
                    'kv_combo_bubbles': [
                        {
                            'bg_color': '#ffe9e8',
                            'kv_bubbles': [
                                {
                                    'key': 'simple value',
                                    'value': 'pr1 value_1',
                                    'key_color': '#000001',
                                    'value_color': '#000002',
                                },
                                {
                                    'key': 'simple value',
                                    'value': 'pr2 value_2',
                                    'key_color': '#000003',
                                    'value_color': '#000004',
                                    'key_font_style': 'bold',
                                    'value_font_style': 'normal',
                                },
                            ],
                        },
                        {
                            'bg_color': '#f0f2f7',
                            'kv_bubbles': [
                                {
                                    'key': 'simple value',
                                    'value': 'pr1 value_1',
                                    'key_color': '#000005',
                                    'value_color': '#000006',
                                },
                            ],
                        },
                    ],
                },
            },
            id='key_value_combo_bubbles_unit',
        ),
    ],
)
def test_build_unit(
        rida_translations,
        unit_template: additional_info_utils.UnitTemplate,
        expected_unit: Dict[str, Any],
):
    unit = additional_info_utils.build_unit(
        rida_translations=rida_translations,
        unit_template=unit_template,
        locale='en',
        template_params={'param_1': 'value_1', 'param_2': 'value_2'},
        prebuilt_units={'prebuilt_unit': {'lol': 'kek'}},
    )
    assert unit == expected_unit
