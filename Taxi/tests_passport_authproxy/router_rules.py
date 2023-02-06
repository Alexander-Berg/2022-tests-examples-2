from typing import Any
from typing import Dict


def make_route_rule(
        prefix: str,
        required_scopes_alias: str,
        authorization_required: bool = True,
) -> dict:
    proxy_settings: Dict[str, Any] = {
        'required-scopes-alias': required_scopes_alias,
    }

    if not authorization_required:
        proxy_settings['proxy-401'] = True

    rule = {
        'input': {'http-path-prefix': prefix},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': proxy_settings,
    }

    return rule
