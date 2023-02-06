import pytest


@pytest.fixture(name='clown_namespaces')
def _clown_namespaces():
    return [{'id': 1, 'name': 'ns1'}, {'id': 2, 'name': 'ns2'}]


@pytest.fixture(name='clown_projects')
def _clown_projects():
    return [{'id': 1, 'name': 'prj-1', 'namespace_id': 1}]


@pytest.fixture(name='clown_services')
def _clown_services():
    return [
        {
            'id': 1,
            'name': 'srv-1',
            'project_id': 1,
            'cluster_type': 'nanny',
            'abc_service': 'srv-1-slug',
        },
        {
            'id': 2,
            'name': 'srv-2',
            'project_id': 1,
            'cluster_type': 'mongo',
            'abc_service': 'srv-2-slug',
        },
        {
            'id': 3,
            'name': 'srv-3',
            'project_id': 1,
            'cluster_type': 'market_service',
            'abc_service': 'srv-3-slug',
        },
    ]


SRV1_TREE = {
    'name': {'en': 'service srv-1', 'ru': 'сервис srv-1'},
    'roles': {
        'name': {'en': 'service role', 'ru': 'роль сервиса'},
        'slug': 'service_role',
        'values': {
            'subsystem_nanny': {
                'name': {
                    'en': 'NANNY subsystem roles',
                    'ru': 'роли подсистемы NANNY',
                },
                'roles': {
                    'name': {
                        'en': 'NANNY subsystem roles',
                        'ru': 'роли подсистемы NANNY',
                    },
                    'slug': 'service_subsystem_nanny',
                    'values': {
                        'nanny_root': {
                            'name': {
                                'en': 'nanny root access',
                                'ru': 'рутовый доступ в няня сервис',
                            },
                            'help': {
                                'en': 'grands owner rights to nanny service',
                                'ru': (
                                    'предоставляет уровень доступа owner '
                                    'в няня сервис'
                                ),
                            },
                            'set': 'subsystem_nanny-nanny_root',
                            'unique_id': 'srv-1-subsystem_nanny-nanny_root',
                            'visible': True,
                        },
                    },
                },
            },
            'subsystem_internal': {
                'name': {
                    'en': 'INTERNAL subsystem roles',
                    'ru': 'роли подсистемы INTERNAL',
                },
                'roles': {
                    'name': {
                        'en': 'INTERNAL subsystem roles',
                        'ru': 'роли подсистемы INTERNAL',
                    },
                    'slug': 'service_subsystem_internal',
                    'values': {
                        'deploy_approve': {
                            'name': {
                                'en': 'deploy approve',
                                'ru': 'ок выкатки',
                            },
                            'help': {
                                'en': 'Allows to approve release',
                                'ru': 'Даёт право на аппрув релиза',
                            },
                            'set': 'subsystem_internal-deploy_approve',
                            'unique_id': (
                                'srv-1-subsystem_internal-deploy_approve'
                            ),
                            'visible': True,
                            'fields': [
                                {
                                    'name': {
                                        'en': 'Inner name',
                                        'ru': 'Имя внутри системы',
                                    },
                                    'required': False,
                                    'slug': 'inner_name',
                                    'type': 'charfield',
                                },
                            ],
                        },
                    },
                },
            },
            'tmp_common_role': {
                'name': {'en': 'tmp_common_role', 'ru': 'tmp_common_role'},
                'help': {'en': 'tmp_common_role', 'ru': 'tmp_common_role'},
                'set': 'tmp_common_role',
                'unique_id': 'srv-1-tmp_common_role',
                'visible': True,
            },
        },
    },
    'unique_id': 'srv-1',
}
SRV3_TREE = {
    'name': {'en': 'service srv-3', 'ru': 'сервис srv-3'},
    'roles': {
        'name': {'en': 'service role', 'ru': 'роль сервиса'},
        'slug': 'service_role',
        'values': {
            'subsystem_nanny': {
                'name': {
                    'en': 'NANNY subsystem roles',
                    'ru': 'роли подсистемы NANNY',
                },
                'roles': {
                    'name': {
                        'en': 'NANNY subsystem roles',
                        'ru': 'роли подсистемы NANNY',
                    },
                    'slug': 'service_subsystem_nanny',
                    'values': {
                        'nanny_root': {
                            'name': {
                                'en': 'nanny root access',
                                'ru': 'рутовый доступ в няня сервис',
                            },
                            'help': {
                                'en': 'grands owner rights to nanny service',
                                'ru': (
                                    'предоставляет уровень доступа owner '
                                    'в няня сервис'
                                ),
                            },
                            'set': 'subsystem_nanny-nanny_root',
                            'unique_id': 'srv-3-subsystem_nanny-nanny_root',
                            'visible': True,
                        },
                        'nanny_invisible': {
                            'name': {'en': '', 'ru': ''},
                            'help': {'en': '', 'ru': ''},
                            'set': 'subsystem_nanny-nanny_invisible',
                            'unique_id': (
                                'srv-3-subsystem_nanny-nanny_invisible'
                            ),
                            'visible': False,
                        },
                    },
                },
            },
            'subsystem_market': {
                'name': {
                    'en': 'MARKET subsystem roles',
                    'ru': 'роли подсистемы MARKET',
                },
                'roles': {
                    'name': {
                        'en': 'MARKET subsystem roles',
                        'ru': 'роли подсистемы MARKET',
                    },
                    'slug': 'service_subsystem_market',
                    'values': {
                        'market_view': {
                            'name': {
                                'en': 'tsum view access',
                                'ru': 'доступ на просмотр к цуму',
                            },
                            'help': {
                                'en': 'grants view rights to tsum service',
                                'ru': 'предоставляет доступ на просмотр в цум',
                            },
                            'set': 'subsystem_market-market_view',
                            'unique_id': 'srv-3-subsystem_market-market_view',
                            'visible': True,
                        },
                    },
                },
            },
            'tmp_common_role': {
                'name': {'en': 'tmp_common_role', 'ru': 'tmp_common_role'},
                'help': {'en': 'tmp_common_role', 'ru': 'tmp_common_role'},
                'set': 'tmp_common_role',
                'unique_id': 'srv-3-tmp_common_role',
                'visible': True,
            },
        },
    },
    'unique_id': 'srv-3',
}
PRJ1_TREE = {
    'name': {'en': 'project PRJ-1', 'ru': 'проект PRJ-1'},
    'roles': {
        'name': {'en': 'project role', 'ru': 'роль на проект'},
        'slug': 'project_role',
        'values': {
            'service_roles': {
                'name': {'en': 'service role', 'ru': 'сервисная роль'},
                'roles': {
                    'name': {'en': 'service role', 'ru': 'сервисная роль'},
                    'slug': 'service',
                    'values': {'srv-1': SRV1_TREE, 'srv-3': SRV3_TREE},
                },
            },
            'subsystem_nanny': {
                'name': {
                    'en': 'NANNY subsystem roles',
                    'ru': 'роли подсистемы NANNY',
                },
                'roles': {
                    'name': {
                        'en': 'NANNY subsystem roles',
                        'ru': 'роли подсистемы NANNY',
                    },
                    'slug': 'project_subsystem_nanny',
                    'values': {
                        'nanny_root': {
                            'name': {
                                'en': 'nanny root access',
                                'ru': 'рутовый доступ в няня сервис',
                            },
                            'help': {
                                'en': 'grands owner rights to nanny service',
                                'ru': (
                                    'предоставляет уровень доступа owner '
                                    'в няня сервис'
                                ),
                            },
                            'set': 'subsystem_nanny-nanny_root',
                            'unique_id': 'prj-1-subsystem_nanny-nanny_root',
                            'visible': True,
                        },
                    },
                },
            },
            'subsystem_internal': {
                'name': {
                    'en': 'INTERNAL subsystem roles',
                    'ru': 'роли подсистемы INTERNAL',
                },
                'roles': {
                    'name': {
                        'en': 'INTERNAL subsystem roles',
                        'ru': 'роли подсистемы INTERNAL',
                    },
                    'slug': 'project_subsystem_internal',
                    'values': {
                        'deploy_approve': {
                            'name': {
                                'en': 'deploy approve',
                                'ru': 'ок выкатки',
                            },
                            'help': {
                                'en': 'Allows to approve release',
                                'ru': 'Даёт право на аппрув релиза',
                            },
                            'set': 'subsystem_internal-deploy_approve',
                            'unique_id': (
                                'prj-1-subsystem_internal-deploy_approve'
                            ),
                            'visible': True,
                        },
                    },
                },
            },
        },
    },
    'unique_id': 'prj-1',
}
NS1_TREE = {
    'name': {'en': 'namespace NS1', 'ru': 'неймспейс NS1'},
    'roles': {
        'name': {'en': 'namespace role', 'ru': 'роль на неймспейс'},
        'slug': 'namespace_role',
        'values': {
            'project_roles': {
                'name': {'en': 'project role', 'ru': 'роль на проект'},
                'roles': {
                    'name': {'en': 'project role', 'ru': 'роль на проект'},
                    'slug': 'project',
                    'values': {'prj-1': PRJ1_TREE},
                },
            },
            'subsystem_nanny': {
                'name': {
                    'en': 'NANNY subsystem roles',
                    'ru': 'роли подсистемы NANNY',
                },
                'roles': {
                    'name': {
                        'en': 'NANNY subsystem roles',
                        'ru': 'роли подсистемы NANNY',
                    },
                    'slug': 'namespace_subsystem_nanny',
                    'values': {
                        'nanny_root': {
                            'name': {
                                'en': 'nanny root access',
                                'ru': 'рутовый доступ в няня сервис',
                            },
                            'help': {
                                'en': 'grands owner rights to nanny service',
                                'ru': (
                                    'предоставляет уровень доступа owner '
                                    'в няня сервис'
                                ),
                            },
                            'set': 'subsystem_nanny-nanny_root',
                            'unique_id': 'ns1-subsystem_nanny-nanny_root',
                            'visible': True,
                        },
                    },
                },
            },
        },
    },
    'unique_id': 'ns-1',
}
NS2_TREE = {
    'name': {'en': 'namespace NS2', 'ru': 'неймспейс NS2'},
    'roles': {
        'name': {'en': 'namespace role', 'ru': 'роль на неймспейс'},
        'slug': 'namespace_role',
        'values': {
            'subsystem_nanny': {
                'name': {
                    'en': 'NANNY subsystem roles',
                    'ru': 'роли подсистемы NANNY',
                },
                'roles': {
                    'name': {
                        'en': 'NANNY subsystem roles',
                        'ru': 'роли подсистемы NANNY',
                    },
                    'slug': 'namespace_subsystem_nanny',
                    'values': {
                        'nanny_root': {
                            'name': {
                                'en': 'nanny root access',
                                'ru': 'рутовый доступ в няня сервис',
                            },
                            'help': {
                                'en': 'grands owner rights to nanny service',
                                'ru': (
                                    'предоставляет уровень доступа owner '
                                    'в няня сервис'
                                ),
                            },
                            'set': 'subsystem_nanny-nanny_root',
                            'unique_id': 'ns2-subsystem_nanny-nanny_root',
                            'visible': True,
                        },
                    },
                },
            },
        },
    },
    'unique_id': 'ns-2',
}
SOME_ABC_SERVICE_NS = {
    'name': {
        'en': 'SOME_ABC_SERVICE standalone abc roles',
        'ru': 'роли отдельного abc сервиса SOME_ABC_SERVICE',
    },
    'roles': {
        'name': {
            'en': 'SOME_ABC_SERVICE standalone abc roles',
            'ru': 'роли отдельного abc сервиса SOME_ABC_SERVICE',
        },
        'slug': 'standalone_subsystem_some_abc_service',
        'values': {
            'subsystem_stq': {
                'name': {
                    'en': 'STQ subsystem roles',
                    'ru': 'роли подсистемы STQ',
                },
                'roles': {
                    'name': {
                        'en': 'STQ subsystem roles',
                        'ru': 'роли подсистемы STQ',
                    },
                    'slug': 'standalone_subsystem_stq',
                    'values': {
                        'queue_change_approve': {
                            'help': {'en': 'en help', 'ru': 'ru help'},
                            'name': {'en': 'en name', 'ru': 'ru name'},
                            'set': 'subsystem_stq-queue_change_approve',
                            'unique_id': (
                                'some_abc_service-subsystem_stq-'
                                'queue_change_approve'
                            ),
                            'visible': True,
                        },
                    },
                },
            },
        },
    },
    'unique_id': 'some_abc_service',
}


