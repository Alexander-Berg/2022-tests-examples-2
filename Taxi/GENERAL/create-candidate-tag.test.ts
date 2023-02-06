import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';

import {createCandidateTagHandler} from './create-candidate-tag';

describe('create candidate tag', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return candidate tag', async () => {
        const res = await createCandidateTagHandler.handle({
            data: {body: {name: 'Test tag'}},
            context
        });

        expect(res.id).not.toBeUndefined();
    });
});
