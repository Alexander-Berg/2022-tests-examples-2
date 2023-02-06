import {groupBy} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {ATTRIBUTES_CODES} from '@/src/constants';
import type {Attribute} from '@/src/entities/attribute/entity';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {Lang} from '@/src/entities/lang/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {Product} from '@/src/entities/product/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {deleteProductComboHandler} from './delete-product-combo';

describe('delete product combos', () => {
    let user: User;
    let langs: [Lang, Lang];
    let region: Region;
    let infoModel: InfoModel;
    let attributes: [Attribute, Attribute, Attribute];
    let masterCategory: MasterCategory;
    let metaProduct: Product;
    let realProducts: [Product, Product, Product];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {comboProduct: {canEdit: true}}});
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});

        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        await TestFactory.createLocale({regionId: region.id, langIds: langs.map(({id}) => id)});

        attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.STRING, code: ATTRIBUTES_CODES.LONG_NAME_LOC, isValueLocalizable: true}
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.IMAGE, code: ATTRIBUTES_CODES.IMAGE, isArray: true}
            }),
            TestFactory.createAttribute({userId: user.id, attribute: {type: AttributeType.NUMBER}})
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

        const realProductParams = {
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id,
            isMeta: false
        };

        realProducts = await Promise.all([
            TestFactory.createProduct(realProductParams),
            TestFactory.createProduct(realProductParams),
            TestFactory.createProduct(realProductParams)
        ]);
    });

    it('should delete product combo with all relations', async () => {
        const productCombo = await TestFactory.createProductCombo({userId: user.id, regionId: region.id});

        await TestFactory.linkProductsToProductCombo({
            userId: user.id,
            productCombo,
            productComboProductIds: [metaProduct.id]
        });

        const productComboGroup = await TestFactory.createProductComboGroup({
            userId: user.id,
            productComboGroup: {productComboId: productCombo.id, optionsToSelect: 1, isSelectUnique: true}
        });

        await Promise.all(
            realProducts.map((it) =>
                TestFactory.createProductComboOption({
                    userId: user.id,
                    productComboOption: {productId: it.id, productComboGroupId: productComboGroup.id}
                })
            )
        );

        await TestFactory.flushHistory();
        const productComboDeletionPromise = deleteProductComboHandler.handle({
            context,
            data: {
                params: {
                    id: productCombo.id
                }
            }
        });

        await expect(productComboDeletionPromise).resolves.not.toThrow();

        const history = await TestFactory.dispatchHistory();
        history.sort((a, b) => a.id - b.id);

        expect(history).toHaveLength(6);
        const groupedHistory = groupBy(history, ({tableName}) => tableName);

        expect(groupedHistory['product_combo']).toHaveLength(1);
        expect(groupedHistory['product_combo_product']).toHaveLength(1);
        expect(groupedHistory['product_combo_group']).toHaveLength(1);
        expect(groupedHistory['product_combo_option']).toHaveLength(3);

        await expect(TestFactory.getProductCombos()).resolves.toEqual([]);
    });
});
