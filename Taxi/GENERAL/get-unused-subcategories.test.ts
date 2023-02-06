/* eslint-disable @typescript-eslint/no-non-null-assertion */
import pMap from 'p-map';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CatalogStatus} from 'types/catalog/base';

import {getUnusedSubcategoriesHandler} from './get-unused-subcategories';

describe('get unused subcategories', () => {
    let user: User;
    let region: Region;
    let lang: Lang;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        lang = await TestFactory.createLang();
        context = await TestFactory.createApiContext({user, region, lang});
    });

    it('should return unused subcategories', async () => {
        const rootFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });
        const parentFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootFrontCategory.id
        });
        const frontCategories = await pMap(
            [
                {
                    userId: user.id,
                    regionId: region.id,
                    nameTranslationMap: {
                        [lang.isoCode]: 'subcategory 0'
                    },
                    descriptionTranslationMap: {
                        [lang.isoCode]: 'subcategory 0 description'
                    },
                    parentId: parentFrontCategory.id
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    nameTranslationMap: {
                        [lang.isoCode]: 'subcategory 1'
                    },
                    descriptionTranslationMap: {
                        [lang.isoCode]: 'subcategory 1 description'
                    },
                    parentId: parentFrontCategory.id
                }
            ],
            TestFactory.createFrontCategory,
            {concurrency: 1}
        );

        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });
        const products = await pMap(
            [
                {
                    userId: user.id,
                    regionId: region.id,
                    masterCategoryId: masterCategory.id
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    masterCategoryId: masterCategory.id
                }
            ],
            TestFactory.createProduct,
            {concurrency: 1}
        );

        await TestFactory.linkProductsToFrontCategory({
            userId: user.id,
            productIds: products.map(({id}) => id),
            frontCategoryId: frontCategories[0].id
        });

        const category = await TestFactory.createCategory({
            userId: user.id,
            regionId: region.id
        });

        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: category.id,
            frontCategoryId: frontCategories[1].id
        });

        await expect(getUnusedSubcategoriesHandler.handle({context, data: {query: {}}})).resolves.toEqual({
            totalCount: 1,
            list: [
                {
                    id: frontCategories[0].id,
                    legacyId: frontCategories[0].id.toString(),
                    code: frontCategories[0].code,
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    status: CatalogStatus.ACTIVE,
                    longTitleTranslations: {
                        [lang.isoCode]: 'subcategory 0'
                    },
                    description: 'subcategory 0 description',
                    productsCount: 2,
                    author: {
                        login: user.login,
                        firstName: user.staffData.name.first,
                        lastName: user.staffData.name.last
                    },
                    createdAt: expect.any(Date),
                    updatedAt: expect.any(Date)
                }
            ]
        });
    });
});
