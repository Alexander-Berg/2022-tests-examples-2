import math

_CONFIG = {'eccentricity': 0.0818191908426, 'tile_size': 256}


def _restrict(value, min_, max_):
    """
    Restricts the given value changing it to the nearest value in [min, max]
    :param value: value
    :param min_: lower bound
    :param max_: upper bound
    :returns: restricted value
    """
    return max(min(value, max_), min_)


def _cycle_restrict(value, min_, max_):
    """
    Restrics the value shifting it by (max - min) to value in [min, max]
    :param value: value
    :param min_: lower bound
    :param max_: upper bound
    :returns: restricted value
    """
    return value - math.floor((value - min_) / (max_ - min_)) * (max_ - min_)


def _get_world_size(zoom):
    """
    Calculates the number of pixels in X, Y axes for current zoom
    :param zoom: zoom
    :returns: int number of pixels
    """
    return 2 ** (zoom + 8)


def _latlon_to_pixel_xy(lat, lon, zoom=15):
    """
    Converts latlon to pixels
    :param lat: float, latitude
    :param lon: float, longitude
    :param zoom: integer, the zoom of the map
    :returns: tuple of pixelX, pixelY
    """
    epsilon = 1e-10
    latitude = _restrict(lat, -90 + epsilon, 90 - epsilon) * math.pi / 180
    tan = math.tan(math.pi * 0.25 + latitude * 0.5)
    world_size = _get_world_size(zoom)
    pow_ = (
        math.tan(
            math.pi * 0.25
            + math.asin(_CONFIG['eccentricity'] * math.sin(latitude)) * 0.5,
        )
        ** _CONFIG['eccentricity']
    )
    longitude = _cycle_restrict(lon, -180, 180 - epsilon)
    return (
        (longitude / 360 + 0.5) * world_size,
        (0.5 - math.log(tan / pow_) / (2 * math.pi)) * world_size,
    )


def _pixel_xy_to_tile_xy(pixel_x, pixel_y):
    """
    Converts pixels to tiles
    :param pixel_x: integer
    :param pixel_y: integer
    :returns: tuple of tileX, tileY
    """
    return (
        int(math.floor(pixel_x / _CONFIG['tile_size'])),
        int(math.floor(pixel_y / _CONFIG['tile_size'])),
    )


def _tile_xy_to_quadkey(tile_x, tile_y, zoom=15):
    """
    Converts tiles to quadkey
    :param tile_x: integer
    :param tile_y: integer
    :param zoom: integer, the zoom of the map
    :returns: string of quadkey
    """
    quadkey = []
    for i in range(zoom, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if (tile_x & mask) != 0:
            digit += 1
        if (tile_y & mask) != 0:
            digit += 1
            digit += 1
        quadkey.append(str(digit))
    return ''.join(quadkey)


def _latlon_to_quadkey(lat, lon, zoom):
    """
    Converts latlon to quadkey
    :param lat: float, latitude
    :param lon: float, longitude
    :param zoom: integer, the zoom of the map
    :returns: string of quadkey
    """
    if zoom is None:
        zoom = 15

    pixels = _latlon_to_pixel_xy(lat, lon, zoom)
    tile_x, tile_y = _pixel_xy_to_tile_xy(*pixels)
    return _tile_xy_to_quadkey(tile_x, tile_y, zoom)


def quadkey_extractor(point, zoom):
    """Extracts quadkey for given point

    :param point: coordinates in form [lon, lat]
    :param zoom: integer, the zoom of the map
    :return: quadkey for the input point
    """
    lon, lat = point
    return _latlon_to_quadkey(lat, lon, zoom)
