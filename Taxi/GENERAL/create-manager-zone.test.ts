import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import {ZONE_COLORS} from 'constants/constants';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {zone} from 'service/seed-db/fixtures';

import {createManagerZoneHandler} from './create-manager-zone';

describe('create manager zones', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return manager zone', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const name = 'test zone';

        const res = await createManagerZoneHandler.handle({
            data: {body: {cityGeoId, zone, name, color: ZONE_COLORS[0]}},
            context
        });

        expect(res.id).not.toBeUndefined();
    });

    it('should return published manager zone if created with isPublished: true', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const name = 'test zone';

        const res = await createManagerZoneHandler.handle({
            data: {body: {cityGeoId, zone, name, isPublished: true}},
            context
        });

        expect(res.id).not.toBeUndefined();
        expect(res.isPublished).toEqual(true);
    });

    it('should return published manager zone if created with isPublished: false', async () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const name = 'test zone';

        const res = await createManagerZoneHandler.handle({
            data: {body: {cityGeoId, zone, name, isPublished: false}},
            context
        });

        expect(res.id).not.toBeUndefined();
        expect(res.isPublished).toEqual(false);
    });
});
