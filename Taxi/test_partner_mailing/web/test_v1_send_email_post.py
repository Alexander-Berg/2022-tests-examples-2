import http

import pytest


@pytest.mark.servicetest
@pytest.mark.parametrize(
    'body, '
    'document_templator_response, has_automailing_response,'
    'expected_status, expected_content',
    (
        (
            {
                'template_name': 'automailing_template_name',
                'template_params': [{'name': 'zone', 'value': 'moscow'}],
                'zone': 'moscow',
            },
            {
                'generated_text': 'from_document_templator',
                'id': '123',
                'status': 'FINISHED',
            },
            True,
            http.HTTPStatus.OK,
            {
                'content': 'from_document_templator',
                'subject': 'from_document_templator',
            },
        ),
        (
            {
                'template_name': 'invalid',
                'zone': 'moscow',
                'template_params': [],
            },
            {
                'generated_text': 'from_document_templator',
                'id': '123',
                'status': 'FINISHED',
            },
            True,
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'INVALID_TEMPLATE_NAME',
                'message': 'invalid template name',
            },
        ),
        (
            {
                'template_name': 'automailing_template_name',
                'zone': 'moscow',
                'template_params': [{'name': 'zone', 'value': 'moscow'}],
                'preview': True,
            },
            {
                'generated_text': 'from_document_templator',
                'id': '123',
                'status': 'FINISHED',
            },
            False,
            http.HTTPStatus.OK,
            {
                'content': 'from_document_templator',
                'subject': 'from_document_templator',
            },
        ),
        (
            {
                'template_name': 'automailing_template_name',
                'zone': 'moscow',
                'template_params': [{'name': 'zone', 'value': 'moscow'}],
            },
            {
                'generated_text': 'from_document_templator',
                'id': '123',
                'status': 'FINISHED',
            },
            False,
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'AUTOMAILING_ERROR',
                'details': {'original_code': 'automailing_error'},
                'message': 'error',
            },
        ),
        (
            {
                'template_name': 'automailing_template_name',
                'zone': 'moscow',
                'template_params': [{'name': 'zone', 'value': 'moscow'}],
            },
            None,
            True,
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DOCUMENT_TEMPLATOR_ERROR',
                'details': {'original_code': 'document_templator_error'},
                'message': 'error',
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
)
async def test_v1_send_email_post(
        taxi_partner_mailing_web,
        body,
        expected_status,
        expected_content,
        mockserver,
        document_templator_response,
        has_automailing_response,
):
    errors = []

    expected_data = {
        'email': {
            'name': 'email',
            'generate_text_immediately': True,
            'description': 'email',
            'template_id': '111111111111111111111111',
            'params': [{'name': 'zone', 'value': 'moscow'}],
        },
        'subject': {
            'name': 'subject',
            'generate_text_immediately': True,
            'description': 'subject',
            'template_id': '222222222222222222222222',
            'params': [{'name': 'zone', 'value': 'moscow'}],
        },
    }

    @mockserver.json_handler(
        'document-templator/v1/dynamic_documents/preview/generate/',
    )
    def _document_templator_mock(request):
        if document_templator_response is None:
            return mockserver.make_response(
                status=400,
                json={'code': 'document_templator_error', 'message': 'error'},
            )
        name = request.json['name']
        if request.json != expected_data[name]:
            errors.append('Invalid data in document_templator_mock')
        return document_templator_response

    @mockserver.json_handler('automailing/mail')
    def _automailing_mock(request):
        if not has_automailing_response:
            return mockserver.make_response(
                status=409,
                json={'code': 'automailing_error', 'message': 'error'},
            )
        request.json.pop('id')
        if request.json != {
                'template_name': 'automailing_template_name',
                'zone': 'moscow',
                'content': 'from_document_templator',
                'subject': 'from_document_templator',
        }:
            errors.append('Invalid data in automailing_mock')

        return {}

    response = await taxi_partner_mailing_web.post('v1/send-email', json=body)
    assert not errors
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_content
