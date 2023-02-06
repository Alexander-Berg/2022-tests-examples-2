import dataclasses
import enum


@dataclasses.dataclass
class CountryInfo:
    country: str
    country_iso3: str
    currency: str
    country_iso2: str
    snake_case_name: str
    geobase_country_id: int


_RUSSIA_INFO = CountryInfo(
    country='Russia',
    country_iso3='RUS',
    currency='RUB',
    country_iso2='RU',
    snake_case_name='russia',
    geobase_country_id=225,
)
_ISRAEL_INFO = CountryInfo(
    country='Israel',
    country_iso3='ISR',
    currency='ILS',
    country_iso2='IL',
    snake_case_name='israel',
    geobase_country_id=181,
)
_FRANCE_INFO = CountryInfo(
    country='France',
    country_iso3='FRA',
    currency='EUR',
    country_iso2='FR',
    snake_case_name='france',
    geobase_country_id=124,
)
_GREAT_BRITAIN_INFO = CountryInfo(
    country='GreatBritain',
    country_iso3='GBR',
    currency='GBP',
    country_iso2='GB',
    snake_case_name='great_britain',
    geobase_country_id=102,
)
_BELARUS_INFO = CountryInfo(
    country='Belarus',
    country_iso3='BLR',
    currency='BYN',
    country_iso2='BY',
    snake_case_name='belarus',
    geobase_country_id=149,
)
_RSA_INFO = CountryInfo(
    country='RSA',
    country_iso3='ZAF',
    currency='ZAR',
    country_iso2='ZA',
    snake_case_name='rsa',
    geobase_country_id=10021,
)


class Country(enum.Enum):
    Russia = _RUSSIA_INFO
    Israel = _ISRAEL_INFO
    France = _FRANCE_INFO
    GreatBritain = _GREAT_BRITAIN_INFO
    Belarus = _BELARUS_INFO
    RSA = _RSA_INFO

    def __init__(self, info):
        self._info = info

    @property
    def name(self):
        return self._info.country

    @property
    def lower_name(self):
        return self._info.snake_case_name

    @property
    def country_iso3(self):
        return self._info.country_iso3

    @property
    def currency(self):
        return self._info.currency

    @property
    def country_iso2(self):
        return self._info.country_iso2

    @property
    def geobase_country_id(self):
        return self._info.geobase_country_id
