/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CatalogStatus} from 'types/catalog/base';
import {FrontCategoryStatus} from 'types/front-category';

import {getCategoryByIdHandler} from './get-category-by-id';

describe('get category by id', () => {
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

    it('should return category', async () => {
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
            parentId: parentFrontCategory.id
        });

        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: category.id,
            frontCategoryId: frontCategory.id
        });

        const result = await getCategoryByIdHandler.handle({context, data: {params: {id: category.id}}});

        expect(result).toEqual({
            id: category.id,
            legacyId: category.legacyId,
            code: category.code,
            region: {
                id: region.id,
                isoCode: region.isoCode
            },
            status: CatalogStatus.ACTIVE,
            shortTitleTranslations: {
                [lang.isoCode]: 'category'
            },
            longTitleTranslations: {
                [lang.isoCode]: 'category'
            },
            description: 'category description',
            meta: {foo: 'category meta'},
            images: [
                {
                    imageUrl: 'http://avatars/category/111',
                    filename: '111.png',
                    formats: [2],
                    links: [
                        {
                            entityId: expect.any(Number),
                            format: 2,
                            linkId: expect.any(Number)
                        }
                    ]
                }
            ],
            specialCategory: 'special',
            deeplink: 'deeplink',
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
            ],
            frontCategories: [
                {
                    id: frontCategory.id,
                    code: frontCategory.code,
                    status: FrontCategoryStatus.ACTIVE,
                    parent: {
                        id: parentFrontCategory.id,
                        nameTranslations: {}
                    },
                    nameTranslations: {},
                    productsCount: 0
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
