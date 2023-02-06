import {range} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {getAttributeGroupsHandler} from './get-attribute-groups';
import {formatAttributeGroups} from './utils/format-attribute-group';

describe('get attribute groups', () => {
    let user: User;
    let region: Region;
    let langs: Lang[];
    let context: ApiRequestContext;
    let langCodes: string[];

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        langs = await Promise.all(range(2).map(() => TestFactory.createLang()));
        langCodes = langs.map(({isoCode}) => isoCode);
        context = await TestFactory.createApiContext({lang: langs[0], user, region});
        await TestFactory.createLocale({regionId: region.id, langIds: [langs[0].id]});
    });

    it('should return existing groups', async () => {
        const firstGroup = await TestFactory.createAttributeGroup({userId: user.id, attributeGroup: {code: 'test1'}});
        const secondGroup = await TestFactory.createAttributeGroup({userId: user.id, attributeGroup: {code: 'test2'}});

        const groups = await getAttributeGroupsHandler.handle({context, data: {query: {}}});

        expect(formatAttributeGroups([firstGroup, secondGroup])).toEqual(groups.list);
    });

    it('should search by code', async () => {
        const firstGroup = await TestFactory.createAttributeGroup({userId: user.id, attributeGroup: {code: 'test1'}});
        await TestFactory.createAttributeGroup({userId: user.id, attributeGroup: {code: 'test2'}});

        const groups = await getAttributeGroupsHandler.handle({context, data: {query: {search: 'test1'}}});

        expect(formatAttributeGroups([firstGroup])).toEqual(groups.list);
    });

    it('should search by region lang name', async () => {
        const firstGroup = await TestFactory.createAttributeGroup({
            userId: user.id,
            attributeGroup: {
                code: 'test1',
                nameTranslationMap: TestFactory.createTranslationMap({langCodes, values: ['Имя 1', 'Name 1']})
            }
        });
        await TestFactory.createAttributeGroup({userId: user.id, attributeGroup: {code: 'test2'}});
        const thirdGroup = await TestFactory.createAttributeGroup({
            userId: user.id,
            attributeGroup: {
                code: 'test3',
                nameTranslationMap: TestFactory.createTranslationMap({langCodes, values: ['Имя 3', 'Name 3']})
            }
        });

        const groups = await getAttributeGroupsHandler.handle({context, data: {query: {search: 'Имя'}}});

        expect(formatAttributeGroups([firstGroup, thirdGroup])).toEqual(groups.list);
    });

    it('should search by attribute code', async () => {
        const attributes = await Promise.all([
            TestFactory.createAttribute({
                attribute: {
                    type: AttributeType.NUMBER,
                    code: 'attribute1'
                },
                userId: user.id
            })
        ]);

        const firstGroup = await TestFactory.createAttributeGroup({
            userId: user.id,
            attributeGroup: {code: 'test1', attributes: attributes.map(({id}) => id)}
        });
        await TestFactory.createAttributeGroup({userId: user.id, attributeGroup: {code: 'test2'}});

        const groups = await getAttributeGroupsHandler.handle({context, data: {query: {search: 'attribute1'}}});

        expect(formatAttributeGroups([firstGroup])).toEqual(groups.list);
    });

    it('should search by attribute region lang name', async () => {
        const thirdGroupAttributes = await Promise.all([
            TestFactory.createAttribute({
                attribute: {
                    type: AttributeType.NUMBER,
                    code: 'attribute1',
                    nameTranslationMap: TestFactory.createTranslationMap({langCodes, values: ['Имя 1', 'Name 1']})
                },
                userId: user.id
            })
        ]);

        const secondGroupAttributes = await Promise.all(
            range(4).map(async () => {
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

        await TestFactory.createAttributeGroup({
            userId: user.id,
            attributeGroup: {code: 'test1'}
        });
        await TestFactory.createAttributeGroup({
            userId: user.id,
            attributeGroup: {code: 'test2', attributes: secondGroupAttributes.map(({id}) => id)}
        });
        const thirdGroup = await TestFactory.createAttributeGroup({
            userId: user.id,
            attributeGroup: {code: 'test3', attributes: thirdGroupAttributes.map(({id}) => id)}
        });

        const groups = await getAttributeGroupsHandler.handle({context, data: {query: {search: 'Имя'}}});

        expect(formatAttributeGroups([thirdGroup])).toEqual(groups.list);
    });
});
