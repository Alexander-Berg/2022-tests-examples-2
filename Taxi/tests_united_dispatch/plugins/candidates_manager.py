"""
    Describe here candidates specific models.
"""
import dataclasses
import typing
import uuid


@dataclasses.dataclass
class CandidateRouteInfo:
    time: int
    distance: int
    approximate: bool


@dataclasses.dataclass
class CandidateChainInfo:
    destination: typing.List[float]  # lon lat Finish point of current order
    left_time: int  # Left time in seconds
    left_dist: int  # Left distance in meters
    order_id: str  # Current taxi order ID


@dataclasses.dataclass
class Candidate:
    park_id: str  # dbid
    driver_profile_id: str  # uuid
    position: typing.List[float]  # lon lat
    classes: typing.Set[str]  # allowed classes
    route_info: CandidateRouteInfo
    status: str  # busy/online/offline
    transport_type: str  # see __post_init__ for enum values
    score: int
    chain_info: typing.Optional[CandidateChainInfo]

    assigned_at: str

    # pylint: disable=invalid-name
    @property
    def id(self):
        return f'{self.park_id}_{self.driver_profile_id}'

    def is_free(self):
        return self.status == 'online'

    def is_busy(self):
        return not self.is_free()

    def set_free(self):
        self.status = 'online'

    def set_busy(self):
        self.status = 'busy'

    def __post_init__(self):
        assert self.status in {'busy', 'online', 'offline'}
        assert self.transport_type in {
            'car',
            'pedestrian',
            'bicycle',
            'electric_bicycle',
            'motorcycle',
            'rover',
            'courier_car',
            'courier_moto',
        }

    def delete_chain_info(self):
        self.chain_info = None

    def set_chain_info(
            self,
            destination: typing.List[float],
            left_time: int,
            left_dist: int,
            taxi_order_id: str,
    ):
        self.chain_info = CandidateChainInfo(
            destination=destination,
            left_time=left_time,
            left_dist=left_dist,
            order_id=taxi_order_id,
        )


def make_candidate(
        park_id=None,
        driver_profile_id=None,
        position=None,
        classes=None,
        status='online',
        route_info_time=10,
        route_info_dist=120,
        route_info_approximate=False,
        transport_type='car',
        score=0,
        chain_info_json=None,
        assigned_at='2021-12-13T10:00:00.000000+00:00',
) -> Candidate:
    if park_id is None:
        park_id = uuid.uuid4().hex
    if driver_profile_id is None:
        driver_profile_id = uuid.uuid4().hex
    if position is None:
        position = [37.0, 55.0]
    if classes is None:
        classes = ['eda', 'lavka', 'courier', 'express']

    chain_info: typing.Optional[CandidateChainInfo] = None
    if chain_info_json:
        chain_info = _parse_chain_info(chain_info_json)

    return Candidate(
        park_id=park_id,
        driver_profile_id=driver_profile_id,
        position=position,
        classes=classes,
        route_info=CandidateRouteInfo(
            time=route_info_time,
            distance=route_info_dist,
            approximate=route_info_approximate,
        ),
        status=status,
        transport_type=transport_type,
        chain_info=chain_info,
        score=score,
        assigned_at=assigned_at,
    )


def _parse_chain_info(chain_info_json: dict) -> CandidateChainInfo:
    return CandidateChainInfo(
        destination=chain_info_json['destination'],
        left_time=chain_info_json['left_time'],
        left_dist=chain_info_json['left_dist'],
        order_id=chain_info_json['order_id'],
    )


def _parse_route_info(route_info_json: dict) -> CandidateRouteInfo:
    return CandidateRouteInfo(
        time=route_info_json['time'],
        distance=route_info_json['distance'],
        approximate=route_info_json['approximate'],
    )


def parse_candidate(candidate_info: dict, assigned_at: str) -> Candidate:
    chain_info_json = candidate_info.get('chain_info', None)
    chain_info: typing.Optional[CandidateChainInfo] = None
    if chain_info_json:
        chain_info = _parse_chain_info(chain_info_json)

    return Candidate(
        park_id=candidate_info['dbid'],
        driver_profile_id=candidate_info['uuid'],
        position=candidate_info['position'],
        classes=candidate_info['classes'],
        status=candidate_info['status']['status'],
        transport_type=candidate_info['transport']['type'],
        score=candidate_info.get('score', 0),
        route_info=_parse_route_info(candidate_info['route_info']),
        chain_info=chain_info,
        assigned_at=assigned_at,
    )
