FLEET_TYPE_VEZET = 'vezet'


def check_parks(docs, suffixes):
    assert len(docs) == len(suffixes)

    expected_names = [f'ParkName{num} - Таксометр X' for num in suffixes]
    expected_logins = [f'login{num} - Таксометр X' for num in suffixes]
    for doc in docs:
        assert doc['login'] in expected_logins
        assert doc['name'] in expected_names


def make_driver_mapping_query(**kwargs):
    return (
        """
        INSERT INTO fleet_sync.drivers_mappings
          (park_id, driver_id, mapped_driver_id, app_family)
        VALUES
          ('{park_id}', '{driver_id}', '{mapped_driver_id}', '{app_family}')
        ON CONFLICT DO NOTHING;
        """.format(
            **kwargs,
        )
    )


def add_parks_mappings(pgsql, parks_list, fleet_type):
    values: str = ''
    for park in parks_list:
        values += f"""('{park}', '{park}Mapped', '{fleet_type}'),"""
    values = values[:-1]

    with pgsql['fleet-synchronizer-db'].cursor() as cursor:
        cursor.execute(
            f"""
            INSERT INTO fleet_sync.parks_mappings
              (park_id, mapped_park_id, app_family)
            VALUES {values}
            ON CONFLICT DO NOTHING;
            """,
        )


def clear_parks_mappings(pgsql, fleet_type):
    with pgsql['fleet-synchronizer-db'].cursor() as cursor:
        cursor.execute(
            f"""
            DELETE FROM fleet_sync.parks_mappings
            WHERE app_family = '{fleet_type}';
            """,
        )


def add_parks_mongo(mongodb):
    mongodb.dbparks.insert_many(
        [
            {
                '_id': 'uber_p1',
                'login': 'uber_p1_login',
                'fleet_type': 'uberdriver',
                'is_active': True,
            },
            {
                '_id': 'vezet_p1',
                'login': 'vezet_p1_login',
                'fleet_type': 'vezet',
                'is_active': True,
            },
        ],
    )


def clear_parks_mongo(mongodb):
    mongodb.dbparks.delete_many({'fleet_type': {'$not': {'$eq': 'taximeter'}}})
