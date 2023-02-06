# pylint: disable=invalid-name
# flake8: noqa


async def test_commit(web_context, web_app_client):
    data = {
        'definitions': {
            'logging/LOG_LEVEL_SETTINGS.yaml': {
                'log': {
                    'type': 'array',
                    'additionalProperties': False,
                    'items': {
                        'type': 'object',
                        'properties': {
                            'level': {
                                'type': 'string',
                                'description': 'Logging level in service',
                            },
                            'type': {
                                'type': 'string',
                                'description': (
                                    'The place to change logging level'
                                ),
                            },
                        },
                        'required': ['level', 'type'],
                    },
                },
            },
        },
        'actual_commit': 'bbb',
        'new_commit': 'ccc',
    }

    response = await web_app_client.post(
        '/v1/schemas/definitions/',
        headers={'X-YaTaxi-Api-Key': 'secret'},
        json=data,
    )

    assert response.status == 200

    data = {
        'definitions': {
            'logging/LOG_LEVEL_SETTINGS.yaml': {
                'log': {
                    'type': 'array',
                    'additionalProperties': False,
                    'items': {
                        'type': 'object',
                        'properties': {
                            'level': {
                                'type': 'string',
                                'description': 'Logging level in service',
                            },
                            'type': {
                                'type': 'string',
                                'description': (
                                    'The place to change logging level'
                                ),
                            },
                        },
                        'required': ['level', 'type'],
                    },
                },
            },
        },
        'actual_commit': 'ccc',
        'new_commit': 'ddd',
    }

    response = await web_app_client.post(
        '/v1/schemas/definitions/',
        headers={'X-YaTaxi-Api-Key': 'secret'},
        json=data,
    )

    assert response.status == 200
