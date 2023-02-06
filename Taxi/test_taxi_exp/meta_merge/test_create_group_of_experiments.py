import pytest

from test_taxi_exp import helpers
from test_taxi_exp import meta_merge
from test_taxi_exp.helpers import experiment


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {
            'common': {'meta_merge_methods': ['dicts_recursive_merge']},
        },
    },
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_create_group_of_experiments(taxi_exp_client):
    # first experiment
    first_body = experiment.generate(
        name='first',
        schema=meta_merge.EMPTY_SCHEMA,
        default_value={},
        merge_values_by=meta_merge.MERGE_VALUES_BY,
    )
    await helpers.add_checked_exp(taxi_exp_client, first_body)

    # add second experiment
    second_body = experiment.generate(
        name='second',
        schema=meta_merge.SCHEMA_WITH_ENABLED,
        default_value={'enabled': False},
        merge_values_by=meta_merge.MERGE_VALUES_BY,
    )
    await helpers.add_checked_exp(taxi_exp_client, second_body)

    # obtaining list
    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'merge_value_tag': 'tag_for_merge'},
    )
    assert response.status == 200
    result = await response.json()
    names = [item['name'] for item in result['experiments']]
    assert names == ['first', 'second']

    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'merge_value_tag': 'non_existed_tag'},
    )
    assert response.status == 200
    result = await response.json()
    assert not result['experiments']

    # check get merge_tag with consumer
    response = await taxi_exp_client.get(
        '/v1/experiments/filters/consumers/list/',
        headers={'X-Ya-Service-Ticket': '123'},
    )
    assert response.status == 200
    result = await response.json()
    assert result == {
        'consumers': [
            {
                'name': 'test_consumer',
                'merge_tags': [
                    {
                        'tag': 'tag_for_merge',
                        'merge_method': 'dicts_recursive_merge',
                    },
                ],
            },
        ],
    }

    # add third experiment with clauses
    third_body = experiment.generate(
        name='third',
        schema=meta_merge.SCHEMA_WITH_DISABLED,
        clauses=[
            experiment.make_clause('title-1', value={'disabled': False}),
            experiment.make_clause('title-2', value={}),
        ],
        merge_values_by=meta_merge.MERGE_VALUES_BY,
    )
    await helpers.add_checked_exp(taxi_exp_client, third_body)

    # fail adding experiment with existed keys
    fail_body = experiment.generate(
        name='fail',
        schema=meta_merge.SCHEMA_WITH_ENABLED,
        clauses=[
            experiment.make_clause('title-1', value={'enabled': False}),
            experiment.make_clause('title-2', value={}),
        ],
        merge_values_by=meta_merge.MERGE_VALUES_BY,
    )
    for response in (
            await helpers.add_exp(taxi_exp_client, fail_body),
            await helpers.verbose_init_exp_by_draft(
                taxi_exp_client, fail_body,
            ),
    ):
        assert response == {
            'message': (
                'Merge method "dicts_recursive_merge" '
                'not allow intersectioned keys: "enabled"'
            ),
            'code': 'CHECK_MERGE_VALUES_BY',
        }

    # fail adding experiment with unsupported merge_method
    fail_body = experiment.generate(
        name='fail',
        schema=meta_merge.SCHEMA_WITH_ENABLED,
        clauses=[
            experiment.make_clause('title-1', value={'enabled': False}),
            experiment.make_clause('title-2', value={}),
        ],
        merge_values_by=meta_merge.UNSUPPORTED_MERGE_VALUES,
    )
    for response in (
            await helpers.add_exp(taxi_exp_client, fail_body),
            await helpers.verbose_init_exp_by_draft(
                taxi_exp_client, fail_body,
            ),
    ):
        assert response['code'] == 'CHECK_MERGE_VALUES_BY'

    # fail adding experiment with unsupported value types
    fail_body = experiment.generate(
        name='fail',
        schema="""type: string""",
        clauses=[experiment.make_clause('title-1', value='123')],
        merge_values_by=meta_merge.MERGE_VALUES_BY,
    )
    for response in (
            await helpers.add_exp(taxi_exp_client, fail_body),
            await helpers.verbose_init_exp_by_draft(
                taxi_exp_client, fail_body,
            ),
    ):
        assert response['code'] == 'CHECK_MERGE_VALUES_BY'

    # fail adding experiment with non used consumer
    fail_body = experiment.generate(
        name='fail',
        schema="""type: string""",
        clauses=[experiment.make_clause('title-1', value='123')],
        merge_values_by=meta_merge.NON_USED_CONSUMER_MERGE_VALUES,
    )
    for response in (
            await helpers.add_exp(taxi_exp_client, fail_body),
            await helpers.verbose_init_exp_by_draft(
                taxi_exp_client, fail_body,
            ),
    ):
        assert response == {
            'code': 'CHECK_MERGE_VALUES_BY',
            'message': (
                'Used consumer "non_used_consumer" not found in request, '
                'existed only: test_consumer'
            ),
        }

    # add experiment with another tag
    second_body = experiment.generate(
        name='second_with_another_tag',
        schema=meta_merge.SCHEMA_WITH_ENABLED,
        default_value={'enabled': False},
        merge_values_by=meta_merge.ANOTHER_TAG_MERGE_VALUES,
    )
    await helpers.add_checked_exp(taxi_exp_client, second_body)

    # check get merge_tag with consumer
    response = await taxi_exp_client.get(
        '/v1/experiments/filters/consumers/list/',
        headers={'X-Ya-Service-Ticket': '123'},
    )
    assert response.status == 200
    result = await response.json()
    assert result == {
        'consumers': [
            {
                'name': 'test_consumer',
                'merge_tags': [
                    {
                        'tag': 'tag_for_merge',
                        'merge_method': 'dicts_recursive_merge',
                    },
                    {
                        'tag': 'tag_for_merge_v2',
                        'merge_method': 'dicts_recursive_merge',
                    },
                ],
            },
        ],
    }

    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'merge_value_tag': 'tag'},
    )
    assert response.status == 200
    result = await response.json()
    names = [item['name'] for item in result['experiments']]
    assert names == ['first', 'second', 'second_with_another_tag', 'third']
