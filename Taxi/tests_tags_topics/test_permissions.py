from typing import Any
from typing import List

import pytest

from tests_tags_topics import constants


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.pgsql('tags_topics', files=['permissions_initial.sql'])
@pytest.mark.parametrize(
    'service, req, expected_response',
    [
        (
            constants.TAGS_SERVICE,
            {'login': 'user1', 'topics': ['topic1', 'topic2']},
            {'permission': 'allowed'},
        ),
        (
            constants.TAGS_SERVICE,
            {'login': 'user2', 'topics': ['topic1', 'topic2']},
            {
                'permission': 'prohibited',
                'details': {'prohibited_topics': ['topic2']},
            },
        ),
        (
            constants.TAGS_SERVICE,
            {'login': 'user1', 'topics': ['topic1', 'topic2']},
            {'permission': 'allowed'},
        ),
        (
            constants.TAGS_SERVICE,
            {'login': 'user1', 'topics': ['topic4', 'topic1']},
            {
                'permission': 'prohibited',
                'details': {'prohibited_topics': ['topic4']},
            },
        ),
        (
            constants.PASSENGER_TAGS_SERVICE,
            {'login': 'user1', 'topics': ['topic3']},
            {'permission': 'allowed'},
        ),
        (
            constants.PASSENGER_TAGS_SERVICE,
            {'login': 'user2', 'topics': ['topic1']},
            {
                'permission': 'prohibited',
                'details': {'prohibited_topics': ['topic1']},
            },
        ),
        (
            constants.PASSENGER_TAGS_SERVICE,
            {'login': 'nologin', 'topics': ['topic1']},
            {
                'permission': 'prohibited',
                'details': {'prohibited_topics': ['topic1']},
            },
        ),
        (
            constants.EATS_TAGS_SERVICE,
            {'login': 'user1', 'topics': ['topic4']},
            {'permission': 'allowed'},
        ),
        (
            constants.GROCERY_TAGS_SERVICE,
            {'login': 'user1', 'topics': ['topic5']},
            {'permission': 'allowed'},
        ),
    ],
)
async def test_permission_check(
        taxi_tags_topics, service, req, expected_response,
):
    response = await taxi_tags_topics.post(
        f'/v1/permissions/check',
        headers={
            constants.TICKET_HEADER: constants.TICKETS_BY_SERVICE[service],
        },
        json=req,
    )

    assert response.status_code == 200

    assert response.json() == expected_response


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.pgsql('tags_topics', files=['permissions_initial.sql'])
@pytest.mark.parametrize(
    'req',
    [
        {'login': '', 'topics': ['topic1', 'topic2']},
        {'login': 'user1', 'topics': []},
    ],
)
async def test_permission_check_validation(taxi_tags_topics, req):
    response = await taxi_tags_topics.post(
        f'/v1/permissions/check',
        headers={
            constants.TICKET_HEADER: constants.TICKETS_BY_SERVICE[
                constants.TAGS_SERVICE
            ],
        },
        json=req,
    )

    assert response.status_code == 400


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': constants.UNKNOWN_SERVICE, 'dst': 'tags-topics'}],
)
@pytest.mark.pgsql('tags_topics', files=['permissions_initial.sql'])
async def test_permission_check_bad_service(taxi_tags_topics):
    response = await taxi_tags_topics.post(
        f'/v1/permissions/check',
        headers={
            constants.TICKET_HEADER: constants.TICKETS_BY_SERVICE[
                constants.UNKNOWN_SERVICE
            ],
        },
        json={'login': 'user1', 'topics': ['topic1', 'topic2']},
    )

    assert response.status_code == 200

    expected_response = {
        'permission': 'prohibited',
        'details': {'prohibited_topics': ['topic1', 'topic2']},
    }

    assert response.json() == expected_response


@pytest.mark.config(TAGS_TOPICS_PERMISSIVE_MODE_TOPICS_ENABLED=True)
@pytest.mark.pgsql('tags_topics', files=['permissions_initial.sql'])
async def test_permission_check_permissive_mode_topic(taxi_tags_topics):
    response = await taxi_tags_topics.post(
        f'/v1/permissions/check',
        headers={
            constants.TICKET_HEADER: constants.TICKETS_BY_SERVICE[
                constants.TAGS_SERVICE
            ],
        },
        json={'login': 'user1', 'topics': ['topic1', 'topic2']},
    )

    assert response.status_code == 200

    assert response.json() == {'permission': 'allowed'}


@pytest.mark.pgsql('tags_topics', files=['permissions_initial.sql'])
@pytest.mark.parametrize(
    'service, topics, expected_code, expected_response',
    [
        pytest.param(
            constants.TAGS_SERVICE,
            ['topic1', 'topic2'],
            200,
            {'owners': ['user1']},
            id='find-owner',
        ),
        pytest.param(
            'market-tags',
            ['marketplace'],
            400,
            {'code': 'BAD_REQUEST', 'message': 'unknown service market-tags'},
            id='unknown-unit',
        ),
        pytest.param(
            constants.TAGS_SERVICE,
            ['unknown-topic'],
            200,
            {'owners': []},
            id='unknown-topic-no-owners',
        ),
        pytest.param(
            constants.TAGS_SERVICE,
            ['topic1'],
            200,
            {'owners': ['user1', 'user2']},
            id='find-two-owners',
        ),
    ],
)
async def test_get_owners(
        taxi_tags_topics,
        service: str,
        topics: List[str],
        expected_code: int,
        expected_response: Any,
):
    response = await taxi_tags_topics.post(
        '/v1/permissions/get-owners',
        json={'service': service, 'topics': topics},
    )
    assert response.status_code == expected_code
    assert response.json() == expected_response
