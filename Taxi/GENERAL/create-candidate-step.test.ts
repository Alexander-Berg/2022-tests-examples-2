import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {CandidateStatus, CandidateStepStatus, StepCode} from 'types/crm-candidates';

import {createCandidateStepHandler} from './create-candidate-step';

describe('create candidate step', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return candidate step', async () => {
        const candidate = await TestFactory.createCandidate(user.uid, {
            name: 'Warehouse 1',
            status: CandidateStatus.PROGRESS,
            description: 'Test',
            cityGeoId: CityGeoId.MOSCOW,
            responsibleUserId: user.uid
        });

        const res = await createCandidateStepHandler.handle({
            data: {
                body: {
                    candidateId: candidate.id,
                    status: CandidateStepStatus.PROGRESS,
                    stepCode: StepCode.N_1_1,
                    responsibleUserId: user.uid
                }
            },
            context
        });

        expect(res.id).not.toBeUndefined();
    });
});
