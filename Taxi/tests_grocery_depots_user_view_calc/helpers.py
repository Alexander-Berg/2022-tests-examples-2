def prepare_depots(grocery_depots):
    depot = grocery_depots.add_depot(1, auto_add_zone=False)

    depot.add_zone(
        zone_id='foot_old',
        effective_from='2018-01-01T12:00:00+0000',
        effective_till='2019-01-02T12:00:00+0000',
        geozone={
            'type': 'MultiPolygon',
            'coordinates': [
                [
                    [
                        {'lon': 0.1, 'lat': 0.0},
                        {'lon': 0.1, 'lat': 0.1},
                        {'lon': 0.2, 'lat': 0.1},
                        {'lon': 0.2, 'lat': 0.0},
                        {'lon': 0.1, 'lat': 0.0},
                    ],
                ],
            ],
        },
    )

    depot.add_zone(
        zone_id='foot_new',
        effective_from='2019-01-02T12:00:00+0000',
        geozone={
            'type': 'MultiPolygon',
            'coordinates': [
                [
                    [
                        {'lon': 0.2, 'lat': 0.1},
                        {'lon': 0.3, 'lat': 0.2},
                        {'lon': 0.3, 'lat': 0.1},
                        {'lon': 0.2, 'lat': 0.1},
                    ],
                ],
            ],
        },
    )

    depot.add_zone(
        zone_id='foot_new_112',
        effective_from='2018-01-01T12:00:00+0000',
        effective_till='2019-01-02T12:00:00+0000',
        geozone={
            'type': 'MultiPolygon',
            'coordinates': [
                [
                    [
                        {'lon': 0.15, 'lat': 0.0},
                        {'lon': 0.3, 'lat': 0.2},
                        {'lon': 0.3, 'lat': 0.1},
                        {'lon': 0.15, 'lat': 0.0},
                    ],
                ],
            ],
        },
    )

    depot_2 = grocery_depots.add_depot(
        2, status='coming_soon', auto_add_zone=False,
    )
    depot_2.add_zone(
        zone_id='soon_zone_1',
        effective_from='2018-01-01T12:00:00+0000',
        effective_till='2019-01-02T12:00:00+0000',
        geozone={
            'type': 'MultiPolygon',
            'coordinates': [
                [
                    [
                        {'lon': 0.1, 'lat': 0.0},
                        {'lon': 0.1, 'lat': 0.1},
                        {'lon': 0.2, 'lat': 0.1},
                        {'lon': 0.2, 'lat': 0.0},
                        {'lon': 0.1, 'lat': 0.0},
                    ],
                ],
            ],
        },
    )

    depot_2.add_zone(
        zone_id='soon_zone_2',
        effective_from='2019-01-01T12:00:00+0000',
        geozone={
            'type': 'MultiPolygon',
            'coordinates': [
                [
                    [
                        {'lon': 0.2, 'lat': 0.1},
                        {'lon': 0.3, 'lat': 0.2},
                        {'lon': 0.3, 'lat': 0.1},
                        {'lon': 0.2, 'lat': 0.1},
                    ],
                ],
            ],
        },
    )

    depot_2.add_zone(
        zone_id='soon_zone_3',
        effective_from='2018-01-01T12:00:00+0000',
        effective_till='2019-01-02T12:00:00+0000',
        geozone={
            'type': 'MultiPolygon',
            'coordinates': [
                [
                    [
                        {'lon': 0.15, 'lat': 0.0},
                        {'lon': 0.3, 'lat': 0.2},
                        {'lon': 0.3, 'lat': 0.1},
                        {'lon': 0.15, 'lat': 0.0},
                    ],
                ],
            ],
        },
    )
