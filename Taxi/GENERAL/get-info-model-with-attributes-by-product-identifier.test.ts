import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {EntityNotFoundError} from '@/src/errors';
import {AttributeType} from '@/src/types/attribute';
import type {ApiRequestContext} from 'server/routes/api/api-handler';

import {getInfoModelWithAttributesByProductIdentifierHandler} from './get-info-model-with-attributes-by-product-identifier';

describe('get info-model with attributes by product identifier', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
    });

    it('should return all tree with correct sorting', async () => {
        const attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.NUMBER, isValueRequired: true, isValueLocalizable: false}
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.STRING, isValueRequired: false, isValueLocalizable: true}
            })
        ]);

        const infoModel = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id,
            attributes: [
                {id: attributes[0].id, isImportant: true},
                {id: attributes[1].id, isImportant: false}
            ]
        });

        const mcParent = await TestFactory.createMasterCategory({
            infoModelId: infoModel.id,
            regionId: region.id,
            userId: user.id
        });

        const product = await TestFactory.createProduct({
            masterCategoryId: mcParent.id,
            userId: user.id,
            regionId: region.id
        });

        const result = await getInfoModelWithAttributesByProductIdentifierHandler.handle({
            context,
            data: {params: {identifier: product.identifier}}
        });

        expect(result).toMatchObject({
            infoModel: {
                id: infoModel.id,
                code: infoModel.code,
                titleTranslations: {}
            },
            attributes: [
                {
                    id: attributes[0].id,
                    type: attributes[0].type,
                    isValueRequired: attributes[0].isValueRequired,
                    isValueLocalizable: attributes[0].isValueLocalizable,
                    isImportant: true
                },
                {
                    id: attributes[1].id,
                    type: attributes[1].type,
                    isValueLocalizable: attributes[1].isValueLocalizable,
                    isImportant: false
                }
            ]
        });
    });

    it('should return error if product does not exist', async () => {
        let error = null;
        const unknownId = Number.MAX_SAFE_INTEGER;

        try {
            await getInfoModelWithAttributesByProductIdentifierHandler.handle({
                context,
                data: {params: {identifier: unknownId}}
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'Product'});
    });
});
