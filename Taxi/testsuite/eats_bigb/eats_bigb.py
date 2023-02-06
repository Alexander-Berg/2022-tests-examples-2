import dataclasses
import enum
import typing

from google.protobuf import json_format
import pytest
# pylint: disable=import-error
from yabs.proto import user_profile_pb2  # noqa: F401

UPDATE_TIME = 1613372688


class Gender(enum.Enum):
    # Male
    MALE = 0
    # Female
    FEMALE = 1


class AgeCategory(enum.Enum):
    # 0 - below 18;
    LESS_THEN_18 = 0
    # 1 - 18-24;
    BETWEEN_18_AND_24 = 1
    # 2 - 25-34;
    BETWEEN_25_AND_34 = 2
    # 3 - 35-44;
    BETWEEN_35_AND_44 = 3
    # 4 - 45-54;
    BETWEEN_45_AND_54 = 4
    # 5 - 55 and older
    GREATER_THEN_55 = 5


class IncomeLevel(enum.Enum):
    # 0: possible low income level. (A OMI/TNS)
    LOW = 0
    # 1: possible below average income level. (B OMI/TNS)
    BELOW_AVERAGE = 1
    # 2: possible slightly above average income level. (B OMI/TNS)
    SLIGHTLY_ABOVE_AVERAGE = 2
    # 3: possible above average income level. (С OMI/TNS)
    ABOVE_AVERAGE = 3
    # 4: possible well above average income level. (С OMI/TNS)
    WELL_ABOVE_AVERAGE = 4


@dataclasses.dataclass
class Demograpics:
    # User's gender
    gender: typing.Optional[Gender] = None
    # User's age category
    age_category: typing.Optional[AgeCategory] = None
    # User's income level
    income_level: typing.Optional[IncomeLevel] = None


@dataclasses.dataclass
class BrandStatistics:
    # Number of times user has seen brand's place.
    views: int = 0
    # Number of times user has visited (opened/clicked) brand's place.
    opens: int = 0


@dataclasses.dataclass
class Profile:
    passport_uid: str = ''
    # User's brand statistics.
    brand_stats: typing.Dict[int, BrandStatistics] = dataclasses.field(
        default_factory=dict,
    )
    # User's social-demographic data.
    demographics: Demograpics = Demograpics()
    # Common heuristic segments.
    heuristic_segments: typing.Set[int] = dataclasses.field(
        default_factory=set,
    )
    # Common audience segments.
    audience_segments: typing.Set[int] = dataclasses.field(default_factory=set)
    # Yandex.Crypta longterm interests segments.
    longterm_interests_segments: typing.Set[int] = dataclasses.field(
        default_factory=set,
    )
    # Yandex.Crypta shortterm interests segments.
    shortterm_interests_segments: typing.Set[int] = dataclasses.field(
        default_factory=set,
    )


def append_demographics(
        items: typing.List[typing.Dict], demographics: Demograpics,
) -> None:
    if demographics.gender is not None:
        items.append(
            {
                'keyword_id': 569,
                'pair_values': [
                    {'first': '174', 'second': str(demographics.gender.value)},
                ],
                'update_time': UPDATE_TIME,
            },
        )

    if demographics.age_category is not None:
        items.append(
            {
                'keyword_id': 569,
                'pair_values': [
                    {
                        'first': '543',
                        'second': str(demographics.age_category.value),
                    },
                ],
                'update_time': UPDATE_TIME,
            },
        )

    if demographics.income_level is not None:
        items.append(
            {
                'keyword_id': 569,
                'pair_values': [
                    {
                        'first': '614',
                        'second': str(demographics.income_level.value),
                    },
                ],
                'update_time': UPDATE_TIME,
            },
        )


def append_brand_stats(
        items: typing.List[typing.Dict],
        brand_stats: typing.Dict[int, BrandStatistics],
) -> None:
    for brand_id in brand_stats:
        items.append(
            {
                'keyword_id': 1112,
                'trio_values': [
                    {
                        'first': str(brand_id),  # brand_id
                        'second': str(brand_stats[brand_id].views),  # views
                        'third': str(brand_stats[brand_id].opens),  # clicks
                    },
                ],
                'update_time': UPDATE_TIME,
            },
        )


def append_uint_values(
        items: typing.List[typing.Dict],
        keyword_id: int,
        values: typing.Set[int],
) -> None:
    items.append(
        {
            'keyword_id': keyword_id,
            'uint_values': list(values),
            'update_time': UPDATE_TIME,
        },
    )


def profile_to_proto(profile: typing.Optional[Profile]) -> str:

    items: typing.List[typing.Dict] = []
    if profile is not None:
        append_demographics(items, profile.demographics)
        append_brand_stats(items, profile.brand_stats)
        append_uint_values(items, 547, profile.heuristic_segments)
        append_uint_values(items, 557, profile.audience_segments)
        append_uint_values(items, 601, profile.longterm_interests_segments)
        append_uint_values(items, 602, profile.shortterm_interests_segments)

    msg = user_profile_pb2.Profile()
    json_format.ParseDict({'items': items}, msg)
    return msg.SerializeToString(deterministic=True)


@pytest.fixture(name='bigb', autouse=True)
def bigb(request, mockserver):
    class Context:
        profiles: typing.Dict[str, Profile] = {}

        def add_profile(self, passport_uid: str, profile: Profile) -> None:
            self.profiles[passport_uid] = profile

        def remove_profile(self, passport_uid: str):
            self.profiles.pop(passport_uid)

        @property
        def times_called(self) -> int:
            return handle.times_called

    ctx = Context()

    @mockserver.json_handler('/bigb/bigb')
    def handle(request):
        assert request.args['format'] == 'protobuf', 'Invalid request format'
        assert request.args['client'], 'Client is required'
        assert request.args['puid'], 'Passport uid is required'

        profile = ctx.profiles.get(request.args['puid'], None)
        print(profile)
        return mockserver.make_response(profile_to_proto(profile))

    marker = request.node.get_closest_marker('bigb')
    if marker:
        if isinstance(marker.args[0], Profile):
            ctx.add_profile(marker.args[0].passport_uid, marker.args[0])

    return ctx
