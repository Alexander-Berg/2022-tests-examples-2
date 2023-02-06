# pylint: disable=invalid-name
import dataclasses
import enum
import json
import typing


class BannerStatus(str, enum.Enum):
    UPLOADED = 'uploaded'
    IN_PROCESS = 'in_process'
    IN_MODERATION = 'in_moderation'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    ACTIVE = 'active'
    STOPPED = 'stopped'
    PRE_MODERATION = 'pre_moderation'

    def __str__(self):
        return self.value


@dataclasses.dataclass
class Banner:
    # pylint: disable=invalid-name
    id: int
    place_id: int

    inner_campaign_id: str
    status: BannerStatus = BannerStatus.UPLOADED

    # FIXME(udalovmax): А точно ли изображение должно быть опциоанальным в БД?
    # Насколько я понимаю, создать баннер без изображения нельзя, на это есть
    # проверка. Скорее всего нужно добавить миграцию, которая устанавливает NOT
    # NULL на image.
    image: typing.Optional[str] = None
    original_image_id: typing.Optional[str] = None
    image_text: typing.Optional[str] = None
    group_id: typing.Optional[int] = None
    ad_id: typing.Optional[int] = None
    creative_id: typing.Optional[int] = None
    banner_id: typing.Optional[int] = None
    feeds_admin_id: typing.Optional[str] = None
    reject_reason: typing.Optional[str] = None


class CampaignType(str, enum.Enum):
    CPM = 'CPM'
    TEXT = 'Text'
    CPM_BANNER_CAMPAIGN = 'CPM_BANNER_CAMPAIGN'


class CampaignStatus(str, enum.Enum):
    NOT_CREATED = 'not_created'
    IN_CREATION_PROCESS = 'in_creation_process'
    REJECTED = 'rejected'
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    ENDED = 'ended'
    READY = 'ready'
    UPDATING = 'updating'


@dataclasses.dataclass
class Campaign:
    # pylint: disable=invalid-name
    id: str
    campaign_type: CampaignType = CampaignType.CPM_BANNER_CAMPAIGN
    campaign_id: typing.Optional[str] = None
    passport_id: int = 1
    parameters: typing.Optional[dict] = None
    status: CampaignStatus = CampaignStatus.NOT_CREATED
    error: typing.Optional[str] = None
    started_at: typing.Optional[str] = None
    suspended_at: typing.Optional[str] = None
    created_at: str = '2022-04-26T13:41:21.145013+0000'


class AdvertStatus(str, enum.Enum):
    STARTED = 'started'
    PAUSED = 'paused'


class AdvertReasonStatus(str, enum.Enum):
    LOW_RATING = 'low_rating'


class StrategyType(str, enum.Enum):
    AVERAGE_CPC = 'average_cpc'
    AVERAGE_CPA = 'average_cpa'


@dataclasses.dataclass
class Advert:
    # pylint: disable=invalid-name
    id: int
    place_id: int
    average_cpc: int
    campaign_id: typing.Optional[int] = None
    group_id: typing.Optional[int] = None
    ad_id: typing.Optional[int] = None
    content_id: typing.Optional[int] = None
    banner_id: typing.Optional[int] = None
    is_active: bool = False
    error: typing.Optional[str] = None
    passport_id: typing.Optional[int] = None
    weekly_spend_limit: typing.Optional[int] = None
    status: typing.Optional[AdvertStatus] = None
    reason_status: typing.Optional[AdvertReasonStatus] = None
    campaign_type: CampaignType = CampaignType.CPM
    strategy_type: StrategyType = StrategyType.AVERAGE_CPC
    campaign_uuid: typing.Optional[str] = None
    experiment: str = ''


@dataclasses.dataclass
class AdvertForCreate:
    # pylint: disable=invalid-name
    id: int
    token_id: int
    advert_id: int
    average_cpc: int
    creation_started: bool = False
    campaign_uuid: typing.Optional[str] = None
    weekly_spend_limit: typing.Optional[str] = None


@dataclasses.dataclass
class AdvertClient:
    # pylint: disable=invalid-name
    id: int
    client_id: int
    passport_id: str
    created_at: str
    updated_at: str = '2022-04-26T13:41:21.145013+0000'


def get_all_banners(database) -> typing.List[Banner]:
    cursor = database.cursor()
    cursor.execute(
        """
        SELECT
            id,
            place_id,
            inner_campaign_id,
            status,
            image,
            original_image_id,
            image_text,
            group_id,
            ad_id,
            creative_id,
            banner_id,
            feeds_admin_id,
            reject_reason
        FROM eats_restapp_marketing.banners
        ORDER BY id;
        """,
    )

    result = [
        Banner(
            row[0],
            row[1],
            row[2],
            BannerStatus(row[3]),
            row[4],
            row[5],
            row[6],
            row[7],
            row[8],
            row[9],
            row[10],
            row[11],
            row[12],
        )
        for row in cursor.fetchall()
    ]

    return result


