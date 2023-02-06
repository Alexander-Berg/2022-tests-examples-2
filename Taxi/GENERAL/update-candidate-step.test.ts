import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {CandidateStepStatus, StepCode} from 'types/crm-candidates';

import {getCandidateStepsHandler} from './get-candidate-steps';
import {updateCandidateStepHandler} from './update-candidate-step';

describe('update candidate step', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return updated candidate step', async () => {
        const candidate = await TestFactory.createCandidate(user.uid, {
            responsibleUserId: user.uid
        });

        const candidateStep = await TestFactory.createCandidateStep(user.uid, {
            candidateId: candidate.id,
            stepCode: StepCode.N_1_1
        });

        const res = await updateCandidateStepHandler.handle({
            data: {body: {id: candidateStep.id, status: CandidateStepStatus.APPROVE}},
            context
        });

        expect(res.id).not.toBeUndefined();
        expect(res.status).toEqual(CandidateStepStatus.APPROVE);
    });

    it('should create the next step', async () => {
        const user = context.user;

        const candidate = await TestFactory.createCandidate(user.uid, {
            responsibleUserId: user.uid
        });

        const candidateItem = await TestFactory.createCandidateStep(user.uid, {
            candidateId: candidate.id,
            status: CandidateStepStatus.PROGRESS,
            stepCode: StepCode.N_1_1
        });

        await updateCandidateStepHandler.handle({
            data: {body: {id: candidateItem.id, status: CandidateStepStatus.APPROVE}},
            context
        });

        const res = await getCandidateStepsHandler.handle({
            data: {query: {filters: {candidateId: candidate.id, status: CandidateStepStatus.PROGRESS}}},
            context
        });

        expect(res.items).toHaveLength(1);
        expect(res.items[0].stepCode).toEqual(StepCode.N_1_2);
        expect(res.items[0].status).toEqual(CandidateStepStatus.PROGRESS);
    });

    it('should create the previous step since the current one was canceled', async () => {
        const user = context.user;

        const candidate = await TestFactory.createCandidate(user.uid, {
            responsibleUserId: user.uid
        });

        const candidateItem = await TestFactory.createCandidateStep(user.uid, {
            candidateId: candidate.id,
            status: CandidateStepStatus.PROGRESS,
            stepCode: StepCode.N_1_2
        });

        await updateCandidateStepHandler.handle({
            data: {body: {id: candidateItem.id, status: CandidateStepStatus.REJECT}},
            context
        });

        const res = await getCandidateStepsHandler.handle({
            data: {query: {filters: {candidateId: candidate.id, status: CandidateStepStatus.PROGRESS}}},
            context
        });

        expect(res.items).toHaveLength(1);
        expect(res.items[0].stepCode).toEqual(StepCode.N_1_1);
        expect(res.items[0].status).toEqual(CandidateStepStatus.PROGRESS);
    });

    it(`should create the next step with the status
        in progress, since all required steps have been confirmed.`, async () => {
        const user = context.user;

        const candidate = await TestFactory.createCandidate(user.uid, {
            responsibleUserId: user.uid
        });

        const candidateStepOne = await TestFactory.createCandidateStep(user.uid, {
            candidateId: candidate.id,
            status: CandidateStepStatus.PROGRESS,
            stepCode: StepCode.N_2_31
        });

        const candidateStepTwo = await TestFactory.createCandidateStep(user.uid, {
            candidateId: candidate.id,
            status: CandidateStepStatus.PROGRESS,
            stepCode: StepCode.N_2_32
        });

        await updateCandidateStepHandler.handle({
            data: {body: {id: candidateStepOne.id, status: CandidateStepStatus.APPROVE}},
            context
        });

        await updateCandidateStepHandler.handle({
            data: {body: {id: candidateStepTwo.id, status: CandidateStepStatus.APPROVE}},
            context
        });

        const res = await getCandidateStepsHandler.handle({
            data: {query: {filters: {candidateId: candidate.id, status: CandidateStepStatus.PROGRESS}}},
            context
        });

        expect(res.items).toHaveLength(1);
        expect(res.items[0].stepCode).toEqual(StepCode.N_2_35);
        expect(res.items[0].status).toEqual(CandidateStepStatus.PROGRESS);
    });
});
