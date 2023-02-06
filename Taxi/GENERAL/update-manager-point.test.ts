import {random} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';

import {updateManagerPointHandler} from './update-manager-point';

describe('update manager points', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return updated manager point', async () => {
        const cityGeoId = 123;
        const user = context.user;
        const managerPoint = await TestFactory.createManagerPoint(user.uid, {
            userId: user.uid,
            cityGeoId,
            point: [12, 23],
            name: 'test name'
        });

        const res = await updateManagerPointHandler.handle({
            data: {body: {id: managerPoint.id, cityGeoId, point: [11, 11], name: 'test point'}},
            context
        });

        expect(res.id).not.toBeUndefined();
        expect(res.point[0]).toEqual(11);
        expect(res.point[1]).toEqual(11);
    });

    it('should throw error if manager point does not exist', async () => {
        const unknownId = random(999999);
        const cityGeoId = 123;

        await expect(
            updateManagerPointHandler.handle({
                data: {body: {id: unknownId.toString(), cityGeoId, point: [11, 12], name: 'test point'}},
                context
            })
        ).rejects.toThrow();
    });

    it('should throw error if the user is not the owner and the point is not published', async () => {
        const cityGeoId = 123;
        const uid = '666';
        await TestFactory.createUserWithUid(uid);

        const managerPoint = await TestFactory.createManagerPoint(uid, {
            userId: uid,
            cityGeoId,
            point: [12, 23],
            name: 'test name'
        });

        await expect(
            updateManagerPointHandler.handle({
                data: {body: {id: managerPoint.id, cityGeoId, point: [11, 12], name: 'test point'}},
                context
            })
        ).rejects.toThrow();
    });

    it('should return updated point if the user is not the owner and the point is published', async () => {
        const cityGeoId = 123;
        const uid = '666';
        await TestFactory.createUserWithUid(uid);

        const managerPoint = await TestFactory.createManagerPoint(uid, {
            userId: uid,
            cityGeoId,
            point: [12, 23],
            name: 'test name',
            isPublished: true
        });

        const res = await updateManagerPointHandler.handle({
            data: {body: {id: managerPoint.id, cityGeoId, point: [11, 12], name: 'test point'}},
            context
        });

        expect(res.id).not.toBeUndefined();
    });
});
