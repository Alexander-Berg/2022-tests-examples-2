import pytest

from taxi_exp.lib import constants
from taxi_exp.util import pg_helpers
from test_taxi_exp.helpers import experiment
from test_taxi_exp.helpers import files

NAME = 'experiment_with_revisions'
TAG_NAME = 'trusted'


async def get_revisions(client, name):
    query = """
        WITH exp AS (
            SELECT id FROM clients_schema.experiments WHERE name = $1
        )
        SELECT * FROM clients_schema.revision_history
        WHERE experiment_id = ANY(ARRAY(SELECT id FROM exp))
    ;
    """
    return await pg_helpers.fetch(client.app['pool'], query, name)


@pytest.mark.parametrize(
    'url, body, updated_body',
    [
        (
            '/v1/experiments/',
            experiment.generate_default(
                clauses=[
                    experiment.make_clause(
                        'title', experiment.userhas_predicate(TAG_NAME),
                    ),
                ],
            ),
            experiment.generate_default(
                match_predicate=experiment.inset_predicate(
                    set_=[1, 2, 3], set_elem_type='int',
                ),
                clauses=[
                    experiment.make_clause(
                        'title', experiment.userhas_predicate(TAG_NAME),
                    ),
                ],
            ),
        ),
        (
            '/v1/configs/',
            experiment.generate_config(
                clauses=[
                    experiment.make_clause(
                        'title', experiment.userhas_predicate(TAG_NAME),
                    ),
                ],
            ),
            experiment.generate_config(
                clauses=[
                    experiment.make_clause(
                        'title',
                        predicate=experiment.inset_predicate(
                            set_=[1, 2, 3], set_elem_type='int',
                        ),
                    ),
                    experiment.make_clause(
                        'title_v2', experiment.userhas_predicate(TAG_NAME),
                    ),
                ],
            ),
        ),
    ],
)
@pytest.mark.now('2020-04-22T00:23:16+0300')
@pytest.mark.config(
    EXP_HISTORY_DEPTH=10,
    EXP3_ADMIN_CONFIG={
        'settings': {
            'common': {'in_set_max_elements_count': 100},
            'backend': {
                'trusted_file_lines_count_change_threshold': {
                    'absolute': 10,
                    'percentage': 20,
                },
                'change_types': [
                    constants.CHANGE_TYPE_DIRECT,
                    constants.CHANGE_TYPE_TRUSTED,
                ],
            },
        },
    },
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_get_revisions(taxi_exp_client, url, body, updated_body):
    # add tag
    response = await files.post_trusted_file(
        taxi_exp_client, TAG_NAME, b'trusted content',
    )
    assert response.status == 200

    # create
    response = await taxi_exp_client.post(
        url,
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
        json=body,
    )
    assert response.status == 200

    # update x2
    for i in range(2):
        response = await taxi_exp_client.put(
            url,
            headers={'X-Ya-Service-Ticket': '123'},
            params={'name': NAME, 'last_modified_at': 1 + i},
            json=updated_body,
        )
        assert response.status == 200

    # check history length
    assert len(await get_revisions(taxi_exp_client, NAME)) == 3

    # check revisions list
    response = await taxi_exp_client.get(
        url + 'revisions/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200
    response_body = await response.json()
    assert 'revisions' in response_body
    revisions = [
        rev_info['revision'] for rev_info in response_body['revisions']
    ]
    assert revisions == [3, 2, 1]

    # check get older revisions
    response = await taxi_exp_client.get(
        url + 'revisions/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'older_than': 3},
    )
    assert response.status == 200
    response_body = await response.json()
    assert 'revisions' in response_body
    revisions = [
        rev_info['revision'] for rev_info in response_body['revisions']
    ]
    assert revisions == [2, 1]

    # update tag
    response = await files.post_trusted_file(
        taxi_exp_client, TAG_NAME, b'new trusted content',
    )
    assert response.status == 200

    # check revisions length
    revisions = await get_revisions(taxi_exp_client, NAME)
    assert len(revisions) == 4
    assert [item['change_type'] for item in revisions] == [
        'direct',
        'direct',
        'direct',
        'trusted_tag_update',
    ]

    # check get newest revisions
    response = await taxi_exp_client.get(
        url + 'revisions/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'newer_than': 2},
    )
    assert response.status == 200
    response_body = await response.json()
    assert 'revisions' in response_body
    revisions = [
        rev_info['revision'] for rev_info in response_body['revisions']
    ]
    assert revisions == [3, 4]

    # check get revisions by type
    for (params, expected_revisions) in (
            (
                {'name': NAME, 'change_types': constants.CHANGE_TYPE_DIRECT},
                [3, 2, 1],
            ),
            (
                {'name': NAME, 'change_types': constants.CHANGE_TYPE_TRUSTED},
                [4],
            ),
            (
                {
                    'name': NAME,
                    'change_types': ','.join(
                        [
                            constants.CHANGE_TYPE_DIRECT,
                            constants.CHANGE_TYPE_TRUSTED,
                        ],
                    ),
                },
                [4, 3, 2, 1],
            ),
            (
                (
                    ('name', NAME),
                    ('change_types', constants.CHANGE_TYPE_DIRECT),
                    ('change_types', constants.CHANGE_TYPE_TRUSTED),
                ),
                [4, 3, 2, 1],
            ),
    ):
        response = await taxi_exp_client.get(
            url + 'revisions/',
            headers={'X-Ya-Service-Ticket': '123'},
            params=params,
        )
        assert response.status == 200, await response.text()
        response_body = await response.json()
        assert 'revisions' in response_body
        revisions = [
            rev_info['revision'] for rev_info in response_body['revisions']
        ]
        assert revisions == expected_revisions
