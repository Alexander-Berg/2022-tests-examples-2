import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {CandidateStepActionType, CandidateStepStatus, StepCode} from 'types/crm-candidates';

import {deleteCandidateStepActionHandler} from './delete-candidate-step-action';

describe('delete candidate step action', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return deleted candidate item action', async () => {
        const user = context.user;

        const candidate = await TestFactory.createCandidate(user.uid, {
            responsibleUserId: user.uid
        });

        const candidateStep = await TestFactory.createCandidateStep(user.uid, {
            candidateId: candidate.id,
            status: CandidateStepStatus.PROGRESS,
            stepCode: StepCode.N_1_1
        });

        const candidateStepAction = await TestFactory.createCandidateStepAction(user.uid, {
            candidateStepId: candidateStep.id,
            type: CandidateStepActionType.COMMENT,
            comment: 'Comment',
            userId: user.uid
        });

        const res = await deleteCandidateStepActionHandler.handle({
            data: {
                body: {
                    id: candidateStepAction.id
                }
            },
            context
        });

        expect(res.raw).not.toBeUndefined();
    });
});
