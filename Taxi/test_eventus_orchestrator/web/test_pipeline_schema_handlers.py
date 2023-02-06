import pytest


def get_test_schema(i):
    return {
        'mappers': [
            {
                'name': f'add_timestamp_{i}',
                'description': f'Add now timestamp {i}',
                'argument_schemas': [
                    {
                        'name': f'dst_key_{i}',
                        'description': f'Set timestamp destination key {i}',
                        'type': 'string',
                        'is_required': True,
                        'default_value': 'enum_value_1',
                        'enum_values': [
                            'enum_value_1',
                            'enum_value_2',
                            'enum_value_3',
                        ],
                    },
                ],
            },
        ],
        'filters': [],
        'customs': [],
        'sources': [],
        'sinks': [],
    }


async def get_schema_and_check(
        taxi_eventus_orchestrator_web, instance, expected_code, expected_index,
):
    response = await taxi_eventus_orchestrator_web.get(
        '/v1/admin/pipeline/schema', params={'instance_name': instance},
    )

    assert response.status == expected_code

    if expected_code != 200:
        return

    body = await response.json()
    assert body['main_version'] == get_test_schema(expected_index)


async def put_schema(
        taxi_eventus_orchestrator_web,
        instance,
        index,
        build_version,
        host,
        expected_code=200,
):
    response = await taxi_eventus_orchestrator_web.put(
        '/v1/eventus/pipeline/schema',
        params={'instance_name': instance},
        json={
            'schema': get_test_schema(index),
            'build_version': build_version,
            'hostname': host,
        },
    )

    assert response.status == expected_code


async def test_pipeline_schema_get_correct_version(
        taxi_eventus_orchestrator_web,
):
    await get_schema_and_check(
        taxi_eventus_orchestrator_web, 'order-events-producer', 200, 0,
    )


@pytest.mark.parametrize(
    'small_version, greater_version_1, greater_version_2, index',
    [
        ('9.1.166', '9.1.167', '9.1.168', 0),
        ('9.1.166', '9.2.166', '9.3.166', 2),
        ('9.1.166', '10.1.166', '11.1.166', 4),
    ],
)
async def test_pipeline_schema_put_and_get(
        taxi_eventus_orchestrator_web,
        small_version,
        greater_version_1,
        greater_version_2,
        index,
):
    await put_schema(
        taxi_eventus_orchestrator_web,
        'order-events-producer',
        index + 22,
        small_version,
        'asdfgvvvv.man.yp-c.yandex.net',
    )
    await put_schema(
        taxi_eventus_orchestrator_web,
        'order-events-producer',
        index,
        greater_version_1,
        'gmqnrk4fmwjqie6o.man.yp-c.yandex.net',
    )
    await put_schema(
        taxi_eventus_orchestrator_web,
        'order-events-producer',
        index + 1,
        greater_version_2,
        'asasfsdg545t.man.yp-c.yandex.net',
    )
    await get_schema_and_check(
        taxi_eventus_orchestrator_web,
        'order-events-producer',
        200,
        index + 22,
    )


async def test_incorrect_version_get_and_put(taxi_eventus_orchestrator_web):
    await get_schema_and_check(
        taxi_eventus_orchestrator_web, 'another-instance', 500, 0,
    )

    await get_schema_and_check(
        taxi_eventus_orchestrator_web, 'another-instance-2', 500, 0,
    )

    incorrect_versions = ['asdasd', '1,2,3,4', '1.2.3.4', 'asdf.1.2']
    for incorrect in incorrect_versions:
        await put_schema(
            taxi_eventus_orchestrator_web,
            'order-events-producer',
            1,
            incorrect,
            'gmqnrk4fmwjqie6o.man.yp-c.yandex.net',
            400,
        )
