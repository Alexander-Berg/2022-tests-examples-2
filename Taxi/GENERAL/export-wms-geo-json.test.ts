import {subDays} from 'date-fns';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {UserEntity} from '@/src/entities/user/entity';
import {createMultiPolygonFeature, createPointFeature} from '@/src/lib/geo-json';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {zone, zonePolygon} from 'service/seed-db/fixtures';
import {EntityFeatureCollection, ExportEntity, ExportFeature, ExportFeatureProperties} from 'types/export';
import type {LongLat} from 'types/geo';
import type {GeoJSON, Geometry} from 'types/geo-json';
import {DeliveryType, StoreStatus, ZoneStatus} from 'types/wms';

import {getWmsGeoJsonHandler} from './export-wms-geo-json';

describe('getWmsGeoJsonHandler()', () => {
    let user: UserEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        context = await TestFactory.createUserApiContext({user});
    });

    it('should export newly created stores', async () => {
        const cityGeoId = CityGeoId.MOSCOW;

        const store1 = await TestFactory.createWmsStore({
            cityGeoId,
            location: createPointFeature([1, 2]),
            status: StoreStatus.ACTIVE
        });
        const store2 = await TestFactory.createWmsStore({
            cityGeoId,
            location: createPointFeature([2, 3]),
            status: StoreStatus.ACTIVE
        });

        const file = await getWmsGeoJsonHandler({
            data: {query: {filters: {cityGeoId: CityGeoId.MOSCOW, entity: ExportEntity.WMS_STORES}}},
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

    it('should export active and disabled stores only', async () => {
        const cityGeoId = CityGeoId.MOSCOW;

        await TestFactory.createWmsStore({
            cityGeoId,
            status: StoreStatus.CLOSED
        });
        const storeDisabled = await TestFactory.createWmsStore({
            cityGeoId,
            status: StoreStatus.DISABLED
        });
        const storeActive = await TestFactory.createWmsStore({
            cityGeoId,
            status: StoreStatus.ACTIVE
        });

        const file = await getWmsGeoJsonHandler({
            data: {query: {filters: {cityGeoId: CityGeoId.MOSCOW, entity: ExportEntity.WMS_STORES}}},
            context
        });

        const exportedWmsZones = JSON.parse(
            Buffer.from(file).toString('ascii')
        ) as EntityFeatureCollection<Geometry.Point>;

        expect(exportedWmsZones.features).toHaveLength(2);
        [storeDisabled, storeActive].forEach((store) => {
            expect(exportedWmsZones.features).toEqual(
                expect.arrayContaining<ExportFeature>([
                    expect.objectContaining<Partial<ExportFeature>>({
                        properties: expect.objectContaining<Partial<ExportFeatureProperties>>({eagle_id: store.id})
                    })
                ])
            );
        });
    });

    it('should export newly created zones', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const nowDate = new Date();

        const store = await TestFactory.createWmsStore({cityGeoId});

        const zone1 = await TestFactory.createWmsZone({
            effectiveFrom: subDays(nowDate, 4),
            effectiveTill: undefined,
            status: ZoneStatus.ACTIVE,
            deliveryType: DeliveryType.FOOT,
            zone: createMultiPolygonFeature([
                [
                    [
                        [1, 2],
                        [2, 3],
                        [3, 4]
                    ]
                ]
            ]),
            storeId: store.id,
            store
        });
        const zone2 = await TestFactory.createWmsZone({
            effectiveFrom: subDays(nowDate, 4),
            effectiveTill: undefined,
            status: ZoneStatus.ACTIVE,
            deliveryType: DeliveryType.FOOT,
            zone: createMultiPolygonFeature([
                [
                    [
                        [10, 20],
                        [20, 30],
                        [30, 40]
                    ]
                ]
            ]),
            storeId: store.id,
            store
        });

        const file = await getWmsGeoJsonHandler({
            data: {query: {filters: {cityGeoId: CityGeoId.MOSCOW, entity: ExportEntity.WMS_ZONES}}},
            context
        });

        const exportedWmsZones = JSON.parse(Buffer.from(file).toString('ascii')) as EntityFeatureCollection;

        expect(exportedWmsZones.type).toEqual('FeatureCollection');
        [zone1, zone2].forEach(({id, zone, status, deliveryType}) => {
            expect(exportedWmsZones.features).toContainEqual<GeoJSON<Geometry.Polygon, ExportFeatureProperties>>({
                type: 'Feature',
                geometry: {
                    type: 'Polygon',
                    coordinates: zone.geometry.coordinates[0]
                },
                properties: {
                    eagle_id: id,
                    eagle_type: 'export-entities-wms-zone',
                    name: `${store.title}: ${deliveryType}, ${status}`,
                    status
                }
            });
        });
    });

    it('should export currently effective zones only', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const nowDate = new Date();

        const store = await TestFactory.createWmsStore({cityGeoId});
        await TestFactory.createWmsZone({
            effectiveFrom: subDays(nowDate, 5),
            effectiveTill: subDays(nowDate, 4),
            storeId: store.id,
            status: ZoneStatus.ACTIVE
        });
        const zoneDisabled = await TestFactory.createWmsZone({
            effectiveFrom: subDays(nowDate, 5),
            effectiveTill: undefined,
            storeId: store.id,
            status: ZoneStatus.DISABLED,
            deliveryType: DeliveryType.FOOT
        });
        const zoneActive = await TestFactory.createWmsZone({
            effectiveFrom: subDays(nowDate, 4),
            effectiveTill: undefined,
            storeId: store.id,
            status: ZoneStatus.ACTIVE,
            deliveryType: DeliveryType.FOOT
        });

        const file = await getWmsGeoJsonHandler({
            data: {
                query: {
                    filters: {
                        cityGeoId: CityGeoId.MOSCOW,
                        entity: ExportEntity.WMS_ZONES
                    }
                }
            },
            context
        });

        const exportedWmsZones = JSON.parse(
            Buffer.from(file).toString('ascii')
        ) as EntityFeatureCollection<Geometry.Polygon>;

        expect(exportedWmsZones.features).toHaveLength(2);
        [zoneDisabled, zoneActive].forEach((zone) => {
            expect(exportedWmsZones.features).toEqual(
                expect.arrayContaining<ExportFeature>([
                    expect.objectContaining<Partial<ExportFeature>>({
                        properties: expect.objectContaining<Partial<ExportFeatureProperties>>({eagle_id: zone.id})
                    })
                ])
            );
        });
    });

    it('should export geojson for wms zone with coordinates by id', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const nowDate = new Date();

        const store = await TestFactory.createWmsStore({cityGeoId});
        const zoneNow = await TestFactory.createWmsZone({
            effectiveFrom: subDays(nowDate, 4),
            effectiveTill: undefined,
            storeId: store.id,
            zone,
            store,
            status: ZoneStatus.ACTIVE,
            deliveryType: DeliveryType.FOOT
        });

        const file = await getWmsGeoJsonHandler({
            data: {
                query: {
                    filters: {
                        cityGeoId: CityGeoId.MOSCOW,
                        entityId: zoneNow.id,
                        entity: ExportEntity.WMS_ZONES
                    }
                }
            },
            context
        });

        const exportedWmsRow = JSON.parse(Buffer.from(file).toString('ascii'));

        expect(exportedWmsRow).toEqual<EntityFeatureCollection<Geometry.Polygon>>({
            type: 'FeatureCollection',
            features: [
                {
                    ...zonePolygon,
                    properties: {
                        eagle_id: zoneNow.id,
                        eagle_type: 'export-entities-wms-zone',
                        name: `${store.title}: ${DeliveryType.FOOT}, ${ZoneStatus.ACTIVE}`,
                        status: ZoneStatus.ACTIVE
                    }
                }
            ]
        });
    });
});
