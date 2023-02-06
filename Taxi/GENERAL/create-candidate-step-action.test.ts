import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {CandidateStepActionType, CandidateStepStatus, StepCode} from 'types/crm-candidates';

import {createCandidateStepActionHandler} from './create-candidate-step-action';

describe('create candidate step action', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return candidate step action', async () => {
        const candidate = await TestFactory.createCandidate(user.uid, {
            responsibleUserId: user.uid
        });

        const candidateStep = await TestFactory.createCandidateStep(user.uid, {
            candidateId: candidate.id,
            status: CandidateStepStatus.PROGRESS,
            stepCode: StepCode.N_1_1
        });

        const res = await createCandidateStepActionHandler.handle({
            data: {
                body: {
                    candidateStepId: candidateStep.id,
                    type: CandidateStepActionType.COMMENT,
                    comment: 'Comment',
                    userId: user.uid,
                    files: [
                        {
                            groupId: '1',
                            name: 'file',
                            userId: user.uid
                        }
                    ],
                    inviteUsers: [
                        {
                            userId: '1'
                        },
                        {
                            userId: '2'
                        }
                    ]
                }
            },
            context
        });

        expect(res.id).not.toBeUndefined();
    });
});
