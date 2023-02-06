import pytest

from clowny_perforator.generated.cron import run_cron


def _make_post_tvm_services(get_tvm_services):
    async def _post_tvm_services(body, env_type):
        tvm_services = get_tvm_services(env_type)['value']
        if env_type == 'testing':
            tvm_services['existed_tvm_service'] = 1001
        elif env_type == 'production':
            del tvm_services['existed_tvm_service']
            tvm_services['existed_tvm_service_7'] = 7000
        else:
            assert False

        assert body['new_value'] == tvm_services
        assert body['old_value'] == get_tvm_services(env_type)['value']

    return _post_tvm_services


def _make_post_tvm_rules(get_tvm_rules):
    async def _post_tvm_rules(body, env_type):
        tvm_rules = get_tvm_rules(env_type)['value']
        new_tvm_rules = get_tvm_rules(env_type)['value']
        if env_type == 'testing':
            new_tvm_rules.append(
                {'src': 'meow_service', 'dst': 'meow_service'},
            )
        elif env_type == 'production':
            new_tvm_rules.append(
                {'src': 'existed_tvm_service', 'dst': 'existed_tvm_service_2'},
            )
            new_tvm_rules.remove(
                {'src': 'existed_tvm_service', 'dst': 'existed_tvm_service'},
            )
        else:
            assert False

        assert body['new_value'] == new_tvm_rules
        assert body['old_value'] == tvm_rules

    return _post_tvm_rules


@pytest.mark.config(
    CLOWNY_PERFORATOR_RACE_CONDITION_CRON={
        'enabled': True,
        'set_config_enabled': True,
        'attempts_limit': 3,
        'time_minutes_limit': 30,
    },
)
@pytest.mark.pgsql('clowny_perforator', files=['warranties_data.sql'])
async def test_config_race_condition_check(
        cte_configs_mockserver, cron_context, get_tvm_services, get_tvm_rules,
):
    mock_handler = cte_configs_mockserver(
        post_tvm_services=_make_post_tvm_services(get_tvm_services),
        post_tvm_rules=_make_post_tvm_rules(get_tvm_rules),
    )
    await run_cron.main(
        [
            'clowny_perforator.crontasks.configs_race_condition_check',
            '-t',
            '0',
        ],
    )

    pstorage = cron_context.pstorage
    async with pstorage.make_conn() as conn:
        warranties = await pstorage.services_warranty.retrieve_not_ensured(
            conn=conn,
        )
        assert len(warranties) == 3, warranties
        expected = [
            ('existed_tvm_service', 'testing'),
            ('existed_tvm_service', 'production'),
            ('existed_tvm_service_7', 'production'),
        ]
        assert [
            (warranty['tvm_name'], warranty['env_type'])
            for warranty in warranties
        ] == expected

        warranties = await pstorage.rules_warranty.retrieve_not_ensured(
            conn=conn,
        )
        assert len(warranties) == 2, warranties
        expected = [
            ('existed_tvm_service', 'existed_tvm_service_2'),
            ('existed_tvm_service', 'existed_tvm_service'),
        ]
        assert [
            (warranty['source'], warranty['destination'])
            for warranty in warranties
        ] == expected

    assert mock_handler.times_called
