import http

import pytest


@pytest.mark.servicetest
@pytest.mark.parametrize(
    'template_name, draft_id,'
    'document_templator_response, has_automailing_response,'
    'expected_status, expected_content',
    (
        (
            'automailing_template_name',
            '12345',
            {
                'generated_text': 'from_document_templator',
                'id': 'id',
                'status': 'FINISHED',
            },
            True,
            http.HTTPStatus.OK,
            {
                'content': 'from_document_templator',
                'subject': 'from_document_templator',
            },
        ),
    ),
)
@pytest.mark.config(
    PARTNER_MAILING_TEMPLATES={
        'automailing_template_name': {
            'template_id': '1' * 24,
            'subject_template_id': '2' * 24,
        },
    },
    PARTNER_MAILING_TARIFF_CATEGORY_FIELDS={
        'simple_fields': ['paid_cancel_fix'],
        'complex_fields': {},
        'list_complex_fields': {
            'special_taximeters': {
                'identity_fields': ['zone_name'],
                'comparator': {
                    'list_complex_fields': {},
                    'complex_fields': {
                        'price': {
                            'list_complex_fields': {
                                'distance_price_intervals': {
                                    'comparator': {'simple_fields': ['end']},
                                    'identity_fields': ['begin', 'price'],
                                    'remove_equal_item': True,
                                },
                            },
                        },
                    },
                },
            },
            # just delete all summable_requirements
            'summable_requirements': {'identity_fields': [], 'comparator': {}},
        },
    },
)
async def test_v1_notify_tariff_changed_post(
        web_app_client,
        template_name,
        draft_id,
        expected_status,
        expected_content,
        mockserver,
        document_templator_response,
        has_automailing_response,
):
    errors = []

    @mockserver.json_handler('taxi-approvals/v2/drafts/')
    def _approvals_mock(request):
        if request.query['id'] != draft_id:
            errors.append('Invalid data in approvals_mock')
        return {
            'id': int(draft_id),
            'version': 1,
            'status': 'succeeded',
            'updated': '2020-01-01T00:00:00',
            'api_path': 'set_tariff',
            'summary': {
                'new': {
                    'categories': [
                        {
                            'category_name': 'not_changed',
                            'category_type': 'not_changed',
                            'time_from': '01.01.2020',
                            'time_to': '01.01.2021',
                            'day_type': 'weekday',
                            'currency': 'rub',
                            'paid_cancel_fix': 0,
                            'summable_requirements': {
                                'type': 'test',
                                'max_price': 10,
                            },
                        },
                        {
                            'category_name': 'changed_simple_field',
                            'category_type': 'changed_simple_field',
                            'time_from': '01.01.2020',
                            'time_to': '01.01.2021',
                            'day_type': 'weekday',
                            'currency': 'rub',
                            'paid_cancel_fix': 1,
                        },
                        {
                            'category_name': 'changed_list_field',
                            'category_type': 'changed_list_field',
                            'time_from': '01.01.2020',
                            'time_to': '01.01.2021',
                            'day_type': 'weekday',
                            'currency': 'rub',
                            'special_taximeters': [{'zone_name': 'new'}],
                        },
                        {
                            'category_name': 'changed_complex_field',
                            'category_type': 'changed_complex_field',
                            'time_from': '01.01.2020',
                            'time_to': '01.01.2021',
                            'day_type': 'weekday',
                            'currency': 'rub',
                            'special_taximeters': [
                                {
                                    'price': {
                                        'time_price_intervals': [],
                                        'distance_price_intervals': [
                                            {
                                                'end': 1,
                                                'begin': 0,
                                                'price': 23,
                                            },
                                        ],
                                    },
                                    'zone_name': 'anapa',
                                },
                                {
                                    'price': {
                                        'time_price_intervals': [],
                                        'distance_price_intervals': [
                                            {
                                                'end': 1,
                                                'begin': 0,
                                                'price': 32,
                                            },
                                        ],
                                    },
                                    'zone_name': 'suburb',
                                },
                            ],
                        },
                    ],
                },
                'current': {
                    'categories': [
                        {
                            'category_name': 'not_changed',
                            'category_type': 'not_changed',
                            'time_from': '01.01.2020',
                            'time_to': '01.01.2021',
                            'day_type': 'weekday',
                            'currency': 'rub',
                            'paid_cancel_fix': 0,
                        },
                        {
                            'category_name': 'changed_simple_field',
                            'category_type': 'changed_simple_field',
                            'time_from': '01.01.2020',
                            'time_to': '01.01.2021',
                            'day_type': 'weekday',
                            'currency': 'rub',
                            'paid_cancel_fix': 0,
                        },
                        {
                            'category_name': 'changed_list_field',
                            'category_type': 'changed_list_field',
                            'time_from': '01.01.2020',
                            'time_to': '01.01.2021',
                            'day_type': 'weekday',
                            'currency': 'rub',
                            'special_taximeters': [{'zone_name': 'old'}],
                        },
                        {
                            'category_name': 'changed_complex_field',
                            'category_type': 'changed_complex_field',
                            'time_from': '01.01.2020',
                            'time_to': '01.01.2021',
                            'day_type': 'weekday',
                            'currency': 'rub',
                            'special_taximeters': [
                                {
                                    'price': {
                                        'time_price_intervals': [],
                                        'distance_price_intervals': [
                                            {
                                                'end': 1,
                                                'begin': 0,
                                                'price': 23,
                                            },
                                        ],
                                    },
                                    'zone_name': 'anapa',
                                },
                                {
                                    'price': {
                                        'time_price_intervals': [],
                                        'distance_price_intervals': [
                                            {
                                                'end': 1,
                                                'begin': 0,
                                                'price': 31,
                                            },
                                        ],
                                    },
                                    'zone_name': 'suburb',
                                },
                            ],
                        },
                    ],
                },
            },
            'data': {'home_zone': 'moscow'},
        }

    expected_params = [
        {
            'name': 'changed_categories',
            'value': [
                {
                    'category_name': 'changed_simple_field',
                    'category_type': 'changed_simple_field',
                    'time_from': '01.01.2020',
                    'time_to': '01.01.2021',
                    'day_type': 'weekday',
                    'currency': 'rub',
                    'paid_cancel_fix': 1,
                },
                {
                    'category_name': 'changed_list_field',
                    'category_type': 'changed_list_field',
                    'time_from': '01.01.2020',
                    'time_to': '01.01.2021',
                    'day_type': 'weekday',
                    'currency': 'rub',
                    'special_taximeters': [{'zone_name': 'new'}],
                },
                {
                    'category_name': 'changed_complex_field',
                    'category_type': 'changed_complex_field',
                    'time_from': '01.01.2020',
                    'time_to': '01.01.2021',
                    'day_type': 'weekday',
                    'currency': 'rub',
                    'special_taximeters': [
                        {
                            'price': {
                                'distance_price_intervals': [],
                                'time_price_intervals': [],
                            },
                            'zone_name': 'anapa',
                        },
                        {
                            'price': {
                                'time_price_intervals': [],
                                'distance_price_intervals': [
                                    {'end': 1, 'begin': 0, 'price': 32},
                                ],
                            },
                            'zone_name': 'suburb',
                        },
                    ],
                },
            ],
        },
        {'name': 'zone', 'value': 'moscow'},
        {'name': 'applying_datetime', 'value': '2020-01-01T00:00:00'},
    ]

    expected_requests = {
        'email': {
            'name': 'email',
            'generate_text_immediately': True,
            'description': 'email',
            'template_id': '111111111111111111111111',
            'params': expected_params,
        },
        'subject': {
            'name': 'subject',
            'generate_text_immediately': True,
            'description': 'subject',
            'template_id': '222222222222222222222222',
            'params': expected_params,
        },
    }
    actual_requests = {}

    @mockserver.json_handler(
        'document-templator/v1/dynamic_documents/preview/generate/',
    )
    def _document_templator_mock(request):
        name = request.json.get('name')
        actual_requests[name] = request.json
        return document_templator_response

    if has_automailing_response:

        @mockserver.json_handler('automailing/mail')
        def _automailing_mock(request):
            request.json.pop('id')
            if request.json != {
                    'template_name': 'automailing_template_name',
                    'zone': 'moscow',
                    'content': 'from_document_templator',
                    'subject': 'from_document_templator',
            }:
                errors.append('Invalid data in automailing_mock')

            return {}

    response = await web_app_client.post(
        'v1/notify-tariff-changed',
        json={'template_name': template_name, 'draft_id': draft_id},
    )
    assert not errors
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_content
    assert actual_requests == expected_requests
