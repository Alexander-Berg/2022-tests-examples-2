import json
import uuid

import ammo

AMMO_FILE_NAME_PATTERN = 'launch/generated_{name}_ammo.txt'
DEFAULT_TOKEN = 'test_token'


def make_simple_launch_ammo():
    return ammo.make_ammo(
        'simple_launch', 'POST', '/3.0/launch',
        headers=ammo.DEFAULT_HEADERS,
        body=json.dumps({})
    )


def make_launch_by_user_id_and_token_ammo(user_id, token):
    headers = ammo.DEFAULT_HEADERS.copy()
    headers['Authorization'] = 'Bearer ' + token
    return ammo.make_ammo(
        'token ' + 'user_id', 'POST', '/3.0/launch',
        headers=headers,
        body=json.dumps({'id': user_id})
    )


def make_launch_with_multiple_users_ids_with_token_ammo(user_ids):
    lines = []
    for user_id in user_ids:
        lines.append(
            make_launch_by_user_id_and_token_ammo(user_id, DEFAULT_TOKEN)
        )
    return '\n'.join(lines)


def make_launch_mixed(user_ids):
    lines = []
    for user_id in user_ids:
        lines.append(
            make_launch_by_user_id_and_token_ammo(user_id, DEFAULT_TOKEN)
        )
        lines.append(
            make_simple_launch_ammo()
        )
    return '\n'.join(lines)


def get_uids(n):
    # TODO: stub
    return {str(uuid.uuid4()) for _ in xrange(n)}


if __name__ == '__main__':
    N = 100
    user_ids = get_uids(N)
    ammo.store_ammo(
        AMMO_FILE_NAME_PATTERN,
        'simple_launch',
        make_simple_launch_ammo
    )
    ammo.store_ammo(
        AMMO_FILE_NAME_PATTERN,
        'launch_with_multiple_users_ids_with_token', lambda:
        make_launch_with_multiple_users_ids_with_token_ammo(user_ids)
    )
    ammo.store_ammo(
        AMMO_FILE_NAME_PATTERN,
        'make_launch_mixed',
        lambda: make_launch_mixed(user_ids)
    )
