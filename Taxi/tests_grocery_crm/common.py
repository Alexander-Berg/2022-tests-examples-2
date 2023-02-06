import datetime

UTC_TZ = datetime.timezone.utc
EXPIRE_AT = '2077-01-01T00:00:00+00:00'
EXPIRE_AT_DT = datetime.datetime(2077, 1, 1, 00, 00, 00, tzinfo=UTC_TZ)

TEXT = 'No one will read this text here, because this is testsuite'
PICTURE = 'www.leningrad.spb.ru'
TEXT_COLOR = '#aabbcc'
BACKGROUND_COLOR = '#aabbcc'
BUTTON = {
    'text': 'GGWP',
    'text_color': '#666666',
    'background_color': '#777777',
    'deeplink': 'deeplink://somewhere',
    'action': 'deeplink',
}
MODAL = {
    'text': 'Modal text',
    'title': 'Modal title',
    'picture': 'www.img.com/png',
    'text_color': '#001122',
    'background_color': '#334455',
    'buttons': [BUTTON, BUTTON],
    'full_screen': False,
}
EXTRA_DATA = {
    'additional_text': 'Some more text',
    'additional_link': 'Another link',
}

DEPOT_ID = '1337'
COUNTRY_ISO3 = 'RUS'
REGION_ID = 213
TIMEZONE = '+3'


def add_default_depot(grocery_depots):
    grocery_depots.add_depot(
        depot_test_id=int(DEPOT_ID),
        legacy_depot_id=DEPOT_ID,
        country_iso3=COUNTRY_ISO3,
        region_id=REGION_ID,
        timezone=TIMEZONE,
    )
