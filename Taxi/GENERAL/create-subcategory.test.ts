/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CatalogStatus} from 'types/catalog/base';
import type {Timetable} from 'types/catalog/timetable';

import {createSubcategoryHandler} from './create-subcategory';

describe('create subcategory', () => {
    let user: User;
    let region: Region;
    let langs: Lang[];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {catalog: {canEdit: true}}});
        region = await TestFactory.createRegion();
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        context = await TestFactory.createApiContext({user, region, lang: langs[0]});
    });

    it('should create subcategory', async () => {
        await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const subcategoryParams = {
            code: 'subcategory',
            status: CatalogStatus.ACTIVE,
            longTitleTranslations: {
                [langs[0].isoCode]: 'subcategory'
            },
            description: 'description',
            deeplink: 'deeplink',
            promo: true,
            legalRestrictions: 'legal restrictions',
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
            } as Timetable
        };

        const result = await createSubcategoryHandler.handle({context, data: {body: subcategoryParams}});
        const createdSubcategory = (await TestFactory.getFrontCategories()).find(({id}) => id === result.id)!;

        expect(createdSubcategory).toBeTruthy();
        expect(result).toEqual({
            ...subcategoryParams,
            id: createdSubcategory.id,
            legacyId: createdSubcategory.id.toString(),
            region: {
                id: region.id,
                isoCode: region.isoCode
            },
            productsCount: 0,
            categories: [],
            author: {
                login: user.login,
                firstName: user.staffData.name.first,
                lastName: user.staffData.name.last
            },
            createdAt: expect.any(Date),
            updatedAt: expect.any(Date)
        });
    });

    it('should create parent front category if it does not exist', async () => {
        const rootFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id
        });

        const anotherParentFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootFrontCategory.id
        });

        const baseSubcategoryParams = {
            status: CatalogStatus.ACTIVE,
            longTitleTranslations: {},
            description: null,
            deeplink: null,
            promo: false,
            legalRestrictions: null,
            timetable: null
        };

        let allParentFrontCategories = (await TestFactory.getFrontCategories()).filter(
            ({parentId}) => parentId === rootFrontCategory.id
        );

        expect(allParentFrontCategories).toHaveLength(1);
        expect(allParentFrontCategories).toMatchObject([{id: anotherParentFrontCategory.id}]);

        await createSubcategoryHandler.handle({
            context,
            data: {body: {...baseSubcategoryParams, code: 'subcategory 1'}}
        });

        allParentFrontCategories = (await TestFactory.getFrontCategories()).filter(
            ({parentId}) => parentId === rootFrontCategory.id
        );

        expect(allParentFrontCategories).toHaveLength(2);

        const parentFrontCategory = allParentFrontCategories.find(({id}) => id !== anotherParentFrontCategory.id)!;

        expect(parentFrontCategory).toMatchObject({
            code: 'subcategories'
        });

        await createSubcategoryHandler.handle({
            context,
            data: {body: {...baseSubcategoryParams, code: 'subcategory 2'}}
        });

        allParentFrontCategories = (await TestFactory.getFrontCategories()).filter(
            ({parentId}) => parentId === rootFrontCategory.id
        );

        expect(allParentFrontCategories).toHaveLength(2);
    });
});
