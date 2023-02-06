import {range} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {emptyArray} from '@/src/constants';
import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {deleteAttributeGroupHandler} from './delete-attribute-group';

describe('delete attribute group', () => {
    let user: User;
    let regions: Region[];
    let langs: Lang[];
    let langCodes: string[];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {attributeGroup: {canEdit: true}}});
        regions = await Promise.all([TestFactory.createRegion(), TestFactory.createRegion()]);
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        langCodes = langs.map(({isoCode}) => isoCode);
        context = await TestFactory.createApiContext({user, region: regions[0], lang: langs[0]});
    });

    it('should delete group', async () => {
        const attributes = await Promise.all(
            range(1).map(async () => {
                const attribute = await TestFactory.createAttribute({
                    attribute: {
                        type: AttributeType.STRING,
                        nameTranslationMap: TestFactory.createTranslationMap({langCodes})
                    },
                    userId: user.id
                });

                return attribute;
            })
        );

        const attributeGroup = {
            code: 'testGroup',
            attributes: attributes.map(({id}) => id)
        };

        const {id: attributeGroupId} = await TestFactory.createAttributeGroup({userId: user.id, attributeGroup});

        await deleteAttributeGroupHandler.handle({context, data: {params: {id: attributeGroupId}}});

        const createdAttributeGroup = await TestFactory.getAttributeGroupById(attributeGroupId);

        expect(createdAttributeGroup).toBeUndefined();
    });

    it('should unlink attributes', async () => {
        const attributes = await Promise.all(
            range(1).map(async () => {
                const attribute = await TestFactory.createAttribute({
                    attribute: {
                        type: AttributeType.STRING,
                        nameTranslationMap: TestFactory.createTranslationMap({langCodes})
                    },
                    userId: user.id
                });

                return attribute;
            })
        );

        const attributeGroup = {
            code: 'testGroup',
            attributes: attributes.map(({id}) => id)
        };

        const {id: attributeGroupId} = await TestFactory.createAttributeGroup({userId: user.id, attributeGroup});

        await deleteAttributeGroupHandler.handle({context, data: {params: {id: attributeGroupId}}});

        const unlinkedAttributes = await TestFactory.getAttributesByGroupId(attributeGroupId);

        expect(unlinkedAttributes).toEqual(emptyArray);
    });
});
