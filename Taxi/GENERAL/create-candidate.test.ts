import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';

import {createCandidateHandler} from './create-candidate';

describe('create candidate', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return candidate', async () => {
        const res = await createCandidateHandler.handle({
            data: {
                body: {
                    name: 'Warehouse 1',
                    description: 'Test',
                    performerId: user.uid,
                    cityGeoId: CityGeoId.MOSCOW
                }
            },
            context
        });

        expect(res.id).not.toBeUndefined();
    });
});
