import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';

import {getCandidatesListHandler} from './get-candidates-list';

describe('get candidates', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return candidates', async () => {
        await TestFactory.createCandidate(user.uid, {
            responsibleUserId: user.uid
        });

        const res = await getCandidatesListHandler.handle({
            data: {query: {filters: {}}},
            context
        });

        expect(res.items).toHaveLength(1);
    });
});
