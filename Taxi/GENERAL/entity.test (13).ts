import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Attribute} from '@/src/entities/attribute/entity';
import {DbTable} from '@/src/entities/const';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {Product} from '@/src/entities/product/entity';
import type {ProductCombo} from '@/src/entities/product-combo/entity';
import {ProductComboGroup} from '@/src/entities/product-combo-group/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {AttributeType} from 'types/attribute';

describe('product_combo_group entity', () => {
    let user: User;
    let region: Region;
    let infoModel: InfoModel;
    let attributes: [Attribute, Attribute, Attribute];
    let masterCategory: MasterCategory;
    let product: Product;
    let productCombo: ProductCombo;

    async function getProductComboGroupHistory() {
        const history = await TestFactory.dispatchHistory();
        return history.filter(({tableName}) => tableName === DbTable.PRODUCT_COMBO_GROUP).sort((a, b) => b.id - a.id);
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

        product = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id,
            isMeta: true
        });

        productCombo = await TestFactory.createProductCombo({
            userId: user.id,
            regionId: region.id
        });

        await TestFactory.linkProductsToProductCombo({
            userId: user.id,
            productCombo,
            productComboProductIds: [product.id]
        });
    });

    it('should update product_combo revision on any update', async () => {
        const manager = await TestFactory.getManager();
        const historySubjectId1 = await TestFactory.getHistorySubject(productCombo.historySubjectId);

        const productComboGroup = await TestFactory.createProductComboGroup({
            userId: user.id,
            productComboGroup: {
                productComboId: productCombo.id,
                optionsToSelect: 1,
                isSelectUnique: true
            }
        });

        const historySubjectId2 = await TestFactory.getHistorySubject(productCombo.historySubjectId);
        expect(historySubjectId1.revision).toEqual(historySubjectId2.revision);

        await manager.update(ProductComboGroup, productComboGroup.id, {sortOrder: 666});
        const historySubjectId3 = await TestFactory.getHistorySubject(productCombo.historySubjectId);
        expect(historySubjectId3.revision).toBeGreaterThan(historySubjectId2.revision);

        await manager.update(ProductComboGroup, productComboGroup.id, {optionsToSelect: 10});
        const historySubjectId4 = await TestFactory.getHistorySubject(productCombo.historySubjectId);
        expect(historySubjectId4.revision).toBeGreaterThan(historySubjectId3.revision);

        await manager.update(ProductComboGroup, productComboGroup.id, {isSelectUnique: false});
        const historySubjectId5 = await TestFactory.getHistorySubject(productCombo.historySubjectId);
        expect(historySubjectId5.revision).toBeGreaterThan(historySubjectId4.revision);

        await manager.delete(ProductComboGroup, productComboGroup.id);
        const historySubjectId6 = await TestFactory.getHistorySubject(productCombo.historySubjectId);
        expect(historySubjectId6.revision).toEqual(historySubjectId5.revision);
    });

    it('should save history', async () => {
        const manager = await TestFactory.getManager();
        await TestFactory.flushHistory();
        await expect(getProductComboGroupHistory()).resolves.toHaveLength(0);

        const productComboGroup = await TestFactory.createProductComboGroup({
            userId: user.id,
            productComboGroup: {
                productComboId: productCombo.id
            }
        });

        const baseRow = {
            id: String(productComboGroup.id),
            product_combo_id: String(productCombo.id),
            options_to_select: '1',
            is_select_unique: 't',
            sort_order: '0'
        };

        const history1 = await getProductComboGroupHistory();
        expect(history1).toHaveLength(1);
        expect(history1[0].oldRow).toBeNull();
        expect(history1[0].newRow).toMatchObject(baseRow);

        await manager.update(ProductComboGroup, productComboGroup.id, {sortOrder: 1});

        const history2 = await getProductComboGroupHistory();
        expect(history2).toHaveLength(2);
        expect(history2[0].oldRow).toMatchObject(baseRow);
        expect(history2[0].newRow).toMatchObject({...baseRow, sort_order: '1'});

        await manager.delete(ProductComboGroup, productComboGroup.id);

        const history3 = await getProductComboGroupHistory();
        expect(history3).toHaveLength(3);
        expect(history3[0].oldRow).toMatchObject({...baseRow, sort_order: '1'});
        expect(history3[0].newRow).toBeNull();
    });
});
