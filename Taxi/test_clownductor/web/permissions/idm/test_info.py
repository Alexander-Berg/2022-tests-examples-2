def deploy_approve_programmer(unique_id: str, visible=True):
    return {
        'help': {
            'en': 'Allows to approve release by developer',
            'ru': 'Даёт право на аппрув релиза разработчиком',
        },
        'name': {
            'en': 'deploy approve by developer',
            'ru': 'ок выкатки разработчика',
        },
        'set': 'deploy_approve_programmer',
        'unique_id': unique_id,
        'visible': visible,
    }


def deploy_approve_manager(unique_id: str, visible=True):
    return {
        'help': {
            'en': 'Allows to approve release by manager',
            'ru': 'Даёт право на аппрув релиза менеджером',
        },
        'name': {
            'en': 'deploy approve by manager',
            'ru': 'ок выкатки менеджера',
        },
        'set': 'deploy_approve_manager',
        'unique_id': unique_id,
        'visible': visible,
    }


def deploy_approve_sandbox_dev(unique_id: str, visible=True):
    return {
        'help': {
            'en': 'Allows to approve sandbox resource release by developer',
            'ru': 'Даёт право на аппрув sandbox-ресурса разработчиком',
        },
        'name': {
            'en': 'deploy approve for sandbox resource by developer',
            'ru': 'ок выкатки sandbox ресурса разработчиком',
        },
        'set': 'deploy_approve_sandbox_programmer',
        'unique_id': unique_id,
        'visible': visible,
    }


def nanny_admin_prod(unique_id: str, visible=True):
    return {
        'help': {
            'en': 'Gives admin role in nanny service (in stable)',
            'ru': 'Выдаёт в няня сервисе админские права (в продакшене)',
        },
        'name': {
            'en': 'admin rights to nanny service (stable)',
            'ru': 'админский доступ в няня сервис (продакшен)',
        },
        'set': 'nanny_admin_prod',
        'unique_id': unique_id,
        'visible': visible,
    }


def strongbox_secrets_prod(unique_id: str, visible=True):
    return {
        'name': {
            'ru': 'доступ на редактирование секретов (продакшен)',
            'en': 'access to change secrets (stable)',
        },
        'help': {
            'ru': (
                'Выдаёт права для создания и '
                'редактирования секретов (в продакшене)'
            ),
            'en': 'Gives rights to change secrets (in stable)',
        },
        'set': 'strongbox_secrets_prod',
        'unique_id': unique_id,
        'visible': visible,
    }


def strongbox_secrets_testing(unique_id: str, visible=True):
    return {
        'name': {
            'ru': 'доступ на редактирование секретов (тестинг)',
            'en': 'access to change secrets (testing)',
        },
        'help': {
            'ru': (
                'Выдаёт права для создания и '
                'редактирования секретов (в тестинге)'
            ),
            'en': 'Gives rights to change secrets (in testing)',
        },
        'set': 'strongbox_secrets_testing',
        'unique_id': unique_id,
        'visible': visible,
    }


def strongbox_secrets_creation(unique_id: str, visible=True):
    return {
        'name': {
            'ru': 'доступ на создание секретов',
            'en': 'access to create secrets',
        },
        'help': {
            'ru': 'Выдаёт права для создания секретов во всех окружениях',
            'en': 'Gives rights to create secrets in all environments',
        },
        'set': 'strongbox_secrets_creation',
        'unique_id': unique_id,
        'visible': visible,
    }


def nanny_admin_testing(unique_id: str, visible=True):
    return {
        'help': {
            'en': 'Gives admin role in nanny service (in testing)',
            'ru': 'Выдаёт в няня сервисе админские права (в тестинге)',
        },
        'name': {
            'en': 'admin rights to nanny service (testing)',
            'ru': 'админский доступ в няня сервис (тестинг)',
        },
        'set': 'nanny_admin_testing',
        'unique_id': unique_id,
        'visible': visible,
    }


def granded(uniq_id: str, visible=True):
    return {
        'help': {
            'en': 'Gives permission to approve new roles for project',
            'ru': 'Даёт право на аппрув выдачи ролей данного проекта',
        },
        'name': {'en': 'granded for project', 'ru': 'ответственный за проект'},
        'set': 'granded',
        'unique_id': uniq_id,
        'visible': visible,
    }


