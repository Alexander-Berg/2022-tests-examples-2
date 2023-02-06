import {random} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {AnalystStoreRoutingStatus} from 'types/analyst-store-routing';

import {getAnalystStoreRoutingHandler} from './get-analyst-store-routing-by-id';

describe('get routing by id', () => {
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
        const searchId = '1';

        const managerPoint = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId: 213,
            point: [12, 23],
            name: 'test name'
        });

        await TestFactory.createAnalystStoreRouting(user.uid, {
            id: searchId,
            status: AnalystStoreRoutingStatus.NEW,
            cityId: CityGeoId.MOSCOW,
            userId: user.uid,
            ticketSlug: 'TEST-1234',
            managerPointId: managerPoint.id
        });

        await TestFactory.createAnalystStoreRouting(user.uid, {
            id: '2',
            status: AnalystStoreRoutingStatus.NEW,
            cityId: CityGeoId.MOSCOW,
            userId: user.uid,
            ticketSlug: 'TEST-1234',
            managerPointId: managerPoint.id
        });

        const res = await getAnalystStoreRoutingHandler.handle({
            data: {query: {id: searchId}},
            context
        });

        expect(res.id).toEqual(searchId);
    });

    it('should throw error if analyst routing does not exist', async () => {
        const unknownId = random(999999).toString();

        await expect(
            getAnalystStoreRoutingHandler.handle({
                data: {query: {id: unknownId}},
                context
            })
        ).rejects.toThrow();
    });
});
