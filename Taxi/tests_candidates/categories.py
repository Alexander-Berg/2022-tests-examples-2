import flatbuffers

# pylint: disable=import-error
import driver_categories_api.yandex.taxi.fbs.categories.AllCarCategories as AllCarCategories  # noqa: E501
import driver_categories_api.yandex.taxi.fbs.categories.AllCategories as AllCategories  # noqa: E501
import driver_categories_api.yandex.taxi.fbs.categories.AllDriverRestrictions as AllDriverRestrictions  # noqa: E501
import driver_categories_api.yandex.taxi.fbs.categories.AllParkCategories as AllParkCategories  # noqa: E501
import driver_categories_api.yandex.taxi.fbs.categories.CarCategories as CarCategories  # noqa: E501
import driver_categories_api.yandex.taxi.fbs.categories.DriverRestrictions as DriverRestrictions  # noqa: E501
import driver_categories_api.yandex.taxi.fbs.categories.ParkCategories as ParkCategories  # noqa: E501


def _fbs_categories_parks(builder, data):  # pylint: disable=R0915
    parks = []
    for park in data['parks']:
        park_id = builder.CreateString(park['park_id'])

        categories = []
        for category in park['categories']:
            categories.append(builder.CreateString(category))

        ParkCategories.ParkCategoriesStartCategoriesVector(
            builder, len(categories),
        )
        for category in categories:
            builder.PrependUOffsetTRelative(category)
        categories = builder.EndVector(len(categories))

        ParkCategories.ParkCategoriesStart(builder)
        ParkCategories.ParkCategoriesAddParkId(builder, park_id)
        ParkCategories.ParkCategoriesAddCategories(builder, categories)

        parks.append(ParkCategories.ParkCategoriesEnd(builder))
    return parks


def _fbs_categories_cars(builder, data):  # pylint: disable=R0915
    cars = []
    for car in data['cars']:
        park_id = builder.CreateString(car['park_id'])
        car_id = builder.CreateString(car['car_id'])

        categories = []
        for category in car['categories']:
            categories.append(builder.CreateString(category))

        CarCategories.CarCategoriesStartCategoriesVector(
            builder, len(categories),
        )
        for category in categories:
            builder.PrependUOffsetTRelative(category)
        categories = builder.EndVector(len(categories))

        CarCategories.CarCategoriesStart(builder)
        CarCategories.CarCategoriesAddParkId(builder, park_id)
        CarCategories.CarCategoriesAddCarId(builder, car_id)
        CarCategories.CarCategoriesAddCategories(builder, categories)

        cars.append(CarCategories.CarCategoriesEnd(builder))
    return cars


def _fbs_categories_drivers(builder, data):  # pylint: disable=R0915
    drivers = []
    for driver in data['blocked_by_driver']:
        park_id = builder.CreateString(driver['park_id'])
        driver_id = builder.CreateString(driver['driver_id'])

        categories = []
        for category in driver['categories']:
            categories.append(builder.CreateString(category))

        DriverRestrictions.DriverRestrictionsStartCategoriesVector(
            builder, len(categories),
        )
        for category in categories:
            builder.PrependUOffsetTRelative(category)
        categories = builder.EndVector(len(categories))

        DriverRestrictions.DriverRestrictionsStart(builder)
        DriverRestrictions.DriverRestrictionsAddParkId(builder, park_id)
        DriverRestrictions.DriverRestrictionsAddDriverId(builder, driver_id)
        DriverRestrictions.DriverRestrictionsAddCategories(builder, categories)

        drivers.append(DriverRestrictions.DriverRestrictionsEnd(builder))
    return drivers


