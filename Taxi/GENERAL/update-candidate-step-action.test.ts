import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {CandidateStepActionType, StepCode} from 'types/crm-candidates';

import {updateCandidateStepActionHandler} from './update-candidate-step-action';

describe('update candidate step action', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return updated candidate step action', async () => {
        const user = context.user;

        const candidate = await TestFactory.createCandidate(user.uid, {
            responsibleUserId: user.uid
        });

        const candidateStep = await TestFactory.createCandidateStep(user.uid, {
            candidateId: candidate.id,
            stepCode: StepCode.N_1_1
        });

        const candidateStepAction = await TestFactory.createCandidateStepAction(user.uid, {
            candidateStepId: candidateStep.id,
            type: CandidateStepActionType.COMMENT,
            comment: 'Comment',
            userId: user.uid
        });

        const res = await updateCandidateStepActionHandler.handle({
            data: {
                body: {
                    id: candidateStepAction.id,
                    comment: 'Comment updated',
                    fileIds: [],
                    filesNew: [
                        {
                            groupId: '1',
                            name: 'file 2',
                            userId: user.uid
                        }
                    ],
                    inviteUserIds: [],
                    inviteUsersNew: [{userId: '3'}]
                }
            },
            context
        });

        expect(res.id).toBeDefined();
        expect(res.comment).toEqual('Comment updated');
        expect(res.files?.[0].name).toEqual('file 2');
        expect(res.inviteUsers?.[0].userId).toEqual('3');
    });
});