def mdb_cluster_ro_access(uniq_id: str, visible=True):
    return {
        'help': {
            'en': (
                'Grants ro access to mdb cluster, '
                'it allows you to view base cluster info, '
                'monitoring in YC interface'
            ),
            'ru': (
                'Выдаёт доступ на кластер mdb, '
                'который позволяет просматривать базовую '
                'информацию о кластере, '
                'а также его мониторинги в интерфейсе yc'
            ),
        },
        'name': {
            'en': 'ro accesses for mdb cluster',
            'ru': 'доступ на чтение до mdb кластера баз',
        },
        'set': 'mdb_cluster_ro_access',
        'unique_id': uniq_id,
        'visible': visible,
    }


def nanny_developer(uniq_id: str, visible=True):
    return {
        'help': {
            'en': (
                'Grants developer role to nanny service. '
                'This role allows to use non-root ssh.'
            ),
            'ru': (
                'Выдаёт роль developer в няня сервисе. '
                'Роль даёт не рутовый ssh доступ к сервису.'
            ),
        },
        'name': {
            'en': 'developer access to nanny service',
            'ru': 'разработческий доступ к няня сервису',
        },
        'set': 'nanny_developer',
        'unique_id': uniq_id,
        'visible': visible,
    }


def nanny_evicter(uniq_id: str, visible=True):
    return {
        'help': {
            'en': (
                'Grants evicter role to nanny service. '
                'This role allows to use pods eviction.'
            ),
            'ru': (
                'Выдаёт роль evicter в няня сервисе. '
                'Роль даёт доступ к эвакуации подов.'
            ),
        },
        'name': {
            'en': 'access to nanny service pods eviction',
            'ru': 'доступ к эвакуации подов няня сервиса',
        },
        'set': 'nanny_evicter',
        'unique_id': uniq_id,
        'visible': visible,
    }


