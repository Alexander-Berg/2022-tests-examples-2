from typing import Any
from typing import Dict


def make_route_rule(
        prefix: str, required_scopes_alias: str, auth_type: str,
) -> dict:
    proxy_settings: Dict[str, Any] = {
        'auth-type': auth_type,
        'required-scopes-alias': required_scopes_alias,
    }

    rule = {
        'input': {'http-path-prefix': prefix},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': proxy_settings,
    }

    return rule