def insert_banner(database, banner: Banner) -> int:
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_restapp_marketing.banners (
            place_id,
            inner_campaign_id,
            status,
            image,
            original_image_id,
            image_text,
            group_id,
            ad_id,
            creative_id,
            banner_id,
            feeds_admin_id,
            reject_reason
        ) VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        ) RETURNING id;
        """,
        (
            banner.place_id,
            banner.inner_campaign_id,
            banner.status,
            banner.image,
            banner.original_image_id,
            banner.image_text,
            banner.group_id,
            banner.ad_id,
            banner.creative_id,
            banner.banner_id,
            banner.feeds_admin_id,
            banner.reject_reason,
        ),
    )
    return cursor.fetchall()[0][0]


def get_all_campaigns(database) -> typing.List[Campaign]:
    cursor = database.cursor()
    cursor.execute(
        """
        SELECT
            id,
            campaign_type,
            campaign_id,
            passport_id,
            parameters,
            status,
            error
        FROM eats_restapp_marketing.campaigns
        ORDER BY id;
        """,
    )

    result = [
        Campaign(
            row[0],
            CampaignType(row[1]),
            row[2],
            row[3],
            row[4],
            CampaignStatus(row[5]),
            row[6],
        )
        for row in cursor.fetchall()
    ]

    return result


def insert_campaign(database, campaign: Campaign) -> str:
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_restapp_marketing.campaigns (
            id,
            campaign_type,
            campaign_id,
            passport_id,
            parameters,
            status,
            error,
            started_at,
            suspended_at,
            created_at
        ) VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        ) RETURNING id;
        """,
        (
            campaign.id,
            campaign.campaign_type,
            campaign.campaign_id if campaign.campaign_id else None,
            campaign.passport_id,
            json.dumps(campaign.parameters) if campaign.parameters else None,
            campaign.status,
            campaign.error if campaign.error else None,
            campaign.started_at if campaign.started_at else None,
            campaign.suspended_at if campaign.suspended_at else None,
            campaign.created_at,
        ),
    )
    return cursor.fetchall()[0][0]


def get_all_adverts(database) -> typing.List[Advert]:
    cursor = database.cursor()
    cursor.execute(
        """
        SELECT
            id,
            place_id,
            averagecpc,
            campaign_id,
            group_id,
            ad_id,
            content_id,
            banner_id,
            is_active,
            error,
            passport_id,
            weekly_spend_limit,
            status,
            reason_status,
            campaign_type,
            strategy_type,
            campaign_uuid,
            experiment
        FROM eats_restapp_marketing.advert
        ORDER BY id;
        """,
    )

    result = []
    for row in cursor.fetchall():
        advert_status: typing.Optional[AdvertStatus] = None
        if row[12] is not None:
            advert_status = AdvertStatus(row[12])

        advert_reason_status: typing.Optional[AdvertReasonStatus] = None
        if row[13] is not None:
            advert_reason_status = AdvertReasonStatus(row[13])

        result.append(
            Advert(
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                row[9],
                row[10],
                row[11],
                advert_status,
                advert_reason_status,
                CampaignType(row[14]),
                StrategyType(row[15]),
                row[16],
                row[17],
            ),
        )

    return result


def insert_advert(database, advert: Advert) -> None:
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_restapp_marketing.advert (
            id,
            place_id,
            averagecpc,
            campaign_id,
            group_id,
            ad_id,
            content_id,
            banner_id,
            is_active,
            error,
            passport_id,
            weekly_spend_limit,
            status,
            reason_status,
            campaign_type,
            strategy_type,
            campaign_uuid,
            created_at,
            updated_at,
            experiment
        ) VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            NOW(),
            NOW(),
            %s
        );
        """,
        (
            advert.id,
            advert.place_id,
            advert.average_cpc,
            advert.campaign_id,
            advert.group_id,
            advert.ad_id,
            advert.content_id,
            advert.banner_id,
            advert.is_active,
            advert.error,
            advert.passport_id,
            advert.weekly_spend_limit,
            advert.status,
            advert.reason_status,
            advert.campaign_type,
            advert.strategy_type,
            advert.campaign_uuid,
            advert.experiment,
        ),
    )


def get_all_adverts_for_create(database) -> typing.List[AdvertForCreate]:
    cursor = database.cursor()
    cursor.execute(
        """
        SELECT
            id,
            token_id,
            advert_id,
            averagecpc,
            creation_started,
            campaign_uuid,
            weekly_spend_limit,
        FROM eats_restapp_marketing.advert_for_create
        ORDER BY id;
        """,
    )

    result = []
    for row in cursor.fetchall():
        result.append(
            AdvertForCreate(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6],
            ),
        )

    return result


def insert_advert_for_create(
        database, advert_for_create: AdvertForCreate,
) -> None:
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_restapp_marketing.advert_for_create (
            id,
            token_id,
            advert_id,
            averagecpc,
            creation_started,
            campaign_uuid,
            weekly_spend_limit,
            created_at,
            updated_at
        ) VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            NOW(),
            NOW()
        );
        """,
        (
            advert_for_create.id,
            advert_for_create.token_id,
            advert_for_create.advert_id,
            advert_for_create.average_cpc,
            advert_for_create.creation_started,
            advert_for_create.campaign_uuid,
            advert_for_create.weekly_spend_limit,
        ),
    )


def get_advert_clients(database) -> typing.List[AdvertClient]:
    cursor = database.cursor()
    cursor.execute(
        """
            SELECT
            id,
            client_id,
            passport_id,
            created_at,
            updated_at
            FROM eats_restapp_marketing.advert_clients
            """,
    )
    result = []
    for row in cursor.fetchall():
        result.append(AdvertClient(row[0], row[1], row[2], row[3], row[4]))
    return result


def insert_advert_client(database, advert_client: AdvertClient):
    cursor = database.cursor()
    exec_result = cursor.execute(
        """
            INSERT INTO eats_restapp_marketing.advert_clients (
            id,
            client_id,
            passport_id,
            created_at,
            updated_at
        ) VALUES (
            %s,
            %s,
            %s,
            %s,
            NOW()
        );
            """,
        (
            advert_client.id,
            advert_client.client_id,
            advert_client.passport_id,
            advert_client.created_at,
        ),
    )
