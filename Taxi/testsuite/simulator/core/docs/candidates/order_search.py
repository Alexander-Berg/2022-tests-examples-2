"""
    Structure for candidates/order-search request.
"""

import collections
import dataclasses
from typing import Dict
from typing import List
from typing import Set

from simulator.core import structures


@dataclasses.dataclass
class OrderSearchRequest:
    point: structures.Point

    # taxi_class -> special_requirement_ids
    special_requirements: Dict[str, Set[str]]

    segment_ids: List[str]

    def __init__(self, request_body: dict):
        order_json = request_body['order']
        point_json = request_body['point']
        virtual_tariffs_json = order_json.get('virtual_tariffs')

        self.point = structures.Point(
            lon=float(point_json[0]), lat=float(point_json[1]),
        )
        self.segment_ids = order_json['cargo_ref_ids']
        self.special_requirements = collections.defaultdict(set)

        if virtual_tariffs_json:
            for special_requirement_json in virtual_tariffs_json:
                taxi_class = special_requirement_json['class']
                special_requirement_ids = {
                    d['id']
                    for d in special_requirement_json['special_requirements']
                }

                self.special_requirements[
                    taxi_class
                ] |= special_requirement_ids
