import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {AttributeType} from '@/src/types/attribute';
import type {ApiRequestContext} from 'server/routes/api/api-handler';

import {getUnusedAttributesByProductIdentifierHandler} from './get-unused-attributes-by-product-identifier';

describe('get unused attributes by product identifier', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
    });

    it('should return lis of unused attributes if products has any', async () => {
        const attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.NUMBER}
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.STRING}
            })
        ]);

        const infoModel = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id,
            attributes: [{id: attributes[0].id}]
        });

        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id
        });

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: product.id,
                attributeId: attributes[0].id,
                value: 123
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: product.id,
                attributeId: attributes[1].id,
                value: 'foo'
            })
        ]);

        const result = await getUnusedAttributesByProductIdentifierHandler.handle({
            context,
            data: {params: {identifier: product.identifier}}
        });

        expect(result).toEqual({
            totalCount: 1,
            list: [
                {
                    id: attributes[1].id,
                    type: attributes[1].type,
                    createdAt: expect.any(Date),
                    updatedAt: expect.any(Date),
                    isArray: attributes[1].isArray,
                    isClient: false,
                    isImmutable: false,
                    isValueLocalizable: attributes[1].isValueLocalizable,
                    code: attributes[1].code,
                    ticket: attributes[1].ticket,
                    nameTranslations: attributes[1].nameTranslationMap,
                    descriptionTranslations: attributes[1].descriptionTranslationMap,
                    author: {
                        login: user.login,
                        firstName: user.staffData.name.first,
                        lastName: user.staffData.name.last
                    },
                    properties: {
                        min: undefined,
                        max: undefined,
                        maxArraySize: undefined
                    },
                    attributeGroupId: null,
                    attributeGroupSortOrder: null
                }
            ]
        });
    });

    it('should return empty list if product has no unused attributes', async () => {
        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.NUMBER}
        });

        const infoModel = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id,
            attributes: [{id: attribute.id}]
        });

        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attribute.id,
            value: 123
        });

        const result = await getUnusedAttributesByProductIdentifierHandler.handle({
            context,
            data: {params: {identifier: product.identifier}}
        });

        expect(result).toEqual({
            totalCount: 0,
            list: []
        });
    });
});
