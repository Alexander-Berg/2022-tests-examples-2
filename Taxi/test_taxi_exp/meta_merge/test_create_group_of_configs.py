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
async def test_create_group_of_configs(taxi_exp_client):
    # first config
    first_body = experiment.generate_config(
        name='first',
        schema=meta_merge.EMPTY_SCHEMA,
        default_value={},
        clauses=[],
        merge_values_by=meta_merge.MERGE_VALUES_BY,
    )
    await helpers.add_checked_config(taxi_exp_client, first_body)

    # add second config
    second_body = experiment.generate_config(
        name='second',
        schema=meta_merge.SCHEMA_WITH_ENABLED,
        default_value={'enabled': False},
        merge_values_by=meta_merge.MERGE_VALUES_BY,
    )
    await helpers.add_checked_config(taxi_exp_client, second_body)

    # obtaining list
    response = await taxi_exp_client.get(
        '/v1/configs/list/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'merge_value_tag': 'tag_for_merge'},
    )
    assert response.status == 200
    result = await response.json()
    names = [item['name'] for item in result['configs']]
    assert names == ['first', 'second']

    response = await taxi_exp_client.get(
        '/v1/configs/list/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'merge_value_tag': 'non_existed_tag'},
    )
    assert response.status == 200
    result = await response.json()
    assert not result['configs']

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

    # add third config with clauses
    third_body = experiment.generate_config(
        name='third',
        schema=meta_merge.SCHEMA_WITH_DISABLED,
        clauses=[
            experiment.make_clause('title-1', value={'disabled': False}),
            experiment.make_clause('title-2', value={}),
        ],
        merge_values_by=meta_merge.MERGE_VALUES_BY,
    )
    await helpers.add_checked_config(taxi_exp_client, third_body)

    # fail adding config with existed keys
    fail_body = experiment.generate_config(
        name='fail',
        schema=meta_merge.SCHEMA_WITH_ENABLED,
        clauses=[
            experiment.make_clause('title-1', value={'enabled': False}),
            experiment.make_clause('title-2', value={}),
        ],
        merge_values_by=meta_merge.MERGE_VALUES_BY,
    )
    for response in (
            await helpers.add_config(taxi_exp_client, fail_body),
            await helpers.verbose_init_config_by_draft(
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
    fail_body = experiment.generate_config(
        name='fail',
        schema=meta_merge.SCHEMA_WITH_ENABLED,
        clauses=[
            experiment.make_clause('title-1', value={'enabled': False}),
            experiment.make_clause('title-2', value={}),
        ],
        merge_values_by=meta_merge.UNSUPPORTED_MERGE_VALUES,
    )
    for response in (
            await helpers.add_config(taxi_exp_client, fail_body),
            await helpers.verbose_init_config_by_draft(
                taxi_exp_client, fail_body,
            ),
    ):
        assert response['code'] == 'CHECK_MERGE_VALUES_BY'

    # fail adding config with unsupported value types
    fail_body = experiment.generate_config(
        name='fail',
        schema=meta_merge.ONEOF_SCHEMA,
        clauses=[experiment.make_clause('title-1', value='abcd')],
        merge_values_by=meta_merge.MERGE_VALUES_BY,
    )
    for response in (
            await helpers.add_config(taxi_exp_client, fail_body),
            await helpers.verbose_init_config_by_draft(
                taxi_exp_client, fail_body,
            ),
    ):
        assert response['code'] == 'CHECK_MERGE_VALUES_BY'

    # fail adding config with nonused consumer
    fail_body = experiment.generate_config(
        name='fail',
        schema=meta_merge.ONEOF_SCHEMA,
        clauses=[experiment.make_clause('title-1', value='abcd')],
        merge_values_by=meta_merge.NON_USED_CONSUMER_MERGE_VALUES,
    )
    for response in (
            await helpers.add_config(taxi_exp_client, fail_body),
            await helpers.verbose_init_config_by_draft(
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

    # add config with another tag
    second_body = experiment.generate_config(
        name='second_with_another_tag',
        schema=meta_merge.SCHEMA_WITH_ENABLED,
        default_value={'enabled': False},
        merge_values_by=meta_merge.ANOTHER_TAG_MERGE_VALUES,
    )
    await helpers.success_init_config_by_draft(taxi_exp_client, second_body)

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
        '/v1/configs/list/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'merge_value_tag': 'tag'},
    )
    assert response.status == 200
    result = await response.json()
    names = [item['name'] for item in result['configs']]
    assert names == ['first', 'second', 'second_with_another_tag', 'third']
