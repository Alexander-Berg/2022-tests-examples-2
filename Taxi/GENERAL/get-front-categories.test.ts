import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';

import {getFrontCategoriesHandler} from './get-front-categories';

describe('get front categories', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
    });

    it('should return all tree with correct sorting', async () => {
        const fc1 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const fc12 = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: fc1.id,
            regionId: region.id,
            sortOrder: 1
        });

        const fc11 = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: fc1.id,
            regionId: region.id,
            sortOrder: 0
        });

        const fc13 = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: fc1.id,
            regionId: region.id,
            sortOrder: 2
        });

        const fc132 = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: fc13.id,
            regionId: region.id,
            sortOrder: 1
        });

        const fc131 = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: fc13.id,
            regionId: region.id,
            sortOrder: 0
        });

        const {list, totalCount} = await getFrontCategoriesHandler.handle({
            context,
            data: {}
        });

        expect(totalCount).toBe(6);
        expect(list).toMatchObject([
            {
                id: fc1.id,
                children: [
                    {
                        id: fc11.id,
                        children: []
                    },
                    {
                        id: fc12.id,
                        children: []
                    },
                    {
                        id: fc13.id,
                        children: [
                            {
                                id: fc131.id,
                                children: []
                            },
                            {
                                id: fc132.id,
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

        const fc1 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const fc11 = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: fc1.id,
            regionId: region.id,
            sortOrder: 0,
            nameTranslationMap: TestFactory.createTranslationMap({langCodes: [lang.isoCode]}),
            descriptionTranslationMap: TestFactory.createTranslationMap({langCodes: [lang.isoCode]})
        });

        const {list, totalCount} = await getFrontCategoriesHandler.handle({
            context,
            data: {}
        });

        expect(totalCount).toBe(2);
        expect(list).toHaveLength(1);

        expect(list).toEqual([
            {
                id: fc1.id,
                code: fc1.code,
                status: fc1.status,
                isPromo: fc1.promo,
                imageUrl: fc1.imageUrl,
                region: {
                    id: region.id,
                    isoCode: region.isoCode
                },
                sortOrder: 0,
                updatedAt: expect.any(Date),
                nameTranslations: {},
                productsCount: 0,
                descriptionTranslations: {},
                children: [
                    {
                        id: fc11.id,
                        code: fc11.code,
                        status: fc11.status,
                        nameTranslations: fc11.nameTranslationMap,
                        productsCount: 0,
                        descriptionTranslations: fc11.descriptionTranslationMap,
                        isPromo: fc11.promo,
                        imageUrl: fc11.imageUrl,
                        region: {
                            id: region.id,
                            isoCode: region.isoCode
                        },
                        sortOrder: 0,
                        updatedAt: expect.any(Date),
                        children: []
                    }
                ]
            }
        ]);
    });

    it('should not return tree from other region', async () => {
        const fc1 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const fc11 = await TestFactory.createFrontCategory({
            userId: user.id,
            parentId: fc1.id,
            regionId: region.id,
            sortOrder: 0
        });

        const anotherRegion = await TestFactory.createRegion();

        await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: anotherRegion.id
        });

        const {list, totalCount} = await getFrontCategoriesHandler.handle({
            context,
            data: {}
        });

        expect(totalCount).toBe(2);
        expect(list).toHaveLength(1);
        expect(list.map((l) => l.id)).toEqual([fc1.id]);
        const children = list.map((l) => l.children);

        expect(children).toHaveLength(1);
        expect(children[0].map((l) => l.id)).toEqual([fc11.id]);
    });
});
