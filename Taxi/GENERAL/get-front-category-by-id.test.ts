/* eslint-disable @typescript-eslint/no-explicit-any */
import {random, range} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {REGION_HEADER} from '@/src/constants';
import {EntityNotFoundError} from '@/src/errors';
import {FrontCategoryStatus} from 'types/front-category';

import {getFrontCategoryByIdApiHandler} from './get-front-category-by-id';

interface ExecuteHandlerParams {
    id: string;
    region: string;
}

function executeHandler({id, region}: ExecuteHandlerParams): Promise<any> {
    return new Promise((resolve, reject) => {
        getFrontCategoryByIdApiHandler(
            {
                params: {id},
                header: (name: string): string | undefined => {
                    if (name === REGION_HEADER) {
                        return region;
                    }

                    return;
                }
            } as any,
            {json: resolve} as any,
            reject
        );
    });
}

describe('get front category by id', () => {
    it('should return front category', async () => {
        const [user, otherUser] = await Promise.all([TestFactory.createUser(), TestFactory.createUser()]);
        const region = await TestFactory.createRegion();
        const langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);

        const root = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            nameTranslationMap: TestFactory.createTranslationMap({langCodes: langs.map((it) => it.isoCode)})
        });

        const children = [];

        for (let i = 0; i < 3; i++) {
            children.push(
                await TestFactory.createFrontCategory({
                    userId: otherUser.id,
                    regionId: region.id,
                    parentId: root.id,
                    status: FrontCategoryStatus.DISABLED
                })
            );
        }

        let lastDeepLink = '';

        // Добавляем изменения от другого пользователя, чтобы проверить создателя
        for (const _ of range(4)) {
            lastDeepLink = Math.random().toString();

            await TestFactory.updateFrontCategory(root.id, {
                userId: otherUser.id,
                frontCategory: {
                    deeplink: lastDeepLink
                }
            });
        }

        const receivedRoot1 = await executeHandler({
            id: root.id.toString(),
            region: region.isoCode
        });

        expect(receivedRoot1).toEqual({
            id: root.id,
            code: root.code,
            deeplink: lastDeepLink,
            imageUrl: root.imageUrl,
            status: root.status,
            isPromo: root.promo,
            author: {
                firstName: user.staffData.name.first,
                lastName: user.staffData.name.last,
                login: user.login
            },
            region: {
                id: region.id,
                isoCode: region.isoCode
            },
            sortOrder: 0,
            maxSortOrder: 0,
            nameTranslations: root.nameTranslationMap,
            descriptionTranslations: {},
            productsCount: 0,
            createdAt: expect.any(Date),
            updatedAt: expect.any(Date),
            breadcrumbs: [
                {
                    id: root.id,
                    code: root.code,
                    nameTranslations: root.nameTranslationMap,
                    status: FrontCategoryStatus.ACTIVE
                }
            ],
            legalRestrictions: root.legalRestrictions,
            parentCategoryId: undefined,
            hasActiveChildren: false,
            referenceCatalogCategoriesIds: []
        });

        children.push(
            await TestFactory.createFrontCategory({
                userId: otherUser.id,
                regionId: region.id,
                parentId: root.id,
                status: FrontCategoryStatus.ACTIVE
            })
        );

        const receivedRoot2 = await executeHandler({
            id: root.id.toString(),
            region: region.isoCode
        });
        expect(receivedRoot2.hasActiveChildren).toBeTruthy();

        const child1 = children[1];
        const receivedChild1 = await executeHandler({
            id: child1.id.toString(),
            region: region.isoCode
        });

        expect(receivedChild1).toEqual({
            id: child1.id,
            code: child1.code,
            deeplink: child1.deeplink,
            imageUrl: child1.imageUrl,
            status: child1.status,
            isPromo: child1.promo,
            author: {
                firstName: otherUser.staffData.name.first,
                lastName: otherUser.staffData.name.last,
                login: otherUser.login
            },
            region: {
                id: region.id,
                isoCode: region.isoCode
            },
            nameTranslations: {},
            descriptionTranslations: {},
            productsCount: 0,
            createdAt: expect.any(Date),
            updatedAt: expect.any(Date),
            sortOrder: 2,
            maxSortOrder: 4,
            breadcrumbs: [
                {
                    id: root.id,
                    code: root.code,
                    nameTranslations: root.nameTranslationMap,
                    status: FrontCategoryStatus.ACTIVE
                },
                {
                    id: child1.id,
                    code: child1.code,
                    nameTranslations: {},
                    status: FrontCategoryStatus.DISABLED
                }
            ],
            legalRestrictions: child1.legalRestrictions,
            parentCategoryId: root.id,
            hasActiveChildren: false,
            referenceCatalogCategoriesIds: []
        });

        const child3 = children[3];
        const receivedChild3 = await executeHandler({
            id: child3.id.toString(),
            region: region.isoCode
        });
        expect(receivedChild3.hasActiveChildren).toBeFalsy();
    });

    it('should return error if front category from other region', async () => {
        let error = null;
        const user = await TestFactory.createUser();
        const region = await TestFactory.createRegion();
        const otherRegion = await TestFactory.createRegion();
        const fc = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            status: FrontCategoryStatus.ACTIVE
        });

        try {
            await executeHandler({
                id: fc.id.toString(),
                region: otherRegion.isoCode
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'FrontCategory'});
    });

    it('should return error if front category does not exist', async () => {
        let error = null;
        const unknownId = random(999999).toString();
        const region = await TestFactory.createRegion();

        try {
            await executeHandler({
                id: unknownId,
                region: region.isoCode
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'FrontCategory'});
    });

    it('should return front category with timetable', async () => {
        const user = await TestFactory.createUser();
        const region = await TestFactory.createRegion();

        const root = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const parent = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: root.id,
            regionId: region.id
        });

        const child = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: parent.id,
            regionId: region.id,
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

        const receivedChild = await executeHandler({
            id: child.id.toString(),
            region: region.isoCode
        });

        expect(receivedChild).toMatchObject({
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
            }
        });
    });
});
