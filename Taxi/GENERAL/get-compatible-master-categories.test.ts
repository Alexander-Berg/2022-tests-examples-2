import {times} from 'lodash';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {getCompatibleMasterCategoriesHandler} from './get-compatible-master-categories';

describe('get compatible master categories', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;

    function createAttribute(isValueRequired: boolean = false) {
        return TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.NUMBER, isValueRequired}
        });
    }

    function createInfoModel(...attributeIds: number[]) {
        return TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: attributeIds.map((id) => ({id}))
        });
    }

    function createMasterCategory(parentId?: number, infoModelId?: number, code?: string) {
        return TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId,
            infoModelId,
            code
        });
    }

    function createProduct(masterCategoryId: number) {
        return TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId
        });
    }

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
    });

    it('should return compatible master category tree by product identifiers', async () => {
        const attribute = await createAttribute();
        const infoModel = await createInfoModel(attribute.id);
        const rootMasterCategory = await createMasterCategory(undefined, infoModel.id);
        const parentMasterCategory = await createMasterCategory(rootMasterCategory.id);

        const masterCategory1 = await createMasterCategory(parentMasterCategory.id);
        const product1 = await createProduct(masterCategory1.id);

        const masterCategory2 = await createMasterCategory(parentMasterCategory.id);
        const product2 = await createProduct(masterCategory2.id);

        await expect(
            getCompatibleMasterCategoriesHandler.handle({
                context,
                data: {body: {identifiers: [product1.identifier, product2.identifier]}}
            })
        ).resolves.toEqual({
            totalCount: 4,
            list: [
                {
                    id: rootMasterCategory.id,
                    code: rootMasterCategory.code,
                    status: rootMasterCategory.status,
                    infoModel: {
                        id: infoModel.id,
                        code: infoModel.code,
                        titleTranslations: infoModel.titleTranslationMap,
                        isInherited: false
                    },
                    updatedAt: expect.any(Date),
                    nameTranslations: rootMasterCategory.nameTranslationMap,
                    descriptionTranslations: rootMasterCategory.descriptionTranslationMap,
                    productsCount: undefined,
                    filledProductsCount: 0,
                    notFilledProductsCount: 0,
                    fullness: 0,
                    averageFullness: 0,
                    sortOrder: 0,
                    children: [
                        {
                            id: parentMasterCategory.id,
                            code: parentMasterCategory.code,
                            status: parentMasterCategory.status,
                            infoModel: {
                                id: infoModel.id,
                                code: infoModel.code,
                                titleTranslations: infoModel.titleTranslationMap,
                                isInherited: true
                            },
                            updatedAt: expect.any(Date),
                            nameTranslations: parentMasterCategory.nameTranslationMap,
                            descriptionTranslations: parentMasterCategory.descriptionTranslationMap,
                            productsCount: undefined,
                            filledProductsCount: 0,
                            notFilledProductsCount: 0,
                            fullness: 0,
                            averageFullness: 0,
                            sortOrder: 0,
                            children: [
                                {
                                    id: masterCategory1.id,
                                    code: masterCategory1.code,
                                    status: masterCategory1.status,
                                    infoModel: {
                                        id: infoModel.id,
                                        code: infoModel.code,
                                        titleTranslations: infoModel.titleTranslationMap,
                                        isInherited: true
                                    },
                                    updatedAt: expect.any(Date),
                                    nameTranslations: masterCategory1.nameTranslationMap,
                                    descriptionTranslations: masterCategory1.descriptionTranslationMap,
                                    productsCount: undefined,
                                    filledProductsCount: 0,
                                    notFilledProductsCount: 0,
                                    sortOrder: 0,
                                    fullness: 0,
                                    averageFullness: 0,
                                    children: []
                                },
                                {
                                    id: masterCategory2.id,
                                    code: masterCategory2.code,
                                    status: masterCategory2.status,
                                    infoModel: {
                                        id: infoModel.id,
                                        code: infoModel.code,
                                        titleTranslations: infoModel.titleTranslationMap,
                                        isInherited: true
                                    },
                                    updatedAt: expect.any(Date),
                                    nameTranslations: masterCategory2.nameTranslationMap,
                                    descriptionTranslations: masterCategory2.descriptionTranslationMap,
                                    productsCount: undefined,
                                    filledProductsCount: 0,
                                    notFilledProductsCount: 0,
                                    sortOrder: 1,
                                    fullness: 0,
                                    averageFullness: 0,
                                    children: []
                                }
                            ]
                        }
                    ]
                }
            ]
        });
    });

    it('should not filter incompatible parents of compatible leaves', async () => {
        /*
            incompatibleRootMasterCategory
            └── incompatibleParentMasterCategory
                ├── masterCategory
                └── compatibleMasterCategory

            result: same
        */

        const attributes = await Promise.all(times(2).map(() => createAttribute()));
        const infoModel = await createInfoModel(attributes[0].id);
        const incompatibleInfoModel = await createInfoModel(attributes[1].id);
        const incompatibleRootMasterCategory = await createMasterCategory(undefined, incompatibleInfoModel.id);
        const incompatibleParentMasterCategory = await createMasterCategory(incompatibleRootMasterCategory.id);
        const masterCategory = await createMasterCategory(incompatibleParentMasterCategory.id, infoModel.id);
        const compatibleMasterCategory = await createMasterCategory(incompatibleParentMasterCategory.id, infoModel.id);
        const product1 = await createProduct(masterCategory.id);
        const product2 = await createProduct(compatibleMasterCategory.id);

        await expect(
            getCompatibleMasterCategoriesHandler.handle({
                context,
                data: {body: {identifiers: [product1.identifier, product2.identifier]}}
            })
        ).resolves.toMatchObject({
            totalCount: 4,
            list: [
                {
                    id: incompatibleRootMasterCategory.id,
                    infoModel: {
                        id: incompatibleInfoModel.id
                    },
                    children: [
                        {
                            id: incompatibleParentMasterCategory.id,
                            infoModel: {
                                id: incompatibleInfoModel.id
                            },
                            children: [
                                {
                                    id: masterCategory.id,
                                    infoModel: {
                                        id: infoModel.id
                                    },
                                    children: []
                                },
                                {
                                    id: compatibleMasterCategory.id,
                                    infoModel: {
                                        id: infoModel.id
                                    },
                                    children: []
                                }
                            ]
                        }
                    ]
                }
            ]
        });
    });

    it('should return filter out master category if all products linked to it', async () => {
        /*
            rootMasterCategory
            ├── masterCategory1 // (product1, product2 linked here)
            └── masterCategory2

            result:
            rootMasterCategory
            └── masterCategory2
        */

        const rootInfoModel = await createInfoModel();
        const rootMasterCategory = await createMasterCategory(undefined, rootInfoModel.id);
        const attribute = await createAttribute();
        const infoModel = await createInfoModel(attribute.id);

        const masterCategory1 = await createMasterCategory(rootMasterCategory.id, infoModel.id);
        const product1 = await createProduct(masterCategory1.id);

        const masterCategory2 = await createMasterCategory(rootMasterCategory.id, infoModel.id);
        const product2 = await createProduct(masterCategory1.id);

        await expect(
            getCompatibleMasterCategoriesHandler.handle({
                context,
                data: {body: {identifiers: [product1.identifier, product2.identifier]}}
            })
        ).resolves.toMatchObject({
            totalCount: 2,
            list: [
                {
                    id: rootMasterCategory.id,
                    infoModel: {
                        id: rootInfoModel.id
                    },
                    children: [
                        {
                            id: masterCategory2.id,
                            infoModel: {
                                id: infoModel.id
                            },
                            children: []
                        }
                    ]
                }
            ]
        });
    });
});
