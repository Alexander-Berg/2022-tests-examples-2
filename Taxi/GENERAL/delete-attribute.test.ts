import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {AccessForbidden, RemoveAttributeUsedInProductsIsForbidden} from '@/src/errors';
import type {ApiRequestContext} from '@/src/server/routes/api/api-handler';
import {AttributeType} from '@/src/types/attribute';

import {getInfoModelByIdHandler} from '../info-models/get-info-model-by-id';
import {deleteAttributeHandler} from './delete-attribute';

describe('delete attribute', () => {
    let user: User;
    let lang: Lang;
    let region: Region;
    let langCodes: string[];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {attribute: {canEdit: true}}});
        region = await TestFactory.createRegion();
        lang = await TestFactory.createLang();
        langCodes = [lang.isoCode];
        context = await TestFactory.createApiContext({lang, user, region});
    });
    it('should delete attribute', async () => {
        const attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.SELECT,
                    isArray: false,
                    isValueLocalizable: false,
                    nameTranslationMap: TestFactory.createTranslationMap({langCodes}),
                    descriptionTranslationMap: TestFactory.createTranslationMap({langCodes})
                }
            }),
            await TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.NUMBER,
                    isArray: false,
                    isValueLocalizable: false,
                    nameTranslationMap: TestFactory.createTranslationMap({langCodes}),
                    descriptionTranslationMap: TestFactory.createTranslationMap({langCodes})
                }
            }),
            await TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.STRING,
                    isArray: false,
                    isValueLocalizable: false,
                    nameTranslationMap: TestFactory.createTranslationMap({langCodes}),
                    descriptionTranslationMap: TestFactory.createTranslationMap({langCodes})
                }
            })
        ]);

        const infoModels = await Promise.all([
            TestFactory.createInfoModel({
                userId: user.id,
                regionId: region.id,
                attributes: [
                    {
                        id: attributes[0].id,
                        isImportant: true
                    },
                    {
                        id: attributes[1].id,
                        isImportant: true
                    }
                ]
            }),
            TestFactory.createInfoModel({
                userId: user.id,
                regionId: region.id,
                attributes: [
                    {
                        id: attributes[0].id,
                        isImportant: true
                    },
                    {
                        id: attributes[1].id,
                        isImportant: true
                    },
                    {
                        id: attributes[2].id,
                        isImportant: true
                    }
                ]
            })
        ]);

        await deleteAttributeHandler.handle({
            context,
            data: {
                params: {id: attributes[1].id}
            }
        });

        const result1 = await getInfoModelByIdHandler.handle({context, data: {params: {id: infoModels[0].id}}});

        expect(result1.attributes).toEqual([
            {
                id: attributes[0].id,
                code: attributes[0].code,
                nameTranslations: attributes[0].nameTranslationMap,
                descriptionTranslations: attributes[0].descriptionTranslationMap,
                type: attributes[0].type,
                isArray: attributes[0].isArray,
                isImportant: true,
                attributeGroupSortOrder: null,
                createdAt: expect.any(Date),
                isConfirmable: false
            }
        ]);

        const result2 = await getInfoModelByIdHandler.handle({context, data: {params: {id: infoModels[1].id}}});

        expect(result2.attributes).toEqual([
            {
                id: attributes[0].id,
                code: attributes[0].code,
                nameTranslations: attributes[0].nameTranslationMap,
                descriptionTranslations: attributes[0].descriptionTranslationMap,
                type: attributes[0].type,
                isArray: attributes[0].isArray,
                isImportant: true,
                attributeGroupSortOrder: null,
                createdAt: expect.any(Date),
                isConfirmable: false
            },
            {
                id: attributes[2].id,
                code: attributes[2].code,
                nameTranslations: attributes[2].nameTranslationMap,
                descriptionTranslations: attributes[2].descriptionTranslationMap,
                type: attributes[2].type,
                isArray: attributes[2].isArray,
                isImportant: true,
                attributeGroupSortOrder: null,
                createdAt: expect.any(Date),
                isConfirmable: false
            }
        ]);
    });

    it('should return error if attribute used in product attribute values', async () => {
        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.NUMBER,
                isArray: false,
                isValueLocalizable: false,
                nameTranslationMap: TestFactory.createTranslationMap({langCodes}),
                descriptionTranslationMap: TestFactory.createTranslationMap({langCodes})
            }
        });

        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attribute.id
                }
            ]
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        const product = await TestFactory.createProduct({
            masterCategoryId: mc.id,
            userId: user.id,
            regionId: region.id
        });

        await TestFactory.createProductAttributeValue({
            productId: product.id,
            attributeId: attribute.id,
            value: 1,
            userId: user.id
        });
        const promise = deleteAttributeHandler.handle({context, data: {params: {id: attribute.id}}});
        await expect(promise).rejects.toThrow(RemoveAttributeUsedInProductsIsForbidden);
    });

    it('should throw when user has not permission', async () => {
        const user = await TestFactory.createUser();
        const context = await TestFactory.createApiContext({lang, user});
        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.NUMBER,
                isArray: false,
                isValueLocalizable: false,
                nameTranslationMap: TestFactory.createTranslationMap({langCodes}),
                descriptionTranslationMap: TestFactory.createTranslationMap({langCodes})
            }
        });

        await expect(deleteAttributeHandler.handle({context, data: {params: {id: attribute.id}}})).rejects.toThrow(
            AccessForbidden
        );
    });
});
