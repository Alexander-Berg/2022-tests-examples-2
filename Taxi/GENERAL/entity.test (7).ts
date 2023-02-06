import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Attribute} from '@/src/entities/attribute/entity';
import {DbTable} from '@/src/entities/const';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {Product} from '@/src/entities/product/entity';
import type {ProductCombo} from '@/src/entities/product-combo/entity';
import type {ProductComboGroup} from '@/src/entities/product-combo-group/entity';
import {ProductComboOption} from '@/src/entities/product-combo-option/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {AttributeType} from 'types/attribute';

describe('product_combo_option entity', () => {
    let user: User;
    let region: Region;
    let infoModel: InfoModel;
    let attributes: [Attribute, Attribute, Attribute];
    let masterCategory: MasterCategory;
    let metaProduct: Product;
    let realProduct: Product;
    let productCombo: ProductCombo;
    let productComboGroup: ProductComboGroup;

    async function getProductComboOptionHistory() {
        const history = await TestFactory.dispatchHistory();
        return history.filter(({tableName}) => tableName === DbTable.PRODUCT_COMBO_OPTION).sort((a, b) => b.id - a.id);
    }

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();

        attributes = await Promise.all([
            TestFactory.createAttribute({userId: user.id, attribute: {type: AttributeType.STRING}}),
            TestFactory.createAttribute({userId: user.id, attribute: {type: AttributeType.NUMBER}}),
            TestFactory.createAttribute({userId: user.id, attribute: {type: AttributeType.BOOLEAN}})
        ]);

        infoModel = await TestFactory.createInfoModel({userId: user.id, regionId: region.id, attributes});

        masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        metaProduct = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id,
            isMeta: true
        });

        realProduct = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id,
            isMeta: false
        });

        productCombo = await TestFactory.createProductCombo({
            userId: user.id,
            regionId: region.id
        });

        productComboGroup = await TestFactory.createProductComboGroup({
            userId: user.id,
            productComboGroup: {
                productComboId: productCombo.id
            }
        });

        await TestFactory.linkProductsToProductCombo({
            userId: user.id,
            productCombo,
            productComboProductIds: [metaProduct.id]
        });
    });

    it('should not allow to reference meta product', async () => {
        const otherMetaProduct = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id,
            isMeta: true
        });

        const productComboOptionPromise = TestFactory.createProductComboOption({
            userId: user.id,
            productComboOption: {
                productId: otherMetaProduct.id,
                productComboGroupId: productComboGroup.id
            }
        });

        await expect(productComboOptionPromise).rejects.toThrow('INVALID_PRODUCT_COMBO_OPTION_PRODUCT');
    });

    it('should not allow to reference product from another region', async () => {
        const anotherRegion = await TestFactory.createRegion();
        const anotherInfoModel = await TestFactory.createInfoModel({userId: user.id, regionId: anotherRegion.id});
        const anotherMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: anotherRegion.id,
            infoModelId: anotherInfoModel.id
        });

        const realProductFromAnotherRegion = await TestFactory.createProduct({
            userId: user.id,
            regionId: anotherRegion.id,
            masterCategoryId: anotherMasterCategory.id,
            isMeta: false
        });

        const productComboOptionPromise = TestFactory.createProductComboOption({
            userId: user.id,
            productComboOption: {
                productId: realProductFromAnotherRegion.id,
                productComboGroupId: productComboGroup.id
            }
        });

        await expect(productComboOptionPromise).rejects.toThrow('INVALID_PRODUCT_COMBO_OPTION_PRODUCT');
    });

    it('should update product_combo revision', async () => {
        const manager = await TestFactory.getManager();
        const historySubject1 = await TestFactory.getHistorySubject(productCombo.historySubjectId);

        const productComboOption = await TestFactory.createProductComboOption({
            userId: user.id,
            productComboOption: {
                productId: realProduct.id,
                productComboGroupId: productComboGroup.id
            }
        });

        const historySubject2 = await TestFactory.getHistorySubject(productCombo.historySubjectId);
        expect(historySubject2.revision).toBeGreaterThan(historySubject1.revision);

        await manager.update(ProductComboOption, productComboOption.id, {sortOrder: 10});
        const historySubject3 = await TestFactory.getHistorySubject(productCombo.historySubjectId);
        expect(historySubject3.revision).toBeGreaterThan(historySubject2.revision);

        await manager.delete(ProductComboOption, productComboOption.id);
        const historySubject4 = await TestFactory.getHistorySubject(productCombo.historySubjectId);
        expect(historySubject4.revision).toBeGreaterThan(historySubject3.revision);
    });

    it('should save history', async () => {
        const manager = await TestFactory.getManager();
        await TestFactory.flushHistory();
        await expect(getProductComboOptionHistory()).resolves.toHaveLength(0);

        const productComboOption = await TestFactory.createProductComboOption({
            userId: user.id,
            productComboOption: {
                productId: realProduct.id,
                productComboGroupId: productComboGroup.id
            }
        });

        const baseRow = {
            id: String(productComboOption.id),
            product_combo_group_id: String(productComboGroup.id),
            product_id: String(realProduct.id),
            sort_order: '0'
        };

        const history1 = await getProductComboOptionHistory();
        expect(history1).toHaveLength(1);
        expect(history1[0].oldRow).toBeNull();
        expect(history1[0].newRow).toMatchObject(baseRow);

        await manager.update(ProductComboOption, productComboOption.id, {sortOrder: 1});

        const history2 = await getProductComboOptionHistory();
        expect(history2).toHaveLength(2);
        expect(history2[0].oldRow).toMatchObject(baseRow);
        expect(history2[0].newRow).toMatchObject({...baseRow, sort_order: '1'});

        await manager.delete(ProductComboOption, productComboOption.id);

        const history3 = await getProductComboOptionHistory();
        expect(history3).toHaveLength(3);
        expect(history3[0].oldRow).toMatchObject({...baseRow, sort_order: '1'});
        expect(history3[0].newRow).toBeNull();
    });
});
