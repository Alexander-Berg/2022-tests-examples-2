# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error, import-only-modules
# flake8: noqa F401
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_passenger_feedback.plugins.mock_order_core import mock_order_core
from tests_passenger_feedback.plugins.mock_order_core import order_core


def default_request(zone: str) -> dict:
    return {
        'id': 'user_id',
        'phone_id': '123456789012345678901234',
        'order_id': 'bfda5489e2215d599abc840fd8f56a76',
        'reorder_id': 'reorder_id',
        'rating': 4,
        'msg': 'message',
        'call_me': True,
        'app_comment': False,
        'created_time': '2018-08-10T21:01:30+0300',
        'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
        'badges': [],
        'order_city': 'Москва',
        'order_zone': zone,
        'order_created_time': '2018-08-10T21:01:30+0300',
        'order_cancelled': False,
        'order_completed': False,
        'order_finished_for_client': True,
        'driver_license_pd_id': 'license_pd_id',
    }


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(PASSENGER_FEEDBACK_SAVE_TO_ORDER=False)
@pytest.mark.parametrize('zone', ['moscow', 'spb'])
async def test_feedback_rating_metrics(
        feedback_save, taxi_passenger_feedback_monitor, zone,
):
    request = default_request(zone)

    async with metrics_helpers.MetricsCollector(
            taxi_passenger_feedback_monitor, sensor='feedback_rating',
    ) as collector:
        await feedback_save.call(request)

    metric = collector.get_single_collected_metric()
    assert metric.value == 1

    expected_zone = zone if zone == 'moscow' else 'undefined'
    assert metric.labels == {
        'sensor': 'feedback_rating',
        'zone': expected_zone,
        'rating': '4',
    }


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.experiments3(filename='ride_quality_survey_exp.json')
@pytest.mark.translations(
    client_messages={
        'question_key1': {'ru': 'Текст вопроса'},
        'answer_key1': {'ru': 'Ответ 1'},
        'answer_key2': {'ru': 'Ответ 2'},
    },
)
async def test_feedback_proposal_metrics(
        taxi_passenger_feedback,
        taxi_passenger_feedback_monitor,
        order_core_api,
):

    order_id = '9b0ef3c5398b3e07b59f03110563479d'
    json_body = {'order_id': order_id}
    headers = ({'X-Yandex-Uid': '123456', 'X-YaTaxi-UserId': 'testsuite'},)

    async with metrics_helpers.MetricsCollector(
            taxi_passenger_feedback_monitor,
            sensor='feedback_survey_questions',
    ) as collector:
        response = await taxi_passenger_feedback.post(
            '/4.0/passenger-feedback/v1/feedback-proposal',
            json=json_body,
            headers=headers,
        )
    assert response.status_code == 200

    metric = collector.get_single_collected_metric()
    assert metric.value == 1

    assert metric.labels == {
        'question_id': 'q_1',
        'sensor': 'feedback_survey_questions',
    }


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(PASSENGER_FEEDBACK_SAVE_TO_ORDER=False)
@pytest.mark.experiments3(filename='ride_quality_survey_exp.json')
@pytest.mark.parametrize('feedback_save', ['v2'], indirect=True)
@pytest.mark.config(
    FEEDBACK_BADGES_MAPPING={
        'feedback_badges': [
            {
                'name': 'pleasantmusic',
                'label': 'feedback_badges.pleasantmusic',
                'filters': {'tariffs': ['default']},
            },
        ],
        'feedback_rating_mapping': [
            {
                'rating': 3,
                'choice_title': 'feedback_badges.rating_title_5',
                'badges': ['pleasantmusic'],
            },
        ],
    },
)
async def test_feedback_survey_metrics(
        feedback_save, taxi_passenger_feedback_monitor,
):
    request = default_request('moscow')

    async with metrics_helpers.MetricsCollector(
            taxi_passenger_feedback_monitor, sensor='feedback_survey_answers',
    ) as collector:
        await feedback_save.call(request)

    metric = collector.get_single_collected_metric()
    assert metric.value == 1

    assert metric.labels == {
        'answer_id': 'a_1',
        'question_id': 'q_1',
        'sensor': 'feedback_survey_answers',
    }
