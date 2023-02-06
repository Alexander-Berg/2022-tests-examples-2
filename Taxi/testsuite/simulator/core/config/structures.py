import datetime
from typing import Dict
from typing import Optional

import pydantic


class CandidatesSpeedSettings(pydantic.BaseSettings):
    # m/s
    pedestrian: float = 1.2
    # m/s
    car: float = 16.0


class OrderSearchSettings(pydantic.BaseSettings):
    # search radius in meters, straight line distance
    search_radius_m: Optional[int] = 1000

    # search radius in seconds, straight line distance
    search_radius_sec: Optional[int] = 600

    # only N best candidates in response
    candidates_limit: int = 20


class CandidatesSettings(pydantic.BaseSettings):
    # constant speed by transport type
    speed: CandidatesSpeedSettings = pydantic.Field(
        default_factory=CandidatesSpeedSettings,
    )

    # waybill will be accepted by candidate with this probability
    # value must be in [0,1]
    acceptance_rate: float = 0.8

    # max candidates in order-search response
    max_in_response: int = 50


class DispatchSettings(pydantic.BaseSettings):
    # interval between sequential planner runs
    run_interval: datetime.timedelta = datetime.timedelta(seconds=5)

    # total timeout to avoid infinity addition of new planner runs
    total_timeout: datetime.timedelta = datetime.timedelta(hours=1)

    # max segments per run
    max_segments: int = 100

    # max active waybills per run
    max_active_waybills: int = 100


class ScoringSettings(pydantic.BaseSettings):
    # score = TAG_SCORE_COEFF * ((1 - ALPHA) * ETA + ALPHA * BETA * DISTANCE)
    #     - limit(sum(bonuses))
    alpha: float = 0.0
    beta: float = 0.0
    tag_score_coeffs: Dict[str, float] = pydantic.Field(default_factory=dict)


class Settings(pydantic.BaseSettings):
    dispatch: DispatchSettings = pydantic.Field(
        default_factory=DispatchSettings,
    )
    candidates: CandidatesSettings = pydantic.Field(
        default_factory=CandidatesSettings,
    )
    order_search: OrderSearchSettings = pydantic.Field(
        default_factory=OrderSearchSettings,
    )
    scoring: ScoringSettings = pydantic.Field(default_factory=ScoringSettings)
