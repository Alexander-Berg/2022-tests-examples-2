async def test_yt(library_context, simple_secdist, patch):
    @patch('taxi.clients.yt.YtClient.refresh_hosts')
    async def patched(*, log_extra=None):
        pass

    await library_context.client_yt['genghis'].refresh_hosts()

    assert patched.calls == [{'log_extra': None}]
