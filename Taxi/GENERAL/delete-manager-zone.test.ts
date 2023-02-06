import {random} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';

import {deleteManagerZoneHandler} from './delete-manager-zone';

describe('delete manager zone', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should delete own zone when given valid zone id', async () => {
        const cityGeoId = 123;
        const user = context.user;

        const managerZone = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: {},
            name: 'test zone'
        });

        const res = await deleteManagerZoneHandler.handle({
            data: {body: {ids: [managerZone.id]}},
            context
        });

        expect(res.deletedCount).toBeGreaterThan(0);
    });

    it('should throw error if the user is not the owner and the zone is not published', async () => {
        const cityGeoId = 123;
        const uid = '666';
        await TestFactory.createUserWithUid(uid);
        const managerZone = await TestFactory.createManagerZone(uid, {
            userId: uid,
            cityGeoId,
            zone: {},
            name: 'test zone'
        });

        await expect(
            deleteManagerZoneHandler.handle({
                data: {body: {ids: [managerZone.id]}},
                context
            })
        ).rejects.toThrow();
    });

    it('should delete if the user is not the owner but the zone is published', async () => {
        const cityGeoId = 123;
        const uid = '666';
        await TestFactory.createUserWithUid(uid);
        const managerZone = await TestFactory.createManagerZone(uid, {
            userId: uid,
            cityGeoId,
            zone: {},
            name: 'test zone',
            isPublished: true
        });

        const res = await deleteManagerZoneHandler.handle({
            data: {body: {ids: [managerZone.id]}},
            context
        });

        expect(res.deletedCount).toBeGreaterThan(0);
    });

    it('should throw error if manager zone does not exist', async () => {
        const unknownId = random(999999);

        await expect(
            deleteManagerZoneHandler.handle({
                data: {body: {ids: [String(unknownId)]}},
                context
            })
        ).rejects.toThrow();
    });

    it('should delete one zones when given valid zone id', async () => {
        const cityGeoId = 123;
        const user = context.user;

        await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: {},
            name: 'test zone #1'
        });

        const secondManagerZone = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: {},
            name: 'test zone #2'
        });

        const res = await deleteManagerZoneHandler.handle({
            data: {body: {ids: [secondManagerZone.id]}},
            context
        });

        expect(res.deletedCount).toBeGreaterThan(0);
    });

    it('should delete two zones when given valid zone id', async () => {
        const cityGeoId = 123;
        const user = context.user;

        const firstManagerZone = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: {},
            name: 'test zone #1'
        });

        const secondManagerZone = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: {},
            name: 'test zone #2'
        });

        const res = await deleteManagerZoneHandler.handle({
            data: {body: {ids: [firstManagerZone.id, secondManagerZone.id]}},
            context
        });

        expect(res.deletedCount).toBeGreaterThan(1);
    });
});
