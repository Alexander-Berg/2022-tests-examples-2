from typing import Any
from typing import Dict


def subscription(
        values: Dict[str, str], settings_type: str = 'driver_fix',
) -> Dict[str, Any]:
    return {'settings': {'type': settings_type, 'values': values}}


# Too short of a name
# pylint: disable=C0103
def ui(
        display_mode: str,
        display_profile: str,
        feature_toggles: Dict[str, Any],
        taximeter_polling_policy: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        'display_mode': display_mode,
        'display_profile': display_profile,
        'feature_toggles': feature_toggles,
        'taximeter_polling_policy': taximeter_polling_policy,
    }
