/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {EntityNotFoundError} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CatalogStatus} from 'types/catalog/base';
import type {UpdatedSubcategory} from 'types/catalog/subcategory';

import {updateSubcategoryHandler} from './update-subcategory';

describe('update subcategory', () => {
    let user: User;
    let regions: Region[];
    let langs: Lang[];
    let langCodes: string[];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {catalog: {canEdit: true}}});
        regions = await Promise.all([TestFactory.createRegion(), TestFactory.createRegion()]);
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        langCodes = langs.map(({isoCode}) => isoCode);
        context = await TestFactory.createApiContext({user, region: regions[0], lang: langs[0]});
    });

    it('should update subcategory itself', async () => {
        const rootFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id
        });
        const parentFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id,
            parentId: rootFrontCategory.id,
            code: 'subcategories'
        });
        const subcategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id,
            parentId: parentFrontCategory.id,
            status: 'disabled',
            nameTranslationMap: {
                [langCodes[0]]: 'category'
            }
        });

        const updateParams: UpdatedSubcategory = {
            status: CatalogStatus.ACTIVE,
            longTitleTranslations: {
                [langCodes[0]]: 'subcategory'
            },
            description: 'description',
            deeplink: 'deeplink',
            promo: true,
            legalRestrictions: 'legal restrictions',
            timetable: {entries: [{days: ['monday'], begin: '09:00', end: '21;00'}]},
            categories: []
        };

        await updateSubcategoryHandler.handle({context, data: {params: {id: subcategory.id}, body: updateParams}});
        const updatedSubcategory = (await TestFactory.getFrontCategories()).find(({id}) => id === subcategory.id)!;

        expect(updatedSubcategory).toEqual({
            ...subcategory,
            status: updateParams.status,
            nameTranslationMap: updateParams.longTitleTranslations,
            descriptionTranslationMap: {
                [langCodes[0]]: updateParams.description
            },
            deeplink: updateParams.deeplink,
            promo: updateParams.promo,
            legalRestrictions: updateParams.legalRestrictions,
            timetable: {days: {monday: {begin: '09:00', end: '21;00'}}, dates: {}}
        });
    });

    it('should update subcategory when all categories selected', async () => {
        const categories = await Promise.all([
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id
            }),
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id
            })
        ]);

        const rootFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id
        });
        const parentFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id,
            parentId: rootFrontCategory.id,
            code: 'subcategories'
        });
        const subcategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id,
            parentId: parentFrontCategory.id
        });

        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: categories[0].id,
            frontCategoryId: subcategory.id
        });

        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: categories[1].id,
            frontCategoryId: subcategory.id
        });

        const updateParams: UpdatedSubcategory = {deeplink: 'deeplink', categories: categories.map(({id}) => ({id}))};
        await updateSubcategoryHandler.handle({context, data: {params: {id: subcategory.id}, body: updateParams}});
        const updatedSubcategory = (await TestFactory.getFrontCategories()).find(({id}) => id === subcategory.id)!;

        expect(updatedSubcategory).toEqual({...subcategory, deeplink: updateParams.deeplink});
    });

    it('should duplicate subcategory with linked products when part of categories selected', async () => {
        const categories = await Promise.all([
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id
            }),
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id
            })
        ]);

        const rootFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id
        });
        const parentFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id,
            parentId: rootFrontCategory.id,
            code: 'subcategories'
        });
        const subcategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id,
            parentId: parentFrontCategory.id,
            status: 'disabled',
            nameTranslationMap: {
                [langCodes[0]]: 'subcategory'
            },
            descriptionTranslationMap: {
                [langCodes[0]]: 'description'
            }
        });

        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: categories[0].id,
            frontCategoryId: subcategory.id
        });
        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: categories[1].id,
            frontCategoryId: subcategory.id
        });

        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: regions[0].id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: regions[0].id,
            infoModelId: infoModel.id
        });
        const products = await Promise.all([
            TestFactory.createProduct({
                userId: user.id,
                regionId: regions[0].id,
                masterCategoryId: masterCategory.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                regionId: regions[0].id,
                masterCategoryId: masterCategory.id
            })
        ]);

        await TestFactory.linkProductsToFrontCategory({
            userId: user.id,
            productIds: products.map(({id}) => id),
            frontCategoryId: subcategory.id
        });

        const updateParams: UpdatedSubcategory = {
            code: subcategory.code + '_duplicated',
            status: CatalogStatus.ACTIVE,
            longTitleTranslations: {
                [langCodes[0]]: 'duplicated subcategory'
            },
            description: 'duplicated description',
            deeplink: 'deeplink',
            promo: true,
            legalRestrictions: 'legal restrictions',
            timetable: {entries: [{days: ['monday'], begin: '09:00', end: '21;00'}]},
            categories: [{id: categories[1].id}]
        };

        const newSubcategory = await updateSubcategoryHandler.handle({
            context,
            data: {params: {id: subcategory.id}, body: updateParams}
        });

        const untouchedSubcategory = (await TestFactory.getFrontCategories()).find(({id}) => id === subcategory.id)!;
        const untouchedFrontCategoryProducts = await TestFactory.getFrontCategoryProduct({
            frontCategoryId: subcategory.id
        });

        expect(untouchedSubcategory).toEqual(subcategory);
        expect(untouchedFrontCategoryProducts).toEqual([
            expect.objectContaining({productId: products[0].id}),
            expect.objectContaining({productId: products[1].id})
        ]);

        const updatedSubcategory = (await TestFactory.getFrontCategories()).find(({id}) => id === newSubcategory.id)!;
        const updatedFrontCategoryProducts = await TestFactory.getFrontCategoryProduct({
            frontCategoryId: newSubcategory.id
        });

        expect(updatedSubcategory).toEqual({
            ...subcategory,
            id: newSubcategory.id,
            tpath: `${rootFrontCategory.id}.${parentFrontCategory.id}.${newSubcategory.id}`,
            sortOrder: expect.any(Number),
            historySubjectId: expect.any(Number),
            code: updateParams.code,
            status: updateParams.status,
            nameTranslationMap: updateParams.longTitleTranslations,
            descriptionTranslationMap: {
                [langCodes[0]]: updateParams.description
            },
            deeplink: updateParams.deeplink,
            promo: true,
            legalRestrictions: 'legal restrictions',
            timetable: {days: {monday: {begin: '09:00', end: '21;00'}}, dates: {}}
        });
        expect(updatedFrontCategoryProducts).toEqual([
            expect.objectContaining({productId: products[0].id}),
            expect.objectContaining({productId: products[1].id})
        ]);
    });

    it('should replace subcategory with duplicated subcategory in selected categories', async () => {
        const categories = await Promise.all([
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id
            }),
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id
            })
        ]);

        const rootFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id
        });
        const parentFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id,
            parentId: rootFrontCategory.id,
            code: 'subcategories'
        });
        const subcategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id,
            parentId: parentFrontCategory.id
        });

        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: categories[0].id,
            frontCategoryId: subcategory.id
        });
        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: categories[1].id,
            frontCategoryId: subcategory.id
        });

        const categoryFrontCategories = await Promise.all(
            categories.map(({id}) => TestFactory.getCategoryFrontCategories(id))
        );

        expect(categoryFrontCategories).toEqual([
            [expect.objectContaining({frontCategoryId: subcategory.id})],
            [expect.objectContaining({frontCategoryId: subcategory.id})]
        ]);

        const updateParams: UpdatedSubcategory = {
            code: subcategory.code + '_duplicated',
            categories: [{id: categories[1].id}]
        };

        const newSubcategory = await updateSubcategoryHandler.handle({
            context,
            data: {params: {id: subcategory.id}, body: updateParams}
        });

        const updatedGroupCategories = await Promise.all(
            categories.map(({id}) => TestFactory.getCategoryFrontCategories(id))
        );

        expect(updatedGroupCategories).toEqual([
            [expect.objectContaining({frontCategoryId: subcategory.id})],
            [expect.objectContaining({frontCategoryId: newSubcategory.id})]
        ]);
    });

    it('should throw error if selected subcategory is not linked', async () => {
        const categories = await Promise.all([
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id
            }),
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id
            })
        ]);

        const rootFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id
        });
        const parentFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id,
            parentId: rootFrontCategory.id,
            code: 'subcategories'
        });
        const subcategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id,
            parentId: parentFrontCategory.id
        });

        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: categories[0].id,
            frontCategoryId: subcategory.id
        });

        const updateParams: UpdatedSubcategory = {categories: [{id: categories[1].id}]};

        await expect(
            updateSubcategoryHandler.handle({context, data: {params: {id: subcategory.id}, body: updateParams}})
        ).rejects.toThrow(EntityNotFoundError);
    });
});
