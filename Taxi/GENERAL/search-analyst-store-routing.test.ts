import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {AnalystStoreRoutingStatus} from 'types/analyst-store-routing';

import {searchAnalystStoreRoutingHandler} from './search-analyst-store-routing';

describe('search routing new store', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return routing', async () => {
        const user = context.user;

        const managerPoint = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId: 213,
            point: [12, 23],
            name: 'test name'
        });

        await TestFactory.createAnalystStoreRouting(user.uid, {
            id: '1',
            status: AnalystStoreRoutingStatus.NEW,
            cityId: CityGeoId.MOSCOW,
            userId: user.uid,
            ticketSlug: 'TEST-1234',
            managerPointId: managerPoint.id
        });

        const res = await searchAnalystStoreRoutingHandler.handle({
            data: {query: {cityGeoId: CityGeoId.MOSCOW}},
            context
        });

        expect(res.items).toHaveLength(1);
    });

    it('should return routing with search name', async () => {
        const user = context.user;

        const managerPoint = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId: CityGeoId.MOSCOW,
            point: [12, 23],
            name: 'test name'
        });

        await TestFactory.createAnalystStoreRouting(user.uid, {
            id: '1',
            status: AnalystStoreRoutingStatus.NEW,
            userId: user.uid,
            cityId: CityGeoId.MOSCOW,
            ticketSlug: 'TEST-1234',
            managerPointId: managerPoint.id
        });

        const res = await searchAnalystStoreRoutingHandler.handle({
            data: {query: {search: 'test', cityGeoId: CityGeoId.MOSCOW}},
            context
        });

        expect(res.items).toHaveLength(1);
    });

    it('should return routing with filter by status', async () => {
        const user = context.user;

        const managerPoint = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId: CityGeoId.MOSCOW,
            point: [12, 23],
            name: 'test name'
        });

        await TestFactory.createAnalystStoreRouting(user.uid, {
            id: '1',
            status: AnalystStoreRoutingStatus.NEW,
            userId: user.uid,
            cityId: CityGeoId.MOSCOW,
            ticketSlug: 'TEST-1234',
            managerPointId: managerPoint.id
        });

        await TestFactory.createAnalystStoreRouting(user.uid, {
            id: '2',
            status: AnalystStoreRoutingStatus.DONE,
            userId: user.uid,
            cityId: CityGeoId.MOSCOW,
            ticketSlug: 'TEST-1234',
            managerPointId: managerPoint.id
        });

        const res = await searchAnalystStoreRoutingHandler.handle({
            data: {query: {statuses: [AnalystStoreRoutingStatus.NEW], cityGeoId: CityGeoId.MOSCOW}},
            context
        });

        expect(res.items).toHaveLength(1);
    });

    it('should return routing with filter by manager point', async () => {
        const user = context.user;

        const managerPointOne = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId: CityGeoId.MOSCOW,
            point: [12, 23],
            name: 'test name'
        });

        const managerPointSecond = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId: CityGeoId.MOSCOW,
            point: [12, 23],
            name: 'test name'
        });

        await TestFactory.createAnalystStoreRouting(user.uid, {
            id: '1',
            status: AnalystStoreRoutingStatus.NEW,
            userId: user.uid,
            cityId: CityGeoId.MOSCOW,
            ticketSlug: 'TEST-1234',
            managerPointId: managerPointOne.id
        });

        await TestFactory.createAnalystStoreRouting(user.uid, {
            id: '2',
            status: AnalystStoreRoutingStatus.DONE,
            userId: user.uid,
            cityId: CityGeoId.MOSCOW,
            ticketSlug: 'TEST-1234',
            managerPointId: managerPointSecond.id
        });

        const res = await searchAnalystStoreRoutingHandler.handle({
            data: {query: {managerPointId: managerPointSecond.id, cityGeoId: CityGeoId.MOSCOW}},
            context
        });

        expect(res.items).toHaveLength(1);
        expect(res.items[0].id).toEqual('2');
    });
});
