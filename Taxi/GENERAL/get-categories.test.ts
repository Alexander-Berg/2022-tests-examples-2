/* eslint-disable @typescript-eslint/no-non-null-assertion */
import pMap from 'p-map';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CatalogStatus} from 'types/catalog/base';

import {getCategoriesHandler} from './get-categories';

describe('get categories', () => {
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

    it('should return categories', async () => {
        const categories = await pMap(
            [
                {
                    userId: user.id,
                    regionId: region.id,
                    shortTitleTranslationMap: {
                        [lang.isoCode]: 'category 0'
                    },
                    longTitleTranslationMap: {
                        [lang.isoCode]: 'category 0'
                    },
                    description: 'category 0 description',
                    images: [{imageUrl: 'http://avatars/category/111', filename: '111.png', width: 2, height: 2}]
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    shortTitleTranslationMap: {
                        [lang.isoCode]: 'category 1'
                    },
                    longTitleTranslationMap: {
                        [lang.isoCode]: 'category 1'
                    },
                    description: 'category 1 description'
                }
            ],
            TestFactory.createCategory,
            {concurrency: 1}
        );

        await expect(getCategoriesHandler.handle({context, data: {query: {}}})).resolves.toEqual({
            totalCount: 2,
            list: [
                {
                    id: categories[1].id,
                    legacyId: categories[1].legacyId,
                    code: categories[1].code,
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    status: CatalogStatus.ACTIVE,
                    shortTitleTranslations: {
                        [lang.isoCode]: 'category 1'
                    },
                    longTitleTranslations: {
                        [lang.isoCode]: 'category 1'
                    },
                    description: 'category 1 description',
                    images: [],
                    frontCategories: [],
                    author: {
                        login: user.login,
                        firstName: user.staffData.name.first,
                        lastName: user.staffData.name.last
                    },
                    createdAt: expect.any(Date),
                    updatedAt: expect.any(Date)
                },
                {
                    id: categories[0].id,
                    legacyId: categories[0].legacyId,
                    code: categories[0].code,
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    status: CatalogStatus.ACTIVE,
                    shortTitleTranslations: {
                        [lang.isoCode]: 'category 0'
                    },
                    longTitleTranslations: {
                        [lang.isoCode]: 'category 0'
                    },
                    description: 'category 0 description',
                    images: [{imageUrl: 'http://avatars/category/111', filename: '111.png', formats: [2]}],
                    frontCategories: [],
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

    it('should filter disabled categories', async () => {
        const categories = await pMap(
            [
                {
                    userId: user.id,
                    regionId: region.id,
                    shortTitleTranslationMap: {
                        [lang.isoCode]: 'category 0'
                    },
                    longTitleTranslationMap: {
                        [lang.isoCode]: 'category 0'
                    },
                    description: 'category 0 description'
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    status: CatalogStatus.DISABLED,
                    shortTitleTranslationMap: {
                        [lang.isoCode]: 'category 1'
                    },
                    longTitleTranslationMap: {
                        [lang.isoCode]: 'category 1'
                    },
                    description: 'category 1 description'
                }
            ],
            TestFactory.createCategory,
            {concurrency: 1}
        );

        await expect(getCategoriesHandler.handle({context, data: {query: {activeOnly: true}}})).resolves.toEqual({
            totalCount: 1,
            list: [
                {
                    id: categories[0].id,
                    legacyId: categories[0].legacyId,
                    code: categories[0].code,
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    status: CatalogStatus.ACTIVE,
                    shortTitleTranslations: {
                        [lang.isoCode]: 'category 0'
                    },
                    longTitleTranslations: {
                        [lang.isoCode]: 'category 0'
                    },
                    description: 'category 0 description',
                    images: [],
                    frontCategories: [],
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

    it('should search by code and translations', async () => {
        const categories = await pMap(
            [
                {
                    userId: user.id,
                    regionId: region.id,
                    shortTitleTranslationMap: {
                        [lang.isoCode]: 'foo'
                    },
                    longTitleTranslationMap: {
                        [lang.isoCode]: 'foo'
                    },
                    description: 'foo description'
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    status: CatalogStatus.DISABLED,
                    shortTitleTranslationMap: {
                        [lang.isoCode]: 'category 1'
                    },
                    longTitleTranslationMap: {
                        [lang.isoCode]: 'category 1'
                    },
                    description: 'category 1 description'
                }
            ],
            TestFactory.createCategory,
            {concurrency: 1}
        );

        await expect(
            getCategoriesHandler.handle({
                context,
                data: {
                    query: {search: categories[0].code}
                }
            })
        ).resolves.toEqual({
            totalCount: 1,
            list: [
                {
                    id: categories[0].id,
                    legacyId: categories[0].legacyId,
                    code: categories[0].code,
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    status: CatalogStatus.ACTIVE,
                    shortTitleTranslations: {
                        [lang.isoCode]: 'foo'
                    },
                    longTitleTranslations: {
                        [lang.isoCode]: 'foo'
                    },
                    description: 'foo description',
                    images: [],
                    frontCategories: [],
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

        await expect(getCategoriesHandler.handle({context, data: {query: {search: 'foo'}}})).resolves.toEqual({
            totalCount: 1,
            list: [
                {
                    id: categories[0].id,
                    legacyId: categories[0].legacyId,
                    code: categories[0].code,
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    status: CatalogStatus.ACTIVE,
                    shortTitleTranslations: {
                        [lang.isoCode]: 'foo'
                    },
                    longTitleTranslations: {
                        [lang.isoCode]: 'foo'
                    },
                    description: 'foo description',
                    images: [],
                    frontCategories: [],
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
