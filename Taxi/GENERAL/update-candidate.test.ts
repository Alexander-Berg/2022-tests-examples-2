import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';

import {updateCandidateHandler} from './update-candidate';

describe('update candidate', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return updated candidate', async () => {
        const user = context.user;

        const candidate = await TestFactory.createCandidate(user.uid, {
            name: 'Warehouse 1'
        });

        const res = await updateCandidateHandler.handle({
            data: {body: {name: 'Warehouse 2', id: candidate.id}},
            context
        });

        expect(res.id).not.toBeUndefined();
        expect(res.name).toEqual('Warehouse 2');
    });
});
