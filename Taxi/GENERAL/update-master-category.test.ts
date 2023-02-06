import {random} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {
    ActiveCategoryWithDisabledParentIsForbidden,
    EntityNotFoundError,
    InactiveCategoryWithActiveChildrenIsForbidden
} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';
import {CategoryStatusUpdateStrategy} from 'types/category-status';
import {MasterCategoryStatus, UpdatedMasterCategory} from 'types/master-category';

import {updateMasterCategoryHandler} from './update-master-category';

describe('update master category', () => {
    let user: User;
    let langs: Lang[];
    let langCodes: string[];
    let region: Region;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {masterCategory: {canEdit: true}}});
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        langCodes = langs.map(({isoCode}) => isoCode);
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({lang: langs[0], region, user});
    });

    it('should add new translations', async () => {
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        const updatedMasterCategoryData: UpdatedMasterCategory = {
            nameTranslations: {
                [langCodes[0]]: 'некая мастер категория',
                [langCodes[1]]: 'some master category'
            },
            descriptionTranslations: {
                [langCodes[0]]: 'некое описание мастер категории',
                [langCodes[1]]: 'some master category description'
            }
        };

        await updateMasterCategoryHandler.handle({
            context,
            data: {
                params: {
                    id: masterCategory.id
                },
                body: updatedMasterCategoryData
            }
        });

        const updatedMasterCategory = (await TestFactory.getMasterCategories())[0];

        expect(updatedMasterCategory.nameTranslationMap).toEqual(updatedMasterCategoryData.nameTranslations);
        expect(updatedMasterCategory.descriptionTranslationMap).toEqual(
            updatedMasterCategoryData.descriptionTranslations
        );
    });

    it('should update translations', async () => {
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            nameTranslationMap: TestFactory.createTranslationMap({langCodes}),
            descriptionTranslationMap: TestFactory.createTranslationMap({langCodes})
        });

        const updatedMasterCategoryData: UpdatedMasterCategory = {
            nameTranslations: {
                [langCodes[0]]: 'некая мастер категория',
                [langCodes[1]]: 'some master category'
            },
            descriptionTranslations: {
                [langCodes[0]]: 'некое описание мастер категории',
                [langCodes[1]]: 'some master category description'
            }
        };

        await updateMasterCategoryHandler.handle({
            context,
            data: {
                params: {
                    id: masterCategory.id
                },
                body: updatedMasterCategoryData
            }
        });

        const updatedMasterCategory = (await TestFactory.getMasterCategories())[0];

        expect(updatedMasterCategory.nameTranslationMap).toEqual(updatedMasterCategoryData.nameTranslations);
        expect(updatedMasterCategory.descriptionTranslationMap).toEqual(
            updatedMasterCategoryData.descriptionTranslations
        );
    });

    it('should update translations partially', async () => {
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            nameTranslationMap: TestFactory.createTranslationMap({langCodes}),
            descriptionTranslationMap: TestFactory.createTranslationMap({langCodes})
        });

        let updatedMasterCategoryData: UpdatedMasterCategory = {
            nameTranslations: {
                [langCodes[0]]: 'некая мастер категория'
            }
        };

        await updateMasterCategoryHandler.handle({
            context,
            data: {
                params: {
                    id: masterCategory.id
                },
                body: updatedMasterCategoryData
            }
        });

        let updatedMasterCategory = (await TestFactory.getMasterCategories())[0];

        expect(updatedMasterCategory.nameTranslationMap).toEqual({
            ...masterCategory.nameTranslationMap,
            ...updatedMasterCategoryData.nameTranslations
        });
        expect(updatedMasterCategory.descriptionTranslationMap).toEqual(masterCategory.descriptionTranslationMap);

        updatedMasterCategoryData = {
            nameTranslations: {
                [langCodes[0]]: 'некая мастер категория'
            },
            descriptionTranslations: {
                [langCodes[0]]: 'некое описание мастер категории'
            }
        };

        await updateMasterCategoryHandler.handle({
            context,
            data: {
                params: {
                    id: masterCategory.id
                },
                body: updatedMasterCategoryData
            }
        });

        updatedMasterCategory = (await TestFactory.getMasterCategories())[0];

        expect(updatedMasterCategory.nameTranslationMap).toEqual({
            ...masterCategory.nameTranslationMap,
            ...updatedMasterCategoryData.nameTranslations
        });
        expect(updatedMasterCategory.descriptionTranslationMap).toEqual({
            ...masterCategory.descriptionTranslationMap,
            ...updatedMasterCategoryData.descriptionTranslations
        });
    });

    it('should update status according to rules', async () => {
        const parentInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: parentInfoModel.id,
            status: MasterCategoryStatus.ACTIVE
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id,
            status: MasterCategoryStatus.ACTIVE
        });

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {
                        status: {value: MasterCategoryStatus.DISABLED, strategy: CategoryStatusUpdateStrategy.SINGLE}
                    }
                }
            })
        ).resolves.toHaveProperty('status', MasterCategoryStatus.DISABLED);

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: parentMasterCategory.id},
                    body: {
                        status: {value: MasterCategoryStatus.DISABLED, strategy: CategoryStatusUpdateStrategy.SINGLE}
                    }
                }
            })
        ).resolves.toHaveProperty('status', MasterCategoryStatus.DISABLED);

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: parentMasterCategory.id},
                    body: {status: {value: MasterCategoryStatus.ACTIVE, strategy: CategoryStatusUpdateStrategy.SINGLE}}
                }
            })
        ).resolves.toHaveProperty('status', MasterCategoryStatus.ACTIVE);

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {status: {value: MasterCategoryStatus.ACTIVE, strategy: CategoryStatusUpdateStrategy.SINGLE}}
                }
            })
        ).resolves.toHaveProperty('status', MasterCategoryStatus.ACTIVE);
    });

    it('should not update status to disabled if any child is active', async () => {
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            status: MasterCategoryStatus.ACTIVE
        });

        await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id,
            status: MasterCategoryStatus.DISABLED
        });

        await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id,
            status: MasterCategoryStatus.ACTIVE
        });

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {
                        id: parentMasterCategory.id
                    },
                    body: {
                        status: {value: MasterCategoryStatus.DISABLED, strategy: CategoryStatusUpdateStrategy.SINGLE}
                    }
                }
            })
        ).rejects.toThrow(InactiveCategoryWithActiveChildrenIsForbidden);
    });

    it('should not update status to active if parent is disabled', async () => {
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            status: MasterCategoryStatus.DISABLED
        });

        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id,
            status: MasterCategoryStatus.DISABLED
        });

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {
                        id: masterCategory.id
                    },
                    body: {status: {value: MasterCategoryStatus.ACTIVE, strategy: CategoryStatusUpdateStrategy.SINGLE}}
                }
            })
        ).rejects.toThrow(ActiveCategoryWithDisabledParentIsForbidden);
    });

    it('should set compatible info model', async () => {
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const newInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id
        });

        await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {infoModelId: newInfoModel.id}
                }
            })
        ).resolves.toMatchObject({infoModel: {id: newInfoModel.id}});
    });

    it('should set incompatible info model if no products affected', async () => {
        const requiredAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {isValueRequired: true, type: AttributeType.NUMBER}
        });
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const newInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [{id: requiredAttribute.id}]
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id
        });

        await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: parentMasterCategory.id,
            regionId: region.id
        });

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {infoModelId: newInfoModel.id}
                }
            })
        ).resolves.toMatchObject({infoModel: {id: newInfoModel.id}});
    });

    it('should set incompatible info model if some products affected', async () => {
        const requiredAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {isValueRequired: true, type: AttributeType.NUMBER}
        });
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const newInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [{id: requiredAttribute.id}]
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id
        });

        await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {infoModelId: newInfoModel.id}
                }
            })
        ).resolves.toMatchObject({infoModel: {id: newInfoModel.id}});
    });

    it('should not set info model with another region', async () => {
        const otherRegion = await TestFactory.createRegion();
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const newInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: otherRegion.id
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id
        });

        const promise = updateMasterCategoryHandler.handle({
            context,
            data: {
                params: {id: masterCategory.id},
                body: {infoModelId: newInfoModel.id}
            }
        });

        await expect(promise).rejects.toThrow(/FALSY is_master_category_and_info_model_in_same_region/);
    });

    it('should update compatible info model', async () => {
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const newInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {infoModelId: newInfoModel.id}
                }
            })
        ).resolves.toMatchObject({infoModel: {id: newInfoModel.id}});
    });

    it('should update incompatible info model if no products affected', async () => {
        const requiredAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {isValueRequired: true, type: AttributeType.NUMBER}
        });
        const parentInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const newInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [{id: requiredAttribute.id}]
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: parentInfoModel.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id,
            infoModelId: infoModel.id
        });

        await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: parentMasterCategory.id,
            regionId: region.id
        });

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {infoModelId: newInfoModel.id}
                }
            })
        ).resolves.toMatchObject({infoModel: {id: newInfoModel.id}});
    });

    it('should update incompatible info model if some products affected', async () => {
        const requiredAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {isValueRequired: true, type: AttributeType.NUMBER}
        });
        const parentInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const newInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [{id: requiredAttribute.id}]
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: parentInfoModel.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id,
            infoModelId: infoModel.id
        });

        await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {infoModelId: newInfoModel.id}
                }
            })
        ).resolves.toMatchObject({infoModel: {id: newInfoModel.id}});
    });

    it('should not update info model with another region', async () => {
        const otherRegion = await TestFactory.createRegion();
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const newInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: otherRegion.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        const promise = updateMasterCategoryHandler.handle({
            context,
            data: {
                params: {id: masterCategory.id},
                body: {infoModelId: newInfoModel.id}
            }
        });

        await expect(promise).rejects.toThrow(/FALSY is_master_category_and_info_model_in_same_region/);
    });

    it('should remove info model if parent is compatible', async () => {
        const parentInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: parentInfoModel.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id,
            infoModelId: infoModel.id
        });

        await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {infoModelId: null}
                }
            })
        ).resolves.toMatchObject({infoModel: {id: parentInfoModel.id}});
    });

    it('should remove info model if parent is incompatible and no products affected', async () => {
        const requiredAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {isValueRequired: true, type: AttributeType.NUMBER}
        });
        const parentInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [{id: requiredAttribute.id}]
        });
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: parentInfoModel.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id,
            infoModelId: infoModel.id
        });

        await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: parentMasterCategory.id,
            regionId: region.id
        });

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {infoModelId: null}
                }
            })
        ).resolves.toMatchObject({infoModel: {id: parentInfoModel.id}});
    });

    it('should remove info model if parent is incompatible and some products affected', async () => {
        const requiredAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {isValueRequired: true, type: AttributeType.NUMBER}
        });
        const parentInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [{id: requiredAttribute.id}]
        });
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: parentInfoModel.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: parentMasterCategory.id,
            infoModelId: infoModel.id
        });

        await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: masterCategory.id},
                    body: {infoModelId: null}
                }
            })
        ).resolves.toMatchObject({infoModel: {id: parentInfoModel.id}});
    });

    it('should not remove info model from root master category', async () => {
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });
        const promise = updateMasterCategoryHandler.handle({
            context,
            data: {
                params: {id: masterCategory.id},
                body: {infoModelId: null}
            }
        });

        await expect(promise).rejects.toThrow(/check__master_category__root_with_info_model/);
    });

    it('should throw error if info model does not exist', async () => {
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });
        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });
        const unknownId = infoModel.id + 1;
        const promise = updateMasterCategoryHandler.handle({
            context,
            data: {
                params: {id: masterCategory.id},
                body: {infoModelId: unknownId}
            }
        });

        await expect(promise).rejects.toThrow(EntityNotFoundError);
        await expect(promise.catch((err) => err.parameters)).resolves.toMatchObject({entity: 'InfoModel'});
    });

    it('should throw error if master category does not exist', async () => {
        const unknownId = random(999999);
        const promise = updateMasterCategoryHandler.handle({
            context,
            data: {
                params: {id: unknownId},
                body: {}
            }
        });

        await expect(promise).rejects.toThrow(EntityNotFoundError);
        await expect(promise.catch((err) => err.parameters)).resolves.toMatchObject({entity: 'MasterCategory'});
    });

    it('should handle recursive status activation', async () => {
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });

        const root = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            status: MasterCategoryStatus.ACTIVE
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: root.id,
            status: MasterCategoryStatus.DISABLED
        });

        const child10 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: mc.id,
            status: MasterCategoryStatus.DISABLED
        });

        const child11 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: child10.id,
            status: MasterCategoryStatus.DISABLED
        });

        const child12 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: child10.id,
            status: MasterCategoryStatus.DISABLED
        });

        const child20 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: mc.id,
            status: MasterCategoryStatus.DISABLED
        });

        const child21 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: child10.id,
            status: MasterCategoryStatus.DISABLED
        });

        const child22 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: child10.id,
            status: MasterCategoryStatus.DISABLED
        });

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: mc.id},
                    body: {
                        status: {value: MasterCategoryStatus.ACTIVE, strategy: CategoryStatusUpdateStrategy.RECURSIVE}
                    }
                }
            })
        ).resolves.not.toThrow();

        const updatedIds = [mc, child10, child11, child12, child20, child21, child22].map(({id}) => id);
        const masterCategories = await TestFactory.getMasterCategories();

        expect(
            masterCategories
                .filter(({id}) => updatedIds.includes(id))
                .every(({status}) => status === MasterCategoryStatus.ACTIVE)
        ).toBeTruthy();
    });

    it('should handle recursive status deactivation', async () => {
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });

        const root = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            status: MasterCategoryStatus.ACTIVE
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: root.id,
            status: MasterCategoryStatus.ACTIVE
        });

        const child10 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: mc.id,
            status: MasterCategoryStatus.ACTIVE
        });

        const child11 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: child10.id,
            status: MasterCategoryStatus.ACTIVE
        });

        const child12 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: child10.id,
            status: MasterCategoryStatus.DISABLED
        });

        const child20 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: mc.id,
            status: MasterCategoryStatus.ACTIVE
        });

        const child21 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: child10.id,
            status: MasterCategoryStatus.ACTIVE
        });

        const child22 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: child10.id,
            status: MasterCategoryStatus.DISABLED
        });

        await TestFactory.flushHistory();

        await expect(
            updateMasterCategoryHandler.handle({
                context,
                data: {
                    params: {id: mc.id},
                    body: {
                        status: {value: MasterCategoryStatus.DISABLED, strategy: CategoryStatusUpdateStrategy.RECURSIVE}
                    }
                }
            })
        ).resolves.not.toThrow();

        const updatedIds = [mc, child10, child11, child20, child21].map(({id}) => id);
        const unchangedIds = [child12, child22].map(({id}) => id);
        const allIds = [...updatedIds, ...unchangedIds];
        const masterCategories = await TestFactory.getMasterCategories();

        expect(
            masterCategories
                .filter(({id}) => allIds.includes(id))
                .every(({status}) => status === MasterCategoryStatus.DISABLED)
        ).toBeTruthy();

        const historyRecords = await TestFactory.dispatchHistory();
        expect(historyRecords).toHaveLength(updatedIds.length);
    });

    it('should move Master Category to a different parent Master Category if sortOrder is in place', async () => {
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

        const returnValue = await updateMasterCategoryHandler.handle({
            context,
            data: {
                params: {id: masterCategory.id},
                body: {parentId: newParentMasterCategory.id, sortOrder: 0}
            }
        });
        expect(returnValue).toMatchObject({parentCategoryId: newParentMasterCategory.id});
    });

    it('should move Master Category even if there is no sortOrder', async () => {
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

        const returnValue = await updateMasterCategoryHandler.handle({
            context,
            data: {
                params: {id: masterCategory.id},
                body: {parentId: newParentMasterCategory.id}
            }
        });
        expect(returnValue).toMatchObject({
            parentCategoryId: newParentMasterCategory.id
        });
    });
});
