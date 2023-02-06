# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.tripster_dialog import experience_meta

DATA = {
    'id': 18072,
    'title': 'Ленинградские коммуналки — снаружи и изнутри',
    'tagline': 'Проникнуться соседством советского быта и помпезной архитектуры в квартирах эпохи уплотнения',
    'url': 'https://experience.tripster.ru/experience/18072/',
    'is_new': False,
    'type': 'group',
    'instant_booking': True,
    'child_friendly': True,
    'max_persons': 20,
    'duration': 2.0,
    'meeting_point': {'text': 'в районе метро Звенигородская'},
    'guide': {
        'id': 229930,
        'first_name': 'Иван',
        'url': 'https://experience.tripster.ru/guide/229930/',
        'avatar': {
            'medium': 'https://experience-ireland.s3.amazonaws.com/avatar/3eef5b46-c79f-11ea-9f7f-02b782d69cda.150x150.jpg',
            'small': 'https://experience-ireland.s3.amazonaws.com/avatar/3eef5b46-c79f-11ea-9f7f-02b782d69cda.150x150.jpg',
        },
        'rating': 4.76,
        'review_count': 718,
        'avg_reaction_delay': 3,
        'links': {
            'reviews': (
                'https://experience.tripster.ru/api/guides/229930/reviews/'
            ),
        },
        'guide_type': 'team',
        'description': 'Привет! Меня зовут Иван. Вместе с командой гидов, влюбленных в Петербург, провожу экскурсии: мы стараемся максимально неформально и при этом информативно рассказывать о нашем городе. Гиды нашей команды максимально сопричастны к теме экскурсий — они историки, музеологи и искусствоведы, провели свое детство в старинных Петербургских домах',
        'exp_count_published': 1,
    },
}


@pytest.fixture(name='mock_tripster_api')
def _mock_tripster_api(mockserver):
    @mockserver.json_handler(
        r'/tripster-api/api/web/v1/experiences/.*', regex=True,
    )
    def _(request):
        return mockserver.make_response(json=DATA)


@pytest.mark.parametrize('_call_param', [[]])
async def test_tripster_dialog_order_meta_validation(_call_param):
    _ = experience_meta.ExperienceMetaAction(
        'tripster_dialog', 'experience_meta', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'experience_id', 'value': 18072}],
                ),
            ),
            [],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'experience_id_2', 'value': 18072}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'experience_id', 'value': '18072'}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_tripster_dialog_experience_meta_state_validation(
        state, _call_param,
):
    action = experience_meta.ExperienceMetaAction(
        'tripster_dialog', 'experience_meta', '0', _call_param,
    )

    action.validate_state(state)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'experience_id', 'value': 18072}],
                ),
            ),
            [],
        ),
    ],
)
async def test_tripster_dialog_experience_meta_call(
        web_context, state, _call_param, mock_tripster_api,
):
    action = experience_meta.ExperienceMetaAction(
        'tripster_dialog', 'experience_meta', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'experience_title' in _state.features
    assert (
        _state.features['experience_title']
        == 'Ленинградские коммуналки — снаружи и изнутри'
    )
