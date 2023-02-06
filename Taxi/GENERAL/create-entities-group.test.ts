import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {EntitiesGroupType} from 'types/entities-group';

import {createEntitiesGroupHandler} from './create-entities-group';

describe('create entities group', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return created draft group', async () => {
        const res = await createEntitiesGroupHandler.handle({
            data: {body: {name: 'test group', groupType: EntitiesGroupType.DRAFT}},
            context
        });

        expect(res.id).not.toBeUndefined();
        expect(res.groupType).toBe(EntitiesGroupType.DRAFT);
    });
});
