import {times} from 'lodash';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {getFrontCategoriesHandler} from './get-front-categories';

describe('get front categories', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
    });

    it('should return full front category tree by product identifiers', async () => {
        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.NUMBER}
        });

        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [{id: attribute.id}]
        });

        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        const rootFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const parentFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootFrontCategory.id
        });

        const frontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentFrontCategory.id
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id
        });

        await TestFactory.linkProductsToFrontCategory({
            userId: user.id,
            productIds: [product.id],
            frontCategoryId: frontCategory.id
        });

        await expect(
            getFrontCategoriesHandler.handle({
                context,
                data: {body: {identifiers: [product.identifier]}}
            })
        ).resolves.toEqual({
            totalCount: 3,
            list: [
                {
                    id: rootFrontCategory.id,
                    code: rootFrontCategory.code,
                    status: rootFrontCategory.status,
                    isPromo: rootFrontCategory.promo,
                    imageUrl: rootFrontCategory.imageUrl,
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    sortOrder: 0,
                    updatedAt: expect.any(Date),
                    nameTranslations: {},
                    productsCount: undefined,
                    descriptionTranslations: {},
                    children: [
                        {
                            id: parentFrontCategory.id,
                            code: parentFrontCategory.code,
                            status: parentFrontCategory.status,
                            nameTranslations: parentFrontCategory.nameTranslationMap,
                            productsCount: undefined,
                            descriptionTranslations: parentFrontCategory.descriptionTranslationMap,
                            isPromo: parentFrontCategory.promo,
                            imageUrl: parentFrontCategory.imageUrl,
                            region: {
                                id: region.id,
                                isoCode: region.isoCode
                            },
                            sortOrder: 0,
                            updatedAt: expect.any(Date),
                            children: [
                                {
                                    id: frontCategory.id,
                                    code: frontCategory.code,
                                    status: frontCategory.status,
                                    nameTranslations: frontCategory.nameTranslationMap,
                                    productsCount: undefined,
                                    descriptionTranslations: frontCategory.descriptionTranslationMap,
                                    isPromo: frontCategory.promo,
                                    imageUrl: frontCategory.imageUrl,
                                    region: {
                                        id: region.id,
                                        isoCode: region.isoCode
                                    },
                                    sortOrder: 0,
                                    updatedAt: expect.any(Date),
                                    children: []
                                }
                            ]
                        }
                    ]
                }
            ]
        });
    });

    it('should only return categories that were used in products', async () => {
        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.NUMBER}
        });

        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [{id: attribute.id}]
        });

        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        const rootFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const parentFrontCategories = await Promise.all(
            times(2).map(() =>
                TestFactory.createFrontCategory({
                    userId: user.id,
                    regionId: region.id,
                    parentId: rootFrontCategory.id
                })
            )
        );

        parentFrontCategories.sort((a, b) => a.id - b.id);

        const frontCategories = await Promise.all(
            times(4).map((i) =>
                TestFactory.createFrontCategory({
                    userId: user.id,
                    regionId: region.id,
                    parentId: parentFrontCategories[Math.floor(i / 2)].id
                })
            )
        );

        frontCategories.sort((a, b) => a.id - b.id);

        const products = await Promise.all(
            times(3).map(() =>
                TestFactory.createProduct({
                    userId: user.id,
                    regionId: region.id,
                    masterCategoryId: masterCategory.id
                })
            )
        );

        products.sort((a, b) => a.id - b.id);

        await TestFactory.linkProductsToFrontCategory({
            userId: user.id,
            productIds: [products[0].id],
            frontCategoryId: frontCategories[0].id
        });

        await TestFactory.linkProductsToFrontCategory({
            userId: user.id,
            productIds: [products[1].id],
            frontCategoryId: frontCategories[2].id
        });

        await expect(
            getFrontCategoriesHandler.handle({
                context,
                data: {body: {identifiers: products.map(({identifier}) => identifier)}}
            })
        ).resolves.toMatchObject({
            totalCount: 5,
            list: [
                {
                    id: rootFrontCategory.id,
                    children: [
                        {
                            id: parentFrontCategories[0].id,
                            children: [
                                {
                                    id: frontCategories[0].id,
                                    children: []
                                }
                            ]
                        },
                        {
                            id: parentFrontCategories[1].id,
                            children: [
                                {
                                    id: frontCategories[2].id,
                                    children: []
                                }
                            ]
                        }
                    ]
                }
            ]
        });
    });
});
