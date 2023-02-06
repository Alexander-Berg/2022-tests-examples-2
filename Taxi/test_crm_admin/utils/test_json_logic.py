from crm_admin.utils import json_logic


async def test_json_logic():

    ultimate_test = {
        'merge': [
            {
                '+': [
                    {
                        'and': [
                            {'==': [0, {'var': 'equal_test.0'}]},
                            {'!=': [0, {'var': 'equal_test.1'}]},
                        ],
                    },
                    {
                        'or': [
                            {'<': [1, {'var': 'less_test'}, 0]},
                            {
                                'all': [
                                    {'var': 'all_test'},
                                    {
                                        '>': [
                                            {
                                                'reduce': [
                                                    {'var': 'values'},
                                                    {
                                                        '*': [
                                                            {'var': 'current'},
                                                            {
                                                                'var': 'accumulator',  # noqa: E501
                                                            },
                                                        ],
                                                    },
                                                    1,
                                                ],
                                            },
                                            -1,
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            {'map': [{'var': 'integers'}, {'*': [{'var': ''}, 2]}]},
        ],
    }

    ultimate_data = {
        'equal_test': [0, 1],
        'less_test': 2,
        'all_test': [{'values': [3, 2, 0]}, {'values': [6, 5, 4]}],
        'integers': [1, 2, 3, 4, 5],
    }

    assert json_logic.json_logic(ultimate_test, ultimate_data) == [
        2,
        2,
        4,
        6,
        8,
        10,
    ]
