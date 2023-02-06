import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import {EntitiesGroupType} from 'types/entities-group';

import {updateEntitiesGroupHandler} from './update-entities-group';

describe('update entities group', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return updated draft group', async () => {
        const entitiesGroup = await TestFactory.createEntitiesGroup(user.uid, {
            name: 'test group',
            groupType: EntitiesGroupType.DRAFT
        });

        const res = await updateEntitiesGroupHandler.handle({
            data: {body: {id: entitiesGroup.id, name: 'rename group', groupType: EntitiesGroupType.DRAFT}},
            context
        });

        expect(res).toMatchObject({id: entitiesGroup.id, name: 'rename group', groupType: EntitiesGroupType.DRAFT});
    });
});
