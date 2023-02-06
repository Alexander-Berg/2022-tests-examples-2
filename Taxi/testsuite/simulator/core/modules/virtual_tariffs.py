"""
    Describes virtual-tariffs (aka special requirements) model.

    Storage and API over special requirements.
"""
from typing import Dict
from typing import Set

from simulator.core import structures


class VirtualTariffsModel:
    # all special requirements. id -> rule
    _SPECIAL_REQUIRMENTS: Dict[str, structures.SpecialRequirement] = {}

    @classmethod
    def add(cls, special_requirement: structures.SpecialRequirement):
        assert special_requirement.id not in cls._SPECIAL_REQUIRMENTS

        cls._SPECIAL_REQUIRMENTS[special_requirement.id] = special_requirement

    @classmethod
    def clear(cls):
        cls._SPECIAL_REQUIRMENTS.clear()

    @classmethod
    def satisfy_candidate_classes(
            cls,
            special_requirements: Dict[str, Set[str]],
            candidate: structures.DispatchCandidate,
            allowed_classes: Set[str],
    ) -> Set[str]:
        allowed_classes &= set(candidate.info.classes)
        for (
                taxi_class,
                special_requirement_ids,
        ) in special_requirements.items():
            if cls._satisfy_candidate_class(
                    special_requirement_ids=special_requirement_ids,
                    candidate=candidate,
            ):
                continue
            allowed_classes.discard(taxi_class)
        return allowed_classes

    @classmethod
    def _satisfy_candidate_class(
            cls,
            special_requirement_ids: Set[str],
            candidate: structures.DispatchCandidate,
    ) -> bool:
        for special_requirement_id in special_requirement_ids:
            special_requirement = cls._SPECIAL_REQUIRMENTS.get(
                special_requirement_id,
            )
            assert (
                special_requirement is not None
            ), f'unknown special requirement {special_requirement}'
            if not special_requirement.required_tags.issubset(candidate.tags):
                return False
        return True
