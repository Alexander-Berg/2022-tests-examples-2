"""
    Structure for point object
"""

import dataclasses
from typing import Set


@dataclasses.dataclass
class SpecialRequirement:
    id: str  # pylint: disable=invalid-name
    required_tags: Set[str] = dataclasses.field(default_factory=set)
