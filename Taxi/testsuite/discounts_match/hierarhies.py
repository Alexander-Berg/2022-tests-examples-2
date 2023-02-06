import copy
import json

import pytest


def remove_hierarchies(*hierarchy_names):
    def updater(config, config_vars):
        component = config['components_manager']['components'][
            'rules-match-hierarchy-conditions'
        ]
        data = json.loads(component['hierarchy_conditions'])
        for hierarchy_name in hierarchy_names:
            data.pop(hierarchy_name)
        component['hierarchy_conditions'] = json.dumps(data)

    return pytest.mark.uservice_oneshot(config_hooks=[updater])


def _remove_active_period_end(hierarchy_descriptions):
    for hierarchy_description in hierarchy_descriptions:
        for condition in hierarchy_description['conditions']:
            if condition['condition_name'] == 'active_period':
                condition['default']['value'].pop('end', None)


@pytest.fixture
def check_hierarchy_descriptions(
        client,
        pgsql,
        condition_descriptions,
        headers,
        hierarchy_descriptions_url,
        service_name,
):

    condition_descriptions = copy.deepcopy(condition_descriptions)

    async def func(missing_hierarchies):
        def sort_hierarchies(item):
            return item['name']

        await client.invalidate_caches()
        response = await client.get(
            hierarchy_descriptions_url, headers=headers,
        )

        assert response.status_code == 200
        content = response.json()

        content['hierarchies'].sort(key=sort_hierarchies)
        descriptions = [
            desc
            for desc in condition_descriptions
            if desc['name'] not in missing_hierarchies
        ]
        descriptions.sort(key=sort_hierarchies)
        _remove_active_period_end(descriptions)
        _remove_active_period_end(content['hierarchies'])
        assert content == {'hierarchies': descriptions}

    return func
