async def test_post_message(library_context, mockserver, load_json):
    @mockserver.handler(
        '/services/T2Z17K63A/B035679UG9J/3OJGV7XjXfDNaSNVGB95MvUH',
    )
    def post_message_mock():  # pylint: disable=W0612
        return mockserver.make_response(
            response='ok', content_type='text/html', status=200,
        )

    response = await library_context.client_slack.post_message(
        username='Teamcity',
        message=['line1', 'line2'],
        slack_channel='#test-channel',
        color='#16AB07',
        icon_url='http://some-url',
    )
    assert response == 'ok'
