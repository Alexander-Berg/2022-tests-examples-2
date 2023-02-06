from projects.geosuggest.pickup_points.common import objects


def create_point():
    return objects.Point(
        id='',
        lon=0,
        lat=0,
        edge_persistent_id='',
        edge_distance=0,
        edge_position=0,
    )


def create_pin():
    return objects.Pin(timestamp=0, lon=0, lat=0)


def create_order_stop():
    return objects.OrderStop(
        order_id='',
        timestamp=0,
        pin_lon=0,
        pin_lat=0,
        stop_type='pickup',
        driver_position=objects.DriverPosition(
            timestamp=0,
            lon=0,
            lat=0,
            point_type='',
            adjusted_lon=0,
            adjusted_lat=0,
            edge_persistent_id='0',
            edge_position=0,
            edge_length=0,
        ),
    )


def create_maps_object():
    return objects.MapsObject(id='', lon=0, lat=0, type_id=0, disp_class=0)


def create_graph_info():
    return objects.GraphInfo(
        lon=0,
        lat=0,
        edge_id=0,
        edge_persistent_id='',
        reversed_edge_id=0,
        reversed_edge_persistent_id='',
        segment_direction=0,
        segment_start=(0, 1),
        segment_end=(1, 0),
        edge_data=objects.EdgeData(
            length=0,
            category=0,
            speed=0,
            speed_limit=None,
            is_toll_road=False,
            is_passable=True,
            access=0,
        ),
        detect_gates_stats=objects.DetectGatesStats(
            edges_visited=123, gates_count=1, loose_ends_count=21,
        ),
        reversed_detect_gates_stats=None,
    )
