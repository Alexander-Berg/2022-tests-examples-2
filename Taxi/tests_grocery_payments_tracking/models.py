import dataclasses
from typing import Dict


@dataclasses.dataclass
class Payment:
    order_id: str
    status: str
    payload: Dict
