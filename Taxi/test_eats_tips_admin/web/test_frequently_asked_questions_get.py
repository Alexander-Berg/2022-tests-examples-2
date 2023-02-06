from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from test_eats_tips_admin import conftest


@pytest.mark.parametrize(
    'expected_answer',
    [
        pytest.param(
            {'categories': []},
            id='empty config',
            marks=[pytest.mark.config(EATS_TIPS_ADMIN_FAQ={'categories': []})],
        ),
        pytest.param(
            {
                'categories': [
                    {
                        'questions': [
                            {
                                'buttons': [
                                    {'title': 'b_title_1', 'url': 'url_1'},
                                ],
                                'text': 'q_text_1',
                                'title': 'q_title_1',
                            },
                        ],
                        'title': 'title_1',
                    },
                ],
            },
            id='no visible in config',
            marks=[
                pytest.mark.config(
                    EATS_TIPS_ADMIN_FAQ={
                        'categories': [
                            {
                                'title': 'title_1',
                                'order': 0,
                                'questions': [
                                    {
                                        'title': 'q_title_1',
                                        'order': 0,
                                        'text': 'q_text_1',
                                        'buttons': [
                                            {
                                                'title': 'b_title_1',
                                                'order': 0,
                                                'url': 'url_1',
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ),
            ],
        ),
        pytest.param(
            {
                'categories': [
                    {
                        'questions': [
                            {
                                'buttons': [
                                    {'title': 'b_title_0_1', 'url': 'url_0_1'},
                                ],
                                'text': 'q_text_0_1',
                                'title': 'q_title_0_1',
                            },
                        ],
                        'title': 'title_0',
                    },
                    {
                        'questions': [
                            {
                                'buttons': [
                                    {'title': 'b_title_0', 'url': 'url_0'},
                                    {'title': 'b_title_1', 'url': 'url_1'},
                                ],
                                'text': 'q_text_0',
                                'title': 'q_title_0',
                            },
                            {
                                'buttons': [
                                    {'title': 'b_title_1', 'url': 'url_1'},
                                ],
                                'text': 'q_text_1',
                                'title': 'q_title_1',
                            },
                        ],
                        'title': 'title_1',
                    },
                ],
            },
            id='full config, filtered category',
            marks=[
                pytest.mark.config(
                    EATS_TIPS_ADMIN_FAQ={
                        'categories': [
                            {
                                'title': 'title_1',
                                'order': 1,
                                'visible': True,
                                'questions': [
                                    {
                                        'title': 'q_title_1',
                                        'order': 1,
                                        'visible': True,
                                        'text': 'q_text_1',
                                        'buttons': [
                                            {
                                                'title': 'b_title_1',
                                                'order': 1,
                                                'url': 'url_1',
                                            },
                                        ],
                                    },
                                    {
                                        'title': 'q_title_0',
                                        'order': 0,
                                        'text': 'q_text_0',
                                        'buttons': [
                                            {
                                                'title': 'b_title_1',
                                                'order': 1,
                                                'url': 'url_1',
                                            },
                                            {
                                                'title': 'b_title_0',
                                                'order': 0,
                                                'url': 'url_0',
                                            },
                                        ],
                                    },
                                ],
                            },
                            {
                                'title': 'title_0',
                                'order': 0,
                                'questions': [
                                    {
                                        'title': 'q_title_0_1',
                                        'order': 0,
                                        'text': 'q_text_0_1',
                                        'buttons': [
                                            {
                                                'title': 'b_title_0_1',
                                                'order': 1,
                                                'url': 'url_0_1',
                                            },
                                        ],
                                    },
                                ],
                            },
                            {
                                'title': 'title_2',
                                'order': 2,
                                'questions': [
                                    {
                                        'title': 'q_title_2',
                                        'order': 0,
                                        'text': 'q_text_2',
                                        'visible': False,
                                        'buttons': [
                                            {
                                                'title': 'b_title_0_1',
                                                'order': 1,
                                                'url': 'url_0_1',
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ),
            ],
        ),
    ],
)
async def test_faq(
        taxi_eats_tips_admin_web, mock_eats_tips_partners, expected_answer,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request: http.Request):
        assert dict(request.query) == {'alias': '1'}
        return web.json_response(conftest.USER_1[1])

    response = await taxi_eats_tips_admin_web.get(
        '/v1/faq', headers={'X-Chaevie-Token': conftest.JWT_USER_1},
    )
    assert response.status == 200
    content = await response.json()
    assert expected_answer == content
