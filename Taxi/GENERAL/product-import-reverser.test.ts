import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {META_PRODUCT_MASTER_CATEGORY_CODE} from '@/src/constants';
import {
    ADDITION_SYMBOL,
    ARRAY_VALUE_DELIMITER,
    FRONT_CATEGORY_HEADER,
    IDENTIFIER_HEADER,
    IS_META_HEADER,
    MASTER_CATEGORY_HEADER,
    STATUS_HEADER,
    SUBTRACTION_SYMBOL
} from '@/src/constants/import';
import type {Attribute} from '@/src/entities/attribute/entity';
import type {AttributeOption} from '@/src/entities/attribute-option/entity';
import type {FrontCategory} from '@/src/entities/front-category/entity';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {Lang} from '@/src/entities/lang/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {Product} from '@/src/entities/product/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {CommitHandler} from 'service/import/commit-handler';
import {ProductImportReverser} from 'service/reverse-import';
import {AttributeType} from 'types/attribute';

describe('Import resolver with modifiers', () => {
    let user: User;
    let region: Region;
    let langs: [Lang, Lang];
    let infoModel: InfoModel;
    let attributes: {
        boolean: Attribute;
        numberSingle: Attribute;
        numberMultiple: Attribute;
        stringSingle: Attribute;
        stringMultiple: Attribute;
        textLocalizable: Attribute;
        select: Attribute;
        multiSelect: Attribute;
    };
    let attributeOptions: {
        select: [AttributeOption, AttributeOption, AttributeOption];
        multiSelect: [AttributeOption, AttributeOption, AttributeOption];
    };
    let rootMasterCategory: MasterCategory;
    let masterCategory: MasterCategory;
    let metaMasterCategory: MasterCategory;
    let rootFrontCategory: FrontCategory;
    let middleFrontCategory: FrontCategory;
    let frontCategories: [FrontCategory, FrontCategory, FrontCategory];
    let products: [Product, Product, Product];

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {product: {canEdit: true}}});
        region = await TestFactory.createRegion();
        langs = await Promise.all([TestFactory.createLang({isoCode: 'en'}), TestFactory.createLang({isoCode: 'ru'})]);

        const userId = user.id;
        const regionId = region.id;

        await TestFactory.createLocale({langIds: [langs[0].id, langs[1].id], regionId});
        infoModel = await TestFactory.createInfoModel({userId, regionId});

        const createAttribute = (attribute: DeepPartial<Attribute>) => TestFactory.createAttribute({userId, attribute});

        attributes = {
            boolean: await createAttribute({type: AttributeType.BOOLEAN}),
            numberSingle: await createAttribute({type: AttributeType.NUMBER}),
            numberMultiple: await createAttribute({type: AttributeType.NUMBER, isArray: true}),
            stringSingle: await createAttribute({type: AttributeType.STRING}),
            stringMultiple: await createAttribute({type: AttributeType.STRING, isArray: true}),
            textLocalizable: await createAttribute({type: AttributeType.TEXT, isValueLocalizable: true}),
            select: await createAttribute({type: AttributeType.SELECT}),
            multiSelect: await createAttribute({type: AttributeType.MULTISELECT})
        };

        const createOption = (attributeOption: DeepPartial<AttributeOption> & Pick<AttributeOption, 'attributeId'>) =>
            TestFactory.createAttributeOption({userId, attributeOption});

        attributeOptions = {
            select: [
                await createOption({code: 'select-option-1', attributeId: attributes.select.id}),
                await createOption({code: 'select-option-2', attributeId: attributes.select.id}),
                await createOption({code: 'select-option-3', attributeId: attributes.select.id})
            ],
            multiSelect: [
                await createOption({code: 'multi-select-option-1', attributeId: attributes.multiSelect.id}),
                await createOption({code: 'multi-select-option-2', attributeId: attributes.multiSelect.id}),
                await createOption({code: 'multi-select-option-3', attributeId: attributes.multiSelect.id})
            ]
        };

        await TestFactory.linkAttributesToInfoModel({
            userId,
            infoModelId: infoModel.id,
            attributes: Object.values(attributes)
        });

        rootMasterCategory = await TestFactory.createMasterCategory({userId, regionId, infoModelId: infoModel.id});
        masterCategory = await TestFactory.createMasterCategory({
            userId,
            regionId,
            infoModelId: infoModel.id,
            parentId: rootMasterCategory.id
        });
        metaMasterCategory = await TestFactory.createMasterCategory({
            userId,
            regionId,
            infoModelId: infoModel.id,
            parentId: rootMasterCategory.id,
            code: META_PRODUCT_MASTER_CATEGORY_CODE
        });

        rootFrontCategory = await TestFactory.createFrontCategory({userId, regionId});
        middleFrontCategory = await TestFactory.createFrontCategory({
            userId,
            regionId,
            parentId: rootFrontCategory.id
        });

        frontCategories = await Promise.all([
            TestFactory.createFrontCategory({userId, regionId, parentId: middleFrontCategory.id, sortOrder: 0}),
            TestFactory.createFrontCategory({userId, regionId, parentId: middleFrontCategory.id, sortOrder: 1}),
            TestFactory.createFrontCategory({userId, regionId, parentId: middleFrontCategory.id, sortOrder: 2})
        ]);

        products = await Promise.all([
            await TestFactory.createProduct({userId, regionId, masterCategoryId: masterCategory.id}),
            await TestFactory.createProduct({userId, regionId, masterCategoryId: masterCategory.id}),
            await TestFactory.createProduct({userId, regionId, masterCategoryId: masterCategory.id})
        ]);

        const productIds = products.map(({id}) => id);

        await TestFactory.linkProductsToFrontCategory({
            userId,
            productIds: [productIds[0], productIds[1]],
            frontCategoryId: frontCategories[0].id
        });

        await TestFactory.linkProductsToFrontCategory({
            userId,
            productIds: [productIds[0], productIds[1]],
            frontCategoryId: frontCategories[1].id
        });

        const createPav = (productId: number, attributeId: number, value: unknown, langId?: number) =>
            TestFactory.createProductAttributeValue({userId, productId, attributeId, value, langId});

        await Promise.all([
            createPav(productIds[0], attributes.boolean.id, true),
            createPav(productIds[0], attributes.numberSingle.id, 1),
            createPav(productIds[0], attributes.numberMultiple.id, [0, 1]),
            createPav(productIds[0], attributes.stringSingle.id, 'string-1'),
            createPav(productIds[0], attributes.stringMultiple.id, ['string-1', 'string-2']),
            createPav(productIds[0], attributes.select.id, 'select-option-1'),
            createPav(productIds[0], attributes.multiSelect.id, ['multi-select-option-1', 'multi-select-option-2']),
            createPav(productIds[0], attributes.textLocalizable.id, 'text-loc-1', langs[0].id),
            createPav(productIds[0], attributes.textLocalizable.id, 'text-loc-2', langs[1].id),

            createPav(productIds[1], attributes.boolean.id, false),
            createPav(productIds[1], attributes.numberSingle.id, 0),
            createPav(productIds[1], attributes.numberMultiple.id, [-1, 0]),
            createPav(productIds[1], attributes.stringSingle.id, 'string-1'),
            createPav(productIds[1], attributes.stringMultiple.id, ['string-1', 'string-2']),
            createPav(productIds[1], attributes.select.id, 'select-option-1'),
            createPav(productIds[1], attributes.multiSelect.id, ['multi-select-option-1', 'multi-select-option-2']),
            createPav(productIds[1], attributes.textLocalizable.id, 'text-loc-1', langs[0].id)
        ]);
    });

    async function createImport(content: (string | number)[][]) {
        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content: content as never});
        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        await commitHandler.handle();
        return importKey;
    }

    async function getImportReverse(stamp: string) {
        const manager = await TestFactory.getManager();
        await TestFactory.dispatchDeferred();
        try {
            const arrayOfArrays = await new ProductImportReverser().initializeEntityManager(manager).reverse(stamp);
            return arrayOfArrays;
        } catch (error) {
            console.log({error: JSON.stringify(error)});
            throw error;
        }
    }

    it('should handle product creation', async () => {
        const content = [
            [MASTER_CATEGORY_HEADER, STATUS_HEADER, attributes.select.code],
            [masterCategory.code, 'active', attributeOptions.select[0].code]
        ];

        const stamp = await createImport(content);
        const arrayOfArrays = await getImportReverse(stamp);
        expect(arrayOfArrays).toEqual([
            [IDENTIFIER_HEADER, attributes.select.code, STATUS_HEADER],
            [expect.stringMatching(/\d+/), attributeOptions.select[0].code, 'disabled']
        ]);
    });

    it('should handle front category product', async () => {
        const existingFcCodes = frontCategories
            .slice(0, 2)
            .map(({code}) => code)
            .join(ARRAY_VALUE_DELIMITER);

        const content = [
            [
                IDENTIFIER_HEADER,
                `${ADDITION_SYMBOL}${FRONT_CATEGORY_HEADER}`,
                `${SUBTRACTION_SYMBOL}${FRONT_CATEGORY_HEADER}`
            ],
            [products[0].identifier, frontCategories[2].code, ''],
            [products[1].identifier, '', frontCategories[1].code],
            [products[2].identifier, existingFcCodes, '']
        ];

        const stamp = await createImport(content);
        const arrayOfArrays = await getImportReverse(stamp);
        expect(arrayOfArrays).toEqual([
            [IDENTIFIER_HEADER, FRONT_CATEGORY_HEADER],
            [String(products[0].identifier), existingFcCodes],
            [String(products[1].identifier), existingFcCodes],
            [String(products[2].identifier), '']
        ]);
    });

    it('should handle product attribute values', async () => {
        const content = [
            [
                IDENTIFIER_HEADER,
                attributes.boolean.code,
                attributes.stringSingle.code,
                `${SUBTRACTION_SYMBOL}${attributes.stringMultiple.code}`,
                attributes.numberSingle.code,
                `${ADDITION_SYMBOL}${attributes.numberMultiple.code}`,
                attributes.select.code,
                attributes.multiSelect.code,
                `${attributes.textLocalizable.code}|${langs[0].isoCode}`,
                `${attributes.textLocalizable.code}|${langs[1].isoCode}`
            ],
            [
                products[0].identifier,
                't',
                'foo-1',
                'string-1',
                100,
                200,
                'select-option-2',
                'multi-select-option-3',
                'bar-1',
                'baz-1'
            ],
            [
                products[1].identifier,
                '',
                'foo-2',
                'string-1',
                100,
                200,
                'select-option-2',
                'multi-select-option-3',
                'bar-2',
                'baz-2'
            ],
            [
                products[2].identifier,
                'f',
                'foo-3',
                'string-1',
                100,
                200,
                'select-option-2',
                'multi-select-option-3',
                'bar-3',
                'baz-3'
            ]
        ];

        const stamp = await createImport(content);
        const arrayOfArrays = await getImportReverse(stamp);
        expect(arrayOfArrays).toEqual([
            expect.arrayContaining([
                IDENTIFIER_HEADER,
                attributes.boolean.code,
                attributes.stringSingle.code,
                attributes.stringMultiple.code,
                attributes.numberSingle.code,
                attributes.numberMultiple.code,
                attributes.select.code,
                attributes.multiSelect.code,
                `${attributes.textLocalizable.code}|${langs[0].isoCode}`,
                `${attributes.textLocalizable.code}|${langs[1].isoCode}`
            ]),
            expect.arrayContaining([
                String(products[0].identifier),
                't',
                'string-1',
                'string-1;string-2',
                '1',
                '0;1',
                'select-option-1',
                'multi-select-option-1;multi-select-option-2',
                'text-loc-1',
                'text-loc-2'
            ]),
            expect.arrayContaining([
                String(products[1].identifier),
                'f',
                'string-1',
                'string-1;string-2',
                '0',
                '-1;0',
                'select-option-1',
                'multi-select-option-1;multi-select-option-2',
                'text-loc-1',
                ''
            ]),
            expect.arrayContaining([String(products[2].identifier), '', '', '', '', '', '', '', '', ''])
        ]);
    });

    it('should handle product master categories', async () => {
        const newMc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: rootMasterCategory.id
        });

        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, attributes.boolean.code, IS_META_HEADER],
            [products[0].identifier, '', 't', ''], // не изменений - не войдет в обратный импорт
            [products[1].identifier, newMc.code, 'f', ''],
            ['', '', 't', 't']
        ];

        const stamp = await createImport(content);
        const arrayOfArrays = await getImportReverse(stamp);
        expect(arrayOfArrays).toEqual([
            [IDENTIFIER_HEADER, attributes.boolean.code, MASTER_CATEGORY_HEADER, STATUS_HEADER],
            [String(products[1].identifier), 'f', masterCategory.code, products[1].status],
            [expect.stringMatching(/\d+/), 't', metaMasterCategory.code, 'disabled']
        ]);
    });

    it('should handle deleted master categories', async () => {
        const newMc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: rootMasterCategory.id
        });

        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER],
            [products[0].identifier, newMc.code],
            [products[1].identifier, newMc.code],
            [products[2].identifier, newMc.code]
        ];

        const stamp = await createImport(content);

        await TestFactory.deleteMasterCategory({userId: user.id, id: masterCategory.id});

        // Если МК удалена, то в обратном импорте останется текущая МК
        const arrayOfArrays = await getImportReverse(stamp);
        expect(arrayOfArrays).toEqual([
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER],
            [String(products[0].identifier), newMc.code],
            [String(products[1].identifier), newMc.code],
            [String(products[2].identifier), newMc.code]
        ]);
    });

    it('should not affect changes made after original import', async () => {
        const content = [
            [IDENTIFIER_HEADER, attributes.stringSingle.code],
            [products[0].identifier, 'foo'],
            [products[1].identifier, 'bar']
        ];

        const stamp = await createImport(content);

        await TestFactory.updateProductAttributeValue({
            userId: user.id,
            productId: products[1].id,
            attributeId: attributes.stringSingle.id,
            volume: {
                value: 'baz'
            }
        });

        const arrayOfArrays = await getImportReverse(stamp);
        expect(arrayOfArrays).toEqual([
            [IDENTIFIER_HEADER, attributes.stringSingle.code],
            [String(products[0].identifier), 'string-1'],
            [String(products[1].identifier), 'baz']
        ]);
    });
});
