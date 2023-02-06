import {pick, sortBy} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {createUnPatchedQueryRunner} from 'tests/unit/setup';
import {TestFactory} from 'tests/unit/test-factory';

import {
    ADDITION_SYMBOL,
    FRONT_CATEGORY_HEADER,
    IDENTIFIER_HEADER,
    MASTER_CATEGORY_HEADER,
    SUBTRACTION_SYMBOL
} from '@/src/constants/import';
import type {Attribute} from '@/src/entities/attribute/entity';
import type {FrontCategory} from '@/src/entities/front-category/entity';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {Lang} from '@/src/entities/lang/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {Product} from '@/src/entities/product/entity';
import type {ProductAttributeValue} from '@/src/entities/product-attribute-value/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {CommitHandler as BaseCommitHandler} from 'service/import/commit-handler';
import {AttributeType} from 'types/attribute';

class CommitHandler extends BaseCommitHandler {
    // Отменять запрос надо с другого соединения
    protected async cancelBackendByPid(pid: number) {
        const queryRunner = await createUnPatchedQueryRunner();
        await queryRunner.query(`SELECT pg_cancel_backend(${pid});`);
        await queryRunner.release();
    }
}

describe('Import commit handler with modifiers', () => {
    let user: User;
    let region: Region;
    let lang: Lang;
    let infoModel: InfoModel;
    let attributes: {
        numberMultiple: Attribute;
        stringMultiple: Attribute;
        multiSelect: Attribute;
    };
    let masterCategory: MasterCategory;
    let rootFrontCategory: FrontCategory;
    let middleFrontCategory: FrontCategory;
    let frontCategories: [FrontCategory, FrontCategory];
    let products: [Product, Product];

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {product: {canEdit: true}}});
        region = await TestFactory.createRegion();
        lang = await TestFactory.createLang({isoCode: 'en'});

        const userId = user.id;
        const regionId = region.id;

        await TestFactory.createLocale({langIds: [lang.id], regionId});

        infoModel = await TestFactory.createInfoModel({userId, regionId});

        const createMultiselectAttribute = async (optionPrefix?: string) => {
            const attribute = await TestFactory.createAttribute({userId, attribute: {type: AttributeType.MULTISELECT}});
            const promises = ['option_1', 'option_2', 'option_3'].map((code) => {
                return TestFactory.createAttributeOption({
                    userId,
                    attributeOption: {code: [optionPrefix, code].filter(Boolean).join('_'), attributeId: attribute.id}
                });
            });
            await Promise.all(promises);
            return attribute;
        };

        attributes = {
            numberMultiple: await TestFactory.createAttribute({
                userId,
                attribute: {type: AttributeType.NUMBER, isArray: true}
            }),
            stringMultiple: await TestFactory.createAttribute({
                userId,
                attribute: {type: AttributeType.STRING, isArray: true}
            }),
            multiSelect: await createMultiselectAttribute()
        };

        await TestFactory.linkAttributesToInfoModel({
            userId,
            infoModelId: infoModel.id,
            attributes: Object.values(attributes)
        });

        masterCategory = await TestFactory.createMasterCategory({userId, regionId, infoModelId: infoModel.id});

        rootFrontCategory = await TestFactory.createFrontCategory({userId, regionId});
        middleFrontCategory = await TestFactory.createFrontCategory({
            userId,
            regionId,
            parentId: rootFrontCategory.id
        });

        frontCategories = await Promise.all([
            TestFactory.createFrontCategory({userId, regionId, parentId: middleFrontCategory.id}),
            TestFactory.createFrontCategory({userId, regionId, parentId: middleFrontCategory.id})
        ]);

        products = await Promise.all([
            await TestFactory.createProduct({userId, regionId, masterCategoryId: masterCategory.id}),
            await TestFactory.createProduct({userId, regionId, masterCategoryId: masterCategory.id})
        ]);

        const productIds = products.map(({id}) => id);

        await TestFactory.linkProductsToFrontCategory({userId, productIds, frontCategoryId: frontCategories[0].id});
        await TestFactory.linkProductsToFrontCategory({userId, productIds, frontCategoryId: frontCategories[1].id});
    });

    async function createProductAttributeValues(attrKeys: Array<keyof typeof attributes>) {
        const productIds = products.map(({id}) => id);

        const createPavPromises: Promise<ProductAttributeValue>[] = [];
        const makePav = (key: keyof typeof attributes, productId: number, value: unknown, langId?: number) => {
            if (attrKeys.includes(key)) {
                createPavPromises.push(
                    TestFactory.createProductAttributeValue({
                        userId: user.id,
                        productId,
                        attributeId: attributes[key].id,
                        value,
                        langId
                    })
                );
            }
        };

        makePav('numberMultiple', productIds[0], [101, 102]);
        makePav('stringMultiple', productIds[0], ['foo1', 'bar1']);
        makePav('multiSelect', productIds[0], ['option_1', 'option_2']);

        makePav('numberMultiple', productIds[1], [201, 202]);
        makePav('stringMultiple', productIds[1], ['foo2', 'bar2']);
        makePav('multiSelect', productIds[1], ['option_1', 'option_2']);

        await Promise.all(createPavPromises);
    }

    it('should save added and subtracted product attributes values', async () => {
        await createProductAttributeValues(['numberMultiple', 'stringMultiple']);

        const content = [
            [
                IDENTIFIER_HEADER,
                `${ADDITION_SYMBOL}${attributes.numberMultiple.code}`,
                `${SUBTRACTION_SYMBOL}${attributes.stringMultiple.code}`
            ],
            [products[0].identifier, '103', 'foo1;bar2'],
            [products[1].identifier, '203', 'foo1;bar2']
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const productAttributeValues1 = sortBy(
            await TestFactory.getProductAttributeValues({productId: products[0].id}),
            'attributeId'
        );

        expect(productAttributeValues1.map((it) => pick(it, 'attributeId', 'productId', 'value'))).toEqual(
            sortBy(
                [
                    {attributeId: attributes.numberMultiple.id, productId: products[0].id, value: [101, 102, 103]},
                    {attributeId: attributes.stringMultiple.id, productId: products[0].id, value: ['bar1']}
                ],
                'attributeId'
            )
        );

        const productAttributeValues2 = sortBy(
            await TestFactory.getProductAttributeValues({productId: products[1].id}),
            'attributeId'
        );

        expect(productAttributeValues2.map((it) => pick(it, 'attributeId', 'productId', 'value'))).toEqual(
            sortBy(
                [
                    {attributeId: attributes.numberMultiple.id, productId: products[1].id, value: [201, 202, 203]},
                    {attributeId: attributes.stringMultiple.id, productId: products[1].id, value: ['foo2']}
                ],
                'attributeId'
            )
        );
    });

    it('should save added and subtracted front categories', async () => {
        const anotherMiddleFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootFrontCategory.id
        });

        const fcToAdd1 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: anotherMiddleFrontCategory.id
        });

        const fcToAdd2 = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: region.id,
            parentId: anotherMiddleFrontCategory.id
        });

        const content = [
            [
                IDENTIFIER_HEADER,
                `${ADDITION_SYMBOL}${FRONT_CATEGORY_HEADER}`,
                `${SUBTRACTION_SYMBOL}${FRONT_CATEGORY_HEADER}`
            ],
            [products[0].identifier, `${fcToAdd1.code};${fcToAdd2.code}`, frontCategories[0].code],
            [products[1].identifier, `${fcToAdd1.code};${fcToAdd2.code}`, frontCategories[1].code]
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const fcs1 = await TestFactory.getFrontCategoryProduct({productId: products[0].id});

        expect(
            fcs1
                .map((it) => pick(it, 'productId', 'frontCategoryId'))
                .sort((a, b) => a.frontCategoryId - b.frontCategoryId)
        ).toEqual([
            {frontCategoryId: frontCategories[1].id, productId: products[0].id},
            {frontCategoryId: fcToAdd1.id, productId: products[0].id},
            {frontCategoryId: fcToAdd2.id, productId: products[0].id}
        ]);

        const fcs2 = await TestFactory.getFrontCategoryProduct({productId: products[1].id});

        expect(
            fcs2
                .map((it) => pick(it, 'productId', 'frontCategoryId'))
                .sort((a, b) => a.frontCategoryId - b.frontCategoryId)
        ).toEqual([
            {frontCategoryId: frontCategories[0].id, productId: products[1].id},
            {frontCategoryId: fcToAdd1.id, productId: products[1].id},
            {frontCategoryId: fcToAdd2.id, productId: products[1].id}
        ]);
    });

    it('should save added and subtracted multiselect product attribute values', async () => {
        await createProductAttributeValues(['multiSelect']);

        const content = [
            [
                IDENTIFIER_HEADER,
                `${SUBTRACTION_SYMBOL}${attributes.multiSelect.code}`,
                `${ADDITION_SYMBOL}${attributes.multiSelect.code}`
            ],
            [products[0].identifier, 'option_1;option_2', 'option_3'],
            [products[1].identifier, 'option_1;option_2', 'option_3']
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const productAttributeValues1 = await TestFactory.getProductAttributeValues({productId: products[0].id});

        expect(productAttributeValues1.map((it) => pick(it, 'attributeId', 'productId', 'value'))).toEqual([
            {
                attributeId: attributes.multiSelect.id,
                productId: products[0].id,
                value: ['option_3']
            }
        ]);

        const productAttributeValues2 = await TestFactory.getProductAttributeValues({productId: products[1].id});

        expect(productAttributeValues2.map((it) => pick(it, 'attributeId', 'productId', 'value'))).toEqual([
            {
                attributeId: attributes.multiSelect.id,
                productId: products[1].id,
                value: ['option_3']
            }
        ]);
    });

    it('should save created products with modifiers columns', async () => {
        const content = [
            [
                MASTER_CATEGORY_HEADER,
                `${ADDITION_SYMBOL}${FRONT_CATEGORY_HEADER}`,
                `${ADDITION_SYMBOL}${attributes.multiSelect.code}`,
                `${SUBTRACTION_SYMBOL}${attributes.multiSelect.code}`
            ],
            [masterCategory.code, frontCategories[0].code, 'option_1', 'option_3'],
            [masterCategory.code, frontCategories[1].code, 'option_2', '']
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const allProducts = await TestFactory.getProducts();
        const oldProductIds = products.map(({id}) => id);
        const newProducts = allProducts.filter(({id}) => !oldProductIds.includes(id));

        expect(newProducts).toHaveLength(2);

        const productAttributeValues1 = await TestFactory.getProductAttributeValues({productId: newProducts[0].id});

        expect(productAttributeValues1.map((it) => pick(it, 'attributeId', 'productId', 'value'))).toEqual([
            {
                attributeId: attributes.multiSelect.id,
                productId: newProducts[0].id,
                value: ['option_1']
            }
        ]);

        const productAttributeValues2 = await TestFactory.getProductAttributeValues({productId: newProducts[1].id});

        expect(productAttributeValues2.map((it) => pick(it, 'attributeId', 'productId', 'value'))).toEqual([
            {
                attributeId: attributes.multiSelect.id,
                productId: newProducts[1].id,
                value: ['option_2']
            }
        ]);

        const fc1 = await TestFactory.getFrontCategoryProduct({productId: newProducts[0].id});
        expect(fc1).toHaveLength(1);

        const fc2 = await TestFactory.getFrontCategoryProduct({productId: newProducts[1].id});
        expect(fc2).toHaveLength(1);
    });
});
