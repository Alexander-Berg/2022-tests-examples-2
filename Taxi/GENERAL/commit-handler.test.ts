import {seed, uuid, word} from 'casual';
import {noop, orderBy, pick, sortBy} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {createUnPatchedQueryRunner} from 'tests/unit/setup';
import {TestFactory} from 'tests/unit/test-factory';
import {createMasterCategoryWithInfoModel, createSelectOptions} from 'tests/unit/util';

import {META_PRODUCT_MASTER_CATEGORY_CODE} from '@/src/constants';
import {
    ARRAY_VALUE_DELIMITER,
    FRONT_CATEGORY_HEADER,
    IDENTIFIER_HEADER,
    IS_META_HEADER,
    MASTER_CATEGORY_HEADER,
    STATUS_HEADER
} from '@/src/constants/import';
import {FrontCategoryProduct} from '@/src/entities/front-category-product/entity';
import {ImportSpreadsheet} from '@/src/entities/import-spreadsheet/entity';
import {ProductAttributeValue} from '@/src/entities/product-attribute-value/entity';
import {NonUniqueProductAttributeValue, OperationTimeoutError} from '@/src/errors';
import {ensureConnection} from 'service/db';
import {delayMs} from 'service/helper/delay';
import {CommitHandler as BaseCommitHandler, CommitHandlerOptions} from 'service/import/commit-handler';
import {Resolver, ResolverConstructorOptions} from 'service/import/resolver';
import {logger} from 'service/logger';
import {AttributeType} from 'types/attribute';
import {ImportMode} from 'types/import';
import {ProductStatus} from 'types/product';

seed(3);

class CommitHandler extends BaseCommitHandler {
    // Отменять запрос надо с другого соединения
    protected async cancelBackendByPid(pid: number) {
        const queryRunner = await createUnPatchedQueryRunner();
        await queryRunner.query(`SELECT pg_cancel_backend(${pid});`);
        await queryRunner.release();
    }
}

class SlowCommitHandler extends CommitHandler {
    protected changesStartPromise: Promise<void>;
    protected changesFinishPromise: Promise<void>;

    public async ensureChangesStarted() {
        return this.changesStartPromise;
    }

    public async ensureChangesFinished() {
        return this.changesFinishPromise;
    }

    constructor(options: CommitHandlerOptions, sleepAmount: number) {
        super(options);
        this.changesStartPromise = new Promise((resolve) => {
            this.handleProductAttributeValues = async () => {
                resolve();
                await super.handleProductAttributeValues().catch(noop);
                await this.getEntityManager().query('SELECT pg_sleep($1)', [sleepAmount]);
            };
        });
        this.changesFinishPromise = new Promise((resolve) => {
            this.commit = async (params: {afterCommit: () => void}) => {
                const commitPromise = super.commit(params);
                commitPromise.then(
                    () => resolve(),
                    () => resolve()
                );
                return commitPromise;
            };
        });
    }
}

class UnsafeResolver extends Resolver {
    protected prepareRowsForStore() {
        return this.storeList;
    }
}

class CommitHandlerWithUnsafeResolver extends CommitHandler {
    protected createResolver(params: ResolverConstructorOptions) {
        return new UnsafeResolver(params);
    }
}

