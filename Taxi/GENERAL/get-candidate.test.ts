import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import type {Candidate} from 'types/crm-candidates';

import {getCandidateHandler} from './get-candidate';

describe('get candidate', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return candidate by id', async () => {
        const {id} = await TestFactory.createCandidate(user.uid, {
            responsibleUserId: user.uid
        });

        const candidateRes = await getCandidateHandler.handle({
            data: {query: {filters: {id}}},
            context
        });

        expect(candidateRes).toMatchObject<Partial<Candidate>>({
            id
        });
    });
});
