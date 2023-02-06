import datetime

from eats_retail_magnit_parser.components.loyalty import magnit_loyalty_client


async def test_token_is_expired(web_context):

    token = magnit_loyalty_client.Token(access_token='token', expires_in=60)
    assert not token.is_expired

    token.created_at = datetime.datetime.utcnow() - datetime.timedelta(hours=1)

    assert token.is_expired


async def test_refresh_token(magnit_loyalty_mocks, web_context):

    cli = magnit_loyalty_client.MagnitLoyaltyClient(web_context)

    assert cli._token is None  # pylint: disable=W0212

    await cli.refresh_token()

    assert cli._token is not None  # pylint: disable=W0212

    token = await cli.get_token()
    assert token.startswith('Bearer eyJhbGciOiJ')
    assert not cli._token.is_expired  # pylint: disable=W0212