describe('import commit handler', () => {
    it('should handle resolve delta', async () => {
        const {user, infoModel, region, masterCategory} = await createMasterCategoryWithInfoModel();
        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'srt_a',
            productId: product.id,
            attributeId: stringAttr.id
        });

        const content = [
            [IDENTIFIER_HEADER, stringAttr.code],
            ['' + product.identifier, 'new_value']
        ];
        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttr.id}]
        });

        const prevResolved = await new Resolver({importKey, authorId: user.id}).handle();
        expect(await new CommitHandler({importKey, authorId: user.id, prevResolved}).handle()).toBeUndefined();

        await TestFactory.updateProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: stringAttr.id,
            volume: {value: 'str_b'}
        });

        expect(await new CommitHandler({importKey, authorId: user.id, prevResolved}).handle()).toEqual({
            delta: {added: {}, deleted: {}, updated: {'1': {columns: {'1': {oldValue: 'str_b'}}}}},
            resolved: [
                [
                    {header: 'id', type: 'identifier'},
                    {header: stringAttr.code, type: 'string'}
                ],
                {
                    action: 'update',
                    columns: [
                        {cast: product.identifier, value: '' + product.identifier},
                        {oldValue: 'str_b', value: 'new_value'}
                    ]
                }
            ]
        });
    });

    it('should save resolved data', async () => {
        const {user, infoModel, region, masterCategory} = await createMasterCategoryWithInfoModel();
        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });
        const ru = await TestFactory.createLang({isoCode: 'ru'});
        const en = await TestFactory.createLang({isoCode: 'en'});
        await TestFactory.createLocale({regionId: region.id, langIds: [ru.id, en.id]});

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isValueLocalizable: true},
            userId: user.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'ru1',
            productId: product.id,
            attributeId: stringAttr.id,
            langId: ru.id
        });
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'en1',
            productId: product.id,
            attributeId: stringAttr.id,
            langId: en.id
        });

        const imageAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.IMAGE},
            userId: user.id
        });
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: '/image1',
            productId: product.id,
            attributeId: imageAttr.id
        });

        const booleanAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.BOOLEAN, isArray: true},
            userId: user.id
        });
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: [true, false],
            productId: product.id,
            attributeId: booleanAttr.id
        });

        const numberAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.NUMBER},
            userId: user.id
        });
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 55,
            productId: product.id,
            attributeId: numberAttr.id
        });

        const multiselectAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.MULTISELECT},
            userId: user.id
        });
        const {optionCodes} = await createSelectOptions({userId: user.id, attributeId: multiselectAttr.id});
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: [optionCodes[0], optionCodes[1]],
            productId: product.id,
            attributeId: multiselectAttr.id
        });

        const importKey = uuid;
        const imgA = await TestFactory.createImportImage({importKey, imageUrl: 'avatars_a', regionId: region.id});
        await TestFactory.createImageCache({url: 'avatars_a'});
        const imgB = await TestFactory.createImportImage({importKey, imageUrl: 'avatars_b', regionId: region.id});
        await TestFactory.createImageCache({url: 'avatars_b'});
        const content = [
            [
                IDENTIFIER_HEADER,
                MASTER_CATEGORY_HEADER,
                `${stringAttr.code}|ru`,
                `${stringAttr.code}|en`,
                imageAttr.code,
                booleanAttr.code,
                numberAttr.code,
                multiselectAttr.code
            ],
            [
                product.identifier,
                masterCategory.code,
                'str_ru_a',
                'str_en_a',
                imgA.relPath,
                'on;да',
                129,
                optionCodes[2]
            ],
            [
                '',
                masterCategory.code,
                'str_ru_b',
                'str_en_b',
                imgB.relPath,
                'off;НЕТ',
                0,
                [optionCodes[1], optionCodes[2]].join(ARRAY_VALUE_DELIMITER)
            ]
        ] as never;
        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [
                {id: stringAttr.id},
                {id: imageAttr.id},
                {id: booleanAttr.id},
                {id: numberAttr.id},
                {id: multiselectAttr.id}
            ]
        });

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const newProductIdentifiers = commitHandler.getNewProductIdentifiers();
        expect(newProductIdentifiers).toHaveLength(1);

        const newProductIds = commitHandler.getNewProductIds();
        expect(newProductIds).toHaveLength(1);
        const newProductId = newProductIds[0];

        const [valuesA, valuesB] = await Promise.all([
            TestFactory.getProductAttributeValues({productId: product.id}),
            TestFactory.getProductAttributeValues({productId: newProductId})
        ]);

        const receivedValuesA = valuesA.map((it) => pick(it, 'attributeId', 'langId', 'productId', 'value'));
        const expectedValuesA = [
            {attributeId: stringAttr.id, langId: ru.id, productId: product.id, value: 'str_ru_a'},
            {attributeId: stringAttr.id, langId: en.id, productId: product.id, value: 'str_en_a'},
            {attributeId: imageAttr.id, langId: null, productId: product.id, value: 'avatars_a'},
            {attributeId: booleanAttr.id, langId: null, productId: product.id, value: [true, true]},
            {attributeId: numberAttr.id, langId: null, productId: product.id, value: 129},
            {attributeId: multiselectAttr.id, langId: null, productId: product.id, value: [optionCodes[2]]}
        ];

        expect(expectedValuesA).toEqual(
            expectedValuesA.map((expected) =>
                receivedValuesA.find((it) => it.attributeId === expected.attributeId && it.langId === expected.langId)
            )
        );

        const receivedValuesB = valuesB.map((it) => pick(it, 'attributeId', 'langId', 'productId', 'value'));
        const expectedValuesB = [
            {attributeId: stringAttr.id, langId: ru.id, productId: newProductId, value: 'str_ru_b'},
            {attributeId: stringAttr.id, langId: en.id, productId: newProductId, value: 'str_en_b'},
            {attributeId: imageAttr.id, langId: null, productId: newProductId, value: 'avatars_b'},
            {attributeId: booleanAttr.id, langId: null, productId: newProductId, value: [false, false]},
            {attributeId: numberAttr.id, langId: null, productId: newProductId, value: 0},
            {
                attributeId: multiselectAttr.id,
                langId: null,
                productId: newProductId,
                value: [optionCodes[1], optionCodes[2]]
            }
        ];

        expect(expectedValuesB).toEqual(
            expectedValuesB.map((expected) =>
                receivedValuesB.find((it) => it.attributeId === expected.attributeId && it.langId === expected.langId)
            )
        );
    });

    it('should save master categories', async () => {
        const {user, infoModel, region, masterCategory: rootMasterCategory} = await createMasterCategoryWithInfoModel();
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });
        const numberAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.NUMBER},
            userId: user.id
        });
        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttr.id}]
        });
        const compatibleInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [stringAttr]
        });
        const incompatibleInfoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [numberAttr]
        });

        const oldMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id
        });
        const compatibleMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id,
            infoModelId: compatibleInfoModel.id
        });
        const incompatibleMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id,
            infoModelId: incompatibleInfoModel.id
        });

        const products = await Promise.all(
            [...Array(2)].map(() =>
                TestFactory.createProduct({
                    userId: user.id,
                    regionId: region.id,
                    masterCategoryId: oldMasterCategory.id
                })
            )
        );

        const importKey = uuid;
        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER],
            [products[0].identifier, compatibleMasterCategory.code],
            [products[1].identifier, incompatibleMasterCategory.code]
        ] as never;
        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        await TestFactory.flushHistory();

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const updatedProducts = await TestFactory.getProducts();
        expect(updatedProducts).toEqual(
            expect.arrayContaining([
                // продукт должен переместиться в совместимую мастер категорию
                expect.objectContaining({id: products[0].id, masterCategoryId: compatibleMasterCategory.id}),
                // продукт должен переместиться в несовместимую мастер категорию
                expect.objectContaining({id: products[1].id, masterCategoryId: incompatibleMasterCategory.id})
            ])
        );

        const history = await TestFactory.dispatchHistory('tableName', 'action', 'oldRow', 'newRow');
        expect(history).toHaveLength(2);
        expect(history).toEqual(
            expect.arrayContaining([
                {
                    action: 'U',
                    tableName: 'product',
                    oldRow: expect.objectContaining({
                        id: String(products[0].id),
                        master_category_id: String(oldMasterCategory.id)
                    }),
                    newRow: expect.objectContaining({
                        id: String(products[0].id),
                        master_category_id: String(compatibleMasterCategory.id)
                    })
                },
                {
                    action: 'U',
                    tableName: 'product',
                    oldRow: expect.objectContaining({
                        id: String(products[1].id),
                        master_category_id: String(oldMasterCategory.id)
                    }),
                    newRow: expect.objectContaining({
                        id: String(products[1].id),
                        master_category_id: String(incompatibleMasterCategory.id)
                    })
                }
            ])
        );
    });

    it('should save front categories', async () => {
        const {user, infoModel, region, masterCategory} = await createMasterCategoryWithInfoModel();
        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const {last: frontCategoryA} = await TestFactory.createNestedFrontCategory({
            authorId: user.id,
            regionId: region.id,
            depth: 3
        });
        const {last: frontCategoryB} = await TestFactory.createNestedFrontCategory({
            authorId: user.id,
            regionId: region.id,
            depth: 3
        });

        await TestFactory.createFrontCategoryProduct({
            userId: user.id,
            productId: product.id,
            frontCategoryId: frontCategoryA.id
        });

        const textAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.TEXT},
            userId: user.id
        });

        const importKey = uuid;
        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, FRONT_CATEGORY_HEADER, textAttr.code],
            [
                product.identifier,
                masterCategory.code,
                [frontCategoryA.code, frontCategoryB.code].join(ARRAY_VALUE_DELIMITER),
                ''
            ],
            ['', masterCategory.code, frontCategoryA.code, '']
        ] as never;
        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: textAttr.id}]
        });

        await TestFactory.flushHistory();

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();
        const newProductId = commitHandler.getNewProductIds()[0];

        const [valuesA, valuesB] = await Promise.all([
            TestFactory.getFrontCategoryProduct({productId: product.id}),
            TestFactory.getFrontCategoryProduct({productId: newProductId})
        ]);

        expect(valuesA.map((it) => pick(it, 'productId', 'frontCategoryId'))).toEqual([
            {frontCategoryId: frontCategoryA.id, productId: product.id},
            {frontCategoryId: frontCategoryB.id, productId: product.id}
        ]);

        expect(valuesB.map((it) => pick(it, 'productId', 'frontCategoryId'))).toEqual([
            {frontCategoryId: frontCategoryA.id, productId: newProductId}
        ]);

        const historyItems = await TestFactory.dispatchHistory('tableName', 'action');
        expect(sortBy(historyItems, ['tableName', 'action'])).toEqual(
            sortBy(
                [
                    {action: 'I', tableName: 'product'},
                    {action: 'I', tableName: 'front_category_product'},
                    {action: 'I', tableName: 'front_category_product'}
                ],
                ['tableName', 'action']
            )
        );
    });

    it('should save statuses', async () => {
        const {user, region, masterCategory} = await createMasterCategoryWithInfoModel();
        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id,
            status: ProductStatus.DISABLED
        });

        const importKey = uuid;
        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, STATUS_HEADER],
            [product.identifier, masterCategory.code, 'active'],
            ['', masterCategory.code, 'active']
        ] as never;
        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const newProductIdentifiers = commitHandler.getNewProductIdentifiers();
        expect(newProductIdentifiers).toHaveLength(1);

        const newProductId = commitHandler.getNewProductIds();
        expect(newProductId).toHaveLength(1);

        const products = await TestFactory.getProducts();
        expect(products).toHaveLength(2);

        products.forEach(({status}) => {
            expect(status).toEqual('active');
        });
    });

    it('should handle clearing volume', async () => {
        const connection = await ensureConnection();
        const {user, infoModel, masterCategory, region} = await createMasterCategoryWithInfoModel();

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: ['old_value'],
            productId: product.id,
            attributeId: stringAttr.id
        });

        // картинки через импорт удалять не надо #doNotDeleteImageViaImport
        const imageAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.IMAGE},
            userId: user.id
        });
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: '/image-old-value',
            productId: product.id,
            attributeId: imageAttr.id
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttr.id}, {id: imageAttr.id}]
        });

        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, stringAttr.code, imageAttr.code],
            [product.identifier, masterCategory.code, '', ''],
            ['', masterCategory.code, '', '']
        ] as never;
        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        const resolver = new Resolver({importKey, prepareForStore: true, authorId: user.id});
        expect(await resolver.handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {header: 'master_category', type: 'masterCategory'},
                {header: stringAttr.code, type: 'string'},
                {header: imageAttr.code, type: 'image'}
            ],
            {
                action: 'update',
                columns: [
                    {cast: product.identifier, value: '' + product.identifier},
                    {cast: masterCategory.code, oldValue: masterCategory.code, value: masterCategory.code},
                    {oldValue: ['old_value'], value: null},
                    {oldValue: '/image-old-value', value: null}
                ]
            },
            {
                action: 'insert',
                columns: [
                    {value: null},
                    {cast: masterCategory.code, value: masterCategory.code},
                    {value: null},
                    {value: null}
                ]
            }
        ]);

        expect(resolver.getStoreList()).toEqual([
            {
                action: 'update',
                masterCategory: masterCategory.code,
                identifier: product.identifier,
                volume: {
                    [stringAttr.code]: null,
                    [imageAttr.code]: '/image-old-value'
                },
                description: {}
            },
            {
                action: 'insert',
                masterCategory: masterCategory.code,
                volume: {
                    [stringAttr.code]: null,
                    [imageAttr.code]: null
                },
                description: {}
            }
        ]);

        expect(await connection.getRepository(ProductAttributeValue).count()).toEqual(2);

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        expect(await connection.getRepository(ProductAttributeValue).count()).toEqual(1);
    });

    it('should handle clearing front category', async () => {
        const connection = await ensureConnection();
        const {user, infoModel, masterCategory, region} = await createMasterCategoryWithInfoModel();

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });
        const stringAttrValue = await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: ['old_value'],
            productId: product.id,
            attributeId: stringAttr.id
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttr.id}]
        });

        const {last: frontCategory} = await TestFactory.createNestedFrontCategory({
            authorId: user.id,
            regionId: region.id,
            depth: 3
        });

        await TestFactory.createFrontCategoryProduct({
            userId: user.id,
            productId: product.id,
            frontCategoryId: frontCategory.id
        });

        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, FRONT_CATEGORY_HEADER],
            [product.identifier, masterCategory.code, ''],
            ['', masterCategory.code, '']
        ] as never;
        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        const resolver = new Resolver({importKey, prepareForStore: true, authorId: user.id});
        expect(await resolver.handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {header: 'master_category', type: 'masterCategory'},
                {header: 'front_category', type: 'frontCategory'}
            ],
            {
                action: 'update',
                columns: [
                    {cast: product.identifier, value: '' + product.identifier},
                    {cast: masterCategory.code, oldValue: masterCategory.code, value: masterCategory.code},
                    {oldValue: [frontCategory.code], value: null}
                ]
            },
            {
                action: 'insert',
                columns: [{value: null}, {cast: masterCategory.code, value: masterCategory.code}, {value: null}]
            }
        ]);

        expect(resolver.getStoreList()).toEqual([
            {
                action: 'update',
                masterCategory: masterCategory.code,
                identifier: product.identifier,
                volume: {},
                description: {}
            },
            {action: 'insert', masterCategory: masterCategory.code, volume: {}, description: {}}
        ]);

        expect(await connection.getRepository(FrontCategoryProduct).count()).toEqual(1);

        await TestFactory.flushHistory();

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        expect(await connection.getRepository(FrontCategoryProduct).count()).toEqual(0);

        const values = await TestFactory.getProductAttributeValues({productId: product.id});
        expect(values).toHaveLength(1);
        expect(pick(values[0], 'id', 'value', 'attributeId', 'productId')).toEqual({
            attributeId: stringAttr.id,
            id: stringAttrValue.id,
            productId: product.id,
            value: ['old_value']
        });

        expect(orderBy(await TestFactory.dispatchHistory('tableName', 'action'), (a) => a.action, 'desc')).toEqual([
            {action: 'I', tableName: 'product'},
            {action: 'D', tableName: 'front_category_product'}
        ]);
    });

    it('should handle large data volumes', async () => {
        const attributesCount = 100;
        const rowsCount = 100;

        jest.setTimeout(Math.min(rowsCount * 200, 120000));

        const {user, infoModel, region, masterCategory} = await createMasterCategoryWithInfoModel();
        const {raw} = await TestFactory.createAttributes({
            count: attributesCount,
            authorId: user.id,
            type: AttributeType.STRING
        });

        expect(raw).toHaveLength(attributesCount);

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: raw.map(({id}: {id: number}) => ({id}))
        });

        const content = [[MASTER_CATEGORY_HEADER, ...raw.map(({code}: {code: string}) => code)]];
        for (let i = 0; i < rowsCount; i++) {
            content.push([masterCategory.code, ...raw.map(() => word)]);
        }

        const importKey = uuid;
        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const connection = await ensureConnection();
        expect(await connection.getRepository(ProductAttributeValue).count()).toEqual(attributesCount * rowsCount);
    });

    it('should handle front categories clearing', async () => {
        const {user, infoModel, region, masterCategory} = await createMasterCategoryWithInfoModel();
        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const {last: frontCategory} = await TestFactory.createNestedFrontCategory({
            authorId: user.id,
            regionId: region.id,
            depth: 3
        });
        await TestFactory.createFrontCategoryProduct({
            userId: user.id,
            productId: product.id,
            frontCategoryId: frontCategory.id
        });

        const textAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.TEXT},
            userId: user.id
        });
        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: textAttr.id}]
        });

        let importKey = uuid;
        let content = [
            [IDENTIFIER_HEADER, textAttr.code],
            [product.identifier, 'foo']
        ] as never;
        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        let crossValues = await TestFactory.getFrontCategoryProduct({productId: product.id});
        expect(crossValues).toHaveLength(1);

        let commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        crossValues = await TestFactory.getFrontCategoryProduct({productId: product.id});
        expect(crossValues).toHaveLength(1);

        let values = await TestFactory.getProductAttributeValues({productId: product.id});
        expect(values).toHaveLength(1);

        importKey = uuid;
        content = [
            [IDENTIFIER_HEADER, FRONT_CATEGORY_HEADER],
            [product.identifier, '']
        ] as never;
        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        crossValues = await TestFactory.getFrontCategoryProduct({productId: product.id});
        expect(crossValues).toHaveLength(0);

        values = await TestFactory.getProductAttributeValues({productId: product.id});
        expect(values).toHaveLength(1);
    });

    it('should save completed import payload', async () => {
        const connection = await ensureConnection();
        const {user, infoModel, masterCategory, region} = await createMasterCategoryWithInfoModel();
        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttr.id}]
        });

        const importKey = uuid;
        const content = [
            [MASTER_CATEGORY_HEADER, IDENTIFIER_HEADER, stringAttr.code],
            [masterCategory.code, '', 'foo'],
            [masterCategory.code, product.identifier, 'foo']
        ] as never;

        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const newProductIdentifiers = commitHandler.getNewProductIdentifiers();
        expect(newProductIdentifiers).toHaveLength(1);

        const [newProductIdentifier] = newProductIdentifiers;
        expect(newProductIdentifier).toBeGreaterThan(0);

        const updatedProductIdentifiers = commitHandler.getUpdatedProductIdentifiers();
        expect(updatedProductIdentifiers).toEqual([product.identifier]);

        const {result} = (await connection.getRepository(ImportSpreadsheet).findOne({where: {importKey}})) ?? {};
        expect(JSON.parse(result ?? '')).toEqual({newProductIdentifiers, updatedProductIdentifiers});
    });

    it('should update only modified statuses', async () => {
        const {user, infoModel, masterCategory, region} = await createMasterCategoryWithInfoModel();
        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id,
            status: ProductStatus.ACTIVE
        });

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });
        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttr.id}]
        });

        const importKey = uuid;
        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, STATUS_HEADER, stringAttr.code],
            [product.identifier, masterCategory.code, 'active', 'foo'],
            ['', masterCategory.code, 'active', 'bar']
        ] as never;
        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        await TestFactory.flushHistory();

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        expect(await TestFactory.dispatchHistory('tableName', 'action')).toEqual([
            {tableName: 'product', action: 'I'},
            {tableName: 'product_attribute_value', action: 'I'},
            {tableName: 'product_attribute_value', action: 'I'}
        ]);
    });

    it('should update only modified product attribute values', async () => {
        const {user, infoModel, masterCategory, region} = await createMasterCategoryWithInfoModel();
        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id,
            status: ProductStatus.ACTIVE
        });

        const fr = await TestFactory.createLang({isoCode: 'fr'});
        const en = await TestFactory.createLang({isoCode: 'en'});
        await TestFactory.createLocale({regionId: region.id, langIds: [fr.id, en.id]});

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isValueLocalizable: true},
            userId: user.id
        });
        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttr.id}]
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'foo',
            productId: product.id,
            attributeId: stringAttr.id,
            langId: fr.id
        });
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'bar',
            productId: product.id,
            attributeId: stringAttr.id,
            langId: en.id
        });

        let importKey = uuid;
        let content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, `${stringAttr.code}|fr`, `${stringAttr.code}|en`],
            [product.identifier, masterCategory.code, 'foo', ''],
            ['', masterCategory.code, 'baz', 'qux']
        ] as never;
        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        await TestFactory.flushHistory();

        let commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const history = await TestFactory.dispatchHistory('id', 'tableName', 'action');
        expect(history.sort((a, b) => a.id - b.id).map(({action, tableName}) => ({action, tableName}))).toEqual([
            {action: 'I', tableName: 'product'},
            {action: 'D', tableName: 'product_attribute_value'},
            {action: 'I', tableName: 'product_attribute_value'},
            {action: 'I', tableName: 'product_attribute_value'}
        ]);

        const [newProductId] = commitHandler.getNewProductIds();
        expect(newProductId).toBeGreaterThan(0);

        const [valuesA, valuesB] = await Promise.all([
            TestFactory.getProductAttributeValues({productId: product.id}),
            TestFactory.getProductAttributeValues({productId: newProductId})
        ]);

        expect(valuesA.map((it) => pick(it, 'attributeId', 'langId', 'productId', 'value'))).toEqual([
            {attributeId: stringAttr.id, langId: fr.id, productId: product.id, value: 'foo'}
        ]);

        expect(
            orderBy(
                valuesB.map((it) => pick(it, 'attributeId', 'langId', 'productId', 'value')),
                'value'
            )
        ).toEqual([
            {attributeId: stringAttr.id, langId: fr.id, productId: newProductId, value: 'baz'},
            {attributeId: stringAttr.id, langId: en.id, productId: newProductId, value: 'qux'}
        ]);

        importKey = uuid;
        content = [
            [IDENTIFIER_HEADER, `${stringAttr.code}|fr`, `${stringAttr.code}|en`],
            [product.identifier, 'baz', 'qux']
        ] as never;
        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        await TestFactory.flushHistory();

        commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        expect(await TestFactory.dispatchHistory('tableName', 'action')).toEqual([
            {action: 'U', tableName: 'product_attribute_value'},
            {action: 'I', tableName: 'product_attribute_value'}
        ]);

        const values = await TestFactory.getProductAttributeValues({productId: product.id});

        expect(
            orderBy(
                values.map((it) => pick(it, 'attributeId', 'langId', 'productId', 'value')),
                'value'
            )
        ).toEqual([
            {attributeId: stringAttr.id, langId: fr.id, productId: product.id, value: 'baz'},
            {attributeId: stringAttr.id, langId: en.id, productId: product.id, value: 'qux'}
        ]);
    });

    it('should stop applying changes after lock timeout', async () => {
        const {user, infoModel, region, masterCategory} = await createMasterCategoryWithInfoModel();
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [stringAttr]
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            regionId: region.id,
            masterCategoryId: masterCategory.id
        });

        const importKey = uuid;
        const content = [
            [IDENTIFIER_HEADER, `${stringAttr.code}`],
            [String(product.identifier), 'foo']
        ];
        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        await TestFactory.flushHistory();

        const loggerMock = jest.spyOn(logger, 'error').mockImplementation(() => undefined);
        const commitHandler = new SlowCommitHandler({importKey, authorId: user.id}, 0.25 /* 250ms */);
        jest.useFakeTimers();
        const handlePromise = commitHandler.handle();
        await commitHandler.ensureChangesStarted();
        jest.runAllTimers();
        jest.useRealTimers();
        await expect(handlePromise).rejects.toThrow(OperationTimeoutError);
        await commitHandler.ensureChangesFinished();
        loggerMock.mockClear();

        await expect(TestFactory.getProductAttributeValues({productId: product.id})).resolves.toHaveLength(0);
        await expect(TestFactory.dispatchHistory('tableName')).resolves.toHaveLength(0);
    });

    it('should update affected products revisions', async () => {
        const {user, region, masterCategory} = await createMasterCategoryWithInfoModel();
        const product1 = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id,
            status: ProductStatus.DISABLED
        });
        const product2 = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id,
            status: ProductStatus.ACTIVE
        });

        const hsBefore1 = await TestFactory.getHistorySubject(product1.historySubjectId);
        const hsBefore2 = await TestFactory.getHistorySubject(product2.historySubjectId);
        await delayMs(200);

        const importKey = uuid;
        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, STATUS_HEADER],
            [product1.identifier, masterCategory.code, 'active'],
            [product2.identifier, masterCategory.code, 'active']
        ] as never;
        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const hsAfter1 = await TestFactory.getHistorySubject(product1.historySubjectId);
        const hsAfter2 = await TestFactory.getHistorySubject(product2.historySubjectId);

        expect(hsBefore1.updatedAt.getTime()).toBeLessThan(hsAfter1.updatedAt.getTime());
        expect(hsBefore1.revision).toBeLessThan(hsAfter1.revision);

        expect(hsBefore2.updatedAt.getTime()).toEqual(hsAfter2.updatedAt.getTime());
        expect(hsBefore2.revision).toEqual(hsAfter2.revision);
    });

    it('should handle values with control symbols', async () => {
        const {user, region, masterCategory, infoModel} = await createMasterCategoryWithInfoModel();

        const textAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.TEXT},
            userId: user.id
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [textAttr]
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id,
            status: ProductStatus.DISABLED
        });

        // eslint-disable-next-line
        const controlCharText = '"foo" \t \'bar\' \\t `baz` \n «qwe» \\n rty \N asd \\N zxc';

        const importKey = uuid;
        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, textAttr.code],
            [product.identifier, masterCategory.code, controlCharText],
            ['', masterCategory.code, controlCharText]
        ] as never;
        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const products = await TestFactory.getProducts();
        expect(products).toHaveLength(2);

        const productAttributeValues = (
            await Promise.all(products.map(({id}) => TestFactory.getProductAttributeValues({productId: id})))
        ).flat();

        expect(productAttributeValues.every(({value}) => value === controlCharText)).toBeTruthy();
    });

    it('should throw on non unique product attribute values', async () => {
        const {user, region, masterCategory, infoModel} = await createMasterCategoryWithInfoModel();

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        const uniqueAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isUnique: true},
            userId: user.id
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [stringAttr, uniqueAttr]
        });

        const product1 = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id,
            status: ProductStatus.ACTIVE
        });

        const product2 = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id,
            status: ProductStatus.ACTIVE
        });

        const importKey = uuid;
        const content = [
            [IDENTIFIER_HEADER, stringAttr.code, uniqueAttr.code],
            [String(product1.identifier), 'foo', 'bar'],
            [String(product2.identifier), 'foo', 'bar']
        ] as never;
        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        const commitHandler = new CommitHandlerWithUnsafeResolver({importKey, authorId: user.id});
        await expect(commitHandler.handle()).rejects.toThrow(NonUniqueProductAttributeValue);
    });

    it('should ignore invalid product attribute values', async () => {
        const {user, region, masterCategory, infoModel} = await createMasterCategoryWithInfoModel();

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, properties: {min: 1, max: 3}},
            userId: user.id
        });

        const selectAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.SELECT},
            userId: user.id
        });

        const {optionCodes} = await createSelectOptions({userId: user.id, attributeId: selectAttr.id});

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [stringAttr, selectAttr]
        });

        const product1 = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id,
            status: ProductStatus.ACTIVE
        });

        const product2 = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id,
            status: ProductStatus.ACTIVE
        });

        const importKey = uuid;
        const content = [
            [IDENTIFIER_HEADER, stringAttr.code, selectAttr.code],
            [String(product1.identifier), 'foo', optionCodes[0]],
            [String(product2.identifier), 'foo_bar', 'baz']
        ] as never;

        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});
        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const productAttributeValues1 = await TestFactory.getProductAttributeValues({productId: product1.id});
        expect(productAttributeValues1).toHaveLength(2);
        const productAttributeValues2 = await TestFactory.getProductAttributeValues({productId: product2.id});
        expect(productAttributeValues2).toHaveLength(0);
    });

    it('should save meta property', async () => {
        const {user, region, masterCategory: rootMasterCategory, infoModel} = await createMasterCategoryWithInfoModel();

        const metaMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id,
            infoModelId: infoModel.id,
            code: META_PRODUCT_MASTER_CATEGORY_CODE
        });

        const product1 = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: metaMasterCategory.id,
            regionId: region.id,
            status: ProductStatus.ACTIVE,
            isMeta: true
        });

        const importKey = uuid;

        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, IS_META_HEADER],
            [product1.identifier, '', 't'],
            ['', '', 't']
        ] as never;

        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const newProductIdentifiers = commitHandler.getNewProductIdentifiers();
        expect(newProductIdentifiers).toHaveLength(1);

        const newProductId = commitHandler.getNewProductIds();
        expect(newProductId).toHaveLength(1);

        const products = await TestFactory.getProducts();
        expect(products).toHaveLength(2);

        products.forEach(({isMeta}) => {
            expect(isMeta).toBeTruthy();
        });
    });

    it('should confirm values correctly', async () => {
        const {user, region, masterCategory} = await createMasterCategoryWithInfoModel();

        const ru = await TestFactory.createLang({isoCode: 'ru'});
        const en = await TestFactory.createLang({isoCode: 'en'});
        await TestFactory.createLocale({regionId: region.id, langIds: [ru.id, en.id]});

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id,
            status: ProductStatus.ACTIVE
        });

        const booleanAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.BOOLEAN, isConfirmable: true},
            userId: user.id
        });

        const booleanValue = await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: false,
            productId: product.id,
            attributeId: booleanAttr.id
        });

        const localizedAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isConfirmable: true, isValueLocalizable: true},
            userId: user.id
        });

        const ruValue = await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'old_ru',
            productId: product.id,
            attributeId: localizedAttr.id,
            langId: ru.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'old_en',
            productId: product.id,
            attributeId: localizedAttr.id,
            langId: en.id
        });

        const importKey = uuid;

        const content = [
            [IDENTIFIER_HEADER, booleanAttr.code, `${localizedAttr.code}|ru`],
            [product.identifier, 't', 'old_ru']
        ] as never;

        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content, mode: ImportMode.CONFIRM});

        await TestFactory.flushHistory();

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const updatedProductIdentifiers = commitHandler.getUpdatedProductIdentifiers();
        expect(updatedProductIdentifiers).toHaveLength(1);

        const history = await TestFactory.dispatchHistory('tableName', 'action', 'oldRow', 'newRow');
        expect(history).toHaveLength(2);
        expect(history).toEqual(
            expect.arrayContaining([
                {
                    action: 'U',
                    tableName: 'product_attribute_value',
                    oldRow: expect.objectContaining({
                        id: String(booleanValue.id),
                        value_boolean: '{f}',
                        is_confirmed: 'f'
                    }),
                    newRow: expect.objectContaining({
                        id: String(booleanValue.id),
                        value_boolean: '{t}',
                        is_confirmed: 't'
                    })
                },
                {
                    action: 'U',
                    tableName: 'product_attribute_value',
                    oldRow: expect.objectContaining({
                        id: String(ruValue.id),
                        value_text: '{old_ru}',
                        is_confirmed: 'f'
                    }),
                    newRow: expect.objectContaining({
                        id: String(ruValue.id),
                        value_text: '{old_ru}',
                        is_confirmed: 't'
                    })
                }
            ])
        );
    });

    it('should erase confirmed from values correctly', async () => {
        const {user, region, masterCategory} = await createMasterCategoryWithInfoModel();

        const ru = await TestFactory.createLang({isoCode: 'ru'});
        const en = await TestFactory.createLang({isoCode: 'en'});
        await TestFactory.createLocale({regionId: region.id, langIds: [ru.id, en.id]});

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id,
            status: ProductStatus.ACTIVE
        });

        const booleanAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.BOOLEAN, isConfirmable: true},
            userId: user.id
        });

        const booleanValue = await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: false,
            productId: product.id,
            attributeId: booleanAttr.id,
            isConfirmed: true
        });

        const localizedAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isConfirmable: true, isValueLocalizable: true},
            userId: user.id
        });

        const ruValue = await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'old_ru',
            productId: product.id,
            attributeId: localizedAttr.id,
            langId: ru.id,
            isConfirmed: true
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'old_en',
            productId: product.id,
            attributeId: localizedAttr.id,
            langId: en.id
        });

        const importKey = uuid;

        const content = [
            [IDENTIFIER_HEADER, booleanAttr.code, `${localizedAttr.code}|ru`],
            [product.identifier, 'f', 'new_ru']
        ] as never;

        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content, mode: ImportMode.DECLINE});

        await TestFactory.flushHistory();

        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();

        const updatedProductIdentifiers = commitHandler.getUpdatedProductIdentifiers();
        expect(updatedProductIdentifiers).toHaveLength(1);

        const history = await TestFactory.dispatchHistory('tableName', 'action', 'oldRow', 'newRow');
        expect(history).toHaveLength(2);
        expect(history).toEqual(
            expect.arrayContaining([
                {
                    action: 'U',
                    tableName: 'product_attribute_value',
                    oldRow: expect.objectContaining({
                        id: String(booleanValue.id),
                        value_boolean: '{f}',
                        is_confirmed: 't'
                    }),
                    newRow: expect.objectContaining({
                        id: String(booleanValue.id),
                        value_boolean: '{f}',
                        is_confirmed: 'f'
                    })
                },
                {
                    action: 'U',
                    tableName: 'product_attribute_value',
                    oldRow: expect.objectContaining({
                        id: String(ruValue.id),
                        value_text: '{old_ru}',
                        is_confirmed: 't'
                    }),
                    newRow: expect.objectContaining({
                        id: String(ruValue.id),
                        value_text: '{new_ru}',
                        is_confirmed: 'f'
                    })
                }
            ])
        );
    });
});
