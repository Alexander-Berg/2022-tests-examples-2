import dataclasses
import typing


@dataclasses.dataclass
class CountLinks:
    url: str
    link_tail: str


@dataclasses.dataclass
class BSData:
    adId: str
    count_links: CountLinks = dataclasses.field(init=False)

    def __post_init__(self):
        self.count_links = CountLinks(
            url=f'http://yandex.ru/click/{self.adId}',
            link_tail=f'/view/{self.adId}',
        )


@dataclasses.dataclass
class BSDataBanner:
    bs_data: BSData


@dataclasses.dataclass
class Common:
    linkHead: typing.Optional[str] = None


@dataclasses.dataclass
class Direct:
    ads: typing.List[BSDataBanner] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class MetaBannersetResponse:
    common: Common = Common()
    direct: typing.Optional[Direct] = None

    def asdict(self) -> dict:
        return dataclasses.asdict(self)
