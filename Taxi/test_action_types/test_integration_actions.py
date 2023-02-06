import aiohttp
import pytest

from supportai_actions.action_types import integration_action
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import params as params_module
from supportai_actions.actions import state as state_module


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_actions', files=['default.sql']),
]


@pytest.fixture(name='mock_integration', autouse=True)
def _mock_integration(monkeypatch, response_mock):
    def request(**kwargs):
        content_type = kwargs['data'].headers['Content-Type']

        class JsonRequestContextManager:
            async def __aenter__(self):
                return response_mock(
                    status=200, json={'promocode': 'PROMO12345'},
                )

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        class XmlRequestContextManager:
            async def __aenter__(self):
                return response_mock(
                    status=200, text=b'<body><info>Hello!!</info></body>',
                )

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        if content_type == 'application/json':
            return JsonRequestContextManager()
        if content_type == 'application/xml':
            assert (
                kwargs['data']._value  # pylint: disable=protected-access
                == b'<body><a>something</a><b>something else</b></body>'
            )
            return XmlRequestContextManager()
        raise ValueError(f'Unknown content-type: {content_type}')

    monkeypatch.setattr(aiohttp, 'request', request)


@pytest.mark.parametrize(
    '_call_param',
    [
        pytest.param([params_module.ActionParam({'integration_id': 1})]),
        pytest.param(
            [
                params_module.ActionParam(
                    {'integration_id': 1, 'parameters': {'size': 1000}},
                ),
            ],
        ),
        pytest.param(
            [params_module.ActionParam({})],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_validate(_call_param):
    integration_action.IntegrationAction(
        'test_project', 'echo', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    [{'key': 'delivery_delay', 'value': '123'}],
                ),
            ),
            [
                params_module.ActionParam(
                    {'integration_id': 1, 'parameters': {'size': 1000}},
                ),
            ],
        ),
        pytest.param(
            state_module.State(features=feature_module.Features(features=[])),
            [
                params_module.ActionParam(
                    {'integration_id': 1, 'parameters': {'size': 1000}},
                ),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationStateError, strict=True,
            ),
        ),
    ],
)
async def test_call_graph_action_json(
        web_context, _call_param, state, mock_integration,
):
    action = integration_action.IntegrationAction(
        'test_project', 'echo', '0', _call_param,
    )
    _state = await action(web_context, state)

    assert 'promocode' in _state.features
    assert _state.features['promocode'] == 'PROMO12345'


@pytest.mark.parametrize('template_body', [True, False])
async def test_call_graph_action_xml(
        web_context, mock_integration, template_body,
):
    features = (
        [{'key': 'something_feature', 'value': 'something'}]
        if template_body
        else []
    )
    state = state_module.State(features=feature_module.Features(features))
    call_param = params_module.ActionParam(
        {
            'integration_id': 3 if template_body else 2,
            'parameters': {'size': 1000},
        },
    )
    action = integration_action.IntegrationAction(
        'test_project', 'echo', '0', [call_param],
    )
    _state = await action(web_context, state)

    assert 'info' in _state.features
    assert _state.features['info'] == 'Hello!!'
