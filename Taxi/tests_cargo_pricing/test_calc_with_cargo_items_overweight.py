from tests_cargo_pricing import utils


def _make_item(quantity, weight, dropoff_id, return_id=None):
    item = {
        'dropoff_point_id': dropoff_id,
        'pickup_point_id': 'pu',
        'quantity': quantity,
        'size': {'height': 0.5, 'length': 20.0, 'width': 5.8},
        'weight': weight,
    }
    if return_id is not None:
        item['return_point_id'] = return_id
    return item


def _make_point(id_, coord, type_=None):
    return {
        'id': id_,
        'type': 'dropoff' if type_ is None else type_,
        'position': coord,
        'first_time_arrived_at': utils.from_start(minutes=11),
        'resolution_info': {
            'resolved_at': utils.from_start(minutes=11),
            'resolution': 'delivered',
        },
    }


def _reset_items_and_waypoints(v1_calc_creator):
    v1_calc_creator.payload['waypoints'] = [
        _make_point(id_='pu', coord=[37.544, 55.906], type_='pickup'),
        # two mergable dropoff points
        _make_point(id_='do1', coord=[37.544, 55.916]),
        _make_point(id_='do2', coord=[37.544, 55.916]),
        _make_point(id_='do3', coord=[37.554, 55.916]),
        _make_point(id_='do4', coord=[37.554, 55.906]),
        _make_point(id_='rp', coord=[37.544, 55.906], type_='return'),
    ]

    v1_calc_creator.payload['cargo_items'] = [
        _make_item(quantity=4, weight=4.1, dropoff_id='do1'),
        _make_item(quantity=1, weight=5.1, dropoff_id='do1', return_id='rp'),
        _make_item(quantity=3, weight=2.8, dropoff_id='do2', return_id='rp'),
        _make_item(quantity=7, weight=3.0, dropoff_id='do3'),
        _make_item(quantity=1, weight=2.5, dropoff_id='do4'),
        _make_item(quantity=3, weight=400, dropoff_id='wrong_id'),
        _make_item(quantity=1, weight=250, dropoff_id=''),
    ]


def _reset_items_and_waypoints2(v1_calc_creator):
    v1_calc_creator.payload['waypoints'] = [
        _make_point(id_='pu', coord=[37.544, 55.906], type_='pickup'),
        _make_point(id_='do1', coord=[37.544, 55.916]),
        _make_point(id_='rp', coord=[37.544, 55.906], type_='return'),
    ]

    v1_calc_creator.payload['cargo_items'] = [
        _make_item(quantity=4, weight=4.1, dropoff_id='do1'),
        _make_item(quantity=1, weight=3.4, dropoff_id='do1', return_id='rp'),
    ]


async def test_calc_with_linear_overweight_and_merging_points(
        v1_calc_creator,
        setup_merge_waypoints_config,
        setup_linear_overweight_config,
):
    _reset_items_and_waypoints(v1_calc_creator)

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['linear_overweight'] == 14
    assert utils.discrete_overweight_count(user_options) == 0


async def test_calc_with_linear_overweight(
        v1_calc_creator, setup_linear_overweight_config,
):
    _reset_items_and_waypoints(v1_calc_creator)

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['linear_overweight'] == 8
    assert utils.discrete_overweight_count(user_options) == 0


async def test_calc_with_discrete_overweight_and_merging_points(
        v1_calc_creator,
        setup_merge_waypoints_config,
        setup_discrete_overweight_config,
):
    _reset_items_and_waypoints(v1_calc_creator)

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert 'linear_overweight' not in user_options
    assert user_options['discrete_overweight.small'] == 1
    assert 'discrete_overweight.medium' not in user_options
    assert user_options['discrete_overweight.large'] == 1


async def test_calc_with_discrete_overweight(
        v1_calc_creator, setup_discrete_overweight_config,
):
    _reset_items_and_waypoints(v1_calc_creator)

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert 'linear_overweight' not in user_options
    assert user_options['discrete_overweight.small'] == 2
    assert 'discrete_overweight.medium' not in user_options
    assert 'discrete_overweight.large' not in user_options


async def test_calc_with_disabled_overweight_config(
        v1_calc_creator, setup_disabled_overweight_config,
):
    _reset_items_and_waypoints(v1_calc_creator)

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert 'linear_overweight' not in user_options
    assert 'discrete_overweight.small' not in user_options
    assert 'discrete_overweight.medium' not in user_options
    assert 'discrete_overweight.large' not in user_options


async def test_calc_with_linear_overweight_below_threshold(
        v1_calc_creator, setup_linear_overweight_config,
):
    _reset_items_and_waypoints2(v1_calc_creator)

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert 'linear_overweight' not in user_options
    assert utils.discrete_overweight_count(user_options) == 0


async def test_calc_with_linear_overweight_equal_threshold(
        v1_calc_creator, setup_linear_overweight_config,
):
    _reset_items_and_waypoints2(v1_calc_creator)
    v1_calc_creator.payload['cargo_items'].append(
        _make_item(quantity=1, weight=0.2, dropoff_id='do1'),
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert 'linear_overweight' not in user_options
    assert utils.discrete_overweight_count(user_options) == 0


async def test_calc_with_linear_overweight_between_threshold_and_min(
        v1_calc_creator, setup_linear_overweight_config,
):
    _reset_items_and_waypoints2(v1_calc_creator)
    v1_calc_creator.payload['cargo_items'].append(
        _make_item(quantity=1, weight=0.4, dropoff_id='do1'),
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['linear_overweight'] == 4
    assert utils.discrete_overweight_count(user_options) == 0


async def test_calc_with_linear_overweight_above_min(
        v1_calc_creator, setup_linear_overweight_config,
):
    _reset_items_and_waypoints2(v1_calc_creator)
    v1_calc_creator.payload['cargo_items'].append(
        _make_item(quantity=1, weight=4.4, dropoff_id='do1'),
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['linear_overweight'] == 5
    assert utils.discrete_overweight_count(user_options) == 0
