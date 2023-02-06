import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';

import {createManagerPointHandler} from './create-manager-point';

describe('create manager points', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return manager point', async () => {
        const cityGeoId = 123;

        const res = await createManagerPointHandler.handle({
            data: {body: {cityGeoId, point: [32, 33], name: 'test point'}},
            context
        });

        expect(res.id).not.toBeUndefined();
    });
});
