import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {CandidateStepStatus, StepCode} from 'types/crm-candidates';

import {getCandidateStepsHandler} from './get-candidate-steps';

describe('get candidate steps', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return candidate items', async () => {
        const user = context.user;
        const candidate = await TestFactory.createCandidate(user.uid, {
            responsibleUserId: user.uid
        });

        await TestFactory.createCandidateStep(user.uid, {
            candidateId: candidate.id,
            status: CandidateStepStatus.PROGRESS,
            stepCode: StepCode.N_1_1
        });

        const res = await getCandidateStepsHandler.handle({
            data: {query: {filters: {candidateId: candidate.id}}},
            context
        });

        expect(res.items).toHaveLength(1);
    });
});
