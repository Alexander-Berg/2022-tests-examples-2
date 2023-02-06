import dataclasses
import typing

import pytest

CONSUMER_CPC_EXPERIMENTAL = (
    'eats_restapp_marketing/cpc-create-bulk-experimental'
)


def always_match(
        name: str,
        consumers: typing.List[str],
        value: dict,
        is_config: bool = True,
):
    return pytest.mark.experiments3(
        name=name,
        consumers=consumers,
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always match',
                'predicate': {'type': 'true'},
                'value': value,
            },
        ],
        is_config=is_config,
    )


def token_id_for_exp():
    return always_match(
        name='eats_restapp_marketing_token_id_for_exp',
        consumers=[CONSUMER_CPC_EXPERIMENTAL],
        value={'token_id': 1},
        is_config=True,
    )


def cpm_create_bulk_settings(
        min_average_cpm: float,
        min_spend_limit: float,
        min_spend_cp: float,
        min_spend_wb: float,
):
    return always_match(
        name='eats_restapp_marketing_cpm_create_bulk_settings',
        consumers=['eats_restapp_marketing/cpm-create-bulk'],
        value={
            'min_average_cpm': min_average_cpm,
            'min_spend_limit': min_spend_limit,
            'min_spend_limit_wb_max_impressions': min_spend_wb,
            'min_spend_limit_cp_max_impressions': min_spend_cp,
        },
        is_config=True,
    )


def send_ads_to_direct_moderation(enabled: bool):
    return always_match(
        name='eats_restapp_marketing_send_ads_to_direct_moderation',
        consumers=['eats_restapp_marketing/stq/add_banner_ads'],
        value={'enabled': enabled},
        is_config=True,
    )


@dataclasses.dataclass
class GroupTagging:
    enabled: bool = False
    tags: typing.List[str] = dataclasses.field(default_factory=list)

    def asdict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class AddBannerAds:
    group_tagging: GroupTagging = GroupTagging()

    def asdict(self) -> dict:
        return {'group_tagging': self.group_tagging.asdict()}


def add_banner_ads(settings: AddBannerAds = AddBannerAds()):
    return always_match(
        name='eats_restapp_marketing_add_banner_ads',
        consumers=['eats_restapp_marketing/stq/add_banner_ads'],
        value=settings.asdict(),
        is_config=True,
    )
