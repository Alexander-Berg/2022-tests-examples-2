import pytest


def default_grouped_services():
    return {
        'groups': [
            {
                'group_id': 'group_id_1',
                'text': 'description of ndd',
                'services': [
                    {
                        'service_id': 'service_id_1',
                        'text': 'description of service',
                    },
                    {
                        'service_id': 'service_id_2',
                        'text': 'description of service',
                    },
                ],
            },
            {
                'group_id': 'group_id_2',
                'text': 'description of express',
                'services': [
                    {
                        'service_id': 'service_id_1',
                        'text': 'description of service',
                    },
                    {
                        'service_id': 'service_id_2',
                        'text': 'description of service',
                    },
                ],
            },
        ],
    }


@pytest.mark.config(CARGO_TARIFFS_GROUPED_SERVICES=default_grouped_services())
async def test_list_handler(v1_tariffs_services_list):
    response = await v1_tariffs_services_list.get()
    assert response.status_code == 200
    assert response.json() == default_grouped_services()
