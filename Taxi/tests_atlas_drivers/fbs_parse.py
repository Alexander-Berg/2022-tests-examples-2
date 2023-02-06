# flake8: noqa IS001
from typing import List, Optional

# pylint: disable=import-error
from atlas_drivers.fbs import DriversInfo
from atlas_drivers.fbs import DriverInfo
from atlas_drivers.fbs import Profile

from . import driver_info


def _decode(val):
    if val is not None:
        return val.decode('utf-8')
    return val


def _parse_string_array(length, get) -> List[str]:
    ans = []
    for i in range(length()):
        ans.append(_decode(get(i)))
    return ans


def _parse_point(point) -> Optional[driver_info.Point]:
    if point is not None:
        return driver_info.Point(point.Lon(), point.Lat())
    return point


def _parse_driver_info(info: DriverInfo) -> driver_info.DriverInfo:
    geopoint = info.Geopoint()
    geopoint = driver_info.Point(geopoint.Lon(), geopoint.Lat())

    ids = info.Ids()
    ids = driver_info.DriverIds(
        _decode(ids.ParkId()),
        _decode(ids.DriverProfileId()),
        _decode(ids.Udid()),
        _decode(ids.CarNumber()),
        ids.DriverLicenseHash(),
    )

    car_classes = info.CarClasses()
    if car_classes is not None:
        car_classes = driver_info.CarClasses(
            _parse_string_array(car_classes.ActualLength, car_classes.Actual),
            _parse_string_array(
                car_classes.DispatchLength, car_classes.Dispatch,
            ),
            _parse_string_array(
                car_classes.TaximeterLength, car_classes.Taximeter,
            ),
            _parse_string_array(car_classes.ChainLength, car_classes.Chain),
        )

    tags = info.Tags()
    if tags is not None:
        tags = driver_info.Tags(
            _parse_string_array(tags.TagNamesLength, tags.TagNames),
        )

    reposition = info.Reposition()
    if reposition is not None:
        reposition = driver_info.Reposition(
            reposition.Enabled(),
            _decode(reposition.Mode()),
            _parse_point(reposition.Geopoint()),
        )

    is_frozen = info.IsFrozen()
    if is_frozen is not None:
        is_frozen = driver_info.IsFrozen(is_frozen.Freeze())

    tariff_zone = info.TariffZone()
    if tariff_zone is not None:
        tariff_zone = _decode(tariff_zone)

    payment_methods = info.PaymentMethods()
    if payment_methods is not None:
        payment_methods = driver_info.PaymentMethods(
            _parse_string_array(
                payment_methods.ActualLength, payment_methods.Actual,
            ),
            _parse_string_array(
                payment_methods.DispatchLength, payment_methods.Dispatch,
            ),
            _parse_string_array(
                payment_methods.TaximeterLength, payment_methods.Taximeter,
            ),
        )

    statuses = info.Statuses()
    if statuses is not None:
        statuses = driver_info.Statuses(
            _decode(statuses.Driver()),
            _decode(statuses.Taximeter()),
            _decode(statuses.Order()),
        )

    order_info = info.OrderInfo()
    if order_info is not None:
        order_info = driver_info.OrderInfo(
            _decode(order_info.Id()),
            _decode(order_info.ChainedId()),
            _parse_point(order_info.PointB()),
        )

    airports = info.Airports()
    if airports is not None:
        airports = driver_info.Airports(airports.QueuePlace())

    location_settings = info.LocationSettings()
    if location_settings is not None:
        location_settings = driver_info.LocationSettings(
            _decode(location_settings.RealtimeSource()),
            _decode(location_settings.VerifiedSource()),
        )

    taximeter_version = info.TaximeterVersion()
    if taximeter_version is not None:
        taximeter_version = driver_info.TaximeterVersion(
            _decode(taximeter_version.TaximeterBrand()),
            _decode(taximeter_version.TaximeterPlatform()),
            _decode(taximeter_version.TaximeterVersion()),
            _decode(taximeter_version.TaximeterVersionType()),
        )

    return driver_info.DriverInfo(
        geopoint,
        ids,
        car_classes=car_classes,
        tags=tags,
        reposition=reposition,
        is_frozen=is_frozen,
        tariff_zone=tariff_zone,
        payment_methods=payment_methods,
        statuses=statuses,
        order_info=order_info,
        airports=airports,
        location_settings=location_settings,
        taximeter_version=taximeter_version,
    )


def parse_driver_info(data) -> Optional[driver_info.DriverInfo]:
    info = Profile.Profile.GetRootAsProfile(data, 0)
    info = info.Profile()
    if info is None:
        return None
    return _parse_driver_info(info)


def parse_drivers_info(data) -> List[driver_info.DriverInfo]:
    root = DriversInfo.DriversInfo.GetRootAsDriversInfo(data, 0)
    ans = []
    for i in range(root.DriversInfoLength()):
        info = root.DriversInfo(i)
        ans.append(_parse_driver_info(info))

    return ans
