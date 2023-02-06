# pylint: disable=redefined-outer-name


async def test_registry(stq3_context):
    from corp_notices.notices import registry
    assert registry.get('OfferScoringNotice')
