async def test_captcha_client(library_context, patch):
    @patch('taxi.clients.captcha.CaptchaClient.generate')
    async def test_generate():
        return

    await library_context.client_captcha.generate()

    assert len(test_generate.calls) == 1
