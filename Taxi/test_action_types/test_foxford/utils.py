from supportai_actions.actions import features as feature_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import state as state_module


def make_new_call_params_and_state(state: state_module.State):
    new_call_params = [
        param_module.ActionParam(
            {
                'input_arguments_mapping': {
                    key: key + '1' for key, _ in state.features
                },
            },
        ),
    ]
    new_state = state_module.State(
        features=feature_module.Features(
            features=[
                {'key': key + '1', 'value': state.features[key]}
                for key, _ in state.features
            ],
        ),
    )
    return new_call_params, new_state
