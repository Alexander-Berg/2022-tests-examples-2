import math
import random

from simulator.core import structures

METERS_CONVERT_COEF_1 = 0.0000089
METERS_CONVERT_COEF_2 = 0.018


# results are more likely to be in the center
def by_center(
        center: structures.Point, radius: int, distance: float = None,
) -> structures.Point:
    if distance is None:
        distance = random.uniform(-radius, radius)

    # result may differ from 'distance' alot
    meter_coef = distance * METERS_CONVERT_COEF_1
    new_lat = center.lat + meter_coef
    new_lon = center.lon + meter_coef / math.cos(
        center.lat * METERS_CONVERT_COEF_2,
    )

    return structures.Point(lat=new_lat, lon=new_lon)
