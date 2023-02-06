import pytest

from taxi_strongbox.components import template_processor as tp


@pytest.mark.parametrize(
    ['input_data', 'expected_link', 'expected_payload'],
    [
        pytest.param(
            {
                'merge_sha': '301261db996a42d5401ceeeb292ba239b6da9a1e',
                'service_name': 'random_service',
                'type_name': 'secdist',
            },
            'https://github.yandex-team.ru/taxi/infra-cfg-graphs/commit/'
            '301261db996a42d5401ceeeb292ba239b6da9a1e',
            {'status': 'success'},
            id='check_merge_sha',
        ),
        pytest.param(
            {
                'pull_request_url': 'https://a.yandex-team.ru/review/2436796',
                'service_name': 'random_service',
                'type_name': 'secdist',
            },
            'https://a.yandex-team.ru/review/2436796',
            {'status': 'success'},
            id='check_pull_request_url',
        ),
        pytest.param(
            {'service_name': 'random_service', 'type_name': 'secdist'},
            None,
            {'status': 'success'},
            id='all_params_not_exists',
        ),
        pytest.param(
            {
                'pull_request_url': 'https://a.yandex-team.ru/review/2436796',
                'merge_sha': '301261db996a42d5401ceeeb292ba239b6da9a1e',
                'service_name': 'random_service',
                'type_name': 'secdist',
            },
            None,
            {
                'status': 'failed',
                'error_message': (
                    'Only one parameter: merge_sha or pull_request_url'
                ),
            },
            id='all_params_exists',
        ),
    ],
)
@pytest.mark.pgsql('strongbox', files=['templates.sql'])
async def test_cube_save_last_change_url(
        call_cube,
        tp_mock,
        web_context,
        input_data,
        expected_link,
        expected_payload,
):
    tp_mock()
    templates_processor = tp.TemplatesProcessor(web_context)
    data = await call_cube('SaveLastChangeUrl', input_data)
    assert data == expected_payload
    updated_template = await templates_processor.get_template_by_service_name(
        input_data['service_name'], input_data['type_name'],
    )
    assert updated_template.last_change_link == expected_link