def fbs_categories(data):  # pylint: disable=R0915
    builder = flatbuffers.Builder(0)
    parks_revision = builder.CreateString(data['revisions']['parks'])
    cars_revision = builder.CreateString(data['revisions']['cars'])
    drivers_revision = builder.CreateString(data['revisions']['drivers'])

    parks = _fbs_categories_parks(builder, data)
    cars = _fbs_categories_cars(builder, data)
    drivers = _fbs_categories_drivers(builder, data)

    AllCategories.AllCategoriesStartCarsClassesInParkVector(builder, len(cars))
    for car in cars:
        builder.PrependUOffsetTRelative(car)
    cars = builder.EndVector(len(cars))

    AllCategories.AllCategoriesStartAvailableInParkVector(builder, len(parks))
    for park in parks:
        builder.PrependUOffsetTRelative(park)
    parks = builder.EndVector(len(parks))

    AllCategories.AllCategoriesStartBlockedByDriverVector(
        builder, len(drivers),
    )
    for driver in drivers:
        builder.PrependUOffsetTRelative(driver)
    drivers = builder.EndVector(len(drivers))

    AllCategories.AllCategoriesStart(builder)
    AllCategories.AllCategoriesAddParksRevision(builder, parks_revision)
    AllCategories.AllCategoriesAddCarsRevision(builder, cars_revision)
    AllCategories.AllCategoriesAddDriversRevision(builder, drivers_revision)
    AllCategories.AllCategoriesAddCarsClassesInPark(builder, cars)
    AllCategories.AllCategoriesAddAvailableInPark(builder, parks)
    AllCategories.AllCategoriesAddBlockedByDriver(builder, drivers)

    obj = AllCategories.AllCategoriesEnd(builder)
    builder.Finish(obj)
    return bytes(builder.Output())


def fbs_categories_drivers(data):  # pylint: disable=R0915
    builder = flatbuffers.Builder(0)
    drivers_revision = builder.CreateString(data['revisions']['drivers'])
    drivers = _fbs_categories_drivers(builder, data)
    AllDriverRestrictions.AllDriverRestrictionsStartBlockedByDriverVector(
        builder, len(drivers),
    )
    for driver in drivers:
        builder.PrependUOffsetTRelative(driver)
    drivers = builder.EndVector(len(drivers))

    AllDriverRestrictions.AllDriverRestrictionsStart(builder)
    AllDriverRestrictions.AllDriverRestrictionsAddDriversRevision(
        builder, drivers_revision,
    )
    AllDriverRestrictions.AllDriverRestrictionsAddBlockedByDriver(
        builder, drivers,
    )

    obj = AllCategories.AllCategoriesEnd(builder)
    builder.Finish(obj)
    return bytes(builder.Output())


def fbs_categories_cars(data):  # pylint: disable=R0915
    builder = flatbuffers.Builder(0)
    cars_revision = builder.CreateString(data['revisions']['cars'])
    cars = _fbs_categories_cars(builder, data)
    AllCarCategories.AllCarCategoriesStartCarsClassesInParkVector(
        builder, len(cars),
    )
    for car in cars:
        builder.PrependUOffsetTRelative(car)
    cars = builder.EndVector(len(cars))

    AllCarCategories.AllCarCategoriesStart(builder)
    AllCarCategories.AllCarCategoriesAddCarsRevision(builder, cars_revision)
    AllCarCategories.AllCarCategoriesAddCarsClassesInPark(builder, cars)

    obj = AllCategories.AllCategoriesEnd(builder)
    builder.Finish(obj)
    return bytes(builder.Output())


def fbs_categories_parks(data):  # pylint: disable=R0915
    builder = flatbuffers.Builder(0)
    parks_revision = builder.CreateString(data['revisions']['parks'])
    parks = _fbs_categories_parks(builder, data)
    AllParkCategories.AllParkCategoriesStartAvailableInParkVector(
        builder, len(parks),
    )
    for park in parks:
        builder.PrependUOffsetTRelative(park)
    parks = builder.EndVector(len(parks))

    AllParkCategories.AllParkCategoriesStart(builder)
    AllParkCategories.AllParkCategoriesAddParksRevision(
        builder, parks_revision,
    )
    AllParkCategories.AllParkCategoriesAddAvailableInPark(builder, parks)

    obj = AllCategories.AllCategoriesEnd(builder)
    builder.Finish(obj)
    return bytes(builder.Output())
