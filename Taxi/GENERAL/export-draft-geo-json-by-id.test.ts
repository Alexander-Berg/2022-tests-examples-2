import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {zone, zonePolygon} from 'service/seed-db/fixtures';
import {EntityFeatureCollection, ExportEntity} from 'types/export';
import type {Geometry} from 'types/geo-json';

import {getDraftGeoJsonByIdHandler} from './export-draft-geo-json-by-id';

describe('getDraftGeoJsonByIdHandler()', () => {
    let user: UserEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        context = await TestFactory.createUserApiContext({user});
    });

    it('should export geojson from newly created manager zone without coordinates', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const name = 'test zone';
        const user = await context.user;
        const managerZone = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: {},
            name
        });

        const file = await getDraftGeoJsonByIdHandler({
            data: {
                query: {
                    filters: {
                        cityGeoId: CityGeoId.MOSCOW,
                        draftId: managerZone.id,
                        entity: ExportEntity.MANAGER_ZONES
                    }
                }
            },
            context
        });

        const exportedDraftsRow = JSON.parse(
            Buffer.from(file).toString('ascii')
        ) as EntityFeatureCollection<Geometry.Polygon>;

        expect(exportedDraftsRow).toEqual({
            type: 'FeatureCollection',
            features: [
                {
                    geometry: {
                        type: 'Polygon',
                        coordinates: []
                    },
                    properties: {
                        eagle_id: managerZone.id,
                        eagle_type: 'export-entities-manager-zone',
                        name: managerZone.name
                    }
                }
            ]
        });
    });

    it('should export geojson from newly created manager zones with coordinates', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const name = 'test zone';
        const user = await context.user;
        const managerZone = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone,
            name
        });

        const file = await getDraftGeoJsonByIdHandler({
            data: {
                query: {
                    filters: {
                        cityGeoId: CityGeoId.MOSCOW,
                        draftId: managerZone.id,
                        entity: ExportEntity.MANAGER_ZONES
                    }
                }
            },
            context
        });

        const exportedDraftsRow = JSON.parse(
            Buffer.from(file).toString('ascii')
        ) as EntityFeatureCollection<Geometry.Polygon>;

        expect(exportedDraftsRow).toEqual({
            type: 'FeatureCollection',
            features: [
                {
                    ...zonePolygon,
                    properties: {
                        eagle_id: managerZone.id,
                        eagle_type: 'export-entities-manager-zone',
                        name: managerZone.name
                    }
                }
            ]
        });
    });
});
