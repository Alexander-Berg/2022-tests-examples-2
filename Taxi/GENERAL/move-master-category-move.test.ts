import {keyBy, mapValues} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {ActiveCategoryWithDisabledParentIsForbidden, EntityNotFoundError} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';
import {MasterCategoryStatus} from 'types/master-category';

import {getParentInfoModelHandler} from './get-parent-info-model';
import {moveMasterCategoryHandler} from './move-master-category';

describe('move master category (move to another parent)', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {masterCategory: {canEdit: true}}});
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
    });

    it('should move to master category with compatible info model', async () => {
        const rootInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const rootMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: rootInfoModel.id
        });

        const parentInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id,
            infoModelId: parentInfoModel.id
        });

        const newParentInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const newParentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id,
            infoModelId: newParentInfoModel.id
        });

        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id
        });

        await Promise.all(
            [rootMasterCategory, parentMasterCategory, newParentMasterCategory, masterCategory].map((masterCategory) =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: masterCategory.id,
                    regionId: region.id
                })
            )
        );

        await expect(
            moveMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {parentId: newParentMasterCategory.id, index: -1}
                }
            })
        ).resolves.not.toThrow();

        // товары перенеслись в дочернюю МК (кто-МК)
        {
            const result = await getParentInfoModelHandler.handle({
                context,
                data: {
                    params: {
                        id: newParentMasterCategory.id
                    }
                }
            });
            expect(result.category.ownProductsCount).toEqual(0);
        }
        {
            const result = await getParentInfoModelHandler.handle({
                context,
                data: {
                    params: {
                        id: masterCategory.id
                    }
                }
            });
            expect(result.category.ownProductsCount).toEqual(2);
        }
    });

    it('should move to master category with incompatible info model if has own info model', async () => {
        const rootInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const rootMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: rootInfoModel.id
        });

        const parentInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id,
            infoModelId: parentInfoModel.id
        });

        const requiredAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {isValueRequired: true, type: AttributeType.NUMBER}
        });
        const newParentInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [{id: requiredAttribute.id}]
        });
        const newParentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id,
            infoModelId: newParentInfoModel.id
        });

        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id,
            infoModelId: infoModel.id
        });

        await Promise.all(
            [rootMasterCategory, parentMasterCategory, newParentMasterCategory, masterCategory].map((masterCategory) =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: masterCategory.id,
                    regionId: region.id
                })
            )
        );

        await expect(
            moveMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {parentId: newParentMasterCategory.id, index: -1}
                }
            })
        ).resolves.not.toThrow();
    });

    it('should rewrite tpath recursively', async () => {
        const rootInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const rootMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: rootInfoModel.id
        });

        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id
        });

        const newParentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id
        });

        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id
        });
        const childMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: masterCategory.id
        });

        await moveMasterCategoryHandler.handle({
            context,
            data: {
                params: {id: masterCategory.id},
                body: {parentId: newParentMasterCategory.id, index: -1}
            }
        });

        const masterCategories = await TestFactory.getMasterCategories();

        const tpathMap = mapValues(
            keyBy(masterCategories, ({id}) => id),
            ({tpath}) => tpath
        );

        expect(tpathMap).toEqual({
            [rootMasterCategory.id]: `${rootMasterCategory.id}`,
            [parentMasterCategory.id]: `${tpathMap[rootMasterCategory.id]}.${parentMasterCategory.id}`,
            [newParentMasterCategory.id]: `${tpathMap[rootMasterCategory.id]}.${newParentMasterCategory.id}`,
            [masterCategory.id]: `${tpathMap[newParentMasterCategory.id]}.${masterCategory.id}`,
            [childMasterCategory.id]: `${tpathMap[masterCategory.id]}.${childMasterCategory.id}`
        });
    });

    it('should not move to itself', async () => {
        const rootInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const rootMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: rootInfoModel.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id
        });

        await expect(
            moveMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {parentId: masterCategory.id, index: -1}
                }
            })
        ).rejects.toThrow('CYCLIC_MOVE_IS_FORBIDDEN');
    });

    it('should not move to child', async () => {
        const rootInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const rootMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: rootInfoModel.id
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id
        });

        await expect(
            moveMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: parentMasterCategory.id},
                    body: {parentId: masterCategory.id, index: -1}
                }
            })
        ).rejects.toThrow('CYCLIC_MOVE_IS_FORBIDDEN');
    });

    it('should not move to another tree', async () => {
        const rootInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const rootMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: rootInfoModel.id
        });

        const anotherRegion = await TestFactory.createRegion();
        const anotherRootInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: anotherRegion.id
        });
        const anotherRootMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: anotherRegion.id,
            infoModelId: anotherRootInfoModel.id
        });

        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id
        });

        await expect(
            moveMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {parentId: anotherRootMasterCategory.id, index: -1}
                }
            })
        ).rejects.toThrow('MOVE_TO_ANOTHER_TREE_IS_FORBIDDEN');
    });

    it('should not move active category to disabled parent', async () => {
        const rootInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const rootMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: rootInfoModel.id,
            status: MasterCategoryStatus.ACTIVE
        });

        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id,
            status: MasterCategoryStatus.ACTIVE
        });
        const disabledParentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id,
            status: MasterCategoryStatus.DISABLED
        });

        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id,
            status: MasterCategoryStatus.ACTIVE
        });

        await expect(
            moveMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {parentId: disabledParentMasterCategory.id, index: -1}
                }
            })
        ).rejects.toThrow(ActiveCategoryWithDisabledParentIsForbidden);
    });

    it('should throw error if master category does not exist', async () => {
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        const unknownId = parentMasterCategory.id + 1;
        const promise = moveMasterCategoryHandler.handle({
            context,
            data: {
                params: {id: unknownId},
                body: {parentId: parentMasterCategory.id, index: -1}
            }
        });

        await expect(promise).rejects.toThrow(EntityNotFoundError);
        await expect(promise.catch((err) => err.parameters)).resolves.toMatchObject({entity: 'MasterCategory'});
    });

    it('should throw error if new parent master category does not exist', async () => {
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        const unknownId = masterCategory.id + 1;
        const promise = moveMasterCategoryHandler.handle({
            context,
            data: {
                params: {id: masterCategory.id},
                body: {parentId: unknownId, index: -1}
            }
        });

        await expect(promise).rejects.toThrow(EntityNotFoundError);
        await expect(promise.catch((err) => err.parameters)).resolves.toMatchObject({entity: 'MasterCategory'});
    });
});
