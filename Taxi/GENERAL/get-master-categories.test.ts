import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';

import {getMasterCategoriesHandler} from './get-master-categories';

describe('get master categories', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
    });

    it('should return all tree with correct sorting', async () => {
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

        const mc1 = await TestFactory.createMasterCategory({
            infoModelId: infoModels[0].id,
            regionId: region.id,
            userId: user.id
        });

        const mc12 = await TestFactory.createMasterCategory({
            userId: user.id,
            parentId: mc1.id,
            regionId: region.id,
            sortOrder: 1
        });

        const mc11 = await TestFactory.createMasterCategory({
            userId: user.id,
            parentId: mc1.id,
            regionId: region.id,
            sortOrder: 0
        });

        const mc13 = await TestFactory.createMasterCategory({
            infoModelId: infoModels[1].id,
            userId: user.id,
            parentId: mc1.id,
            regionId: region.id,
            sortOrder: 2
        });

        const mc132 = await TestFactory.createMasterCategory({
            userId: user.id,
            parentId: mc13.id,
            regionId: region.id,
            sortOrder: 1
        });

        const mc131 = await TestFactory.createMasterCategory({
            userId: user.id,
            parentId: mc13.id,
            regionId: region.id,
            sortOrder: 0
        });

        const {list, totalCount} = await getMasterCategoriesHandler.handle({
            context,
            data: {}
        });

        expect(totalCount).toBe(6);
        expect(list).toMatchObject([
            {
                id: mc1.id,
                infoModel: {
                    id: infoModels[0].id
                },
                children: [
                    {
                        id: mc11.id,
                        infoModel: {
                            id: infoModels[0].id
                        },
                        children: []
                    },
                    {
                        id: mc12.id,
                        infoModel: {
                            id: infoModels[0].id
                        },
                        children: []
                    },
                    {
                        id: mc13.id,
                        infoModel: {
                            id: infoModels[1].id
                        },
                        children: [
                            {
                                id: mc131.id,
                                infoModel: {
                                    id: infoModels[1].id
                                },
                                children: []
                            },
                            {
                                id: mc132.id,
                                infoModel: {
                                    id: infoModels[1].id
                                },
                                children: []
                            }
                        ]
                    }
                ]
            }
        ]);
    });

    it('should return tree in correct format', async () => {
        const lang = await TestFactory.createLang();

        const infoModel = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id
        });

        const mc1 = await TestFactory.createMasterCategory({
            infoModelId: infoModel.id,
            regionId: region.id,
            userId: user.id
        });

        const mc11 = await TestFactory.createMasterCategory({
            userId: user.id,
            parentId: mc1.id,
            regionId: region.id,
            sortOrder: 0,
            nameTranslationMap: TestFactory.createTranslationMap({langCodes: [lang.isoCode]}),
            descriptionTranslationMap: TestFactory.createTranslationMap({langCodes: [lang.isoCode]})
        });

        const {list, totalCount} = await getMasterCategoriesHandler.handle({
            context,
            data: {}
        });

        expect(totalCount).toBe(2);
        expect(list).toHaveLength(1);

        expect(list).toEqual([
            {
                id: mc1.id,
                code: mc1.code,
                status: mc1.status,
                infoModel: {
                    id: infoModel.id,
                    code: infoModel.code,
                    titleTranslations: {},
                    isInherited: false
                },
                nameTranslations: {},
                productsCount: 0,
                filledProductsCount: 0,
                notFilledProductsCount: 0,
                descriptionTranslations: {},
                updatedAt: expect.any(Date),
                fullness: 0,
                averageFullness: 0,
                sortOrder: 0,
                children: [
                    {
                        id: mc11.id,
                        code: mc11.code,
                        status: mc11.status,
                        infoModel: {
                            id: infoModel.id,
                            code: infoModel.code,
                            titleTranslations: {},
                            isInherited: true
                        },
                        nameTranslations: mc11.nameTranslationMap,
                        productsCount: 0,
                        filledProductsCount: 0,
                        notFilledProductsCount: 0,
                        descriptionTranslations: mc11.descriptionTranslationMap,
                        updatedAt: expect.any(Date),
                        fullness: 0,
                        averageFullness: 0,
                        sortOrder: 0,
                        children: []
                    }
                ]
            }
        ]);
    });

    it('should not return tree from other region', async () => {
        const infoModel = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id
        });

        const mc1 = await TestFactory.createMasterCategory({
            infoModelId: infoModel.id,
            regionId: region.id,
            userId: user.id
        });

        const mc11 = await TestFactory.createMasterCategory({
            userId: user.id,
            parentId: mc1.id,
            regionId: region.id,
            sortOrder: 0
        });

        const otherRegion = await TestFactory.createRegion();

        const otherInfoModel = await TestFactory.createInfoModel({
            regionId: otherRegion.id,
            userId: user.id
        });

        await TestFactory.createMasterCategory({
            infoModelId: otherInfoModel.id,
            regionId: otherRegion.id,
            userId: user.id
        });

        const {list, totalCount} = await getMasterCategoriesHandler.handle({
            context,
            data: {}
        });

        expect(totalCount).toBe(2);
        expect(list).toHaveLength(1);
        expect(list).toEqual([
            {
                id: mc1.id,
                code: mc1.code,
                status: mc1.status,
                infoModel: {
                    id: infoModel.id,
                    code: infoModel.code,
                    titleTranslations: {},
                    isInherited: false
                },
                nameTranslations: {},
                productsCount: 0,
                filledProductsCount: 0,
                notFilledProductsCount: 0,
                descriptionTranslations: {},
                updatedAt: expect.any(Date),
                fullness: 0,
                averageFullness: 0,
                sortOrder: 0,
                children: [
                    {
                        id: mc11.id,
                        code: mc11.code,
                        status: mc11.status,
                        infoModel: {
                            id: infoModel.id,
                            code: infoModel.code,
                            titleTranslations: {},
                            isInherited: true
                        },
                        nameTranslations: {},
                        productsCount: 0,
                        filledProductsCount: 0,
                        notFilledProductsCount: 0,
                        descriptionTranslations: {},
                        updatedAt: expect.any(Date),
                        fullness: 0,
                        averageFullness: 0,
                        sortOrder: 0,
                        children: []
                    }
                ]
            }
        ]);
    });
});
