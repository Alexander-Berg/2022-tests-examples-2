from projects.geosuggest.common import storages


def test_empty_geo_storages():
    for storage in [storages.DummyGeoStorage(), storages.KDTreeStorage()]:
        storage.build()
        nearest = storage.find_nearest(lon=0, lat=0, radius=100)
        assert len(list(nearest)) == 0


def test_geo_storages():
    for storage in [storages.DummyGeoStorage(), storages.KDTreeStorage()]:
        storage.add(obj=None, lon=37.6421, lat=55.7351)
        storage.add(obj=None, lon=37.6417, lat=55.7361)
        storage.build()

        nearest = storage.find_nearest(lon=37.6427, lat=55.7340, radius=10)
        assert len(list(nearest)) == 0

        nearest = storage.find_nearest(lon=37.6427, lat=55.7340, radius=200)
        assert len(list(nearest)) == 1

        nearest = storage.find_nearest(lon=37.6427, lat=55.7340, radius=1000)
        assert len(list(nearest)) == 2
