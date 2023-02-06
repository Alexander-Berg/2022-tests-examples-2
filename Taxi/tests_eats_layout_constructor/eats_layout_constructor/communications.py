import dataclasses
import enum
import typing


class Kind(str, enum.Enum):
    Info = 'info'
    Place = 'place'
    Brand = 'brand'
    Collection = 'collection'


class Format(str, enum.Enum):
    Classic = 'classic'
    Shortcut = 'shortcut'
    WideAndShort = 'wide_and_short'


class Theme(str, enum.Enum):
    Light = 'light'
    Dark = 'dark'


class Platform(str, enum.Enum):
    Web = 'web'
    Mobile = 'mobile'


@dataclasses.dataclass
class Image:
    url: str
    theme: Theme
    platform: Platform


@dataclasses.dataclass
class BannerPayload:
    banner_id: int

    def asdict(self):
        return {'id': self.banner_id}


@dataclasses.dataclass
class ViewTracking:
    feed_id: str = 'CHANGE_ME_FEED_ID'
    type: str = 'banner'


@dataclasses.dataclass
class BannerMeta:
    view_tracking: ViewTracking = ViewTracking()
    analytics: typing.Optional[str] = None

    def asdict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class Banner:
    id: int
    kind: Kind = Kind.Info
    url: str = ''
    app_link: str = ''
    payload: BannerPayload = dataclasses.field(init=False)
    images: typing.List[Image] = dataclasses.field(default_factory=list)
    shortcuts: typing.List[Image] = dataclasses.field(default_factory=list)
    wide_and_short: typing.List[Image] = dataclasses.field(
        default_factory=list,
    )
    meta: BannerMeta = BannerMeta()

    def __post_init__(self) -> None:
        self.payload = BannerPayload(banner_id=self.id)

    def asdict(self) -> dict:
        return {
            'id': self.id,
            'kind': self.kind,
            'url': self.url,
            'appLink': self.app_link,
            'payload': self.payload.asdict(),
            'images': self.images,
            'shortcuts': self.shortcuts,
            'wide_and_short': self.wide_and_short,
            'meta': self.meta.asdict(),
        }


class BlockType(str, enum.Enum):
    BannersCarousel = 'banners_carousel'
    HighBannersCarousel = 'high_banners_carousel'
    Advert = 'advert'
    Popup = 'popup'


class BannerCarouselItemWidth(str, enum.Enum):
    Single = 'single'
    Double = 'double'
    Triple = 'triple'


@dataclasses.dataclass
class BannersCarouselItem:
    banner_id: str
    url: str
    app_link: str
    images: typing.List[Image] = dataclasses.field(default_factory=list)
    width: BannerCarouselItemWidth = BannerCarouselItemWidth.Single
    meta: BannerMeta = BannerMeta()

    def asdict(self) -> dict:
        return {
            'id': self.banner_id,
            'url': self.url,
            'appLink': self.app_link,
            'images': self.images,
            'width': self.width,
            'meta': self.meta.asdict(),
        }


@dataclasses.dataclass
class BannersCarouselPage:
    banners: typing.List[BannersCarouselItem] = dataclasses.field(
        default_factory=list,
    )

    def asdict(self) -> dict:
        # pylint: disable=not-an-iterable
        return {'banners': [banner.asdict() for banner in self.banners]}


@dataclasses.dataclass
class BannersCarouselPayload:
    pages: typing.List[BannersCarouselPage] = dataclasses.field(
        default_factory=list,
    )

    def asdict(self) -> dict:
        # pylint: disable=not-an-iterable
        return {'pages': [page.asdict() for page in self.pages]}


@dataclasses.dataclass
class HighBannerItem:
    banner_id: str
    url: str
    app_link: str
    images: typing.List[Image] = dataclasses.field(default_factory=list)
    meta: BannerMeta = BannerMeta()

    def asdict(self) -> dict:
        return {
            'id': self.banner_id,
            'url': self.url,
            'appLink': self.app_link,
            'images': self.images,
            'meta': self.meta.asdict(),
        }


@dataclasses.dataclass
class HighBannersCarouselPayload:
    banners: typing.List[HighBannerItem] = dataclasses.field(
        default_factory=list,
    )

    def asdict(self) -> dict:
        # pylint: disable=not-an-iterable
        return {'banners': [banner.asdict() for banner in self.banners]}


@dataclasses.dataclass
class AdvertBannersPayload:
    advert_banners: typing.List[Banner] = dataclasses.field(
        default_factory=list,
    )

    def asdict(self) -> dict:
        # pylint: disable=not-an-iterable
        advert_banners = [banner.asdict() for banner in self.advert_banners]
        return {'advert_banners': advert_banners}


@dataclasses.dataclass
class PopupBanner:
    banner_id: str
    url: str
    app_link: str
    images: typing.List[Image] = dataclasses.field(default_factory=list)
    meta: BannerMeta = BannerMeta()

    def asdict(self) -> dict:
        return {
            'id': self.banner_id,
            'url': self.url,
            'appLink': self.app_link,
            'images': self.images,
            'meta': self.meta.asdict(),
        }


@dataclasses.dataclass
class PopupBannerPayload:
    banner: PopupBanner

    def asdict(self) -> dict:
        return {'banner': self.banner.asdict()}


@dataclasses.dataclass
class Block:
    block_id: str
    type: BlockType
    payload: typing.Union[
        BannersCarouselPayload,
        HighBannersCarouselPayload,
        AdvertBannersPayload,
        PopupBannerPayload,
    ]

    def asdict(self) -> dict:
        payload = self.payload.asdict()
        payload['block_type'] = self.type

        return {
            'block_id': self.block_id,
            'type': self.type,
            'payload': payload,
        }


@dataclasses.dataclass
class LayoutBanner:
    id: int
    payload: Banner = None
    kind: Kind = Kind.Info
    formats: typing.List[Format] = dataclasses.field(default_factory=list)
    place_id: typing.Optional[int] = None
    brand_id: typing.Optional[int] = None
    collection_slug: typing.Optional[str] = None

    def __post_init__(self) -> None:
        if self.payload is None:
            self.payload = Banner(id=self.id)

    def asdict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )
