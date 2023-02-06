import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {HistorySubject} from '@/src/entities/history-subject/entity';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {Product} from '@/src/entities/product/entity';
import {ProductCombo} from '@/src/entities/product-combo/entity';
import {ProductComboGroup} from '@/src/entities/product-combo-group/entity';
import {ProductComboOption} from '@/src/entities/product-combo-option/entity';
import {ProductComboProduct} from '@/src/entities/product-combo-product/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import assertDefined from '@/src/utils/assert-defined';
import getProductCombos from 'server/routes/export-api/v1/product-combos';
import {config} from 'service/cfg';
import {ProductComboStatus, ProductComboType} from 'types/product-combo';

describe('update product combo', () => {
    let user: User;
    let region: Region;
    let infoModel: InfoModel;
    let masterCategory: MasterCategory;
    let metaProducts: [Product, Product];
    let realProducts: [Product, Product, Product, Product];
    let productCombos: [ProductCombo, ProductCombo, ProductCombo, ProductCombo];

    async function getLastCursor() {
        const manager = await TestFactory.getManager();
        const queryResult = await manager
            .createQueryBuilder()
            .select('hs.revision', 'revision')
            .from(ProductCombo, 'pc')
            .innerJoin(HistorySubject, 'hs', 'hs.id = pc.historySubjectId')
            .orderBy('hs.revision', 'DESC')
            .getRawOne<{revision: number}>();

        return assertDefined(queryResult).revision;
    }

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();

        infoModel = await TestFactory.createInfoModel({userId: user.id, regionId: region.id});

        masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id
        });

        const metaProductParams = {
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id,
            isMeta: true
        };

        metaProducts = await Promise.all([
            TestFactory.createProduct(metaProductParams),
            TestFactory.createProduct(metaProductParams)
        ]);

        const realProductParams = {
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id,
            isMeta: false
        };

        realProducts = await Promise.all([
            TestFactory.createProduct(realProductParams),
            TestFactory.createProduct(realProductParams),
            TestFactory.createProduct(realProductParams),
            TestFactory.createProduct(realProductParams)
        ]);

        const combo1 = await TestFactory.createProductCombo({
            userId: user.id,
            regionId: region.id,
            metaProductsIds: [metaProducts[0].id],
            productCombo: {
                status: ProductComboStatus.ACTIVE,
                type: ProductComboType.DISCOUNT,
                groups: [
                    {isSelectUnique: true, optionsToSelect: 1, options: [{productId: realProducts[0].id}]},
                    {isSelectUnique: true, optionsToSelect: 1, options: [{productId: realProducts[1].id}]}
                ]
            }
        });

        const combo2 = await TestFactory.createProductCombo({
            userId: user.id,
            regionId: region.id,
            productCombo: {
                status: ProductComboStatus.ACTIVE,
                type: ProductComboType.RECIPE,
                groups: [
                    {isSelectUnique: true, optionsToSelect: 1, options: [{productId: realProducts[0].id}]},
                    {
                        isSelectUnique: true,
                        optionsToSelect: 1,
                        options: [{productId: realProducts[1].id}, {productId: realProducts[2].id}]
                    }
                ]
            }
        });

        const combo3 = await TestFactory.createProductCombo({
            userId: user.id,
            regionId: region.id,
            metaProductsIds: [metaProducts[1].id],
            productCombo: {
                status: ProductComboStatus.ACTIVE,
                type: ProductComboType.DISCOUNT,
                groups: [
                    {
                        isSelectUnique: true,
                        optionsToSelect: 1,
                        options: [{productId: realProducts[0].id}, {productId: realProducts[1].id}]
                    },
                    {
                        isSelectUnique: true,
                        optionsToSelect: 1,
                        options: [{productId: realProducts[2].id}, {productId: realProducts[3].id}]
                    }
                ]
            }
        });

        const combo4 = await TestFactory.createProductCombo({
            userId: user.id,
            regionId: region.id,
            productCombo: {
                status: ProductComboStatus.ACTIVE,
                type: ProductComboType.RECIPE,
                groups: [
                    {
                        isSelectUnique: false,
                        optionsToSelect: 3,
                        options: [
                            {productId: realProducts[0].id},
                            {productId: realProducts[1].id},
                            {productId: realProducts[2].id}
                        ]
                    }
                ]
            }
        });

        productCombos = [combo1, combo2, combo3, combo4];
    });

    it('should return product combos after cursor', async () => {
        const data1 = await getProductCombos({limit: 1, lastCursor: 0});

        expect(data1.items).toEqual([
            {
                comboId: `pigeon_combo_${productCombos[0].id}`,
                comboRevision: `pigeon_combo_${productCombos[0].uuid}`,
                linkedMetaProducts: [{skuId: String(metaProducts[0].identifier)}],
                nameTankerKey: {
                    keyset: config.tankerExport.productComboKeyset,
                    key: `product-combo:${productCombos[0].id}`
                },
                meta: {
                    status: ProductComboStatus.ACTIVE,
                    type: ProductComboType.DISCOUNT
                },
                groups: [
                    {
                        optionsToSelect: 1,
                        nameTankerKey: {
                            keyset: config.tankerExport.productComboGroupsKeyset,
                            key: `product-combo-group:${productCombos[0].id}:${productCombos[0].groups[0].id}`
                        },
                        isSelectUnique: true,
                        options: [{skuId: String(realProducts[0].identifier)}]
                    },
                    {
                        optionsToSelect: 1,
                        nameTankerKey: {
                            keyset: config.tankerExport.productComboGroupsKeyset,
                            key: `product-combo-group:${productCombos[0].id}:${productCombos[0].groups[1].id}`
                        },
                        isSelectUnique: true,
                        options: [{skuId: String(realProducts[1].identifier)}]
                    }
                ]
            }
        ]);

        const data2 = await getProductCombos({limit: 1, lastCursor: data1.lastCursor});
        expect(data2.items).toHaveLength(1);
        expect(data2.items).toMatchObject([
            {
                comboId: `pigeon_combo_${productCombos[1].id}`,
                comboRevision: `pigeon_combo_${productCombos[1].uuid}`
            }
        ]);
    });

    it('should return product combos after updating', async () => {
        const cursor = await getLastCursor();
        const manager = await TestFactory.getManager();
        await manager.update(ProductCombo, productCombos[0].id, {status: ProductComboStatus.DISABLED});

        const data = await getProductCombos({limit: 10, lastCursor: cursor});

        expect(data.items).toHaveLength(1);
        expect(data.items).toMatchObject([
            {
                comboId: `pigeon_combo_${productCombos[0].id}`,
                meta: {status: ProductComboStatus.DISABLED}
            }
        ]);
    });

    it('should return deleted product combos', async () => {
        const cursor = await getLastCursor();
        await TestFactory.deleteProductCombo({userId: user.id, id: productCombos[0].id});

        const data = await getProductCombos({limit: 10, lastCursor: cursor});

        expect(data.items).toHaveLength(1);
        expect(data.items).toMatchObject([
            {
                comboId: `pigeon_combo_${productCombos[0].id}`,
                comboRevision: expect.stringMatching(/pigeon_combo_\w+/),
                linkedMetaProducts: [],
                nameTankerKey: {
                    keyset: '',
                    key: ''
                },
                meta: {
                    status: 'removed'
                },
                groups: []
            }
        ]);
    });

    it('should return product combos after updating product combo product', async () => {
        const cursor = await getLastCursor();
        const manager = await TestFactory.getManager();

        await manager.update(ProductComboGroup, productCombos[0].groups[1].id, {sortOrder: 2});
        await manager.update(ProductComboGroup, productCombos[3].groups[0].id, {optionsToSelect: 4});

        const data = await getProductCombos({limit: 10, lastCursor: cursor});

        expect(data.items).toHaveLength(2);
        expect(data.items).toMatchObject([
            {comboId: `pigeon_combo_${productCombos[0].id}`},
            {comboId: `pigeon_combo_${productCombos[3].id}`}
        ]);
    });

    it('should return product combos after changes in product combo group', async () => {
        const cursor = await getLastCursor();
        const manager = await TestFactory.getManager();

        await manager.delete(
            ProductComboProduct,
            productCombos[0].productComboProducts.map(({id}) => id)
        );

        const data1 = await getProductCombos({limit: 10, lastCursor: cursor});
        expect(data1.items).toHaveLength(1);
        expect(data1.items).toMatchObject([{comboId: `pigeon_combo_${productCombos[0].id}`, linkedMetaProducts: []}]);

        await TestFactory.linkProductsToProductCombo({
            userId: user.id,
            productCombo: productCombos[0],
            productComboProductIds: [metaProducts[1].id]
        });

        const data2 = await getProductCombos({limit: 10, lastCursor: data1.lastCursor});
        expect(data2.items).toHaveLength(1);
        expect(data2.items).toMatchObject([
            {
                comboId: `pigeon_combo_${productCombos[0].id}`,
                linkedMetaProducts: [{skuId: String(metaProducts[1].identifier)}],
                comboRevision: `pigeon_combo_${productCombos[0].uuid}`
            }
        ]);
    });

    it('should return product combos after changes in product combo options', async () => {
        const cursor = await getLastCursor();
        const manager = await TestFactory.getManager();

        await manager.delete(ProductComboOption, productCombos[3].groups[0].options[0].id);

        await manager.update(ProductComboOption, productCombos[2].groups[1].options[1].id, {
            sortOrder: 666
        });

        await manager.insert(ProductComboOption, {
            productComboGroupId: productCombos[1].groups[1].id,
            productId: realProducts[3].id,
            sortOrder: 2
        });

        const data = await getProductCombos({limit: 10, lastCursor: cursor});
        expect(data.items).toHaveLength(3);
        expect(data.items).toMatchObject([
            {comboId: `pigeon_combo_${productCombos[3].id}`},
            {comboId: `pigeon_combo_${productCombos[2].id}`},
            {comboId: `pigeon_combo_${productCombos[1].id}`}
        ]);
    });
});
