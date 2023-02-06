/* eslint-disable @typescript-eslint/no-non-null-assertion */
import pMap from 'p-map';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CatalogStatus} from 'types/catalog/base';

import {getGroupsHandler} from './get-groups';

describe('get groups', () => {
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

    it('should return groups', async () => {
        const groups = await pMap(
            [
                {
                    userId: user.id,
                    regionId: region.id,
                    shortTitleTranslationMap: {
                        [lang.isoCode]: 'group 0'
                    },
                    longTitleTranslationMap: {
                        [lang.isoCode]: 'group 0'
                    },
                    description: 'group 0 description',
                    images: [{imageUrl: 'http://avatars/group/111', filename: '111.png', width: 2, height: 2}]
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    shortTitleTranslationMap: {
                        [lang.isoCode]: 'group 1'
                    },
                    longTitleTranslationMap: {
                        [lang.isoCode]: 'group 1'
                    },
                    description: 'group 1 description'
                }
            ],
            TestFactory.createGroup,
            {concurrency: 1}
        );

        await expect(getGroupsHandler.handle({context, data: {query: {}}})).resolves.toEqual({
            totalCount: 2,
            list: [
                {
                    id: groups[1].id,
                    legacyId: groups[1].legacyId,
                    code: groups[1].code,
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    status: CatalogStatus.ACTIVE,
                    shortTitleTranslations: {
                        [lang.isoCode]: 'group 1'
                    },
                    longTitleTranslations: {
                        [lang.isoCode]: 'group 1'
                    },
                    description: 'group 1 description',
                    images: [],
                    author: {
                        login: user.login,
                        firstName: user.staffData.name.first,
                        lastName: user.staffData.name.last
                    },
                    createdAt: expect.any(Date),
                    updatedAt: expect.any(Date)
                },
                {
                    id: groups[0].id,
                    legacyId: groups[0].legacyId,
                    code: groups[0].code,
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    status: CatalogStatus.ACTIVE,
                    shortTitleTranslations: {
                        [lang.isoCode]: 'group 0'
                    },
                    longTitleTranslations: {
                        [lang.isoCode]: 'group 0'
                    },
                    description: 'group 0 description',
                    images: [{imageUrl: 'http://avatars/group/111', filename: '111.png'}],
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

    it('should filter disabled groups', async () => {
        const groups = await pMap(
            [
                {
                    userId: user.id,
                    regionId: region.id,
                    shortTitleTranslationMap: {
                        [lang.isoCode]: 'group 0'
                    },
                    longTitleTranslationMap: {
                        [lang.isoCode]: 'group 0'
                    },
                    description: 'group 0 description'
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    status: CatalogStatus.DISABLED,
                    shortTitleTranslationMap: {
                        [lang.isoCode]: 'group 1'
                    },
                    longTitleTranslationMap: {
                        [lang.isoCode]: 'group 1'
                    },
                    description: 'group 1 description'
                }
            ],
            TestFactory.createGroup,
            {concurrency: 1}
        );

        await expect(getGroupsHandler.handle({context, data: {query: {activeOnly: true}}})).resolves.toEqual({
            totalCount: 1,
            list: [
                {
                    id: groups[0].id,
                    legacyId: groups[0].legacyId,
                    code: groups[0].code,
                    region: {
                        id: region.id,
                        isoCode: region.isoCode
                    },
                    status: CatalogStatus.ACTIVE,
                    shortTitleTranslations: {
                        [lang.isoCode]: 'group 0'
                    },
                    longTitleTranslations: {
                        [lang.isoCode]: 'group 0'
                    },
                    description: 'group 0 description',
                    images: [],
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
        const groups = await pMap(
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
            TestFactory.createGroup,
            {concurrency: 1}
        );

        await expect(getGroupsHandler.handle({context, data: {query: {search: groups[0].code}}})).resolves.toEqual({
            totalCount: 1,
            list: [
                {
                    id: groups[0].id,
                    legacyId: groups[0].legacyId,
                    code: groups[0].code,
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

        await expect(getGroupsHandler.handle({context, data: {query: {search: 'foo'}}})).resolves.toEqual({
            totalCount: 1,
            list: [
                {
                    id: groups[0].id,
                    legacyId: groups[0].legacyId,
                    code: groups[0].code,
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
