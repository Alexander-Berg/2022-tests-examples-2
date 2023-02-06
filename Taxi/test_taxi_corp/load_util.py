def load_access_data(load_json, yandex_uid):
    mock_access_data = load_json('mock_access_data.json')
    perms_by_role = load_json('access_data_permissions_by_role.json')

    for access_data in mock_access_data:
        if access_data['yandex_uid'] == yandex_uid:
            role = access_data['role']
            access_data['permissions'] = perms_by_role[role]
            return access_data
    return None
