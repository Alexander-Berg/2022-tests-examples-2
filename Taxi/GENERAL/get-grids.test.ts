/* eslint-disable @typescript-eslint/no-non-null-assertion */
import pMap from 'p-map';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CatalogStatus} from 'types/catalog/base';

import {getGridsHandler} from './get-grids';

describe('get grids', () => {
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

    it('should return grids', async () => {
        const grids = await pMap(
            [
                {
                    userId: user.id,
                    regionId: region.id,
                    shortTitleTranslationMap: {
                        [lang.isoCode]: 'grid 0'
                    },
                    longTitleTranslationMap: {
                        [lang.isoCode]: 'grid 0'
                    },
                    description: 'grid 0 description'
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    shortTitleTranslationMap: {
                        [lang.isoCode]: 'grid 1'
                    },
                    longTitleTranslationMap: {
                        [lang.isoCode]: 'grid 1'
                    },
                    description: 'grid 1 description'
                }
            ],
            TestFactory.createGrid,
            {concurrency: 1}
        );

        await expect(getGridsHandler.handle({context, data: {query: {}}})).resolves.toEqual({
            totalCount: 2,
            list: [
                {
                    id: grids[1].id,
                    legacyId: grids[1].legacyId,
                    code: grids[1].code,
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    status: CatalogStatus.ACTIVE,
                    shortTitleTranslations: {
                        [lang.isoCode]: 'grid 1'
                    },
                    longTitleTranslations: {
                        [lang.isoCode]: 'grid 1'
                    },
                    description: 'grid 1 description',
                    author: {
                        login: user.login,
                        firstName: user.staffData.name.first,
                        lastName: user.staffData.name.last
                    },
                    createdAt: expect.any(Date),
                    updatedAt: expect.any(Date)
                },
                {
                    id: grids[0].id,
                    legacyId: grids[0].legacyId,
                    code: grids[0].code,
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    status: CatalogStatus.ACTIVE,
                    shortTitleTranslations: {
                        [lang.isoCode]: 'grid 0'
                    },
                    longTitleTranslations: {
                        [lang.isoCode]: 'grid 0'
                    },
                    description: 'grid 0 description',
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

    it('should filter disabled grids', async () => {
        const grids = await pMap(
            [
                {
                    userId: user.id,
                    regionId: region.id,
                    shortTitleTranslationMap: {
                        [lang.isoCode]: 'grid 0'
                    },
                    longTitleTranslationMap: {
                        [lang.isoCode]: 'grid 0'
                    },
                    description: 'grid 0 description'
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    status: CatalogStatus.DISABLED,
                    shortTitleTranslationMap: {
                        [lang.isoCode]: 'grid 1'
                    },
                    longTitleTranslationMap: {
                        [lang.isoCode]: 'grid 1'
                    },
                    description: 'grid 1 description'
                }
            ],
            TestFactory.createGrid,
            {concurrency: 1}
        );

        await expect(getGridsHandler.handle({context, data: {query: {activeOnly: true}}})).resolves.toEqual({
            totalCount: 1,
            list: [
                {
                    id: grids[0].id,
                    legacyId: grids[0].legacyId,
                    code: grids[0].code,
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    status: CatalogStatus.ACTIVE,
                    shortTitleTranslations: {
                        [lang.isoCode]: 'grid 0'
                    },
                    longTitleTranslations: {
                        [lang.isoCode]: 'grid 0'
                    },
                    description: 'grid 0 description',
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
        const grids = await pMap(
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
                        [lang.isoCode]: 'bar'
                    },
                    longTitleTranslationMap: {
                        [lang.isoCode]: 'bar'
                    },
                    description: 'bar description'
                }
            ],
            TestFactory.createGrid,
            {concurrency: 1}
        );

        await expect(getGridsHandler.handle({context, data: {query: {search: grids[0].code}}})).resolves.toEqual({
            totalCount: 1,
            list: [
                {
                    id: grids[0].id,
                    legacyId: grids[0].legacyId,
                    code: grids[0].code,
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

        await expect(getGridsHandler.handle({context, data: {query: {search: 'foo'}}})).resolves.toEqual({
            totalCount: 1,
            list: [
                {
                    id: grids[0].id,
                    legacyId: grids[0].legacyId,
                    code: grids[0].code,
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
