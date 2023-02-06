# pylint: disable=unused-variable
import pytest

from eslogadminpy3.generated.cron import run_cron


@pytest.mark.parametrize(
    'es_templates, es_version',
    [('es7_templates.json', '7.0.1'), ('es2_templates.json', '2.4.1')],
)
@pytest.mark.config(
    LOGS_ELASTIC_UPDATE_DYNAMIC_TEMPLATES_TASK={
        'commit_changes': True,
        'update_template': True,
    },
)
async def test_task(patch, load_json, es_templates, es_version):
    @patch('elasticsearch.client.indices.IndicesClient.get_template')
    async def indices_get_template(*args, **kwargs):
        return load_json(es_templates)

    @patch('elasticsearch.client.indices.IndicesClient.put_template')
    async def indices_put_template(*args, **kwargs):
        return {}

    @patch('elasticsearch.client.Elasticsearch.info')
    async def es_info(*args, **kwargs):
        return {'version': {'number': es_version}}

    await run_cron.main(
        ['eslogadminpy3.crontasks.update_indices_templates', '-t', '0', '-d'],
    )

    assert indices_put_template.calls
    assert indices_get_template.calls
    assert es_info.calls


@pytest.mark.parametrize(
    'use_db_whitelist,clean_extra',
    [
        pytest.param(
            False,
            False,
            marks=pytest.mark.config(
                LOGS_ELASTIC_WHITELIST_SETTINGS={
                    'use_db_whitelist': False,
                    'clean_extra': False,
                    'templates': ['yandex-taxi'],
                },
            ),
        ),
        pytest.param(
            True,
            True,
            marks=pytest.mark.config(
                LOGS_ELASTIC_WHITELIST_SETTINGS={
                    'use_db_whitelist': True,
                    'clean_extra': True,
                    'templates': ['yandex-taxi'],
                },
            ),
        ),
        pytest.param(
            True,
            False,
            marks=pytest.mark.config(
                LOGS_ELASTIC_WHITELIST_SETTINGS={
                    'use_db_whitelist': True,
                    'clean_extra': False,
                    'templates': ['yandex-taxi'],
                },
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'es_templates, es_version',
    [('es7_templates.json', '7.0.1'), ('es2_templates.json', '2.4.1')],
)
@pytest.mark.config(
    LOGS_ELASTIC_UPDATE_DYNAMIC_TEMPLATES_TASK={
        'commit_changes': True,
        'update_template': True,
    },
)
async def test_template_updates(
        patch,
        load_json,
        cron_context,
        es_templates,
        es_version,
        use_db_whitelist,
        clean_extra,
):
    templates_after_applying = {}

    @patch('elasticsearch.client.indices.IndicesClient.get_template')
    async def indices_get_template(*args, **kwargs):
        if not templates_after_applying:
            return load_json(es_templates)
        return templates_after_applying

    @patch('elasticsearch.client.indices.IndicesClient.put_template')
    async def indices_put_template(name, body):
        templates_after_applying[name] = body

    @patch('elasticsearch.client.Elasticsearch.info')
    async def es_info(*args, **kwargs):
        return {'version': {'number': es_version}}

    await run_cron.main(
        ['eslogadminpy3.crontasks.update_indices_templates', '-t', '0', '-d'],
    )

    assert indices_put_template.calls
    assert indices_get_template.calls
    assert es_info.calls

    await run_cron.main(
        ['eslogadminpy3.crontasks.update_indices_templates', '-t', '0', '-d'],
    )

    assert not indices_put_template.calls
    assert indices_get_template.calls
    assert es_info.calls

    if use_db_whitelist and 'yandex-taxi' in templates_after_applying:
        properties = templates_after_applying['yandex-taxi']['mappings'][
            'properties'
        ]
        assert 'expected_field' in properties
        if clean_extra:
            assert len(properties.keys()) == 1
        else:
            assert len(properties.keys()) > 1
            assert 'meta_driver_id' in properties
