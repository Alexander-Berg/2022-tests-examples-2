import {random} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {zone} from 'service/seed-db/fixtures';
import {ColorPatternType} from 'types/colors';

import {updateManagerZoneHandler} from './update-manager-zone';

describe('update manager zones', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return updated manager zone', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const oldName = 'old test zone name';
        const user = context.user;
        const managerZone = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: {},
            name: oldName
        });

        const name = 'new test zone name';
        const res = await updateManagerZoneHandler.handle({
            data: {body: {cityGeoId, zone, id: managerZone.id, name}},
            context
        });

        expect(res.id).not.toBeUndefined();
        expect(res.name).toEqual(name);
    });

    it('should throw error if the user is not the owner and the zone is not published', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const name = 'new test zone name';
        const uid = '666';
        await TestFactory.createUserWithUid(uid);
        const managerZone = await TestFactory.createManagerZone(uid, {
            userId: uid,
            cityGeoId,
            zone: {},
            name: 'test zone'
        });

        await expect(
            updateManagerZoneHandler.handle({
                data: {body: {cityGeoId, zone, id: managerZone.id, name}},
                context
            })
        ).rejects.toThrow();
    });

    it('should return updated zone if the user is not the owner but the zone is published', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const name = 'new test zone name';
        const uid = '666';
        await TestFactory.createUserWithUid(uid);
        const managerZone = await TestFactory.createManagerZone(uid, {
            userId: uid,
            cityGeoId,
            zone: {},
            name: 'test zone',
            isPublished: true
        });

        const res = await updateManagerZoneHandler.handle({
            data: {body: {cityGeoId, zone, id: managerZone.id, name}},
            context
        });

        expect(res.id).not.toBeUndefined();
        expect(res.name).toEqual(name);
    });

    it('should throw error if manager zone does not exist', async () => {
        const unknownId = String(random(999999));
        const cityGeoId = CityGeoId.MOSCOW;
        const name = 'Name';

        await expect(
            updateManagerZoneHandler.handle({
                data: {body: {cityGeoId, zone, id: unknownId.toString(), name}},
                context
            })
        ).rejects.toThrow();
    });

    it('should return updated manager zone color', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const zoneName = 'zone name';
        const user = context.user;
        const managerZone = await TestFactory.createManagerZone(user.uid, {
            userId: user.uid,
            cityGeoId,
            zone: {},
            name: zoneName
        });

        const color = '#ffffff';
        const colorPattern = ColorPatternType.ANGLE;
        const res = await updateManagerZoneHandler.handle({
            data: {body: {cityGeoId, zone, id: managerZone.id, color, colorPattern}},
            context
        });

        expect(res.id).not.toBeUndefined();
        expect(res.color).toEqual(color);
        expect(res.colorPattern).toEqual(colorPattern);
    });
});
