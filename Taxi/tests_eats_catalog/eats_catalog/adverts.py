import dataclasses
import enum
import typing


@dataclasses.dataclass
class Coefficients:
    yabs_ctr: float = 1
    relevance_multiplier: int = 0
    send_relevance: bool = False
    send_ctr: bool = False

    def asdict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class YabsSettings:
    page_id: int = 1
    target_ref: str = 'testsuite'
    page_ref: typing.Optional[str] = None
    coefficients: typing.Optional[Coefficients] = None
    secure_urls_schema: bool = False

    def asdict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class PlaceStatsTable:
    name: str = 'non_personal_stats'
    path: str = '//testsuite/eats_catalog/adverts'

    def get_yt_path(self) -> str:
        return self.path + '/' + self.name

    def get_attributes(self) -> dict:
        return {
            'replication_factor': 1,
            'dynamic': 'false',
            'optimize_for': 'lookup',
            'schema': [
                {'name': 'brand_id', 'type': 'int64', 'required': 'true'},
                {
                    'name': 'viewed_to_opened',
                    'type': 'double',
                    'required': 'false',
                },
                {
                    'name': 'viewed_to_opened_sess',
                    'type': 'double',
                    'required': 'false',
                },
                {
                    'name': 'viewed_to_ordered',
                    'type': 'double',
                    'required': 'false',
                },
                {
                    'name': 'viewed_to_ordered_sess',
                    'type': 'double',
                    'required': 'false',
                },
                {
                    'name': 'opened_to_ordered',
                    'type': 'double',
                    'required': 'false',
                },
                {
                    'name': 'opened_to_ordered_sess',
                    'type': 'double',
                    'required': 'false',
                },
            ],
        }


class CTRSource(str, enum.Enum):
    VIEWED_TO_OPENED = 'viewed_to_opened'
    VIEWED_TO_OPENED_SESSION = 'viewed_to_opened_sess'

    VIEWED_TO_ORDERED = 'viewed_to_ordered'
    VIEWED_TO_ORDERED_SESSION = 'viewed_to_ordered_sess'

    OPENED_TO_ORDERED = 'opened_to_ordered'
    OPENED_TO_ORDERED_SESSION = 'opened_to_ordered_sess'


@dataclasses.dataclass
class PlaceStats:
    brand_id: int
    viewed_to_opened: typing.Optional[float] = None
    viewed_to_opened_sess: typing.Optional[float] = None
    viewed_to_ordered: typing.Optional[float] = None
    viewed_to_ordered_sess: typing.Optional[float] = None
    opened_to_ordered: typing.Optional[float] = None
    opened_to_ordered_sess: typing.Optional[float] = None

    def asdict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class PlacesRelevanceTable:
    name: str = 'place_relevances'
    path: str = '//testsuite/eats_catalog/adverts'

    def get_yt_path(self) -> str:
        return self.path + '/' + self.name

    def get_attributes(self) -> dict:
        return {
            'replication_factor': 1,
            'dynamic': 'false',
            'optimize_for': 'lookup',
            'schema': [
                {'name': 'cm2_mean', 'type': 'double', 'required': 'false'},
                {'name': 'place_id', 'type': 'int64', 'required': 'true'},
                {
                    'name': 'viewed_to_ordered',
                    'type': 'double',
                    'required': 'false',
                },
            ],
        }


@dataclasses.dataclass
class RelevantPlaceStats:
    place_id: int
    cm2_mean: typing.Optional[float] = None
    viewed_to_ordered: typing.Optional[float] = None

    def asdict(self):
        return dataclasses.asdict(self)


class RelevanceSource(enum.Enum):
    CM2_MEAN = 'cm2_mean'
    CR_X_CM2 = 'cr_x_cm2'
    VIEWED = 'viewed_to_ordered'


@dataclasses.dataclass
class YabsServiceBannerDirectData:
    url: str
    link_head: str
    link_tail: str


@dataclasses.dataclass
class YabsServiceBanner(dict):
    banner_id: str
    direct_data: YabsServiceBannerDirectData

    def asdict(self) -> dict:
        return dataclasses.asdict(self)


def create_yabs_service_banner(banner_id: int) -> YabsServiceBanner:
    return YabsServiceBanner(
        banner_id=str(banner_id),
        direct_data=YabsServiceBannerDirectData(
            url=f'https://eda.yandex.ru/click/{banner_id}',
            link_head='https://eda.yandex.ru/view',
            link_tail=f'/{banner_id}',
        ),
    )
