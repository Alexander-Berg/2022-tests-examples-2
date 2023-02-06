import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {UserEntity} from '@/src/entities/user/entity';
import {createMultiPolygonFeature, createPointFeature} from '@/src/lib/geo-json';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import type {EntityFeatureCollection, ExportFeature, ExportFeatureProperties} from 'types/export';
import type {Coordinates, LongLat} from 'types/geo';
import type {GeoJSON, Geometry} from 'types/geo-json';
import {StoreStatus} from 'types/wms';

import {getEntitiesGeoJSONByIdsHandler} from './export-entities-geo-json-by-ids';

describe('getEntitiesGeoJSONByIdsHandler()', () => {
    let user: UserEntity;
    let context: UserApiRequestContext;
    const cityGeoId = CityGeoId.MOSCOW;

    async function createManagerZone(coordinates: number[][]) {
        const user = await context.user;

        return await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: createMultiPolygonFeature([[coordinates]] as Coordinates.MultiPolygon),
            name: 'test zone'
        });
    }

    async function createManagerPoint(coordinates: [number, number]) {
        const user = await context.user;

        return await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId,
            point: coordinates,
            name: 'test point'
        });
    }

    async function createWmsStore(coordinates: [number, number]) {
        return await TestFactory.createWmsStore({
            cityGeoId,
            location: createPointFeature(coordinates),
            status: StoreStatus.ACTIVE
        });
    }

    beforeEach(async () => {
        user = await TestFactory.createUser();
        context = await TestFactory.createUserApiContext({user});
    });

    it('should export newly created manager zones', async () => {
        const zone1 = await createManagerZone([
            [1, 2],
            [2, 3],
            [3, 1]
        ]);
        const zone2 = await createManagerZone([
            [10, 20],
            [20, 30]
        ]);

        const file = await getEntitiesGeoJSONByIdsHandler({
            data: {query: {filters: {cityGeoId: CityGeoId.MOSCOW, managerZonesIds: [zone1.id, zone2.id]}}},
            context
        });

        const exportedManagerPoints = JSON.parse(Buffer.from(file).toString('ascii')) as EntityFeatureCollection;

        [zone1, zone2].forEach(({id, name, zone}) => {
            expect(exportedManagerPoints.features).toContainEqual<ExportFeature<Geometry.Polygon>>({
                type: 'Feature',
                geometry: {
                    type: 'Polygon',
                    coordinates: zone.geometry.coordinates[0]
                },
                properties: {
                    eagle_id: id,
                    eagle_type: 'export-entities-manager-zone',
                    name
                }
            });
        });
    });

    it('should export newly created manager points', async () => {
        const point1 = await createManagerPoint([23, 33]);
        const point2 = await createManagerPoint([24, 33]);

        const file = await getEntitiesGeoJSONByIdsHandler({
            data: {query: {filters: {cityGeoId: CityGeoId.MOSCOW, managerPointsIds: [point1.id, point2.id]}}},
            context
        });

        const exportedManagerPoints = JSON.parse(Buffer.from(file).toString('ascii')) as EntityFeatureCollection;

        [point1, point2].forEach(({id, name, point}) => {
            expect(exportedManagerPoints.features).toContainEqual<ExportFeature<Geometry.Point>>({
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: point
                },
                properties: {
                    eagle_id: id,
                    eagle_type: 'export-entities-manager-point',
                    name
                }
            });
        });
    });

    it('should export one of the created points', async () => {
        const {id, name, point} = await createManagerPoint([23, 33]);
        await createManagerPoint([24, 33]);

        const file = await getEntitiesGeoJSONByIdsHandler({
            data: {query: {filters: {cityGeoId: CityGeoId.MOSCOW, managerPointsIds: [id]}}},
            context
        });

        const exportedManagerPoint = JSON.parse(Buffer.from(file).toString('ascii')) as EntityFeatureCollection;

        expect(exportedManagerPoint.features).toContainEqual<ExportFeature<Geometry.Point>>({
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: point
            },
            properties: {
                eagle_id: id,
                eagle_type: 'export-entities-manager-point',
                name
            }
        });
    });

    it('should export newly manager zone and manager point', async () => {
        const point1 = await createManagerPoint([23, 33]);
        await createManagerPoint([24, 33]);

        const zone1 = await createManagerZone([
            [1, 2],
            [2, 3],
            [3, 1]
        ]);

        const file = await getEntitiesGeoJSONByIdsHandler({
            data: {
                query: {
                    filters: {cityGeoId: CityGeoId.MOSCOW, managerPointsIds: [point1.id], managerZonesIds: [zone1.id]}
                }
            },
            context
        });

        const exportedDrafts = JSON.parse(Buffer.from(file).toString('ascii')) as EntityFeatureCollection;

        expect(exportedDrafts.features).toContainEqual<ExportFeature<Geometry.Point>>({
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: point1.point
            },
            properties: {
                eagle_id: point1.id,
                eagle_type: 'export-entities-manager-point',
                name: point1.name
            }
        });

        expect(exportedDrafts.features).toContainEqual<ExportFeature<Geometry.Polygon>>({
            type: 'Feature',
            geometry: {
                type: 'Polygon',
                coordinates: zone1.zone.geometry.coordinates[0]
            },
            properties: {
                eagle_id: zone1.id,
                eagle_type: 'export-entities-manager-zone',
                name: zone1.name
            }
        });
    });

    it('should export newly created wms stores', async () => {
        const store1 = await createWmsStore([1, 2]);
        const store2 = await createWmsStore([2, 3]);

        const file = await getEntitiesGeoJSONByIdsHandler({
            data: {query: {filters: {cityGeoId: CityGeoId.MOSCOW, wmsStoresIds: [store1.id, store2.id]}}},
            context
        });

        const exportedWmsStores = JSON.parse(
            Buffer.from(file).toString('ascii')
        ) as EntityFeatureCollection<Geometry.Point>;

        expect(exportedWmsStores.type).toEqual('FeatureCollection');
        [store1, store2].forEach(({id, status, title, location}) => {
            expect(exportedWmsStores.features).toContainEqual<GeoJSON<Geometry.Point, ExportFeatureProperties>>({
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: location?.geometry.coordinates as LongLat
                },
                properties: {
                    eagle_id: id,
                    eagle_type: 'export-entities-wms-store',
                    name: `${title}: ${StoreStatus.ACTIVE}`,
                    status
                }
            });
        });
    });

    it('should export an empty file', async () => {
        await createManagerPoint([23, 33]);
        await createManagerPoint([24, 33]);
        await createManagerZone([
            [1, 2],
            [2, 3],
            [3, 1]
        ]);
        await createWmsStore([1, 2]);

        const file = await getEntitiesGeoJSONByIdsHandler({
            data: {query: {filters: {cityGeoId: CityGeoId.MOSCOW}}},
            context
        });

        const exportedEntities = JSON.parse(Buffer.from(file).toString('ascii')) as EntityFeatureCollection;

        expect(exportedEntities.features).toEqual([]);
    });
});
