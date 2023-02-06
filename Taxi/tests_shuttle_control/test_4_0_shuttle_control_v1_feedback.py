# pylint: disable=import-only-modules, import-error, redefined-outer-name
import pytest

from tests_shuttle_control.utils import select_named


@pytest.mark.parametrize(
    'booking_id, code, choices, message, rating_variant_id, survey, survey_db',
    [
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            200,
            ['tag1', 'tag2', 'tag3'],
            None,
            'gudgud',
            {'what': 'yes'},
            '{"(what,yes)"}',
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            200,
            [],
            'some user message',
            None,
            None,
            '{}',
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            200,
            ['tag1'],
            'some user message',
            'badbad',
            {'what': 'no', 'bye': 'bye'},
            '{"(what,no)","(bye,bye)"}',
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
            400,
            [],
            None,
            'yareyare',
            {'what': 'daze'},
            None,
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
            400,
            [],
            'good message',
            None,
            None,
            None,
        ),
    ],
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_main(
        taxi_shuttle_control,
        pgsql,
        booking_id,
        code,
        choices,
        message,
        rating_variant_id,
        survey,
        survey_db,
):
    req = {'booking_id': booking_id, 'choices': choices}
    if message:
        req['message'] = message
    if rating_variant_id:
        req['rating_variant_id'] = rating_variant_id
    if survey:
        req['survey'] = [
            {'question_id': k, 'answer_id': v} for k, v in survey.items()
        ]

    response = await taxi_shuttle_control.post(
        '/4.0/shuttle-control/v1/feedback',
        headers={'X-Yandex-UID': '0123456789'},
        json=req,
    )

    assert response.status_code == code

    if code == 200:
        rows = select_named(
            'SELECT choices, message, rating_variant_id, survey_answers '
            'FROM state.feedbacks '
            f'WHERE booking_id = \'{booking_id}\'',
            pgsql['shuttle_control'],
        )
        assert rows == [
            {
                'choices': choices,
                'message': message,
                'rating_variant_id': rating_variant_id,
                'survey_answers': survey_db,
            },
        ]