SUPERS = {
    'name': {'en': 'All projects roles', 'ru': 'Роли на все проекты'},
    'roles': {
        'name': {'en': 'All projects role', 'ru': 'Роль на все проекты'},
        'slug': 'super_role',
        'values': {
            'deploy_approve_manager': deploy_approve_manager(
                'super-deploy_approve_manager',
            ),
            'deploy_approve_programmer': deploy_approve_programmer(
                'super-deploy_approve_programmer',
            ),
            'deploy_approve_sandbox_programmer': (
                deploy_approve_sandbox_dev(
                    'super-deploy_approve_sandbox_programmer',
                )
            ),
            'nanny_admin_prod': nanny_admin_prod('super-nanny_admin_prod'),
            'nanny_admin_testing': nanny_admin_testing(
                'super-nanny_admin_testing',
            ),
            'strongbox_secrets_prod': strongbox_secrets_prod(
                'super-strongbox_secrets_prod',
            ),
            'strongbox_secrets_testing': strongbox_secrets_testing(
                'super-strongbox_secrets_testing',
            ),
            'strongbox_secrets_creation': strongbox_secrets_creation(
                'super-strongbox_secrets_creation',
            ),
            'mdb_cluster_ro_access': mdb_cluster_ro_access(
                'super-mdb_cluster_ro_access',
            ),
            'nanny_developer': nanny_developer('super-nanny_developer'),
            'nanny_evicter': nanny_evicter('super-nanny_evicter'),
        },
    },
}
EDA = {
    'name': {'en': 'project EDA', 'ru': 'проект EDA'},
    'roles': {
        'name': {'en': 'project role', 'ru': 'проектная роль'},
        'slug': 'project_role',
        'values': {
            'deploy_approve_manager': deploy_approve_manager(
                'prj-2-deploy_approve_manager',
            ),
            'deploy_approve_programmer': deploy_approve_programmer(
                'prj-2-deploy_approve_programmer',
            ),
            'deploy_approve_sandbox_programmer': (
                deploy_approve_sandbox_dev(
                    'prj-2-deploy_approve_sandbox_programmer',
                )
            ),
            'granded': granded('prj-2-granded'),
            'strongbox_secrets_prod': strongbox_secrets_prod(
                'prj-2-strongbox_secrets_prod',
            ),
            'strongbox_secrets_testing': strongbox_secrets_testing(
                'prj-2-strongbox_secrets_testing',
            ),
            'strongbox_secrets_creation': strongbox_secrets_creation(
                'prj-2-strongbox_secrets_creation',
            ),
            'nanny_admin_prod': nanny_admin_prod('prj-2-nanny_admin_prod'),
            'nanny_admin_testing': nanny_admin_testing(
                'prj-2-nanny_admin_testing',
            ),
            'mdb_cluster_ro_access': mdb_cluster_ro_access(
                'prj-2-mdb_cluster_ro_access',
            ),
            'nanny_developer': nanny_developer('prj-2-nanny_developer'),
            'nanny_evicter': nanny_evicter('prj-2-nanny_evicter'),
        },
    },
    'unique_id': 'prj-2',
}
CLOWN = {
    'name': {'en': 'clownductor', 'ru': 'clownductor'},
    'roles': {
        'name': {'en': 'service role', 'ru': 'сервисная роль'},
        'slug': 'service_role',
        'values': {
            'deploy_approve_manager': deploy_approve_manager(
                'srv-1-deploy_approve_manager',
            ),
            'deploy_approve_programmer': deploy_approve_programmer(
                'srv-1-deploy_approve_programmer',
            ),
            'deploy_approve_sandbox_programmer': (
                deploy_approve_sandbox_dev(
                    'srv-1-deploy_approve_sandbox_programmer',
                )
            ),
            'nanny_admin_prod': nanny_admin_prod('srv-1-nanny_admin_prod'),
            'nanny_admin_testing': nanny_admin_testing(
                'srv-1-nanny_admin_testing',
            ),
            'strongbox_secrets_prod': strongbox_secrets_prod(
                'srv-1-strongbox_secrets_prod',
            ),
            'strongbox_secrets_testing': strongbox_secrets_testing(
                'srv-1-strongbox_secrets_testing',
            ),
            'strongbox_secrets_creation': strongbox_secrets_creation(
                'srv-1-strongbox_secrets_creation',
            ),
            'mdb_cluster_ro_access': mdb_cluster_ro_access(
                'srv-1-mdb_cluster_ro_access',
            ),
            'nanny_developer': nanny_developer('srv-1-nanny_developer'),
            'nanny_evicter': nanny_evicter('srv-1-nanny_evicter'),
        },
    },
    'unique_id': 'srv-1',
}
TAXI = {
    'name': {'en': 'project TAXI', 'ru': 'проект TAXI'},
    'roles': {
        'name': {'en': 'project role', 'ru': 'проектная роль'},
        'slug': 'project_role',
        'values': {
            'deploy_approve_manager': deploy_approve_manager(
                'prj-1-deploy_approve_manager',
            ),
            'deploy_approve_programmer': deploy_approve_programmer(
                'prj-1-deploy_approve_programmer',
            ),
            'deploy_approve_sandbox_programmer': (
                deploy_approve_sandbox_dev(
                    'prj-1-deploy_approve_sandbox_programmer',
                )
            ),
            'strongbox_secrets_prod': strongbox_secrets_prod(
                'prj-1-strongbox_secrets_prod',
            ),
            'strongbox_secrets_testing': strongbox_secrets_testing(
                'prj-1-strongbox_secrets_testing',
            ),
            'strongbox_secrets_creation': strongbox_secrets_creation(
                'prj-1-strongbox_secrets_creation',
            ),
            'granded': granded('prj-1-granded'),
            'nanny_admin_prod': nanny_admin_prod('prj-1-nanny_admin_prod'),
            'nanny_admin_testing': nanny_admin_testing(
                'prj-1-nanny_admin_testing',
            ),
            'mdb_cluster_ro_access': mdb_cluster_ro_access(
                'prj-1-mdb_cluster_ro_access',
            ),
            'nanny_developer': nanny_developer('prj-1-nanny_developer'),
            'nanny_evicter': nanny_evicter('prj-1-nanny_evicter'),
            'services_roles': {
                'name': {'en': 'service role', 'ru': 'сервисная роль'},
                'roles': {
                    'name': {'en': 'service role', 'ru': 'сервисная роль'},
                    'slug': 'service',
                    'values': {'clownductor': CLOWN},
                },
            },
        },
    },
    'unique_id': 'prj-1',
}


async def test_handler(web_app_client):
    response = await web_app_client.get(
        '/permissions/v1/idm/info/', headers={'X-IDM-Request-Id': 'abc'},
    )
    assert response.status == 200
    assert (await response.json()) == {
        'code': 0,
        'roles': {
            'name': {'en': 'project', 'ru': 'проект'},
            'slug': 'project',
            'values': {'taxi': TAXI, 'eda': EDA, '__supers__': SUPERS},
        },
    }
