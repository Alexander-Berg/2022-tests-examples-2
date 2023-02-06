import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';

import {getManagerPointsHandler} from './get-manager-points';

describe('get manager points', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return manager points by geo id', async () => {
        const cityGeoId = 123;
        const user = context.user;
        await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId,
            point: [23, 33],
            name: 'test point'
        });

        const res = await getManagerPointsHandler.handle({
            data: {query: {filters: {cityGeoId}}},
            context
        });

        expect(res.items).toHaveLength(1);
    });

    it('should return empty result if there`re no points for geo id', async () => {
        const cityGeoId = 123;
        const user = context.user;
        await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId,
            point: [2, 3],
            name: 'test point'
        });

        const res = await getManagerPointsHandler.handle({
            data: {query: {filters: {cityGeoId: 4000}}},
            context
        });

        expect(res.items).toHaveLength(0);
    });

    it("should return empty result if the user doesn't have access to any point", async () => {
        const cityGeoId = 123;
        const uid = '666';
        await TestFactory.createUserWithUid(uid);
        await TestFactory.createManagerPoint(uid, {
            userId: uid,
            cityGeoId,
            point: [2, 3],
            name: 'test point'
        });

        const res = await getManagerPointsHandler.handle({
            data: {query: {filters: {cityGeoId}}},
            context
        });

        expect(res.items).toHaveLength(0);
    });

    it('should return point if the user is not the owner but the point was published', async () => {
        const cityGeoId = 123;
        const uid = '666';
        await TestFactory.createUserWithUid(uid);
        await TestFactory.createManagerPoint(uid, {
            userId: uid,
            cityGeoId,
            point: [2, 3],
            name: 'test point',
            isPublished: true
        });

        const res = await getManagerPointsHandler.handle({
            data: {query: {filters: {cityGeoId}}},
            context
        });

        expect(res.items).toHaveLength(1);
    });
});
