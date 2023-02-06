import {random} from 'lodash';
import {beforeEach, describe, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {EntityNotFoundError} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';

import {moveAttributeGroupHandler} from './move-group-attribute';

describe('move group attribute', () => {
    let user: User;
    let regions: Region[];
    let langs: Lang[];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {attributeGroup: {canEdit: true}}});
        regions = await Promise.all([TestFactory.createRegion(), TestFactory.createRegion()]);
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        context = await TestFactory.createApiContext({user, region: regions[0], lang: langs[0]});
    });

    it('should move group', async () => {
        const firstGroup = await TestFactory.createAttributeGroup({userId: user.id, attributeGroup: {code: 'test1'}});
        const secondGroup = await TestFactory.createAttributeGroup({userId: user.id, attributeGroup: {code: 'test2'}});
        const thirdGroup = await TestFactory.createAttributeGroup({userId: user.id, attributeGroup: {code: 'test3'}});

        const expectedGroupOrder = [secondGroup, thirdGroup, firstGroup].map(({id}) => id);

        await moveAttributeGroupHandler.handle({context, data: {params: {id: firstGroup.id}, body: {index: 2}}});

        const resortedGroups = await TestFactory.getAttributeGroups();

        expect(resortedGroups.map(({id}) => id)).toEqual(expectedGroupOrder);
    });

    it('should throw not found if group does not exist', async () => {
        const moveGroupPromise = moveAttributeGroupHandler.handle({
            context,
            data: {params: {id: random(420)}, body: {index: 2}}
        });

        await expect(moveGroupPromise).rejects.toThrow(EntityNotFoundError);
        await expect(moveGroupPromise.catch((err) => err.parameters)).resolves.toMatchObject({
            entity: 'AttributeGroup'
        });
    });
});
