import math
from typing import List

from simulator.core import structures

# approximate radius of earth in meters
EARTH_RADIUS = 6373.0 * 1000.0


def between_coordinates(
        first: structures.Point, second: structures.Point,
) -> float:
    """
    Calculates the Haversine distance.
    Returns distance in meters.
    """

    lat1 = math.radians(first.lat)
    lon1 = math.radians(first.lon)
    lat2 = math.radians(second.lat)
    lon2 = math.radians(second.lon)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a_part = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    coef = 2 * math.atan2(math.sqrt(a_part), math.sqrt(1 - a_part))

    return EARTH_RADIUS * coef


def path_distance(path: List[structures.Point]) -> float:
    route_distance = 0.0
    for i in range(len(path) - 1):
        route_distance += between_coordinates(path[i], path[i + 1])
    return route_distance


def get_current_position(
        start_point: structures.Point,
        end_point: structures.Point,
        passed_meters: float,
) -> structures.Point:
    """
    Get new position between two points in passed meters from start
    """

    lat_meters_coef = 180.0 / math.pi / EARTH_RADIUS
    lon_meters_coef = lat_meters_coef / math.cos(
        math.pi * (start_point.lat + end_point.lat) / 360.0,
    )

    lat_distance = (end_point.lat - start_point.lat) / lat_meters_coef
    lon_distance = (end_point.lon - start_point.lon) / lon_meters_coef

    distance = math.sqrt(
        lat_distance * lat_distance + lon_distance * lon_distance,
    )
    if distance < 1.0:
        return end_point

    ratio = passed_meters / distance

    if ratio >= 1:
        return end_point

    new_lat = start_point.lat + lat_meters_coef * ratio * lat_distance
    new_lon = start_point.lon + lon_meters_coef * ratio * lon_distance

    return structures.Point(lat=new_lat, lon=new_lon)
