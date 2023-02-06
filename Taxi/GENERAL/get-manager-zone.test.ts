import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';

import {getManagerZonesHandler} from './get-manager-zones';

describe('get manager zones', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return manager zones by geo id', async () => {
        const cityGeoId = 123;
        const name = 'test zone';
        const user = context.user;
        await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: {},
            name
        });

        const res = await getManagerZonesHandler.handle({
            data: {query: {filters: {cityGeoId}}},
            context
        });

        expect(res.items).toHaveLength(1);
    });

    it('should return empty result if there`re no zones for geo id', async () => {
        const cityGeoId = 123;
        const name = 'test zone';
        const user = context.user;
        await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: {},
            name
        });

        const res = await getManagerZonesHandler.handle({
            data: {query: {filters: {cityGeoId: 4000}}},
            context
        });

        expect(res.items).toHaveLength(0);
    });

    it('should return empty result if there`re no zones for this user', async () => {
        const cityGeoId = 123;
        const uid = '666';
        const name = 'test zone';
        await TestFactory.createUserWithUid(uid);
        await TestFactory.createManagerZone(user.uid, {
            userId: uid,
            cityGeoId,
            zone: {},
            name
        });

        const res = await getManagerZonesHandler.handle({
            data: {query: {filters: {cityGeoId}}},
            context
        });

        expect(res.items).toHaveLength(0);
    });

    it('should return the zone if the user is not the owner but the zone is published', async () => {
        const cityGeoId = 123;
        const uid = '666';
        const name = 'test zone';
        await TestFactory.createUserWithUid(uid);
        await TestFactory.createManagerZone(user.uid, {
            userId: uid,
            cityGeoId,
            zone: {},
            name,
            isPublished: true
        });

        const res = await getManagerZonesHandler.handle({
            data: {query: {filters: {cityGeoId}}},
            context
        });

        expect(res.items).toHaveLength(1);
    });
});
