/* eslint-disable @typescript-eslint/no-explicit-any */
import {random} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {REGION_HEADER} from '@/src/constants';
import {EntityNotFoundError} from '@/src/errors';
import {MasterCategoryStatus} from 'types/master-category';

import {getMasterCategoryByIdApiHandler} from './get-master-category-by-id';

interface ExecuteHandlerParams {
    id: string;
    region: string;
}

function executeHandler({id, region}: ExecuteHandlerParams): Promise<any> {
    return new Promise((resolve, reject) => {
        getMasterCategoryByIdApiHandler(
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

describe('get master category by id', () => {
    it('should return master category', async () => {
        const [user, otherUser] = await Promise.all([TestFactory.createUser(), TestFactory.createUser()]);
        const region = await TestFactory.createRegion();
        const langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);

        const infoModels = await Promise.all([
            TestFactory.createInfoModel({
                regionId: region.id,
                userId: user.id
            }),
            TestFactory.createInfoModel({
                regionId: region.id,
                userId: user.id
            })
        ]);

        const root = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModels[0].id,
            nameTranslationMap: TestFactory.createTranslationMap({langCodes: langs.map((it) => it.isoCode)}),
            descriptionTranslationMap: TestFactory.createTranslationMap({langCodes: langs.map((it) => it.isoCode)})
        });

        const children = [];

        for (let i = 0; i < 3; i++) {
            children.push(
                await TestFactory.createMasterCategory({
                    userId: otherUser.id,
                    parentId: root.id,
                    regionId: region.id,
                    sortOrder: i,
                    infoModelId: i === 0 ? infoModels[1].id : undefined,
                    status: MasterCategoryStatus.DISABLED
                })
            );
        }

        const receivedRoot1 = await executeHandler({
            id: root.id.toString(),
            region: region.isoCode
        });

        expect(receivedRoot1).toEqual({
            id: root.id,
            code: root.code,
            status: root.status,
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
            descriptionTranslations: root.descriptionTranslationMap,
            infoModel: {
                id: infoModels[0].id,
                code: infoModels[0].code,
                titleTranslations: {},
                isInherited: false
            },
            createdAt: expect.any(Date),
            breadcrumbs: [],
            parentCategoryId: undefined,
            updatedAt: expect.any(Date),
            hasActiveChildren: false,
            productsCount: 0,
            filledProductsCount: 0,
            notFilledProductsCount: 0,
            isLeaf: false,
            fullness: 0,
            averageFullness: 0
        });

        children.push(
            await TestFactory.createMasterCategory({
                userId: otherUser.id,
                parentId: root.id,
                regionId: region.id,
                status: MasterCategoryStatus.ACTIVE
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
            status: child1.status,
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
            infoModel: {
                id: infoModels[0].id,
                code: infoModels[0].code,
                titleTranslations: {},
                isInherited: true
            },
            createdAt: expect.any(Date),
            breadcrumbs: [
                {
                    id: root.id,
                    code: root.code,
                    nameTranslations: root.nameTranslationMap,
                    status: MasterCategoryStatus.ACTIVE
                }
            ],
            sortOrder: 1,
            maxSortOrder: 3,
            parentCategoryId: root.id,
            updatedAt: expect.any(Date),
            hasActiveChildren: false,
            productsCount: 0,
            filledProductsCount: 0,
            notFilledProductsCount: 0,
            isLeaf: true,
            fullness: 0,
            averageFullness: 0
        });

        const child0 = children[0];
        const receivedChild0 = await executeHandler({
            id: child0.id.toString(),
            region: region.isoCode
        });

        expect(receivedChild0.infoModel).toEqual({
            id: infoModels[1].id,
            code: infoModels[1].code,
            titleTranslations: {},
            isInherited: false
        });

        const child3 = children[3];
        const receivedChild3 = await executeHandler({
            id: child3.id.toString(),
            region: region.isoCode
        });
        expect(receivedChild3.hasActiveChildren).toBeFalsy();
    });

    it('should return error if master category from other region', async () => {
        let error = null;
        const user = await TestFactory.createUser();
        const region = await TestFactory.createRegion();
        const otherRegion = await TestFactory.createRegion();
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: []
        });
        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            status: MasterCategoryStatus.ACTIVE
        });

        try {
            await executeHandler({
                id: mc.id.toString(),
                region: otherRegion.isoCode
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'MasterCategory'});
    });

    it('should return error if master category does not exist', async () => {
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
        expect(error.parameters).toMatchObject({entity: 'MasterCategory'});
    });
});
