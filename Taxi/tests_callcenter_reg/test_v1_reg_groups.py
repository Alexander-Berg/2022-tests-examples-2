import pytest


@pytest.mark.parametrize(
    ('group_filter', 'project', 'expected'),
    (
        (
            None,
            None,
            {
                'reg_groups': [
                    {
                        'group_name': 'ru',
                        'regs': ['reg_1', 'reg_2'],
                        'reg_domain': 'yandex.ru',
                    },
                    {
                        'group_name': 'kz',
                        'regs': ['reg_3', 'reg_4'],
                        'reg_domain': 'yandex.ru',
                    },
                    {
                        'group_name': 'by',
                        'regs': ['reg_5', 'reg_6'],
                        'reg_domain': 'yandex.ru',
                    },
                ],
            },
        ),
        (
            None,
            'disp',
            {
                'reg_groups': [
                    {
                        'group_name': 'ru',
                        'regs': ['reg_1', 'reg_2'],
                        'reg_domain': 'yandex.ru',
                    },
                    {
                        'group_name': 'by',
                        'regs': ['reg_5', 'reg_6'],
                        'reg_domain': 'yandex.ru',
                    },
                ],
            },
        ),
        ([], None, {'reg_groups': []}),
        (
            ['ru'],
            None,
            {
                'reg_groups': [
                    {
                        'group_name': 'ru',
                        'regs': ['reg_1', 'reg_2'],
                        'reg_domain': 'yandex.ru',
                    },
                ],
            },
        ),
        (
            ['ru'],
            'disp',
            {
                'reg_groups': [
                    {
                        'group_name': 'ru',
                        'regs': ['reg_1', 'reg_2'],
                        'reg_domain': 'yandex.ru',
                    },
                ],
            },
        ),
    ),
)
@pytest.mark.config(
    CALLCENTER_REG_REG_GROUPS={
        'reg_groups': [
            {
                'group_name': 'ru',
                'regs': ['reg_1', 'reg_2'],
                'reg_domain': 'yandex.ru',
            },
            {
                'group_name': 'kz',
                'regs': ['reg_3', 'reg_4'],
                'reg_domain': 'yandex.ru',
            },
            {
                'group_name': 'by',
                'regs': ['reg_5', 'reg_6'],
                'reg_domain': 'yandex.ru',
            },
        ],
    },
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'disp': {
            'metaqueues': ['ru_taxi_disp'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru', 'by'],
        },
        'support': {
            'metaqueues': ['ru_taxi_support'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': ['kz'],
        },
    },
)
async def test_v1_reg_groups(
        taxi_callcenter_reg, group_filter, project, expected,
):
    response = await taxi_callcenter_reg.post(
        '/v1/reg_groups',
        {'project': project, 'reg_group_filter': group_filter},
    )
    # check ok scenario
    assert response.status_code == 200
    assert response.json() == expected
