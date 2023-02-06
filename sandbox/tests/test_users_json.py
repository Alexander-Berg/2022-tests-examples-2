# -*- coding: utf-8 -*-

from datetime import datetime

from sandbox.projects.yabs.SysConstLifetime.sys_const.users_json_helper import UsersJsonHelper


def test_update_users():
    '''
        Check-list:

        1) Если юзера из abc нет в users.json, то он добавится в users.json
        2) Если у юзера не пустой список дат, но он есть в abc, то обнулять список дат
        3) Если юзера нет в abc, то в users.json в days_without_abc...
            a) если нет дат, то добавится текущая
            b) если текущая дата сопадает с последней, то ничего не произойдёт
            c) если у него 10 дат, то произойдет сдвиг дат влево и добавится текущая дата
        4) Если у юзера рук из staff отличается от последнего в leaders, то он добавится в leaders
        5) Если у юзера groupID из staff отличается от id last group, то добавится новая группа
        6) Если у группы юзера в staff поменялась url или name, но groupID не отличается от id last group,
        то у последней группы поменяются url и name

        If key is user<num> then num is point of check-list
    '''

    MAX_DATES_WITHOUT_ABC_COUNT = 10

    current_date = datetime.now().strftime('%Y-%m-%d')

    users = {
        'user2': {
            'leaders': [
                'leader1'
            ],
            'groups': [
                {
                    'id': 1,
                    'url': 'url1',
                    'name': 'name1'
                }
            ],
            'days_without_abc': [
                '2021-03-01',
                '2021-03-02'
            ]
        },
        'user3A': {
            'leaders': [
                'leader1'
            ],
            'groups': [
                {
                    'id': 1,
                    'url': 'url1',
                    'name': 'name1'
                }
            ],
            'days_without_abc': []
        },
        'user3B': {
            'leaders': [
                'leader1'
            ],
            'groups': [
                {
                    'id': 1,
                    'url': 'url1',
                    'name': 'name1'
                }
            ],
            'days_without_abc': [
                '2021-03-01',
                '2021-03-02',
                current_date
            ]
        },
        'user3C': {
            'leaders': [
                'leader1'
            ],
            'groups': [
                {
                    'id': 1,
                    'url': 'url1',
                    'name': 'name1'
                }
            ],
            'days_without_abc': [
                '2021-03-01',
                '2021-03-02',
                '2021-03-03',
                '2021-03-04',
                '2021-03-05',
                '2021-03-06',
                '2021-03-07',
                '2021-03-08',
                '2021-03-09',
                '2021-03-10'
            ]
        },
        'user_new_leader': {
            'leaders': [
                'leader1'
            ],
            'groups': [
                {
                    'id': 1,
                    'url': 'url1',
                    'name': 'name1'
                }
            ],
            'days_without_abc': []
        },
        'user_new_group': {
            'leaders': [
                'leader1'
            ],
            'groups': [
                {
                    'id': 1,
                    'url': 'url1',
                    'name': 'name1'
                }
            ],
            'days_without_abc': []
        },
        'user_change_group': {
            'leaders': [
                'leader1'
            ],
            'groups': [
                {
                    'id': 1,
                    'url': 'url1',
                    'name': 'name1'
                }
            ],
            'days_without_abc': []
        },
        'user_mix': {
            'leaders': [
                'leader1',
                'leader2'
            ],
            'groups': [
                {
                    'id': 1,
                    'url': 'url1',
                    'name': 'name1'
                },
                {
                    'id': 2,
                    'url': 'url2',
                    'name': 'name2'
                }
            ],
            'days_without_abc': [
                '2020-03-01',
                '2020-03-02'
            ]
        }
    }

    staff_users_dict = {
        'user_new': {
            'leader': 'leader_new',
            'group': {
                'id': 1,
                'url': 'url_new',
                'name': 'name_new'
            }
        },
        'user2': {
            'leader': 'leader_return',
            'group': {
                'id': 2,
                'url': 'url_return',
                'name': 'name_return'
            }
        },
        'user_new_leader': {
            'leader': 'leader2',
            'group': {
                'id': 1,
                'url': 'url1',
                'name': 'name1'
            }
        },
        'user_new_group': {
            'leader': 'leader1',
            'group': {
                'id': 2,
                'url': 'url2',
                'name': 'name2'
            }
        },
        'user_change_group': {
            'leader': 'leader1',
            'group': {
                'id': 1,
                'url': 'url_change',
                'name': 'name_change'
            }
        },
        'user_mix': {
            'leader': 'leader3',
            'group': {
                'id': 3,
                'url': 'url3',
                'name': 'name3'
            }
        }
    }

    users_json_helper = UsersJsonHelper(
        users_local_path=None,
        staff_client=None,
        arcadia_helper=None,
        abc_client=None,
        dry_run=True
    )

    users_json_helper.update_users(users, staff_users_dict)

    assert len(users) == 9

    assert users['user_new']

    assert len(users['user2']['days_without_abc']) == 0

    assert len(users['user3A']['days_without_abc']) == 1

    assert users['user3A']['days_without_abc'][-1] == current_date

    assert len(users['user3B']['days_without_abc']) == 3

    assert users['user3B']['days_without_abc'][0] == '2021-03-01'

    assert users['user3B']['days_without_abc'][-1] == current_date

    assert len(users['user3C']['days_without_abc']) == MAX_DATES_WITHOUT_ABC_COUNT

    assert users['user3C']['days_without_abc'][0] == '2021-03-02'

    assert users['user3C']['days_without_abc'][-1] == current_date

    assert len(users['user_new_leader']['leaders']) == 2

    assert users['user_new_leader']['leaders'][-1] == 'leader2'

    assert len(users['user_new_group']['groups']) == 2

    assert users['user_new_group']['groups'][-1]['id'] == 2

    assert len(users['user_change_group']['groups']) == 1

    assert users['user_change_group']['groups'][0]['id'] == 1

    assert users['user_change_group']['groups'][0]['url'] == 'url_change'

    assert users['user_change_group']['groups'][0]['name'] == 'name_change'

    assert len(users['user_mix']['leaders']) == 3

    assert len(users['user_mix']['groups']) == 3

    assert len(users['user_mix']['days_without_abc']) == 0

    assert users['user_mix']['leaders'][-1] == 'leader3'

    assert users['user_mix']['groups'][-1]['id'] == 3
