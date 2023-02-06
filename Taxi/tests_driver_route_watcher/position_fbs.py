# pylint: disable=import-error
import math

import geometry.fbs.Position as FbsPosition


def _round_away_from_zero(value):
    abs_value = abs(value)
    res = math.floor(abs_value) + math.floor(2 * (abs_value % 1))
    return res if value >= 0.0 else -res


def serialize_position(builder, pos):
    lon = int(_round_away_from_zero(pos[0] * 1000000))
    lat = int(_round_away_from_zero(pos[1] * 1000000))
    return FbsPosition.CreatePosition(builder, lon, lat)


def deserialize_position(fbs_position):
    return [fbs_position.Longitude() / 1e6, fbs_position.Latitude() / 1e6]
