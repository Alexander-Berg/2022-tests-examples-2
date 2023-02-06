import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';

import {getCandidateTagsHandler} from './get-candidate-tags';

describe('get candidate tags', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return candidate tags by name', async () => {
        const user = context.user;
        await TestFactory.createCandidateTag(user.uid, {
            name: 'Moscow',
            userId: '1'
        });

        await TestFactory.createCandidateTag(user.uid, {
            name: 'Minsk',
            userId: '1'
        });

        const res = await getCandidateTagsHandler.handle({
            data: {query: {filters: {name: 'Mos'}}},
            context
        });

        expect(res.items).toHaveLength(1);
    });
});
