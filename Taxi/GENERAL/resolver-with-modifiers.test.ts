import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {
    ADDITION_SYMBOL,
    ARRAY_VALUE_DELIMITER,
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
import {
    DisallowedImportSpreadsheetModifiersNotOnMultipleAttribute,
    DisallowedImportSpreadsheetModifiersWithRegularColumns,
    DisallowedNonUniqueImportSpreadsheetModifiers,
    ExactImportSpreadsheetProductVolume
} from '@/src/errors';
import {Resolver} from 'service/import/resolver';
import {AttributeType} from 'types/attribute';

describe('Import resolver with modifiers', () => {
    let user: User;
    let region: Region;
    let lang: Lang;
    let infoModel: InfoModel;
    let attributes: {
        numberSingle: Attribute;
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
            numberSingle: await TestFactory.createAttribute({userId, attribute: {type: AttributeType.NUMBER}}),
            numberMultiple: await TestFactory.createAttribute({
                userId,
                attribute: {type: AttributeType.NUMBER, isArray: true}
            }),
            stringMultiple: await TestFactory.createAttribute({
                userId,
                attribute: {type: AttributeType.STRING, isArray: true}
            }),
            multiSelect: await createMultiselectAttribute('multiselect')
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

        const createPavPromises: Promise<ProductAttributeValue>[] = [];
        const makePav = (productId: number, attributeId: number, value: unknown, langId?: number) =>
            createPavPromises.push(
                TestFactory.createProductAttributeValue({userId, productId, attributeId, value, langId})
            );

        makePav(productIds[0], attributes.numberSingle.id, 100);
        makePav(productIds[0], attributes.numberMultiple.id, [101, 102]);
        makePav(productIds[0], attributes.stringMultiple.id, ['foo1', 'bar1']);
        makePav(productIds[0], attributes.multiSelect.id, ['multiselect_option_1']);

        makePav(productIds[1], attributes.numberSingle.id, 200);
        makePav(productIds[1], attributes.numberMultiple.id, [201, 202]);
        makePav(productIds[1], attributes.stringMultiple.id, ['foo2', 'bar2']);
        makePav(productIds[1], attributes.multiSelect.id, ['multiselect_option_2']);

        await Promise.all(createPavPromises);
    });

    it('Should add and subtract values to multiple attribute if special control symbol specified', async () => {
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

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {header: attributes.numberMultiple.code, type: 'number'},
                {header: attributes.stringMultiple.code, type: 'string'}
            ],
            {
                action: 'update',
                columns: [
                    {cast: products[0].identifier, value: `${products[0].identifier}`},
                    {oldValue: [101, 102], cast: [101, 102, 103], value: '101;102;103'},
                    {oldValue: ['foo1', 'bar1'], cast: ['bar1'], value: 'bar1'}
                ]
            },
            {
                action: 'update',
                columns: [
                    {cast: products[1].identifier, value: `${products[1].identifier}`},
                    {oldValue: [201, 202], cast: [201, 202, 203], value: '201;202;203'},
                    {oldValue: ['foo2', 'bar2'], cast: ['foo2'], value: 'foo2'}
                ]
            }
        ]);
    });

    it('Should throw if more than one multiplier supplied for same attribute', async () => {
        const content = [
            [
                IDENTIFIER_HEADER,
                `${ADDITION_SYMBOL}${attributes.numberMultiple.code}`,
                `${ADDITION_SYMBOL}${attributes.numberMultiple.code}`
            ],
            [products[0].identifier, '103', '104'],
            [products[1].identifier, '203', '204']
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        const expectedCellError = new DisallowedNonUniqueImportSpreadsheetModifiers({
            modifier: ADDITION_SYMBOL
        }).toFlatArray();

        const expectedRowError = [new ExactImportSpreadsheetProductVolume().toFlatArray()].flat();

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {
                    header: `${ADDITION_SYMBOL}${attributes.numberMultiple.code}`,
                    error: expectedCellError
                },
                {
                    header: `${ADDITION_SYMBOL}${attributes.numberMultiple.code}`,
                    error: expectedCellError
                }
            ],
            {
                columns: [
                    {cast: products[0].identifier, value: `${products[0].identifier}`},
                    {value: '103', error: expectedCellError},
                    {value: '104', error: expectedCellError}
                ],
                error: expectedRowError
            },
            {
                columns: [
                    {cast: products[1].identifier, value: `${products[1].identifier}`},
                    {value: '203', error: expectedCellError},
                    {value: '204', error: expectedCellError}
                ],
                error: expectedRowError
            }
        ]);
    });

    it('Should throw if regular column and column with modifier supplied', async () => {
        const content = [
            [
                IDENTIFIER_HEADER,
                `${ADDITION_SYMBOL}${attributes.numberMultiple.code}`,
                attributes.numberMultiple.code,
                attributes.numberSingle.code
            ],
            [products[0].identifier, '666', '777', '888'],
            [products[1].identifier, '666', '777', '888']
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        const expectedCellError = new DisallowedImportSpreadsheetModifiersWithRegularColumns().toFlatArray();

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {
                    header: `${ADDITION_SYMBOL}${attributes.numberMultiple.code}`,
                    error: expectedCellError
                },
                {
                    header: attributes.numberMultiple.code,
                    type: 'number'
                },
                {header: attributes.numberSingle.code, type: 'number'}
            ],
            {
                action: 'update',
                columns: [
                    {cast: products[0].identifier, value: `${products[0].identifier}`},
                    {value: '666', error: expectedCellError},
                    {oldValue: [101, 102], cast: [777], value: '777'},
                    {oldValue: 100, cast: 888, value: '888'}
                ]
            },
            {
                action: 'update',
                columns: [
                    {cast: products[1].identifier, value: `${products[1].identifier}`},
                    {value: '666', error: expectedCellError},
                    {oldValue: [201, 202], cast: [777], value: '777'},
                    {oldValue: 200, cast: 888, value: '888'}
                ]
            }
        ]);
    });

    it('Should throw if modifier applied not to multiple attribute', async () => {
        const content = [
            [
                IDENTIFIER_HEADER,
                `${ADDITION_SYMBOL}${attributes.numberSingle.code}`,
                `${SUBTRACTION_SYMBOL}${attributes.stringMultiple.code}`
            ],
            [products[0].identifier, '666', 'baz'],
            [products[1].identifier, '666', 'baz']
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        const expectedCellError = new DisallowedImportSpreadsheetModifiersNotOnMultipleAttribute().toFlatArray();

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {
                    header: `${ADDITION_SYMBOL}${attributes.numberSingle.code}`,
                    error: expectedCellError
                },
                {
                    header: attributes.stringMultiple.code,
                    type: 'string'
                }
            ],
            {
                error: new ExactImportSpreadsheetProductVolume().toFlatArray(),
                columns: [
                    {cast: products[0].identifier, value: `${products[0].identifier}`},
                    {value: '666', error: expectedCellError},
                    {oldValue: ['foo1', 'bar1'], cast: ['foo1', 'bar1'], value: 'foo1;bar1'}
                ]
            },
            {
                error: new ExactImportSpreadsheetProductVolume().toFlatArray(),
                columns: [
                    {cast: products[1].identifier, value: `${products[1].identifier}`},
                    {value: '666', error: expectedCellError},
                    {oldValue: ['foo2', 'bar2'], cast: ['foo2', 'bar2'], value: 'foo2;bar2'}
                ]
            }
        ]);
    });

    it('Should handle front categories', async () => {
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
            [products[1].identifier, `${fcToAdd1.code};${fcToAdd2.code}`, frontCategories[0].code]
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        const expectedOldFrontCategories = [frontCategories[0].code, frontCategories[1].code].sort();

        const expectedFrontCategories = [frontCategories[1].code, fcToAdd1.code, fcToAdd2.code].sort();

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {
                    header: FRONT_CATEGORY_HEADER,
                    type: 'frontCategory'
                }
            ],
            {
                action: 'update',
                columns: [
                    {cast: products[0].identifier, value: `${products[0].identifier}`},
                    {
                        oldValue: expectedOldFrontCategories,
                        cast: expectedFrontCategories,
                        value: expectedFrontCategories.join(ARRAY_VALUE_DELIMITER)
                    }
                ]
            },
            {
                action: 'update',
                columns: [
                    {cast: products[1].identifier, value: `${products[1].identifier}`},
                    {
                        oldValue: expectedOldFrontCategories,
                        cast: expectedFrontCategories,
                        value: expectedFrontCategories.join(ARRAY_VALUE_DELIMITER)
                    }
                ]
            }
        ]);
    });

    it('Should merge modifier columns on same attribute', async () => {
        const content = [
            [
                IDENTIFIER_HEADER,
                `${ADDITION_SYMBOL}${attributes.multiSelect.code}`,
                `${SUBTRACTION_SYMBOL}${attributes.multiSelect.code}`,
                `${ADDITION_SYMBOL}${attributes.numberMultiple.code}`,
                `${SUBTRACTION_SYMBOL}${attributes.numberMultiple.code}`
            ],
            [products[0].identifier, 'multiselect_option_3', 'multiselect_option_1;multiselect_option_2', '103', '101'],
            [products[1].identifier, 'multiselect_option_3', 'multiselect_option_2;multiselect_option_2', '203', '201']
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {
                    header: attributes.multiSelect.code,
                    type: 'multiselect'
                },
                {
                    header: attributes.numberMultiple.code,
                    type: 'number'
                }
            ],
            {
                action: 'update',
                columns: [
                    {cast: products[0].identifier, value: `${products[0].identifier}`},
                    {
                        oldValue: ['multiselect_option_1'],
                        cast: ['multiselect_option_3'],
                        value: 'multiselect_option_3'
                    },
                    {
                        oldValue: [101, 102],
                        cast: [102, 103],
                        value: '102;103'
                    }
                ]
            },
            {
                action: 'update',
                columns: [
                    {cast: products[1].identifier, value: `${products[1].identifier}`},
                    {
                        oldValue: ['multiselect_option_2'],
                        cast: ['multiselect_option_3'],
                        value: 'multiselect_option_3'
                    },
                    {
                        oldValue: [201, 202],
                        cast: [202, 203],
                        value: '202;203'
                    }
                ]
            }
        ]);
    });

    it('Should handle empty product attribute value', async () => {
        const anotherMultipleNumberAttribute1 = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.NUMBER, isArray: true}
        });

        const anotherMultipleNumberAttribute2 = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.NUMBER, isArray: true}
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [anotherMultipleNumberAttribute1, anotherMultipleNumberAttribute2]
        });

        const content = [
            [
                IDENTIFIER_HEADER,
                `${ADDITION_SYMBOL}${anotherMultipleNumberAttribute1.code}`,
                `${SUBTRACTION_SYMBOL}${anotherMultipleNumberAttribute2.code}`
            ],
            [products[0].identifier, '666;777', '888;999']
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {
                    header: anotherMultipleNumberAttribute1.code,
                    type: 'number'
                },
                {
                    header: anotherMultipleNumberAttribute2.code,
                    type: 'number'
                }
            ],
            {
                action: 'update',
                columns: [
                    {cast: products[0].identifier, value: `${products[0].identifier}`},
                    {
                        cast: [666, 777],
                        value: '666;777'
                    },
                    {
                        value: null
                    }
                ]
            }
        ]);
    });

    it('Should handle empty modifier cell', async () => {
        const content = [
            [
                IDENTIFIER_HEADER,
                `${ADDITION_SYMBOL}${attributes.numberMultiple.code}`,
                `${SUBTRACTION_SYMBOL}${attributes.stringMultiple.code}`
            ],
            [products[0].identifier, '', '']
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {
                    header: attributes.numberMultiple.code,
                    type: 'number'
                },
                {
                    header: attributes.stringMultiple.code,
                    type: 'string'
                }
            ],
            {
                error: new ExactImportSpreadsheetProductVolume().toFlatArray(),
                columns: [
                    {cast: products[0].identifier, value: `${products[0].identifier}`},
                    {
                        oldValue: [101, 102],
                        cast: [101, 102],
                        value: '101;102'
                    },
                    {
                        oldValue: ['foo1', 'bar1'],
                        cast: ['foo1', 'bar1'],
                        value: 'foo1;bar1'
                    }
                ]
            }
        ]);
    });

    it('Should allow creation', async () => {
        const content = [
            [
                MASTER_CATEGORY_HEADER,
                `${ADDITION_SYMBOL}${attributes.numberMultiple.code}`,
                `${SUBTRACTION_SYMBOL}${attributes.stringMultiple.code}`
            ],
            [masterCategory.code, '666', '']
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: MASTER_CATEGORY_HEADER, type: 'masterCategory'},
                {
                    header: attributes.numberMultiple.code,
                    type: 'number'
                },
                {
                    header: attributes.stringMultiple.code,
                    type: 'string'
                }
            ],
            {
                action: 'insert',
                columns: [
                    {cast: masterCategory.code, value: masterCategory.code},
                    {
                        cast: [666],
                        value: '666'
                    },
                    {
                        value: null
                    }
                ]
            }
        ]);
    });
});
