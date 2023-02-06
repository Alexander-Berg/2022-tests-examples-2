async def test_add_existing(taxi_eats_user_reactions, pgsql):
    request_json = {
        'eater_id': 'eater_id_1',
        'subject': {'namespace': 'catalog_brand', 'id': 'subject_id_1'},
    }
    response = await taxi_eats_user_reactions.post(
        '/eats-user-reactions/v1/favourites/add', json=request_json,
    )
    assert response.status_code == 204
    assert response.content == b''

    cursor = pgsql['eats_user_reactions'].cursor()
    cursor.execute(
        """SELECT * FROM eats_user_reactions.favourite_reactions
        WHERE eater_id = %s
        AND subject_namespace = %s
        AND subject_id = %s;""",
        (
            request_json['eater_id'],
            request_json['subject']['namespace'],
            request_json['subject']['id'],
        ),
    )
    reactions = list(cursor)
    assert len(reactions) == 1
    assert reactions[0][0] == '9fc54b04-2dd9-4fba-bd0b-6770abb77577'


async def test_add_nonexistent(taxi_eats_user_reactions, pgsql):
    request_json = {
        'eater_id': 'nonexistent_eater_id',
        'subject': {
            'namespace': 'catalog_brand',
            'id': 'nonexistent_subject_id',
        },
    }
    response = await taxi_eats_user_reactions.post(
        '/eats-user-reactions/v1/favourites/add', json=request_json,
    )
    assert response.status_code == 204
    assert response.content == b''

    cursor = pgsql['eats_user_reactions'].cursor()
    cursor.execute(
        """SELECT * FROM eats_user_reactions.favourite_reactions
        WHERE eater_id = %s
        AND subject_namespace = %s
        AND subject_id = %s;""",
        (
            request_json['eater_id'],
            request_json['subject']['namespace'],
            request_json['subject']['id'],
        ),
    )
    reactions = list(cursor)
    assert len(reactions) == 1


async def test_add_removed(taxi_eats_user_reactions, pgsql):
    request_json = {
        'eater_id': 'eater_id_1',
        'subject': {'namespace': 'catalog_brand', 'id': 'subject_id_1'},
    }
    response = await taxi_eats_user_reactions.post(
        '/eats-user-reactions/v1/favourites/remove', json=request_json,
    )
    assert response.status_code == 204
    assert response.content == b''

    response = await taxi_eats_user_reactions.post(
        '/eats-user-reactions/v1/favourites/add', json=request_json,
    )
    assert response.status_code == 204
    assert response.content == b''

    cursor = pgsql['eats_user_reactions'].cursor()
    cursor.execute(
        """SELECT * FROM eats_user_reactions.favourite_reactions
        WHERE eater_id = %s
        AND subject_namespace = %s
        AND subject_id = %s
        AND deleted_at IS NULL;""",
        (
            request_json['eater_id'],
            request_json['subject']['namespace'],
            request_json['subject']['id'],
        ),
    )
    assert list(cursor)
