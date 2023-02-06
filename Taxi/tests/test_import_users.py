from taxi.crm.masshire.tools.import_amocrm_users.lib.import_users import transform_users


def test_transform_users__given_non_active_user__ignores_it() -> None:
    result = transform_users(
        [
            {
                "id": 42,
                "email": "",
                "rights": {"is_active": False},
            }
        ]
    )

    assert len(result) == 0


def test_transform_users__given_non_yandex_user__ignores_it() -> None:
    result = transform_users(
        [
            {
                "id": 42,
                "email": "user@example.com",
                "rights": {"is_active": True},
            }
        ]
    )

    assert len(result) == 0


def test_transform_users__given_yandex_user__transforms_it() -> None:
    result = transform_users(
        [
            {
                "id": 42,
                "email": "user@yandex-team.com",
                "rights": {"is_active": True},
            }
        ]
    )

    assert len(result) == 1
    assert result[0].login == "user"
    assert result[0].amo_id == 42
