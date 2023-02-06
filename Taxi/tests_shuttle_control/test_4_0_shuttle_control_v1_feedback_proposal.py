import pytest


@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_feedback_proposal(taxi_shuttle_control, experiments3):
    experiments3.add_config(
        name='shuttle_feedback_settings',
        consumers=['shuttle-control/v1_feedback_proposal'],
        match={'enabled': True, 'predicate': {'type': 'true'}},
        clauses=[
            {
                'title': 'first',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'finished': {
                        'enable': True,
                        'ttl': 60,
                        'shuffle_choices': False,
                        'title_tanker_key': (
                            'shuttle_control.feedback.finished.title'
                        ),
                        'comment_placeholder_tanker_key': (
                            'shuttle_control.feedback.finished.'
                            'comment_placeholder'
                        ),
                        'survey': [
                            {
                                'question_id': 'ololo_question',
                                'answer_options': [
                                    {
                                        'id': 'yup',
                                        'text_tanker_key': (
                                            'shuttle_control.survey.yup'
                                        ),
                                    },
                                    {
                                        'id': 'nah',
                                        'text_tanker_key': (
                                            'shuttle_control.survey.nah'
                                        ),
                                    },
                                ],
                                'question_text_tanker_key': (
                                    'shuttle_control.survey.question'
                                ),
                                'weight': 1337,
                            },
                            {
                                'question_id': 'another_question',
                                'answer_options': [
                                    {
                                        'id': 'yup',
                                        'text_tanker_key': (
                                            'shuttle_control.survey.yup'
                                        ),
                                    },
                                    {
                                        'id': 'nah',
                                        'text_tanker_key': (
                                            'shuttle_control.survey.nah'
                                        ),
                                    },
                                ],
                                'question_text_tanker_key': (
                                    'shuttle_control.survey.question'
                                ),
                                'weight': 1,
                            },
                        ],
                    },
                },
            },
        ],
    )

    response = await taxi_shuttle_control.post(
        f'/4.0/shuttle-control/v1/feedback-proposal',
        {'order_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730769'},
        headers={
            'X-Yandex-UID': '0123456722',
            'X-Request-Language': 'ru',
            'X-YaTaxi-UserId': 'userid',
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'survey_info': [
            {
                'answer_options': [
                    {'id': 'yup', 'text': 'Агаа'},
                    {'id': 'nah', 'text': 'Неа'},
                ],
                'question_id': 'ololo_question',
                'question_text': 'Водитель делал плохое зло?',
            },
        ],
    }
