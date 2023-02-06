import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {UserEntity} from '@/src/entities/user/entity';
import {createMultiPolygonFeature} from '@/src/lib/geo-json';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import type {EntityFeatureCollection, ExportFeature} from 'types/export';
import type {Geometry} from 'types/geo-json';

import {getDraftsGeoJsonHandler} from './export-drafts-geo-json';

describe('getDraftsGeoJsonHandler()', () => {
    let user: UserEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        context = await TestFactory.createUserApiContext({user});
    });

    it('should export newly created manager zones', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const name = 'test zone';
        const user = await context.user;
        const zone1 = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: createMultiPolygonFeature([
                [
                    [
                        [1, 2],
                        [2, 3],
                        [3, 1]
                    ]
                ]
            ]),
            name
        });
        const zone2 = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: createMultiPolygonFeature([
                [
                    [
                        [10, 20],
                        [20, 30],
                        [30, 10]
                    ]
                ]
            ]),
            name
        });

        const file = await getDraftsGeoJsonHandler({
            data: {query: {filters: {cityGeoId: CityGeoId.MOSCOW}}},
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
        const cityGeoId = CityGeoId.MOSCOW;
        const user = await context.user;
        const point1 = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId,
            point: [23, 33],
            name: 'test point'
        });
        const point2 = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId,
            point: [24, 33],
            name: 'test point'
        });

        const file = await getDraftsGeoJsonHandler({
            data: {query: {filters: {cityGeoId: CityGeoId.MOSCOW}}},
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
});
