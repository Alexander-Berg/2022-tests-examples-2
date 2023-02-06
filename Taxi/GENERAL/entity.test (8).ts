import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Attribute} from '@/src/entities/attribute/entity';
import {DbTable} from '@/src/entities/const';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {Product} from '@/src/entities/product/entity';
import type {ProductCombo} from '@/src/entities/product-combo/entity';
import {ProductComboProduct} from '@/src/entities/product-combo-product/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {AttributeType} from 'types/attribute';

describe('product_combo_product entity', () => {
    let user: User;
    let region: Region;
    let infoModel: InfoModel;
    let attributes: [Attribute, Attribute, Attribute];
    let masterCategory: MasterCategory;
    let products: [Product, Product];
    let productCombo: ProductCombo;

    async function getProductComboProductHistory() {
        const history = await TestFactory.dispatchHistory();
        return history.filter(({tableName}) => tableName === DbTable.PRODUCT_COMBO_PRODUCT).sort((a, b) => b.id - a.id);
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

        products = await Promise.all([
            TestFactory.createProduct({
                userId: user.id,
                regionId: region.id,
                masterCategoryId: masterCategory.id,
                isMeta: false
            }),
            TestFactory.createProduct({
                userId: user.id,
                regionId: region.id,
                masterCategoryId: masterCategory.id,
                isMeta: true
            })
        ]);

        productCombo = await TestFactory.createProductCombo({userId: user.id, regionId: region.id});
    });

    it('should not allow to reference real product', async () => {
        const productComboProductPromise = TestFactory.linkProductsToProductCombo({
            userId: user.id,
            productCombo,
            productComboProductIds: [products[0].id]
        });

        await expect(productComboProductPromise).rejects.toThrow('INVALID_PRODUCT_COMBO_META_PRODUCT');
    });

    it('should not allow to reference meta product from another region', async () => {
        const anotherRegion = await TestFactory.createRegion();
        const anotherInfoModel = await TestFactory.createInfoModel({userId: user.id, regionId: anotherRegion.id});
        const anotherMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: anotherRegion.id,
            infoModelId: anotherInfoModel.id
        });
        const product = await TestFactory.createProduct({
            userId: user.id,
            regionId: anotherRegion.id,
            masterCategoryId: anotherMasterCategory.id,
            isMeta: true
        });

        const productComboProductPromise = TestFactory.linkProductsToProductCombo({
            userId: user.id,
            productCombo,
            productComboProductIds: [product.id]
        });

        await expect(productComboProductPromise).rejects.toThrow('INVALID_PRODUCT_COMBO_META_PRODUCT');
    });

    it('should save history', async () => {
        const manager = await TestFactory.getManager();
        await TestFactory.flushHistory();
        await expect(getProductComboProductHistory()).resolves.toHaveLength(0);

        const [productComboProduct] = await TestFactory.linkProductsToProductCombo({
            userId: user.id,
            productCombo,
            productComboProductIds: [products[1].id]
        });

        const baseRow = {
            id: String(productComboProduct.id),
            product_id: String(products[1].id),
            sort_order: '0',
            product_combo_id: String(productCombo.id)
        };

        const history1 = await getProductComboProductHistory();
        expect(history1).toHaveLength(1);
        expect(history1[0].oldRow).toBeNull();
        expect(history1[0].newRow).toMatchObject(baseRow);

        await manager.update(ProductComboProduct, productComboProduct.id, {sortOrder: 1});

        const history2 = await getProductComboProductHistory();
        expect(history2).toHaveLength(2);
        expect(history2[0].oldRow).toMatchObject(baseRow);
        expect(history2[0].newRow).toMatchObject({...baseRow, sort_order: '1'});

        await manager.delete(ProductComboProduct, productComboProduct.id);

        const history3 = await getProductComboProductHistory();
        expect(history3).toHaveLength(3);
        expect(history3[0].oldRow).toMatchObject({...baseRow, sort_order: '1'});
        expect(history3[0].newRow).toBeNull();
    });

    it('should update product_combo revision on meaningful changes only', async () => {
        const manager = await TestFactory.getManager();

        const historySubject1 = await TestFactory.getHistorySubject(productCombo.historySubjectId);

        const [productComboProduct] = await TestFactory.linkProductsToProductCombo({
            userId: user.id,
            productCombo,
            productComboProductIds: [products[1].id]
        });

        const historySubject2 = await TestFactory.getHistorySubject(productCombo.historySubjectId);
        expect(historySubject2.revision).toBeGreaterThan(historySubject1.revision);

        await manager.update(ProductComboProduct, productComboProduct.id, {sortOrder: 1});
        const historySubject3 = await TestFactory.getHistorySubject(productCombo.historySubjectId);
        expect(historySubject3.revision).toEqual(historySubject2.revision);

        await manager.delete(ProductComboProduct, productComboProduct.id);
        const historySubject4 = await TestFactory.getHistorySubject(productCombo.historySubjectId);
        expect(historySubject4.revision).toBeGreaterThan(historySubject3.revision);
    });
});
