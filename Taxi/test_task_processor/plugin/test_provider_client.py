import pytest


@pytest.mark.config(
    TVM_RULES=[{'src': 'task-processor', 'dst': 'clownductor'}],
)
@pytest.mark.pgsql('task_processor', files=['test_provider_client.sql'])
async def test_get_provider_cubes(
        web_context, get_providers, add_providers, mock_provider_client,
):
    @mock_provider_client('/task-processor/v1/cubes/')
    # pylint: disable=unused-variable
    def handler(request):
        return {
            'cubes': [
                {
                    'name': 'testCube',
                    'needed_parameters': ['test'],
                    'optional_parameters': ['optional'],
                },
            ],
        }

    await add_providers('test', 123, 'test')
    provider = await get_providers(1)
    provider_cubes = await web_context.provider_client.get_provider_cubes(
        provider,
    )
    assert provider_cubes == [
        {
            'name': 'testCube',
            'needed_parameters': ['test'],
            'optional_parameters': ['optional'],
        },
    ]
