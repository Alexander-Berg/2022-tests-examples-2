import pytest


@pytest.fixture(autouse=True)
def virtual_tariffs(mockserver):
    @mockserver.json_handler('/virtual_tariffs/v1/match')
    def mock_virtual_tariffs_view(request):
        return {'virtual_tariffs': []}

    @mockserver.json_handler(
        '/virtual_tariffs/v1/special-requirements/updates',
    )
    def _special_requirements_updates(request):
        params = request.args.to_dict()
        if params.get('cursor'):
            return {
                'special_requirements': [],
                'cursor': 'cursor',
                'has_more_records': False,
            }
        return {
            'special_requirements': [
                {
                    'id': 'tag_group1',
                    'requirements': [
                        {
                            'field': 'Tags',
                            'operation': 'ContainsAll',
                            'arguments': [
                                {'value': 'tag1'},
                                {'value': 'tag2'},
                                {'value': 'tag3'},
                            ],
                        },
                    ],
                },
                {
                    'id': 'tag_group2',
                    'requirements': [
                        {
                            'field': 'Tags',
                            'operation': 'ContainsAll',
                            'arguments': [
                                {'value': 'tag1'},
                                {'value': 'tag2'},
                                {'value': 'tag3'},
                                {'value': 'tag4'},
                            ],
                        },
                    ],
                },
            ],
            'cursor': 'cursor',
            'has_more_records': False,
        }
