# # flake8: noqa: I100
# # pylint: disable=broad-except
# import pytest
#
# from supportai_actions.actions import action as action_module
# from supportai_actions.actions import params as param_module
# from supportai_actions.actions import features as feature_module
# from supportai_actions.actions import state as state_module
#
# from supportai_actions.action_types.justschool_dialog import (
#     module,
# )
#
#
# @pytest.mark.parametrize(
#     '_call_param',
#     [
#         [],
#         pytest.param(
#             [param_module.ActionParam({'message_type': 'failed'})],
#             marks=pytest.mark.xfail(
#                 raises=action_module.ValidationError, strict=True,
#             ),
#         ),
#     ],
# )
# async def test_module_validation(_call_param):
#     _ = module.Class(
#         'test', 'action_name', '0', _call_param,
#     )
#
#
# @pytest.mark.parametrize(
#     'state, _call_param',
#     [
#         (
#             state_module.State(
#                 features=feature_module.Features(
#                     features=[{'key': 'track_number', 'value': 'XXX-XXXX'}],
#                 ),
#             ),
#             [],
#         ),
#         pytest.param(
#             state_module.State(
#                 features=feature_module.Features(
#                     features=[{'key': 'track_number', 'value': 'some'}],
#                 ),
#             ),
#             [
#                 param_module.ActionParam(
#                     {'track_number_feature_name': 'number'},
#                 ),
#             ],
#             marks=pytest.mark.xfail(
#                 raises=action_module.ValidationError, strict=True,
#             ),
#         ),
#     ],
# )
# async def test_module_state_validation(
#         state, _call_param,
# ):
#     action = module.Class(
#         'test', 'action_name', '0', _call_param,
#     )
#
#     action.validate_state(state)
#
#
# @pytest.mark.parametrize(
#     'state, _call_param',
#     [
#         (
#             state_module.State(
#                 features=feature_module.Features(
#                     features=[{'key': 'track_number', 'value': 'XXX-XXXX'}],
#                 ),
#             ),
#             [],
#         ),
#         (
#             state_module.State(
#                 features=feature_module.Features(
#                     features=[{'key': 'track_number_2', 'value': 'some'}],
#                 ),
#             ),
#             [
#                 param_module.ActionParam(
#                     {'track_number_feature_name': 'track_number_2'},
#                 ),
#             ],
#         ),
#     ],
# )
# @pytest.mark.russian_post_mock(records=[{'oper_type': 'Test'}])
# async def test_module_call(
#         web_context, state, _call_param,
# ):
#     action = module.Class(
#         'test', 'action_name', '0', _call_param,
#     )
#
#     _state = await action(web_context, state)
#
#     assert 'oper_type' in _state.features
