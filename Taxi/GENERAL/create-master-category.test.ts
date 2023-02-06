/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {range} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {ActiveCategoryWithDisabledParentIsForbidden} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {MasterCategoryStatus, NewMasterCategory} from 'types/master-category';

import {createMasterCategoryHandler} from './create-master-category';
import {getParentInfoModelHandler} from './get-parent-info-model';

describe('create master category', () => {
    let user: User;
    let langs: Lang[];
    let regions: Region[];
    let langCodes: string[];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {masterCategory: {canEdit: true}}});
        regions = await Promise.all(['RU', 'US'].map((code) => TestFactory.createRegion({code})));
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        langCodes = langs.map(({isoCode}) => isoCode);
        context = await TestFactory.createApiContext({lang: langs[0], user, region: regions[0]});
    });

    it('should create master category with translations', async () => {
        const infoModel = await TestFactory.createInfoModel({userId: user.id, regionId: regions[0].id});
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: regions[0].id,
            infoModelId: infoModel.id
        });

        await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: parentMasterCategory.id,
            regionId: regions[0].id
        });

        const masterCategoryData: NewMasterCategory = {
            code: 'master_category',
            parentId: parentMasterCategory.id,
            status: MasterCategoryStatus.ACTIVE,
            nameTranslations: {
                [langCodes[0]]: 'мастер категория',
                [langCodes[1]]: 'master category'
            },
            descriptionTranslations: {
                [langCodes[0]]: 'описание мастер категории',
                [langCodes[1]]: 'master category description'
            }
        };

        const createdMasterCategory = await createMasterCategoryHandler.handle({
            context,
            data: {
                body: masterCategoryData
            }
        });

        const foundMasterCategory = (await TestFactory.getMasterCategories()).find(
            ({id}) => id === createdMasterCategory.id
        )!;

        expect(foundMasterCategory).toBeTruthy();

        const history = (await TestFactory.getHistory()).filter((it) => it.newRowMatchEntity(foundMasterCategory));

        expect(history).toHaveLength(1);

        expect(createdMasterCategory).toEqual({
            id: foundMasterCategory.id,
            code: masterCategoryData.code,
            nameTranslations: masterCategoryData.nameTranslations,
            descriptionTranslations: masterCategoryData.descriptionTranslations,
            author: user.formatAuthor(),
            region: {
                id: regions[0].id,
                isoCode: regions[0].isoCode
            },
            infoModel: {
                id: infoModel.id,
                code: infoModel.code,
                titleTranslations: {},
                isInherited: true
            },
            status: masterCategoryData.status,
            parentCategoryId: masterCategoryData.parentId,
            breadcrumbs: [
                {
                    id: parentMasterCategory.id,
                    code: parentMasterCategory.code,
                    nameTranslations: {},
                    status: MasterCategoryStatus.ACTIVE
                }
            ],
            sortOrder: 0,
            maxSortOrder: 0,
            createdAt: history[0].createdAt,
            updatedAt: history[0].createdAt,
            hasActiveChildren: false,
            isLeaf: true,
            productsCount: 1,
            filledProductsCount: 0,
            notFilledProductsCount: 0,
            fullness: 0,
            averageFullness: 0
        });

        // товары перенеслись в дочернюю МК (кто-МК)
        {
            const result = await getParentInfoModelHandler.handle({
                context,
                data: {
                    params: {
                        id: parentMasterCategory.id
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
                        id: createdMasterCategory.id
                    }
                }
            });
            expect(result.category.ownProductsCount).toEqual(1);
        }
    });

    it('should calculate sort order', async () => {
        const infoModel = await TestFactory.createInfoModel({userId: user.id, regionId: regions[0].id});
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: regions[0].id,
            infoModelId: infoModel.id
        });
        const siblingMasterCategories = await Promise.all(
            range(2).map((i) =>
                TestFactory.createMasterCategory({
                    userId: user.id,
                    regionId: regions[0].id,
                    parentId: parentMasterCategory.id,
                    infoModelId: infoModel.id,
                    sortOrder: i
                })
            )
        );

        const masterCategoryData: NewMasterCategory = {
            code: 'master_category',
            parentId: parentMasterCategory.id,
            status: MasterCategoryStatus.ACTIVE,
            nameTranslations: {},
            descriptionTranslations: {}
        };

        const createdMasterCategory = await createMasterCategoryHandler.handle({
            context,
            data: {
                body: masterCategoryData
            }
        });

        const foundMasterCategory = (await TestFactory.getMasterCategories()).find(
            ({id}) => id === createdMasterCategory.id
        )!;

        expect(foundMasterCategory).toHaveProperty('sortOrder', siblingMasterCategories.length);
    });

    it('should not create master category with info model from another region', async () => {
        const parentInfoModel = await TestFactory.createInfoModel({userId: user.id, regionId: regions[0].id});
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: regions[0].id,
            infoModelId: parentInfoModel.id
        });

        const infoModel = await TestFactory.createInfoModel({userId: user.id, regionId: regions[1].id});

        const masterCategoryData: NewMasterCategory = {
            code: 'master_category',
            parentId: parentMasterCategory.id,
            infoModelId: infoModel.id,
            status: MasterCategoryStatus.ACTIVE,
            nameTranslations: {},
            descriptionTranslations: {}
        };

        const promise = createMasterCategoryHandler.handle({
            context,
            data: {
                body: masterCategoryData
            }
        });

        await expect(promise).rejects.toThrow(/FALSY is_master_category_and_info_model_in_same_region/);
    });

    it('should not create active category if parent is disabled', async () => {
        const infoModel = await TestFactory.createInfoModel({userId: user.id, regionId: regions[0].id});
        const parentMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            infoModelId: infoModel.id,
            regionId: regions[0].id,
            status: MasterCategoryStatus.DISABLED
        });

        const masterCategoryData: NewMasterCategory = {
            code: 'master_category',
            parentId: parentMasterCategory.id,
            status: MasterCategoryStatus.ACTIVE,
            nameTranslations: {},
            descriptionTranslations: {}
        };

        const promise = createMasterCategoryHandler.handle({
            context,
            data: {
                body: masterCategoryData
            }
        });

        await expect(promise).rejects.toThrow(ActiveCategoryWithDisabledParentIsForbidden);
    });

    it('should not create another root master category with same region', async () => {
        const infoModel = await TestFactory.createInfoModel({userId: user.id, regionId: regions[0].id});

        await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: regions[0].id,
            infoModelId: infoModel.id
        });

        const promise = TestFactory.createMasterCategory({
            userId: user.id,
            regionId: regions[0].id,
            infoModelId: infoModel.id
        });

        await expect(promise).rejects.toThrow(
            'duplicate key value violates unique constraint "idx__master_category__only_one_root_in_region"'
        );
    });
});
