import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';

import {getCandidateToTagsHandler} from './get-candidate-to-tags';

describe('get candidate to tags', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return tags by candidate id', async () => {
        const user = context.user;
        const candidate1 = await TestFactory.createCandidate(user.uid, {
            name: 'Warehouse 1'
        });

        const candidate2 = await TestFactory.createCandidate(user.uid, {
            name: 'Warehouse 2'
        });

        const tag = await TestFactory.createCandidateTag(user.uid, {
            name: 'Test tag 1',
            userId: '1'
        });

        await TestFactory.createCandidateToTag(user.uid, {
            candidateId: candidate1.id,
            candidateTagId: tag.id
        });

        await TestFactory.createCandidateToTag(user.uid, {
            candidateId: candidate2.id,
            candidateTagId: tag.id
        });

        const res = await getCandidateToTagsHandler.handle({
            data: {query: {filters: {candidateId: candidate1.id}}},
            context
        });

        expect(res.items).toHaveLength(1);
    });
});
