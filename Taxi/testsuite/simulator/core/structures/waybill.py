"""
    Structure for dispatch waybill and candidate
"""

import dataclasses
from typing import Optional

from tests_united_dispatch.plugins import candidates_manager
from tests_united_dispatch.plugins import cargo_dispatch_manager


@dataclasses.dataclass
class DispatchWaybill:
    info: cargo_dispatch_manager.Waybill
    candidate: Optional[candidates_manager.Candidate] = None
    is_accepted_by_candidate: bool = False

    # pylint: disable=invalid-name
    @property
    def id(self) -> str:
        return self.info.id
