import {random, range} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {EntityNotFoundError, UnknownAttributesError} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {updateAttributeGroupHandler} from './update-attribute-group';

describe('update attribute group', () => {
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

    it('should update translations', async () => {
        const attributeGroupData = {
            code: 'testGroup',
            nameTranslationMap: TestFactory.createTranslationMap({langCodes, values: ['имя', 'name']}),
            descriptionTranslationMap: TestFactory.createTranslationMap({
                langCodes,
                values: ['описание', 'description']
            })
        };

        const attributeGroup = await TestFactory.createAttributeGroup({
            userId: user.id,
            attributeGroup: attributeGroupData
        });

        const newNameTranslationsMap = TestFactory.createTranslationMap({langCodes, values: ['Новое имя', 'New name']});
        const newDescriptionTranslationsMap = TestFactory.createTranslationMap({
            langCodes,
            values: ['Новое описание', 'New description']
        });

        await updateAttributeGroupHandler.handle({
            context,
            data: {
                params: {id: attributeGroup.id},
                body: {
                    nameTranslations: newNameTranslationsMap,
                    descriptionTranslations: newDescriptionTranslationsMap
                }
            }
        });

        const updatedGroup = await TestFactory.getAttributeGroupById(attributeGroup.id);

        expect(updatedGroup).toEqual({
            ...attributeGroup,
            nameTranslationMap: newNameTranslationsMap,
            descriptionTranslationMap: newDescriptionTranslationsMap
        });
    });

    it('should update attributes', async () => {
        const initialAttributes = await Promise.all(
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

        const attributeGroupData = {
            code: 'testGroup',
            nameTranslationMap: TestFactory.createTranslationMap({langCodes, values: ['имя', 'name']}),
            descriptionTranslationMap: TestFactory.createTranslationMap({
                langCodes,
                values: ['описание', 'description']
            }),
            attributes: initialAttributes.map(({id}) => id)
        };

        const attributeGroup = await TestFactory.createAttributeGroup({
            userId: user.id,
            attributeGroup: attributeGroupData
        });

        const newAttributes = await Promise.all(
            range(2).map(async () => {
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

        await updateAttributeGroupHandler.handle({
            context,
            data: {
                params: {id: attributeGroup.id},
                body: {
                    attributes: newAttributes.map(({id}) => id)
                }
            }
        });

        const updatedGroup = await TestFactory.getAttributeGroupById(attributeGroup.id);
        const linkedNewAttributes = newAttributes.map((group, index) => ({
            ...group,
            attributeGroupId: updatedGroup?.id,
            attributeGroupSortOrder: index
        }));

        expect(updatedGroup).toEqual({
            ...attributeGroup,
            attributes: linkedNewAttributes
        });
    });

    it('should throw error if attribute does not exist', async () => {
        const attributeGroupData = {
            code: 'testGroup'
        };

        const attributeGroup = await TestFactory.createAttributeGroup({
            userId: user.id,
            attributeGroup: attributeGroupData
        });

        const updatePromise = updateAttributeGroupHandler.handle({
            context,
            data: {
                params: {id: attributeGroup.id},
                body: {
                    attributes: [random(420)]
                }
            }
        });

        await expect(updatePromise).rejects.toThrow(UnknownAttributesError);
    });

    it('should throw error if group does not exist', async () => {
        const updatePromise = updateAttributeGroupHandler.handle({
            context,
            data: {
                params: {id: random(420)},
                body: {
                    descriptionTranslations: {}
                }
            }
        });

        await expect(updatePromise).rejects.toThrow(EntityNotFoundError);
        await expect(updatePromise.catch((err) => err.parameters)).resolves.toMatchObject({
            entity: 'AttributeGroup'
        });
    });
});
