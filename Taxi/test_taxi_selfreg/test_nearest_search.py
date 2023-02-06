# pylint: disable=invalid-name

import taxi_selfreg.generated.service.cities_cache.plugin as cities_cache


async def test_distance():
    def aprrox_equal(a: float, b: float, rel_error: float) -> bool:
        return abs(a - b) / a < rel_error

    msk = cities_cache.City(
        name='', lat=55.75, lon=37.61, country_id='', geoarea='',
    )
    spb = cities_cache.City(
        name='', lat=59.93, lon=30.31, country_id='', geoarea='',
    )
    helsinki = cities_cache.City(
        name='', lat=60.16, lon=24.94, country_id='', geoarea='',
    )
    hab = cities_cache.City(
        name='', lat=48.48, lon=135.07, country_id='', geoarea='',
    )
    earth_r = 6371.0  # in km

    # Moscow - SPB: ~630 km
    assert aprrox_equal(
        msk.approx_arc_dist(spb.lat_rad, spb.lon_rad) * earth_r, 630.0, 0.05,
    )

    # Moscow - Khabarovsk: ~6140 km
    assert aprrox_equal(
        msk.approx_arc_dist(hab.lat_rad, hab.lon_rad) * earth_r, 6140.0, 0.05,
    )

    # Moscow - Helsinki: ~890 km
    assert aprrox_equal(
        msk.approx_arc_dist(helsinki.lat_rad, helsinki.lon_rad) * earth_r,
        890.0,
        0.05,
    )

    # distance is symmetric
    assert aprrox_equal(
        msk.approx_arc_dist(spb.lat_rad, spb.lon_rad),
        spb.approx_arc_dist(msk.lat_rad, msk.lon_rad),
        0.001,
    )
