MARKET_LOCALE = 'ru'

MARKET_COUNTRY_ISO3 = 'FRA'
MARKET_REGION_ID = 213

MARKET_SERVICE_ID = 'lavka:ru'
MARKET_EATS_AND_LAVKA_ID = '54321'
MARKET_FEED_ID = 239
MARKET_PARTNER_ID = 239239
MARKET_BUSINESS_ID = 239239239


def make_market_offer(entity, offer_id):
    return {'entity': entity, 'shop': {'feed': {'offerId': offer_id}}}


def make_market_search_response(results):
    return {'search': {'results': results}}


SAAS_SERVICE = 'grocery'
SAAS_PREFIX = 123
SAAS_CUSTOM_PREFIX = 999
SAAS_MISPELL = 'force'
