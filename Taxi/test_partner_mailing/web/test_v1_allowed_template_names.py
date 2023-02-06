import http

import pytest


@pytest.mark.servicetest
@pytest.mark.config(
    PARTNER_MAILING_TEMPLATES={
        'automailing_template_name': {
            'template_id': '1' * 24,
            'subject_template_id': '2' * 24,
        },
    },
)
async def test_v1_allowed_template_names_get(taxi_partner_mailing_web):
    response = await taxi_partner_mailing_web.get('/v1/allowed-template-names')
    content = await response.json()
    assert response.status == http.HTTPStatus.OK
    assert content == {'template_names': ['automailing_template_name']}
