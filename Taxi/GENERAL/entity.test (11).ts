import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Attribute} from '@/src/entities/attribute/entity';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import {Product} from '@/src/entities/product/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {AttributeType} from 'types/attribute';

describe('product entity', () => {
    let user: User;
    let region: Region;
    let infoModel: InfoModel;
    let attributes: [Attribute, Attribute, Attribute];
    let rootMasterCategory: MasterCategory;
    let masterCategory: MasterCategory;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();

        attributes = await Promise.all([
            TestFactory.createAttribute({userId: user.id, attribute: {type: AttributeType.STRING}}),
            TestFactory.createAttribute({userId: user.id, attribute: {type: AttributeType.NUMBER}}),
            TestFactory.createAttribute({userId: user.id, attribute: {type: AttributeType.BOOLEAN}})
        ]);

        infoModel = await TestFactory.createInfoModel({userId: user.id, regionId: region.id, attributes});

        rootMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: rootMasterCategory.id
        });
    });

    it('should not allow change is_meta to "false" after creation', async () => {
        const manager = await TestFactory.getManager();

        const product = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id,
            isMeta: true
        });

        await expect(manager.update(Product, product.id, {isMeta: false})).rejects.toThrow(
            'PRODUCT_IS_META_CHANGING_FORBIDDEN'
        );
    });

    it('should not allow change is_meta to "true" after creation', async () => {
        const manager = await TestFactory.getManager();

        const product = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id,
            isMeta: false
        });

        await expect(manager.update(Product, product.id, {isMeta: true})).rejects.toThrow(
            'PRODUCT_IS_META_CHANGING_FORBIDDEN'
        );
    });

    it('should not allow change master category on meta-product', async () => {
        const manager = await TestFactory.getManager();

        const anotherMc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: rootMasterCategory.id
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id,
            isMeta: true
        });

        await expect(manager.update(Product, product.id, {masterCategoryId: anotherMc.id})).rejects.toThrow(
            'META_PRODUCT_MASTER_CATEGORY_CHANGING_FORBIDDEN'
        );
    });
});
