import flatbuffers

from eventus_orchestrator_mock import fbs_tools


def _make_point(builder, point):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_polygon_values_response import (  # noqa: IS001
        Point,
    )

    response = Point
    response.PointStart(builder)
    response.PointAddLon(builder, point['lon'])
    response.PointAddLat(builder, point['lat'])
    return response.PointEnd(builder)


def _make_coordinates(builder, coordinates):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_polygon_values_response import (  # noqa: IS001
        Coordinates,
    )
    response = Coordinates

    points_obj = fbs_tools.make_fbs_vector_via_func(
        builder,
        coordinates['points'],
        _make_point,
        response.CoordinatesStartPointsVector,
    )

    response.CoordinatesStart(builder)
    response.CoordinatesAddPoints(builder, points_obj)
    return response.CoordinatesEnd(builder)


def _make_polygon(builder, polygon):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_polygon_values_response import (  # noqa: IS001
        Polygon,
    )
    response = Polygon

    polygon_id = builder.CreateString(polygon['polygon_id'])
    groups_obj = fbs_tools.make_fbs_vector_via_func(
        builder,
        polygon['groups'],
        fbs_tools.make_fbs_string,
        response.PolygonStartGroupsVector,
    )
    coordinates_obj = fbs_tools.make_fbs_vector_via_func(
        builder,
        polygon['coordinates'],
        _make_coordinates,
        response.PolygonStartCoordinatesVector,
    )

    response.PolygonStart(builder)
    response.PolygonAddPolygonId(builder, polygon_id)
    response.PolygonAddGroups(builder, groups_obj)
    response.PolygonAddCoordinates(builder, coordinates_obj)
    response.PolygonAddEnabled(builder, polygon['enabled'])
    return response.PolygonEnd(builder)


def make_polygon_values_response(polygons_dict):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_polygon_values_response import (  # noqa: IS001
        PolygonValuesResponse,
    )
    response = PolygonValuesResponse

    builder = flatbuffers.Builder(0)

    cursor_obj = builder.CreateString(polygons_dict['cursor'])
    polygons_obj = fbs_tools.make_fbs_vector_via_func(
        builder,
        polygons_dict['polygons'],
        _make_polygon,
        response.PolygonValuesResponseStartPolygonsVector,
    )

    response.PolygonValuesResponseStart(builder)
    response.PolygonValuesResponseAddCursor(builder, cursor_obj)
    response.PolygonValuesResponseAddPolygons(builder, polygons_obj)
    obj = response.PolygonValuesResponseEnd(builder)
    builder.Finish(obj)
    return bytes(builder.Output())
