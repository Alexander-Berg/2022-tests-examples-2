import {range} from 'lodash';
import {beforeEach, describe, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {getAttributeGroupHistory} from './get-history-by-attribute-group-id';

describe('get attribute group history by id', () => {
    let user: User;
    let region: Region;
    let langs: Lang[];
    let context: ApiRequestContext;
    let langCodes: string[];

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        langs = await Promise.all(range(2).map(() => TestFactory.createLang()));
        context = await TestFactory.createApiContext({lang: langs[0], user, region});
        langCodes = langs.map(({isoCode}) => isoCode);
    });

    it('should return attribute group history', async () => {
        const attributes = await Promise.all(
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

        const attributeGroup = await TestFactory.createAttributeGroup({
            userId: user.id,
            attributeGroup: {
                code: 'test1',
                attributes: attributes.map(({id}) => id),
                nameTranslationMap: TestFactory.createTranslationMap({langCodes, values: ['Имя группы', 'Group Name']}),
                descriptionTranslationMap: TestFactory.createTranslationMap({
                    langCodes,
                    values: ['Описание группы', 'Group Description']
                })
            }
        });

        const history = await getAttributeGroupHistory.handle({context, data: {params: {id: attributeGroup.id}}});

        const expectedMutationAttributes = attributeGroup.attributes.map((attribute) => ({code: attribute.code}));

        expect(history.list).toMatchObject([
            {
                author: {id: user.id, login: user.login},
                stamp: MOCKED_STAMP,
                mutation: {
                    id: {old: null, new: attributeGroup.id},
                    code: {old: null, new: attributeGroup.code},
                    nameTranslationMap: {old: null, new: attributeGroup.nameTranslationMap},
                    descriptionTranslationMap: {old: null, new: attributeGroup.descriptionTranslationMap},
                    sortOrder: {old: null, new: attributeGroup.sortOrder + 1},
                    attributesSortOrder: {old: [], new: expectedMutationAttributes},
                    attributes: {old: [], new: expectedMutationAttributes}
                }
            }
        ]);
    });

    it('should show changes in history', async () => {
        const attributeGroup = await TestFactory.createAttributeGroup({
            userId: user.id,
            attributeGroup: {
                code: 'test1',
                nameTranslationMap: TestFactory.createTranslationMap({langCodes, values: ['Имя группы', 'Group Name']})
            }
        });

        const newNameTranslationMap = TestFactory.createTranslationMap({
            langCodes,
            values: ['Новое имя группы', 'New Group Name']
        });

        const newStamp = MOCKED_STAMP.replace(/0$/, '1');

        await TestFactory.updateAttributeGroup(attributeGroup.id, {
            attributeGroup: {nameTranslationMap: newNameTranslationMap},
            userId: user.id,
            stamp: newStamp
        });

        const history = await getAttributeGroupHistory.handle({context, data: {params: {id: attributeGroup.id}}});

        expect(history.list[0]).toMatchObject({
            author: {id: user.id, login: user.login},
            stamp: newStamp,
            mutation: {
                nameTranslationMap: {old: attributeGroup.nameTranslationMap, new: newNameTranslationMap},
                attributes: {old: [], new: []}
            }
        });
    });
});
