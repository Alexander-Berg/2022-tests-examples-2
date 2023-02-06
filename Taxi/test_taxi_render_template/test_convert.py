import pytest


@pytest.mark.parametrize(
    'html,expected_status, expected_error, fetch_called',
    [
        ('<a> hello there </a>', 200, None, False),
        ('', 200, None, False),
        ('<img src="http://forbidden.yandex.net"/>', 200, None, False),
        (
            '<img src="https://avatars.mds.yandex.net/'
            'get-bunker/someimage.png"/>',
            200,
            None,
            True,
        ),
        (f'<img src="data:image/png;base64,somebase64"/>', 200, None, True),
    ],
)
async def test_render(
        mock_default_weasyprint_fetcher,
        taxi_render_template_client,
        html,
        expected_status,
        expected_error,
        fetch_called,
):
    response = await taxi_render_template_client.post('/convert', data=html)
    assert response.status == expected_status
    calls = mock_default_weasyprint_fetcher.calls
    assert calls if fetch_called else not calls
    if expected_status == 200:
        content = await response.content.read()
        assert response.content_type == 'application/pdf'
        assert content
    else:
        error = response.text
        assert error == expected_error
