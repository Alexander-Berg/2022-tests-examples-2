import json

import pytest


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
@pytest.mark.parametrize(
    ('task_id', 'result'),
    [
        (
            7,
            {
                'equals_percent': 40,
                'topic_accuracy_v1': 50,
                'topic_accuracy_v2': 25,
                'reply_percent_v1': 80,
                'reply_percent_v2': 90,
                'close_percent_v1': 70,
                'close_percent_v2': 50,
                'reply_or_close_v1': 100,
                'reply_or_close_v2': 90,
                'topic_details': {'topic_1': {'v1': 5, 'v2': 6, 'IOU': 57}},
            },
        ),
        (
            8,
            {
                'equals_percent': 25,
                'topic_accuracy_v1': 100,
                'topic_accuracy_v2': 75,
                'reply_percent_v1': 40,
                'reply_percent_v2': 45,
                'close_percent_v1': 35,
                'close_percent_v2': 25,
                'reply_or_close_v1': 50,
                'reply_or_close_v2': 40,
                'topic_details': {'topic_1': {'v1': 6, 'v2': 1, 'IOU': 0}},
            },
        ),
    ],
)
async def test_get_testing_aggregation(web_app_client, task_id, result):
    response = await web_app_client.get(
        f'/v1/testing/results/aggregated?task_id={task_id}&user_id=34',  # noqa: E501
    )
    assert response.status == 200

    response_json = await response.json()

    assert response_json['equals_percent'] == result['equals_percent']
    assert response_json['topic_accuracy_v1'] == result['topic_accuracy_v1']
    assert response_json['topic_accuracy_v2'] == result['topic_accuracy_v2']
    assert response_json['reply_percent_v1'] == result['reply_percent_v1']
    assert response_json['reply_percent_v2'] == result['reply_percent_v2']
    assert response_json['close_percent_v1'] == result['close_percent_v1']
    assert response_json['close_percent_v2'] == result['close_percent_v2']
    assert response_json['reply_or_close_v1'] == result['reply_or_close_v1']
    assert response_json['reply_or_close_v2'] == result['reply_or_close_v2']
    assert (
        json.loads(response_json['topic_details']) == result['topic_details']
    )


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_no_aggregation(web_app_client):
    response = await web_app_client.get(
        f'/v1/testing/results/aggregated?task_id=9&user_id=34',  # noqa: E501
    )
    assert response.status == 204