async def test_handler(
        taxi_clowny_roles_web, add_abc_scope, add_subsystem, add_role,
):
    nanny_id = await add_subsystem('nanny')
    nanny_root_name = ('nanny root access', 'рутовый доступ в няня сервис')
    nanny_root_help = (
        'grands owner rights to nanny service',
        'предоставляет уровень доступа owner в няня сервис',
    )
    await add_role(
        'nanny_root',
        'ns1',
        'namespace',
        nanny_id,
        nanny_root_name,
        nanny_root_help,
    )
    await add_role(
        'nanny_root',
        'ns2',
        'namespace',
        nanny_id,
        nanny_root_name,
        nanny_root_help,
    )
    await add_role(
        'nanny_root',
        'prj-1',
        'project',
        nanny_id,
        nanny_root_name,
        nanny_root_help,
    )
    await add_role(
        'nanny_root',
        'srv-1-slug',
        'service',
        nanny_id,
        nanny_root_name,
        nanny_root_help,
    )
    await add_role(
        'nanny_root',
        'srv-3-slug',
        'service',
        nanny_id,
        nanny_root_name,
        nanny_root_help,
    )
    await add_role(
        'nanny_invisible',
        'srv-3-slug',
        'service',
        nanny_id,
        ('', ''),
        ('', ''),
        visible=False,
    )
    internal_id = await add_subsystem('internal')
    deploy_name = ('deploy approve', 'ок выкатки')
    deploy_help = ('Allows to approve release', 'Даёт право на аппрув релиза')
    await add_role(
        'deploy_approve',
        'prj-1',
        'project',
        internal_id,
        deploy_name,
        deploy_help,
    )
    await add_role(
        'deploy_approve',
        'srv-1-slug',
        'service',
        internal_id,
        deploy_name,
        deploy_help,
        [
            {
                'slug': 'inner_name',
                'name': {'ru': 'Имя внутри системы', 'en': 'Inner name'},
                'type': 'charfield',
                'required': False,
            },
        ],
    )
    market_id = await add_subsystem('market')
    market_name = ('tsum view access', 'доступ на просмотр к цуму')
    market_help = (
        'grants view rights to tsum service',
        'предоставляет доступ на просмотр в цум',
    )
    await add_role(
        'market_view',
        'srv-3-slug',
        'service',
        market_id,
        market_name,
        market_help,
    )
    abc_scope_id = await add_abc_scope('some_abc_service')
    stq_id = await add_subsystem('stq')
    await add_role(
        'queue_change_approve',
        abc_scope_id,
        'standalone',
        stq_id,
        ('en name', 'ru name'),
        ('en help', 'ru help'),
    )

    await add_role('tmp_common_role', 'srv-1-slug', 'service', None)
    await add_role('tmp_common_role', 'srv-3-slug', 'service', None)

    response = await taxi_clowny_roles_web.get('/idm/v1/info/')
    assert response.status == 200, await response.text()
    result = await response.json()
    assert result['roles']['values']['ns1'] == NS1_TREE
    assert result['roles']['values']['ns2'] == NS2_TREE
    assert result['roles']['values']['some_abc_service'] == SOME_ABC_SERVICE_NS
