import {subDays} from 'date-fns';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {WmsStoreEntity} from '@/src/entities/wms-stores/entity';
import type {WmsZoneEntity} from '@/src/entities/wms-zones/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {DeliveryType, StoreStatus, ZoneStatus} from 'types/wms';

import {getWmsZonesHandler} from './get-wms-zones';

describe('getWmsZonesHandler()', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should retrieve effective zones only', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const nowDate = new Date();

        const store = await TestFactory.createWmsStore({cityGeoId});
        await TestFactory.createWmsZone({
            effectiveFrom: subDays(nowDate, 5),
            effectiveTill: subDays(nowDate, 4),
            storeId: store.id
        });
        const zoneNow = await TestFactory.createWmsZone({
            effectiveFrom: subDays(nowDate, 4),
            effectiveTill: undefined,
            storeId: store.id
        });

        const {zones, stores} = await getWmsZonesHandler({
            data: {query: {filters: {cityGeoId}}},
            context
        });

        expect(zones).toHaveLength(1);
        expect(stores).toHaveLength(1);
        expect(zones[0].id).toBe(zoneNow.id);
    });

    describe('zones and stores activeness', () => {
        let storeDisabled: WmsStoreEntity;
        let storeClosed: WmsStoreEntity;
        let storeActive: WmsStoreEntity;

        let zoneDisabledForStoreClosed: WmsZoneEntity;
        let zoneDisabledForStoreActive: WmsZoneEntity;
        let zoneActiveForStoreActive: WmsZoneEntity;

        beforeEach(async () => {
            storeClosed = await TestFactory.createWmsStore({status: StoreStatus.CLOSED});
            await TestFactory.createWmsZone({
                storeId: storeClosed.id,
                status: ZoneStatus.ACTIVE
            });
            zoneDisabledForStoreClosed = await TestFactory.createWmsZone({
                storeId: storeClosed.id,
                status: ZoneStatus.DISABLED
            });

            storeDisabled = await TestFactory.createWmsStore({status: StoreStatus.DISABLED});
            await TestFactory.createWmsZone({
                storeId: storeDisabled.id,
                status: ZoneStatus.ACTIVE
            });

            storeActive = await TestFactory.createWmsStore({
                status: StoreStatus.ACTIVE
            });
            zoneDisabledForStoreActive = await TestFactory.createWmsZone({
                storeId: storeActive.id,
                status: ZoneStatus.DISABLED
            });
            zoneActiveForStoreActive = await TestFactory.createWmsZone({
                storeId: storeActive.id,
                status: ZoneStatus.ACTIVE
            });
        });

        it('should retrieve active and disabled zones if no zone status specified', async () => {
            const {zones, stores} = await getWmsZonesHandler({
                data: {
                    query: {
                        filters: {
                            storeStatuses: [StoreStatus.ACTIVE],
                            cityGeoId: CityGeoId.MOSCOW
                        }
                    }
                },
                context
            });

            expect(zones).toHaveLength(2);
            expect(stores).toHaveLength(1);

            const zonesIds = zones.map(({id}) => id);
            expect(zonesIds).toContain(zoneActiveForStoreActive.id);
            expect(zonesIds).toContain(zoneDisabledForStoreActive.id);
        });

        it('should retrieve active and disabled stores if no store status specified', async () => {
            const {stores} = await getWmsZonesHandler({
                data: {
                    query: {filters: {cityGeoId: CityGeoId.MOSCOW}}
                },
                context
            });

            expect(stores).toHaveLength(2);

            const storesIds = stores.map(({id}) => id);
            expect(storesIds).toContain(storeActive.id);
            expect(storesIds).toContain(storeDisabled.id);
        });

        it('should retrieve statuses specified in request', async () => {
            const {zones, stores} = await getWmsZonesHandler({
                data: {
                    query: {
                        filters: {
                            zoneStatuses: [ZoneStatus.DISABLED],
                            storeStatuses: [StoreStatus.CLOSED, StoreStatus.DISABLED],
                            cityGeoId: CityGeoId.MOSCOW
                        }
                    }
                },
                context
            });

            expect(stores).toHaveLength(1);
            expect(zones).toHaveLength(1);
            expect(zones[0].id).toBe(zoneDisabledForStoreClosed.id);
        });
    });

    describe('zones delivery type', () => {
        let store: WmsStoreEntity;

        let zoneFoot: WmsZoneEntity;
        let zoneCar: WmsZoneEntity;

        beforeEach(async () => {
            store = await TestFactory.createWmsStore({
                status: StoreStatus.ACTIVE
            });
            zoneFoot = await TestFactory.createWmsZone({
                storeId: store.id,
                deliveryType: DeliveryType.FOOT
            });
            zoneCar = await TestFactory.createWmsZone({
                storeId: store.id,
                deliveryType: DeliveryType.CAR
            });
            await TestFactory.createWmsZone({
                storeId: store.id,
                deliveryType: DeliveryType.YANDEX_TAXI
            });
        });

        it('should retrieve foot zones by default', async () => {
            const {zones, stores} = await getWmsZonesHandler({
                data: {query: {filters: {cityGeoId: CityGeoId.MOSCOW}}},
                context
            });

            expect(zones).toHaveLength(1);
            expect(stores).toHaveLength(1);
            expect(zones[0].id).toBe(zoneFoot.id);
        });

        it('should retrieve zones with delivery type specified in request', async () => {
            const {zones, stores} = await getWmsZonesHandler({
                data: {
                    query: {
                        filters: {
                            zoneDeliveryTypes: [DeliveryType.FOOT, DeliveryType.CAR],
                            cityGeoId: CityGeoId.MOSCOW
                        }
                    }
                },
                context
            });

            expect(stores).toHaveLength(1);
            expect(zones).toHaveLength(2);

            const zonesIds = zones.map(({id}) => id);
            expect(zonesIds).toContain(zoneFoot.id);
            expect(zonesIds).toContain(zoneCar.id);
        });
    });
});
