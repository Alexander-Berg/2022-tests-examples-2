/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CatalogStatus} from 'types/catalog/base';

import {getSubcategoryByIdHandler} from './get-subcategory-by-id';

describe('get subcategory by id', () => {
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

    it('should return subcategory', async () => {
        const grid = await TestFactory.createGrid({
            userId: user.id,
            regionId: region.id,
            shortTitleTranslationMap: {
                [lang.isoCode]: 'grid'
            },
            longTitleTranslationMap: {
                [lang.isoCode]: 'grid'
            },
            meta: {foo: 'grid meta'},
            description: 'grid description'
        });

        const group = await TestFactory.createGroup({
            userId: user.id,
            regionId: region.id,
            shortTitleTranslationMap: {
                [lang.isoCode]: 'group'
            },
            longTitleTranslationMap: {
                [lang.isoCode]: 'group'
            },
            meta: {foo: 'group meta'},
            description: 'group description',
            images: [{imageUrl: 'http://avatars/group/111', filename: '111.png', width: 2, height: 2}]
        });

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            gridId: grid.id,
            groupId: group.id,
            images: [{imageUrl: 'http://avatars/group/111', width: 2, height: 2}]
        });

        const category = await TestFactory.createCategory({
            userId: user.id,
            regionId: region.id,
            shortTitleTranslationMap: {
                [lang.isoCode]: 'category'
            },
            longTitleTranslationMap: {
                [lang.isoCode]: 'category'
            },
            meta: {foo: 'category meta'},
            description: 'category description',
            specialCategory: 'special',
            deeplink: 'deeplink',
            images: [{imageUrl: 'http://avatars/category/111', filename: '111.png', width: 2, height: 2}]
        });

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: group.id,
            categoryId: category.id,
            images: [{imageUrl: 'http://avatars/category/111', width: 2, height: 2}]
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
            parentId: parentFrontCategory.id,
            nameTranslationMap: {
                [lang.isoCode]: 'subcategory'
            },
            descriptionTranslationMap: {
                [lang.isoCode]: 'subcategory description'
            },
            deeplink: 'deeplink',
            legalRestrictions: 'legal restrictions',
            promo: true,
            timetable: {
                dates: {
                    begin: '01.01.2022',
                    end: '31.12.2022'
                },
                days: {
                    friday: {
                        begin: '09:00',
                        end: '19:00'
                    },
                    monday: {
                        begin: '08:00',
                        end: '20:00'
                    },
                    saturday: {
                        begin: '10:00',
                        end: '18:00'
                    },
                    sunday: {
                        begin: '10:00',
                        end: '18:00'
                    }
                }
            }
        });

        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: category.id,
            frontCategoryId: frontCategory.id
        });

        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
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

        const result = await getSubcategoryByIdHandler.handle({context, data: {params: {id: frontCategory.id}}});

        expect(result).toEqual({
            id: frontCategory.id,
            legacyId: frontCategory.id.toString(),
            code: frontCategory.code,
            region: {
                id: region.id,
                isoCode: region.isoCode
            },
            status: CatalogStatus.ACTIVE,
            longTitleTranslations: {
                [lang.isoCode]: 'subcategory'
            },
            description: 'subcategory description',
            deeplink: 'deeplink',
            legalRestrictions: 'legal restrictions',
            promo: true,
            timetable: {
                beginDate: '01.01.2022',
                endDate: '31.12.2022',
                entries: [
                    {
                        days: ['monday'],
                        begin: '08:00',
                        end: '20:00'
                    },
                    {
                        days: ['friday'],
                        begin: '09:00',
                        end: '19:00'
                    },
                    {
                        days: ['saturday', 'sunday'],
                        begin: '10:00',
                        end: '18:00'
                    }
                ]
            },
            productsCount: 1,
            categories: [
                {
                    id: category.id,
                    legacyId: category.legacyId,
                    code: category.code,
                    status: CatalogStatus.ACTIVE,
                    shortTitleTranslations: {
                        [lang.isoCode]: 'category'
                    },
                    longTitleTranslations: {
                        [lang.isoCode]: 'category'
                    },
                    images: [{imageUrl: 'http://avatars/category/111', formats: [2], filename: '111.png'}],
                    groups: [
                        {
                            id: group.id,
                            legacyId: group.legacyId,
                            code: group.code,
                            status: CatalogStatus.ACTIVE,
                            shortTitleTranslations: {
                                [lang.isoCode]: 'group'
                            },
                            longTitleTranslations: {
                                [lang.isoCode]: 'group'
                            },
                            images: [{imageUrl: 'http://avatars/group/111', filename: '111.png'}],
                            grids: [
                                {
                                    id: grid.id,
                                    legacyId: grid.legacyId,
                                    code: grid.code,
                                    status: CatalogStatus.ACTIVE,
                                    shortTitleTranslations: {
                                        [lang.isoCode]: 'grid'
                                    },
                                    longTitleTranslations: {
                                        [lang.isoCode]: 'grid'
                                    }
                                }
                            ]
                        }
                    ]
                }
            ],
            author: {
                login: user.login,
                firstName: user.staffData.name.first,
                lastName: user.staffData.name.last
            },
            createdAt: expect.any(Date),
            updatedAt: expect.any(Date)
        });
    });
});
