import json
import pytest

from django import test as django_test

from taxi.core import async


@pytest.mark.parametrize(
    'rule,expected_steps,expected_hours', [
        (
            {
                "id": "some_id",
                "zone": "moscow",
                "week_days": [
                    "mon",
                    "tue"
                ],
                "hours": "1, 2, 3",
                "begin_at": "2018-06-07",
                "end_at": "2018-06-09",
                "has_commission": True,
                "ticket": "TAXIBACKEND-6666",
                "steps_csv": 'step,income\n10,100\n20,250\n30,500\n'
            },

            [
                [10, '100'],
                [20, '250'],
                [30, '500']
            ],

            [1, 2, 3]
        ),
        (
            {
                "id": "another_id",
                "zone": "moscow",
                "week_days": [
                    "thu",
                    "sat",
                    "wed"
                ],
                "hours": "3, 16-20, 21",
                "begin_at": "2018-06-07",
                "end_at": "2018-06-09",
                "has_commission": False,
                "ticket": "TAXIBACKEND-6666",
                "acceptance_rate": 0.2,
                "completion_rate": 0.5,
                "activity_points": 12,
                "steps_csv": 'step,income\n30,500\n10,100\n'
            },

            [
                [30, '500'],
                [10, '100']
            ],

            [3, 16, 17, 18, 19, 20, 21]
        )
    ]
)
@pytest.mark.asyncenv('blocking')
def test_add_daily_guarantee(patch, rule, expected_steps, expected_hours):

    @patch('taxi.external.subventions.create_daily_guarantees')
    @async.inline_callbacks
    def create_daily_guarantees(data, **kwargs):
        assert data['steps'] == expected_steps
        assert data['hours'] == expected_hours
        yield async.return_value({})

    test_client = django_test.Client()
    response = test_client.post(
        '/api/subventions/daily_guarantees/',
        data=json.dumps(rule),
        content_type='application/json'
    )

    assert response.content == '{}'
    assert response.status_code == 200
