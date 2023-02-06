import math


EARTH_RADIUS = 6372795


def approx_distance(pnt1, pnt2):
    lat1, lng1 = math.radians(pnt1[1]), math.radians(pnt1[0])
    lat2, lng2 = math.radians(pnt2[1]), math.radians(pnt2[0])

    sin_lat1, cos_lat1 = math.sin(lat1), math.cos(lat1)
    sin_lat2, cos_lat2 = math.sin(lat2), math.cos(lat2)

    delta_lng = lng2 - lng1
    cos_delta_lng, sin_delta_lng = math.cos(delta_lng), math.sin(delta_lng)

    dist = math.atan2(
        math.sqrt(
            (cos_lat2 * sin_delta_lng) ** 2 +
            (cos_lat1 * sin_lat2 - sin_lat1 * cos_lat2 * cos_delta_lng) ** 2,
        ),
        sin_lat1 * sin_lat2 + cos_lat1 * cos_lat2 * cos_delta_lng,
    )

    return EARTH_RADIUS * dist
