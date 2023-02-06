"""
    Structure for dispatch output
"""

import dataclasses
from typing import List

from . import waybill as waybill_structures


@dataclasses.dataclass
class DispatchOutput:
    propositions: List[waybill_structures.DispatchWaybill]
    assigned_candidates: List[waybill_structures.DispatchWaybill]
    passed_segment_ids: List[str]
    skipped_segment_ids: List[str]
