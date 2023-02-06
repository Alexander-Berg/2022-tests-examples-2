import {random} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';

import {deleteManagerPointsHandler} from './delete-manager-point';

describe('update manager points', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return deleted manager point', async () => {
        const cityGeoId = 123;
        const user = context.user;
        const managerPoint = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId,
            point: [12, 213],
            name: 'test name'
        });

        const res = await deleteManagerPointsHandler.handle({
            data: {body: {ids: [managerPoint.id]}},
            context
        });

        expect(res.raw).not.toBeUndefined();
    });

    it('should throw error if manager point does not exist', async () => {
        const unknownId = random(999999);

        await expect(
            deleteManagerPointsHandler.handle({
                data: {body: {ids: [unknownId.toString()]}},
                context
            })
        ).rejects.toThrow();
    });

    it('should throw error if the user is not point owner', async () => {
        const cityGeoId = 123;
        const uid = '666';
        await TestFactory.createUserWithUid(uid);
        const managerPoint = await TestFactory.createManagerPoint(uid, {
            userId: uid,
            cityGeoId,
            point: [12, 213],
            name: 'test name'
        });

        await expect(
            deleteManagerPointsHandler.handle({
                data: {body: {ids: [managerPoint.id]}},
                context
            })
        ).rejects.toThrow();
    });

    it('should return deleted point if the user is not point owner and point was published', async () => {
        const cityGeoId = 123;
        const uid = '666';
        await TestFactory.createUserWithUid(uid);
        const managerPoint = await TestFactory.createManagerPoint(uid, {
            userId: uid,
            cityGeoId,
            point: [12, 213],
            name: 'test name',
            isPublished: true
        });

        const res = await deleteManagerPointsHandler.handle({
            data: {body: {ids: [managerPoint.id]}},
            context
        });

        expect(res.raw).not.toBeUndefined();
    });

    it('should throw if the user is not point owner and point was not published', async () => {
        const cityGeoId = 123;
        const uid = '666';
        await TestFactory.createUserWithUid(uid);
        const managerPoint = await TestFactory.createManagerPoint(uid, {
            userId: uid,
            cityGeoId,
            point: [12, 213],
            name: 'test name'
        });

        await expect(
            deleteManagerPointsHandler.handle({
                data: {body: {ids: [managerPoint.id]}},
                context
            })
        ).rejects.toThrow();
    });

    it('should return deleted two manager points', async () => {
        const cityGeoId = 123;
        const user = context.user;
        const firstManagerPoint = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId,
            point: [12, 213],
            name: 'test name #1'
        });

        const secondManagerPoint = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId,
            point: [12, 213],
            name: 'test name #2'
        });

        const res = await deleteManagerPointsHandler.handle({
            data: {body: {ids: [firstManagerPoint.id, secondManagerPoint.id]}},
            context
        });

        expect(res.raw).not.toBeUndefined();
    });
});
