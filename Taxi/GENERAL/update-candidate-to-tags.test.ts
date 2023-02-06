import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {CandidateStatus} from 'types/crm-candidates';

import {updateCandidateToTagsHandler} from './update-candidate-to-tags';

describe('update candidate to tags', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return updated candidate to tags', async () => {
        const user = context.user;

        const candidate = await TestFactory.createCandidate(user.uid, {
            name: 'Warehouse 1',
            status: CandidateStatus.PROGRESS,
            description: 'Test',
            cityGeoId: CityGeoId.MOSCOW
        });

        const tag = await TestFactory.createCandidateTag(user.uid, {
            name: 'Test tag 1',
            userId: '1'
        });

        const res = await updateCandidateToTagsHandler.handle({
            data: {body: {tagsId: [tag.id], candidateId: candidate.id, newTags: ['Test tag 2']}},
            context
        });

        expect(res).toHaveLength(2);
    });
});
