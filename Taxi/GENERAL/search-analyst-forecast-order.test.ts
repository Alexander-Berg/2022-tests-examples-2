import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {zone} from 'service/seed-db/fixtures';
import {AnalystForecastMode, CourierTypePredict} from 'types/analyst-forecast-orders';
import {AnalystStoreRoutingStatus} from 'types/analyst-store-routing';

import {searchAnalystForecastOrdersHandler} from './search-analyst-forecast-order';

describe('search analyst forecast orders', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return forecast orders', async () => {
        const user = context.user;

        const managerPoint = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId: CityGeoId.MOSCOW,
            point: [12, 23],
            name: 'test name'
        });

        const managerZone = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId: CityGeoId.MOSCOW,
            zone,
            name: 'test name'
        });

        await TestFactory.createAnalystForecastOrders(user.uid, {
            id: '1',
            status: AnalystStoreRoutingStatus.NEW,
            userId: user.uid,
            ticketSlug: 'TEST-1234',
            cityGeoId: CityGeoId.MOSCOW,
            managerPointId: managerPoint.id,
            managerZoneId: managerZone.id,
            mode: AnalystForecastMode.NEW_STORE_NEW_ZONE,
            courierTypePredict: CourierTypePredict.FOOT
        });

        const res = await searchAnalystForecastOrdersHandler.handle({
            data: {query: {cityGeoId: CityGeoId.MOSCOW}},
            context
        });

        expect(res.items).toHaveLength(1);
    });

    it('should return forecast orders with search name', async () => {
        const user = context.user;

        const managerPoint = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId: CityGeoId.MOSCOW,
            point: [12, 23],
            name: 'test name'
        });

        const managerZone = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId: CityGeoId.MOSCOW,
            zone,
            name: 'test name'
        });

        await TestFactory.createAnalystForecastOrders(user.uid, {
            id: '1',
            status: AnalystStoreRoutingStatus.NEW,
            userId: user.uid,
            ticketSlug: 'TEST-1234',
            managerPointId: managerPoint.id,
            managerZoneId: managerZone.id,
            cityGeoId: CityGeoId.MOSCOW,
            mode: AnalystForecastMode.NEW_STORE_NEW_ZONE,
            courierTypePredict: CourierTypePredict.FOOT
        });

        const res = await searchAnalystForecastOrdersHandler.handle({
            data: {query: {search: 'test', cityGeoId: CityGeoId.MOSCOW}},
            context
        });

        expect(res.items).toHaveLength(1);
    });

    it('should return forecast orders with filter by status', async () => {
        const user = context.user;

        const managerPoint = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId: CityGeoId.MOSCOW,
            point: [12, 23],
            name: 'test name'
        });

        const managerZone = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId: CityGeoId.MOSCOW,
            zone,
            name: 'test name'
        });

        await TestFactory.createAnalystStoreRouting(user.uid, {
            id: '1',
            status: AnalystStoreRoutingStatus.NEW,
            userId: user.uid,
            ticketSlug: 'TEST-1234',
            cityId: CityGeoId.MOSCOW,
            managerPointId: managerPoint.id
        });

        await TestFactory.createAnalystForecastOrders(user.uid, {
            id: '1',
            status: AnalystStoreRoutingStatus.NEW,
            userId: user.uid,
            ticketSlug: 'TEST-1234',
            cityGeoId: CityGeoId.MOSCOW,
            managerPointId: managerPoint.id,
            managerZoneId: managerZone.id,
            mode: AnalystForecastMode.NEW_STORE_NEW_ZONE,
            courierTypePredict: CourierTypePredict.FOOT
        });

        const res = await searchAnalystForecastOrdersHandler.handle({
            data: {query: {statuses: [AnalystStoreRoutingStatus.NEW], cityGeoId: CityGeoId.MOSCOW}},
            context
        });

        expect(res.items).toHaveLength(1);
    });
});
