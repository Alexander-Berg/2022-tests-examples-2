import {seed, uuid} from 'casual';
import {orderBy} from 'lodash';
import pMap from 'p-map';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {createMasterCategoryWithInfoModel, createSelectOptions} from 'tests/unit/util';

seed(3);

import {META_PRODUCT_MASTER_CATEGORY_CODE} from '@/src/constants';
import {
    ARRAY_VALUE_DELIMITER,
    FRONT_CATEGORY_HEADER,
    IDENTIFIER_HEADER,
    IS_META_HEADER,
    MASTER_CATEGORY_HEADER,
    STATUS_HEADER
} from '@/src/constants/import';
import type {User} from '@/src/entities/user/entity';
import {
    ChangingIsMetaForProductIsForbidden,
    DisallowedMasterCategoryForMetaProduct,
    DuplicateImportSpreadsheetIdentifier,
    DuplicatesSpreadsheetHeader,
    ExactImportSpreadsheetProductVolume,
    ImportSpreadsheetAttributeMissedInProductInfoModel,
    ImportSpreadsheetTooManyProductInserts,
    InvalidImportSpreadsheetAttributeLocalization,
    InvalidImportSpreadsheetHeaders,
    InvalidImportSpreadsheetProductAttributeValue,
    InvalidImportSpreadsheetProductBooleanValue,
    InvalidImportSpreadsheetProductFrontCategoryValue,
    InvalidImportSpreadsheetProductIdentifierValue,
    InvalidImportSpreadsheetProductImageValue,
    InvalidImportSpreadsheetProductMasterCategoryValue,
    InvalidImportSpreadsheetProductRegion,
    MissedImportSpreadsheetNewProductRequiredAttributes,
    MissedImportSpreadsheetStoredAttribute,
    NonUniqueProductAttributeValue,
    serializeErrorToFlatArray,
    UnknownImportSpreadsheetProductAction
} from '@/src/errors';
import {config} from 'service/cfg';
import {Resolver} from 'service/import/resolver';
import {AttributeType} from 'types/attribute';
import {ProductStatus} from 'types/product';

describe('import resolver', () => {
    let user: User;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {product: {canEdit: true}}});
    });

    it('should throw error on illegal headers', async () => {
        for (const {content} of [
            {content: [[IDENTIFIER_HEADER, undefined]]},
            {content: [[IDENTIFIER_HEADER, '']]},
            {content: [[IDENTIFIER_HEADER, null]]}
        ]) {
            const {importKey} = await TestFactory.createImportSpreadsheet({content} as never);
            await expect(new Resolver({importKey, authorId: user.id}).handle()).rejects.toThrow(
                InvalidImportSpreadsheetHeaders
            );
        }
    });

    it('should point invalid identifier headers', async () => {
        const content = [[IDENTIFIER_HEADER, IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER]];
        const {importKey} = await TestFactory.createImportSpreadsheet({content});

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {error: new DuplicatesSpreadsheetHeader({key: 'id'}).toFlatArray(), header: 'id'},
                {error: new DuplicatesSpreadsheetHeader({key: 'id'}).toFlatArray(), header: 'id'},
                {header: 'master_category', type: 'masterCategory'}
            ]
        ]);
    });

    it('should point invalid stored headers', async () => {
        const {attr: stringAttr} = await createAttribute();
        const content = [[IDENTIFIER_HEADER, 'foo', stringAttr.code, 'bar']];
        const {importKey} = await TestFactory.createImportSpreadsheet({content});

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {error: new MissedImportSpreadsheetStoredAttribute({key: 'foo'}).toFlatArray(), header: 'foo'},
                {header: stringAttr.code, type: 'string'},
                {error: new MissedImportSpreadsheetStoredAttribute({key: 'bar'}).toFlatArray(), header: 'bar'}
            ]
        ]);
    });

    it('should throw error on invalid "headers <> rows" sizes', async () => {
        const {attr: stringAttr} = await createAttribute();
        const content = [
            [IDENTIFIER_HEADER, 'foo', stringAttr.code, 'bar'],
            ['', 'foo value', 'baz', 'bar value', 'wrong!']
        ];
        const promise = TestFactory.createImportSpreadsheet({content});
        const expectedErrMessage =
            `malformed array literal: "{{"id","foo","${stringAttr.code}","bar"}` +
            ',{"","foo value","baz","bar value","wrong!"}}"';

        await expect(promise.catch((err) => err.message)).resolves.toEqual(expectedErrMessage);
    });

    it('should handle invalid row action: identifier', async () => {
        const {attr: stringAttr} = await createAttribute();
        const content = [
            [IDENTIFIER_HEADER, 'foo', stringAttr.code, 'bar'],
            ['', 'foo value', 'baz', 'bar value']
        ];
        const {importKey} = await TestFactory.createImportSpreadsheet({content});

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {error: new MissedImportSpreadsheetStoredAttribute({key: 'foo'}).toFlatArray(), header: 'foo'},
                {header: stringAttr.code, type: 'string'},
                {error: new MissedImportSpreadsheetStoredAttribute({key: 'bar'}).toFlatArray(), header: 'bar'}
            ],
            {
                columns: [
                    {
                        error: new UnknownImportSpreadsheetProductAction().toFlatArray(),
                        value: null
                    },
                    {value: 'foo value'},
                    {value: 'baz'},
                    {value: 'bar value'}
                ],
                error: new UnknownImportSpreadsheetProductAction().toFlatArray()
            }
        ]);
    });

    it('should handle invalid row action: master category', async () => {
        const {attr: stringAttr} = await createAttribute();
        const content = [
            [MASTER_CATEGORY_HEADER, 'foo', stringAttr.code, 'bar'],
            ['', 'foo value', 'baz', 'bar value']
        ];
        const {importKey} = await TestFactory.createImportSpreadsheet({content});

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'master_category', type: 'masterCategory'},
                {error: new MissedImportSpreadsheetStoredAttribute({key: 'foo'}).toFlatArray(), header: 'foo'},
                {header: stringAttr.code, type: 'string'},
                {error: new MissedImportSpreadsheetStoredAttribute({key: 'bar'}).toFlatArray(), header: 'bar'}
            ],
            {
                columns: [
                    {
                        error: new UnknownImportSpreadsheetProductAction().toFlatArray(),
                        value: null
                    },
                    {value: 'foo value'},
                    {value: 'baz'},
                    {value: 'bar value'}
                ],
                error: new UnknownImportSpreadsheetProductAction().toFlatArray()
            }
        ]);
    });

    it('should handle invalid row action: identifier and master category', async () => {
        const {attr: stringAttr} = await createAttribute();
        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, 'foo', stringAttr.code, 'bar'],
            ['', '', 'foo value', 'baz', 'bar value']
        ];
        const {importKey} = await TestFactory.createImportSpreadsheet({content});

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {header: 'master_category', type: 'masterCategory'},
                {error: new MissedImportSpreadsheetStoredAttribute({key: 'foo'}).toFlatArray(), header: 'foo'},
                {header: stringAttr.code, type: 'string'},
                {error: new MissedImportSpreadsheetStoredAttribute({key: 'bar'}).toFlatArray(), header: 'bar'}
            ],
            {
                columns: [
                    {
                        error: new UnknownImportSpreadsheetProductAction().toFlatArray(),
                        value: null
                    },
                    {
                        error: new UnknownImportSpreadsheetProductAction().toFlatArray(),
                        value: null
                    },
                    {value: 'foo value'},
                    {value: 'baz'},
                    {value: 'bar value'}
                ],
                error: new UnknownImportSpreadsheetProductAction().toFlatArray()
            }
        ]);
    });

    it('should prepare allowed identifiers, master categories, front categories, attributes', async () => {
        const {user, infoModel, masterCategory, region} = await createMasterCategoryWithInfoModel();

        const products = await pMap([...Array(2)], () => {
            return TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: masterCategory.id,
                regionId: region.id
            });
        });

        const {last: parentFrontCategory} = await TestFactory.createNestedFrontCategory({
            authorId: user.id,
            regionId: region.id,
            depth: 2
        });

        const frontCategories = orderBy(
            await pMap([...Array(2)], () => {
                return TestFactory.createFrontCategory({
                    userId: user.id,
                    regionId: region.id,
                    parentId: parentFrontCategory.id
                });
            }),
            'id'
        );

        const {attr: stringAttr} = await createAttribute({user});

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttr.id}]
        });

        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, FRONT_CATEGORY_HEADER, stringAttr.code],
            [products[0].identifier, masterCategory.code, frontCategories[0].code, 'bar'],
            [
                '',
                masterCategory.code,
                frontCategories
                    .map(({code}) => code)
                    .sort()
                    .join(ARRAY_VALUE_DELIMITER),
                'bar'
            ],
            [products[1].identifier, masterCategory.code, frontCategories[0].code, 'bar'],
            [Number.MAX_SAFE_INTEGER, Number.MAX_SAFE_INTEGER, Number.MAX_SAFE_INTEGER, 'bar']
        ] as never;
        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        const resolver = new Resolver({importKey, authorId: user.id});
        const resolved = await resolver.handle();

        expect(orderBy([...resolver.getIdentifiersAllowed()], (a) => a[0])).toEqual(
            orderBy(
                [
                    [products[0].identifier, {regionId: region.id}],
                    [products[1].identifier, {regionId: region.id}]
                ],
                (a) => a[0]
            )
        );
        expect([...resolver.getMasterCategoriesAllowed()]).toEqual([[masterCategory.code, {id: masterCategory.id}]]);
        expect([...resolver.getFrontCategoriesAllowed()]).toEqual(
            orderBy(
                frontCategories.map(({id, code}) => [code, {id}]),
                'id'
            )
        );
        expect(resolver.getAttributesAllowed().masterCategory).toEqual(
            new Map([[masterCategory.code, new Set([stringAttr.code])]])
        );
        expect(resolver.getAttributesAllowed().product).toEqual(
            new Map([
                [products[0].identifier, new Set([stringAttr.code])],
                [products[1].identifier, new Set([stringAttr.code])]
            ])
        );

        expect(resolved).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {header: 'master_category', type: 'masterCategory'},
                {header: 'front_category', type: 'frontCategory'},
                {header: stringAttr.code, type: 'string'}
            ],
            {
                action: 'update',
                columns: [
                    {cast: products[0].identifier, value: String(products[0].identifier)},
                    {cast: masterCategory.code, oldValue: masterCategory.code, value: masterCategory.code},
                    {cast: [frontCategories[0].code], value: frontCategories[0].code},
                    {value: 'bar'}
                ]
            },
            {
                action: 'insert',
                columns: [
                    {value: null},
                    {cast: masterCategory.code, value: masterCategory.code},
                    {
                        cast: frontCategories.map(({code}) => code).sort(),
                        value: frontCategories
                            .map(({code}) => code)
                            .sort()
                            .join(ARRAY_VALUE_DELIMITER)
                    },
                    {value: 'bar'}
                ]
            },
            {
                action: 'update',
                columns: [
                    {cast: products[1].identifier, value: String(products[1].identifier)},
                    {cast: masterCategory.code, value: masterCategory.code, oldValue: masterCategory.code},
                    {cast: [frontCategories[0].code], value: frontCategories[0].code},
                    {value: 'bar'}
                ]
            },
            {
                columns: [
                    {
                        error: new InvalidImportSpreadsheetProductIdentifierValue().toFlatArray(),
                        value: String(Number.MAX_SAFE_INTEGER)
                    },
                    {value: String(Number.MAX_SAFE_INTEGER)},
                    {
                        error: new InvalidImportSpreadsheetProductFrontCategoryValue({
                            codes: Number.MAX_SAFE_INTEGER.toString()
                        }).toFlatArray(),
                        value: String(Number.MAX_SAFE_INTEGER)
                    },
                    {value: 'bar'}
                ],
                error: new UnknownImportSpreadsheetProductAction().toFlatArray()
            }
        ]);
    });

    it('should prepare old master categories', async () => {
        const {user, infoModel, masterCategory, region} = await createMasterCategoryWithInfoModel();

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const {attr: stringAttr} = await createAttribute({user});

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttr.id}]
        });

        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER],
            [product.identifier, masterCategory.code]
        ] as never;
        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        const resolver = new Resolver({importKey, authorId: user.id});

        await resolver.handle();

        expect([...resolver.getOldMasterCategories()]).toEqual([[product.identifier, masterCategory.code]]);
    });

    it('should handle localization', async () => {
        const {user, infoModel, masterCategory, region} = await createMasterCategoryWithInfoModel();

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const {attr: stringAttr} = await createAttribute({user, isValueLocalizable: true, isArray: true});

        const {attr: textAttr} = await createAttribute({
            user,
            type: AttributeType.TEXT,
            isValueLocalizable: true
        });

        const ru = await TestFactory.createLang({isoCode: 'ru'});
        const en = await TestFactory.createLang({isoCode: 'en'});

        await TestFactory.createLocale({regionId: region.id, langIds: [ru.id, en.id]});

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: ['ru1', 'ru2'],
            productId: product.id,
            attributeId: stringAttr.id,
            langId: ru.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: ['en1', 'en3'],
            productId: product.id,
            attributeId: stringAttr.id,
            langId: en.id
        });

        const content = [
            [
                IDENTIFIER_HEADER,
                MASTER_CATEGORY_HEADER,
                textAttr.code,
                `${stringAttr.code}|en`,
                `${stringAttr.code}|ru`
            ],
            [product.identifier, masterCategory.code, 'foo', 'new_en_a1;new_en_a2', 'new_ru_a1;new_ru_a2'],
            ['', masterCategory.code, 'bar', 'new_en_b1', 'new_ru_b1;new_ru_b2']
        ] as never;
        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttr.id}]
        });

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {header: 'master_category', type: 'masterCategory'},
                {
                    error: new InvalidImportSpreadsheetAttributeLocalization({key: textAttr.code}).toFlatArray(),
                    header: textAttr.code
                },
                {header: `${stringAttr.code}|en`, type: 'string'},
                {header: `${stringAttr.code}|ru`, type: 'string'}
            ],
            {
                action: 'update',
                columns: [
                    {cast: product.identifier, value: `${product.identifier}`},
                    {cast: masterCategory.code, oldValue: masterCategory.code, value: masterCategory.code},
                    {value: 'foo'},

                    {oldValue: ['en1', 'en3'], cast: ['new_en_a1', 'new_en_a2'], value: 'new_en_a1;new_en_a2'},
                    {oldValue: ['ru1', 'ru2'], cast: ['new_ru_a1', 'new_ru_a2'], value: 'new_ru_a1;new_ru_a2'}
                ]
            },
            {
                action: 'insert',
                columns: [
                    {value: null},
                    {cast: masterCategory.code, value: `${masterCategory.code}`},
                    {value: 'bar'},
                    {cast: ['new_en_b1'], value: 'new_en_b1'},
                    {cast: ['new_ru_b1', 'new_ru_b2'], value: 'new_ru_b1;new_ru_b2'}
                ]
            }
        ]);
    });

    it('should allow not to specify attribute language if there is only one language for region', async () => {
        const {user, infoModel, masterCategory, region} = await createMasterCategoryWithInfoModel();

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const {attr: stringAttr} = await createAttribute({user, isValueLocalizable: true, isArray: true});
        const {attr: boolAttr} = await createAttribute({user, type: AttributeType.BOOLEAN});

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttr.id}, {id: boolAttr.id}]
        });

        // Один доступный язык для региона
        const ru = await TestFactory.createLang({isoCode: 'ru'});
        await TestFactory.createLocale({langIds: [ru.id], regionId: region.id});

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: ['ru1', 'ru2'],
            productId: product.id,
            attributeId: stringAttr.id,
            langId: ru.id
        });

        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, stringAttr.code, boolAttr.code],
            [product.identifier, masterCategory.code, 'foo;bar', false],
            ['', masterCategory.code, 'foo;bar', false]
        ] as never;

        const {importKey: importKey1} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        expect(await new Resolver({importKey: importKey1, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {header: 'master_category', type: 'masterCategory'},
                {header: stringAttr.code, type: 'string'},
                {header: boolAttr.code, type: 'boolean'}
            ],
            {
                action: 'update',
                columns: [
                    {cast: product.identifier, value: `${product.identifier}`},
                    {cast: masterCategory.code, oldValue: masterCategory.code, value: masterCategory.code},
                    {oldValue: ['ru1', 'ru2'], cast: ['foo', 'bar'], value: 'foo;bar'},
                    {cast: false, value: 'false'}
                ]
            },
            {
                action: 'insert',
                columns: [
                    {value: null},
                    {cast: masterCategory.code, value: `${masterCategory.code}`},
                    {cast: ['foo', 'bar'], value: 'foo;bar'},
                    {cast: false, value: 'false'}
                ]
            }
        ]);

        // Два доступных языка для региона
        const en = await TestFactory.createLang({isoCode: 'en'});
        await TestFactory.createLocale({langIds: [en.id], regionId: region.id});

        const {importKey: importKey2} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        expect(await new Resolver({importKey: importKey2, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {header: 'master_category', type: 'masterCategory'},
                {
                    header: stringAttr.code,
                    error: new InvalidImportSpreadsheetAttributeLocalization({key: stringAttr.code}).toFlatArray()
                },
                {header: boolAttr.code, type: 'boolean'}
            ],
            {
                action: 'update',
                columns: [
                    {cast: product.identifier, value: `${product.identifier}`},
                    {cast: masterCategory.code, oldValue: masterCategory.code, value: masterCategory.code},
                    {value: 'foo;bar'},
                    {cast: false, value: 'false'}
                ]
            },
            {
                action: 'insert',
                columns: [
                    {value: null},
                    {cast: masterCategory.code, value: `${masterCategory.code}`},
                    {value: 'foo;bar'},
                    {cast: false, value: 'false'}
                ]
            }
        ]);
    });

    it('should handle complex spreadsheet', async () => {
        const {user, infoModel, masterCategory, region} = await createMasterCategoryWithInfoModel();
        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });
        const ru = await TestFactory.createLang({isoCode: 'ru'});
        const en = await TestFactory.createLang({isoCode: 'en'});
        await TestFactory.createLocale({regionId: region.id, langIds: [ru.id, en.id]});

        const {attr: stringAttr} = await createAttribute({user, isValueLocalizable: true});
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

        const {attr: imageAttr} = await createAttribute({user, type: AttributeType.IMAGE});
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: '/image1',
            productId: product.id,
            attributeId: imageAttr.id
        });

        const {attr: booleanAttr} = await createAttribute({user, type: AttributeType.BOOLEAN, isArray: true});
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: [true, false],
            productId: product.id,
            attributeId: booleanAttr.id
        });

        const {attr: numberAttr} = await createAttribute({user, type: AttributeType.NUMBER});
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 55,
            productId: product.id,
            attributeId: numberAttr.id
        });

        const {attr: multiselectAttr} = await createAttribute({user, type: AttributeType.MULTISELECT});
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

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {header: 'master_category', type: 'masterCategory'},
                {header: `${stringAttr.code}|ru`, type: 'string'},
                {header: `${stringAttr.code}|en`, type: 'string'},
                {header: imageAttr.code, type: 'image'},
                {header: booleanAttr.code, type: 'boolean'},
                {header: numberAttr.code, type: 'number'},
                {header: multiselectAttr.code, type: 'multiselect'}
            ],
            {
                action: 'update',
                columns: [
                    {cast: product.identifier, value: `${product.identifier}`},
                    {cast: masterCategory.code, oldValue: masterCategory.code, value: masterCategory.code},
                    {oldValue: 'ru1', value: 'str_ru_a'},
                    {oldValue: 'en1', value: 'str_en_a'},
                    {cast: 'avatars_a', oldValue: '/image1', value: imgA.relPath},
                    {cast: [true, true], oldValue: [true, false], value: 'on;да'},
                    {cast: 129, oldValue: 55, value: '129'},
                    {
                        oldValue: [optionCodes[0], optionCodes[1]],
                        cast: [optionCodes[2]],
                        value: optionCodes[2]
                    }
                ]
            },
            {
                action: 'insert',
                columns: [
                    {value: null},
                    {cast: masterCategory.code, value: masterCategory.code},
                    {value: 'str_ru_b'},
                    {value: 'str_en_b'},
                    {cast: 'avatars_b', value: imgB.relPath},
                    {cast: [false, false], value: 'off;НЕТ'},
                    {cast: 0, value: '0'},
                    {
                        cast: [optionCodes[1], optionCodes[2]],
                        value: [optionCodes[1], optionCodes[2]].join(ARRAY_VALUE_DELIMITER)
                    }
                ]
            }
        ]);
    });

    it('should handle update values equality', async () => {
        const {user, infoModel, masterCategory, region} = await createMasterCategoryWithInfoModel();

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id,
            status: ProductStatus.ACTIVE
        });

        const ru = await TestFactory.createLang({isoCode: 'ru'});
        const en = await TestFactory.createLang({isoCode: 'en'});
        await TestFactory.createLocale({regionId: region.id, langIds: [ru.id, en.id]});

        const {attr: stringAttr} = await createAttribute({user, isValueLocalizable: true, isArray: true});
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: ['ru_old'],
            productId: product.id,
            attributeId: stringAttr.id,
            langId: ru.id
        });
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: ['en_old_1', 'en_old_2'],
            productId: product.id,
            attributeId: stringAttr.id,
            langId: en.id
        });

        const {attr: textAttr} = await createAttribute({user, type: AttributeType.TEXT});
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'text_old',
            productId: product.id,
            attributeId: textAttr.id
        });

        const {attr: numberAttr} = await createAttribute({user, type: AttributeType.NUMBER, isArray: true});
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: [1, 2, 3],
            productId: product.id,
            attributeId: numberAttr.id
        });

        const {last: parentFrontCategory} = await TestFactory.createNestedFrontCategory({
            authorId: user.id,
            regionId: region.id,
            depth: 2
        });

        const frontCategories = await pMap([...Array(2)], async () => {
            const frontCategory = await TestFactory.createFrontCategory({
                userId: user.id,
                regionId: region.id,
                parentId: parentFrontCategory.id
            });

            await TestFactory.linkProductsToFrontCategory({
                userId: user.id,
                frontCategoryId: frontCategory.id,
                productIds: [product.id]
            });

            return frontCategory;
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttr.id}, {id: textAttr.id}, {id: numberAttr.id}]
        });

        const content = [
            [
                IDENTIFIER_HEADER,
                MASTER_CATEGORY_HEADER,
                FRONT_CATEGORY_HEADER,
                `${stringAttr.code}|ru`,
                `${stringAttr.code}|en`,
                textAttr.code,
                numberAttr.code,
                STATUS_HEADER
            ],
            [
                product.identifier,
                masterCategory.code,
                frontCategories
                    .map(({code}) => code)
                    .sort()
                    .join(ARRAY_VALUE_DELIMITER),
                'ru_old',
                'en_old_1;en_old_2',
                'text_old',
                '1;2;3',
                'active'
            ]
        ] as never;
        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {header: 'master_category', type: 'masterCategory'},
                {header: 'front_category', type: 'frontCategory'},
                {header: `${stringAttr.code}|ru`, type: 'string'},
                {header: `${stringAttr.code}|en`, type: 'string'},
                {header: textAttr.code, type: 'text'},
                {header: numberAttr.code, type: 'number'},
                {header: 'status', type: 'status'}
            ],
            {
                columns: [
                    {cast: product.identifier, value: '' + product.identifier},
                    {cast: masterCategory.code, oldValue: masterCategory.code, value: masterCategory.code},
                    {
                        cast: frontCategories.map(({code}) => code).sort(),
                        oldValue: frontCategories.map(({code}) => code).sort(),
                        value: frontCategories
                            .map(({code}) => code)
                            .sort()
                            .join(ARRAY_VALUE_DELIMITER)
                    },
                    {oldValue: ['ru_old'], value: 'ru_old', cast: ['ru_old']},
                    {oldValue: ['en_old_1', 'en_old_2'], cast: ['en_old_1', 'en_old_2'], value: 'en_old_1;en_old_2'},
                    {oldValue: 'text_old', value: 'text_old'},
                    {cast: [1, 2, 3], oldValue: [1, 2, 3], value: '1;2;3'},
                    {cast: 'active', oldValue: 'active', value: 'active'}
                ],
                error: new ExactImportSpreadsheetProductVolume().toFlatArray()
            }
        ]);
    });

    it('should handle untouched image urls', async () => {
        const {user, infoModel, masterCategory, region} = await createMasterCategoryWithInfoModel();

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const {attr: imageAttr} = await createAttribute({user, type: AttributeType.IMAGE});
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: '/image1',
            productId: product.id,
            attributeId: imageAttr.id
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: imageAttr.id}]
        });

        const content = [
            [IDENTIFIER_HEADER, imageAttr.code],
            [product.identifier, '/image1']
        ] as never;
        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});
        const resolver = new Resolver({importKey, prepareForStore: true, authorId: user.id});

        expect(await resolver.handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {header: imageAttr.code, type: 'image'}
            ],
            {
                columns: [
                    {cast: product.identifier, value: '' + product.identifier},
                    {cast: '/image1', oldValue: '/image1', value: '/image1'}
                ],
                error: new ExactImportSpreadsheetProductVolume().toFlatArray()
            }
        ]);

        expect(resolver.getStoreList()).toEqual([]);
    });

    it('should handle new product required properties', async () => {
        const {user, infoModel, masterCategory, region} = await createMasterCategoryWithInfoModel();

        const {attr: stringAttrA} = await createAttribute({user, isValueRequired: true});
        const {attr: stringAttrB} = await createAttribute({user, isValueRequired: true});
        const {attr: stringAttrC} = await createAttribute({user, isValueRequired: true, isValueLocalizable: true});

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttrA.id}, {id: stringAttrB.id}, {id: stringAttrC.id}]
        });

        const fr = await TestFactory.createLang({isoCode: 'fr'});
        const he = await TestFactory.createLang({isoCode: 'he'});

        await TestFactory.createLocale({regionId: region.id, langIds: [fr.id, he.id]});

        let content = [
            [MASTER_CATEGORY_HEADER, stringAttrA.code],
            [masterCategory.code, 'baz']
        ] as never;
        let {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});
        let resolver = new Resolver({importKey, prepareForStore: true, authorId: user.id});

        expect(await resolver.handle()).toEqual([
            [
                {header: 'master_category', type: 'masterCategory'},
                {header: stringAttrA.code, type: 'string'}
            ],
            {
                action: 'insert',
                columns: [{cast: masterCategory.code, value: masterCategory.code}, {value: 'baz'}],
                error: new MissedImportSpreadsheetNewProductRequiredAttributes({
                    attributes: [stringAttrB.code, stringAttrC.code].join(', ')
                }).toFlatArray()
            }
        ]);
        expect(resolver.getStoreList()).toEqual([]);

        content = [
            [MASTER_CATEGORY_HEADER, `${stringAttrC.code}|fr`],
            [masterCategory.code, 'fr_val']
        ] as never;
        ({importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content}));
        resolver = new Resolver({importKey, prepareForStore: true, authorId: user.id});

        expect(await resolver.handle()).toEqual([
            [
                {header: 'master_category', type: 'masterCategory'},
                {header: `${stringAttrC.code}|fr`, type: 'string'}
            ],
            {
                action: 'insert',
                columns: [{cast: masterCategory.code, value: masterCategory.code}, {value: 'fr_val'}],
                error: new MissedImportSpreadsheetNewProductRequiredAttributes({
                    attributes: [stringAttrA.code, stringAttrB.code, stringAttrC.code].join(', ')
                }).toFlatArray()
            }
        ]);
        expect(resolver.getStoreList()).toEqual([]);

        content = [
            [MASTER_CATEGORY_HEADER, `${stringAttrC.code}|fr`, `${stringAttrC.code}|he`],
            [masterCategory.code, 'fr_val', 'he_val']
        ] as never;
        ({importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content}));
        resolver = new Resolver({importKey, prepareForStore: true, authorId: user.id});

        expect(await resolver.handle()).toEqual([
            [
                {header: 'master_category', type: 'masterCategory'},
                {header: `${stringAttrC.code}|fr`, type: 'string'},
                {header: `${stringAttrC.code}|he`, type: 'string'}
            ],
            {
                action: 'insert',
                columns: [
                    {cast: masterCategory.code, value: masterCategory.code},
                    {value: 'fr_val'},
                    {value: 'he_val'}
                ],
                error: new MissedImportSpreadsheetNewProductRequiredAttributes({
                    attributes: [stringAttrA.code, stringAttrB.code].join(', ')
                }).toFlatArray()
            }
        ]);
        expect(resolver.getStoreList()).toEqual([]);
    });

    it('should handle attributes with unique values', async () => {
        const {user, infoModel, masterCategory, region} = await createMasterCategoryWithInfoModel();

        const {attr: stringAttrA} = await createAttribute({user, isUnique: true});
        const {attr: stringAttrB} = await createAttribute({user, isUnique: true, isArray: true});

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttrA.id}, {id: stringAttrB.id}]
        });

        const productA = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'old_A1',
            productId: productA.id,
            attributeId: stringAttrA.id
        });
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: ['old_B1', 'old_B2'],
            productId: productA.id,
            attributeId: stringAttrB.id
        });

        const productB = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });
        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'old_A2',
            productId: productB.id,
            attributeId: stringAttrA.id
        });

        const HEADER_RESULT = [
            {header: 'id', type: 'identifier'},
            {header: 'master_category', type: 'masterCategory'},
            {header: stringAttrA.code, type: 'string'},
            {header: stringAttrB.code, type: 'string'}
        ];

        /** Update only */
        let content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, stringAttrA.code, stringAttrB.code],
            [productA.identifier, masterCategory.code, 'old_A1', 'new_B ; old_B1'],
            [productB.identifier, masterCategory.code, 'new_A', 'new_B ; ']
        ] as never;
        let {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});
        let resolver = new Resolver({importKey, prepareForStore: true, authorId: user.id});

        expect(await resolver.handle()).toEqual([
            HEADER_RESULT,
            {
                action: 'update',
                columns: [
                    {cast: productA.identifier, value: '' + productA.identifier},
                    {cast: masterCategory.code, oldValue: masterCategory.code, value: masterCategory.code},
                    {oldValue: 'old_A1', value: 'old_A1'},
                    {
                        error: new NonUniqueProductAttributeValue({
                            key: stringAttrB.code,
                            value: 'new_B'
                        }).toFlatArray(),
                        cast: ['new_B', 'old_B1'],
                        oldValue: ['old_B1', 'old_B2'],
                        value: 'new_B ; old_B1'
                    }
                ]
            },
            {
                action: 'update',
                columns: [
                    {cast: productB.identifier, value: '' + productB.identifier},
                    {cast: masterCategory.code, oldValue: masterCategory.code, value: masterCategory.code},
                    {
                        oldValue: 'old_A2',
                        value: 'new_A'
                    },
                    {
                        error: new NonUniqueProductAttributeValue({
                            key: stringAttrB.code,
                            value: 'new_B'
                        }).toFlatArray(),
                        cast: ['new_B'],
                        value: 'new_B ;'
                    }
                ]
            }
        ]);
        expect(resolver.getStoreList()).toEqual([]);

        /** Insert only */
        content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, stringAttrA.code, stringAttrB.code],
            ['', masterCategory.code, 'old_A1', 'new_B ; old_B1'],
            ['', masterCategory.code, 'new_A', 'new_B']
        ] as never;
        ({importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content}));
        resolver = new Resolver({importKey, prepareForStore: true, authorId: user.id});

        expect(await resolver.handle()).toEqual([
            HEADER_RESULT,
            {
                action: 'insert',
                columns: [
                    {value: null},
                    {cast: masterCategory.code, value: masterCategory.code},
                    {
                        error: new NonUniqueProductAttributeValue({
                            key: stringAttrA.code,
                            value: 'old_A1'
                        }).toFlatArray(),
                        value: 'old_A1'
                    },
                    {
                        cast: ['new_B', 'old_B1'],
                        error: new NonUniqueProductAttributeValue({
                            key: stringAttrB.code,
                            value: 'new_B'
                        }).toFlatArray(),
                        value: 'new_B ; old_B1'
                    }
                ]
            },
            {
                action: 'insert',
                columns: [
                    {value: null},
                    {cast: masterCategory.code, value: masterCategory.code},
                    {value: 'new_A'},
                    {
                        cast: ['new_B'],
                        error: new NonUniqueProductAttributeValue({
                            key: stringAttrB.code,
                            value: 'new_B'
                        }).toFlatArray(),
                        value: 'new_B'
                    }
                ]
            }
        ]);
        expect(resolver.getStoreList()).toEqual([]);

        /** Insert And Update */
        content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, stringAttrA.code, stringAttrB.code],
            [productA.identifier, masterCategory.code, 'old_A1', 'a'],
            [productB.identifier, masterCategory.code, 'b', 'old_B2'],
            ['', masterCategory.code, 'old_A1', 'b'],
            ['', masterCategory.code, 'a', 'old_B1']
        ] as never;
        ({importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content}));
        resolver = new Resolver({importKey, prepareForStore: true, authorId: user.id});

        expect(await resolver.handle()).toEqual([
            HEADER_RESULT,
            {
                action: 'update',
                columns: [
                    {cast: productA.identifier, value: '' + productA.identifier},
                    {cast: masterCategory.code, oldValue: masterCategory.code, value: masterCategory.code},
                    {
                        error: new NonUniqueProductAttributeValue({
                            key: stringAttrA.code,
                            value: 'old_A1'
                        }).toFlatArray(),
                        oldValue: 'old_A1',
                        value: 'old_A1'
                    },
                    {cast: ['a'], oldValue: ['old_B1', 'old_B2'], value: 'a'}
                ]
            },
            {
                action: 'update',
                columns: [
                    {cast: productB.identifier, value: '' + productB.identifier},
                    {cast: masterCategory.code, oldValue: masterCategory.code, value: masterCategory.code},
                    {oldValue: 'old_A2', value: 'b'},
                    {cast: ['old_B2'], value: 'old_B2'}
                ]
            },
            {
                action: 'insert',
                columns: [
                    {value: null},
                    {cast: masterCategory.code, value: masterCategory.code},
                    {
                        error: new NonUniqueProductAttributeValue({
                            key: stringAttrA.code,
                            value: 'old_A1'
                        }).toFlatArray(),
                        value: 'old_A1'
                    },
                    {cast: ['b'], value: 'b'}
                ]
            },
            {
                action: 'insert',
                columns: [
                    {value: null},
                    {cast: masterCategory.code, value: masterCategory.code},
                    {value: 'a'},
                    {cast: ['old_B1'], value: 'old_B1'}
                ]
            }
        ]);
        expect(resolver.getStoreList()).toEqual([
            {
                action: 'update',
                identifier: productB.identifier,
                masterCategory: masterCategory.code,
                volume: {
                    [stringAttrA.code]: 'b',
                    [stringAttrB.code]: ['old_B2']
                }
            },
            {
                action: 'insert',
                masterCategory: masterCategory.code,
                volume: {
                    [stringAttrA.code]: 'a',
                    [stringAttrB.code]: ['old_B1']
                }
            }
        ]);
    });

    it('should handle allowed attributes from ancestors', async () => {
        const {user, infoModel, masterCategory: baseMasterCategory, region} = await createMasterCategoryWithInfoModel();

        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: baseMasterCategory.id
        });

        const {attr: stringAttr} = await createAttribute({user});
        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttr.id}]
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, stringAttr.code],
            ['', masterCategory.code, 'foo'],
            [product.identifier, masterCategory.code, 'bar']
        ] as never;
        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});
        const resolver = new Resolver({importKey, authorId: user.id});

        expect(await resolver.handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {header: 'master_category', type: 'masterCategory'},
                {header: stringAttr.code, type: 'string'}
            ],
            {
                action: 'insert',
                columns: [{value: null}, {cast: masterCategory.code, value: masterCategory.code}, {value: 'foo'}]
            },
            {
                action: 'update',
                columns: [
                    {cast: product.identifier, value: '' + product.identifier},
                    {cast: masterCategory.code, value: masterCategory.code, oldValue: masterCategory.code},
                    {value: 'bar'}
                ]
            }
        ]);
    });

    it('should be disallowed master categories with children', async () => {
        const {user, infoModel, masterCategory: baseMasterCategory, region} = await createMasterCategoryWithInfoModel();

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: baseMasterCategory.id
        });
        await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModel.id,
            parentId: mc.id
        });

        const {attr: stringAttr} = await createAttribute({user});

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttr.id}]
        });

        const content = [
            [MASTER_CATEGORY_HEADER, stringAttr.code],
            [mc.code, 'foo']
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});
        const resolver = new Resolver({importKey, authorId: user.id});

        expect(await resolver.handle()).toEqual([
            [
                {header: 'master_category', type: 'masterCategory'},
                {header: stringAttr.code, type: 'string'}
            ],
            {
                columns: [
                    {
                        error: new InvalidImportSpreadsheetProductMasterCategoryValue().toFlatArray(),
                        value: mc.code
                    },
                    {value: 'foo'}
                ],
                error: new UnknownImportSpreadsheetProductAction().toFlatArray()
            }
        ]);
    });

    it('should ignore disallowed attributes', async () => {
        const {user, infoModel, masterCategory, region} = await createMasterCategoryWithInfoModel();

        const {attr: stringAttr} = await createAttribute({user});
        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: stringAttr.id}]
        });

        const {attr: textAttr} = await createAttribute({user});

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, stringAttr.code, textAttr.code],
            ['', masterCategory.code, 'foo', 'baz'],
            [product.identifier, masterCategory.code, 'bar', 'qux']
        ] as never;
        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});
        const resolver = new Resolver({importKey, prepareForStore: true, authorId: user.id});

        expect(await resolver.handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {header: 'master_category', type: 'masterCategory'},
                {header: stringAttr.code, type: 'string'},
                {header: textAttr.code, type: 'string'}
            ],
            {
                action: 'insert',
                columns: [
                    {value: null},
                    {cast: masterCategory.code, value: masterCategory.code},
                    {value: 'foo'},
                    {
                        error: serializeErrorToFlatArray(
                            new InvalidImportSpreadsheetProductAttributeValue({key: textAttr.code}),
                            new ImportSpreadsheetAttributeMissedInProductInfoModel()
                        ),
                        value: 'baz'
                    }
                ]
            },
            {
                action: 'update',
                columns: [
                    {cast: product.identifier, value: '' + product.identifier},
                    {cast: masterCategory.code, oldValue: masterCategory.code, value: masterCategory.code},
                    {value: 'bar'},
                    {
                        error: serializeErrorToFlatArray(
                            new InvalidImportSpreadsheetProductAttributeValue({key: textAttr.code}),
                            new ImportSpreadsheetAttributeMissedInProductInfoModel()
                        ),
                        value: 'qux'
                    }
                ]
            }
        ]);

        expect(resolver.getStoreList()).toEqual([
            {action: 'insert', masterCategory: masterCategory.code, volume: {[stringAttr.code]: 'foo'}},
            {
                action: 'update',
                masterCategory: masterCategory.code,
                identifier: product.identifier,
                volume: {[stringAttr.code]: 'bar'}
            }
        ]);
    });

    it('should point identifiers from another region', async () => {
        const baseDataSet = await Promise.all([
            createMasterCategoryWithInfoModel({infoModel: {code: 'im_code'}, masterCategory: {code: 'mc_code'}}),
            createMasterCategoryWithInfoModel({infoModel: {code: 'im_code'}, masterCategory: {code: 'mc_code'}})
        ]);

        const {attr: stringAttr} = await createAttribute();

        const products = await Promise.all(
            baseDataSet.map(async (set) => {
                await TestFactory.linkAttributesToInfoModel({
                    userId: set.user.id,
                    infoModelId: set.infoModel.id,
                    attributes: [stringAttr]
                });

                const product = await TestFactory.createProduct({
                    userId: set.user.id,
                    masterCategoryId: set.masterCategory.id,
                    regionId: set.region.id
                });

                await TestFactory.createProductAttributeValue({
                    userId: set.user.id,
                    productId: product.id,
                    attributeId: stringAttr.id,
                    value: 'foo'
                });

                return product;
            })
        );

        const content = [
            [IDENTIFIER_HEADER, stringAttr.code],
            [products[0].identifier, 'bar1'],
            [products[1].identifier, 'bar2']
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: baseDataSet[0].region.id});

        expect(await new Resolver({importKey, authorId: user.id}).handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {header: stringAttr.code, type: 'string'}
            ],
            {
                action: 'update',
                columns: [
                    {cast: products[0].identifier, value: String(products[0].identifier)},
                    {oldValue: 'foo', value: 'bar1'}
                ]
            },
            {
                columns: [
                    {
                        value: String(products[1].identifier),
                        error: new InvalidImportSpreadsheetProductRegion().toFlatArray()
                    },
                    {
                        value: 'bar2'
                    }
                ],
                error: new UnknownImportSpreadsheetProductAction().toFlatArray()
            }
        ]);
    });

    it('should concern duplicate product identifiers', async () => {
        const {user, region, masterCategory, infoModel} = await createMasterCategoryWithInfoModel();

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [stringAttr]
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
            [IDENTIFIER_HEADER, stringAttr.code],
            [String(product1.identifier), 'bar1'],
            [String(product1.identifier), 'bar2'],
            [String(product2.identifier), 'bar3']
        ] as never;
        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});
        const resolver = new Resolver({importKey, prepareForStore: true, authorId: user.id});

        expect(await resolver.handle()).toEqual([
            [
                {header: 'id', type: 'identifier'},
                {header: stringAttr.code, type: 'string'}
            ],
            {
                action: 'update',
                error: serializeErrorToFlatArray(
                    new DuplicateImportSpreadsheetIdentifier({identifier: product1.identifier})
                ),
                columns: [{cast: product1.identifier, value: String(product1.identifier)}, {value: 'bar1'}]
            },
            {
                action: 'update',
                error: serializeErrorToFlatArray(
                    new DuplicateImportSpreadsheetIdentifier({identifier: product1.identifier})
                ),
                columns: [{cast: product1.identifier, value: String(product1.identifier)}, {value: 'bar2'}]
            },
            {
                action: 'update',
                columns: [{cast: product2.identifier, value: String(product2.identifier)}, {value: 'bar3'}]
            }
        ]);

        expect(resolver.getStoreList()).toEqual([
            {action: 'update', identifier: product2.identifier, volume: {[stringAttr.code]: 'bar3'}}
        ]);
    });

    it('should handle is_meta', async () => {
        const {user, region, masterCategory: rootMasterCategory} = await createMasterCategoryWithInfoModel();

        const masterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id
        });

        const metaProductMasterCategory = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMasterCategory.id,
            code: META_PRODUCT_MASTER_CATEGORY_CODE
        });

        const product1 = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id,
            status: ProductStatus.ACTIVE,
            isMeta: false
        });

        const product2 = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: metaProductMasterCategory.id,
            regionId: region.id,
            status: ProductStatus.ACTIVE,
            isMeta: true
        });

        const product3 = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: metaProductMasterCategory.id,
            regionId: region.id,
            status: ProductStatus.ACTIVE,
            isMeta: true
        });

        const importKey = uuid;
        const content = [
            [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, STATUS_HEADER, IS_META_HEADER],
            ['', masterCategory.code, 'active', ''],
            ['', masterCategory.code, 'active', 't'],
            ['', masterCategory.code, 'active', 'f'],
            ['', masterCategory.code, 'active', 'qwerty'],
            [String(product1.identifier), masterCategory.code, 'disabled', 'f'],
            [String(product2.identifier), masterCategory.code, 'disabled', 'f'],
            [String(product3.identifier), '', 'disabled', '']
        ] as never;

        await TestFactory.createImportSpreadsheet({importKey, regionId: region.id, content});
        const resolver = new Resolver({importKey, authorId: user.id, prepareForStore: true});

        expect(await resolver.handle()).toEqual([
            [
                {header: IDENTIFIER_HEADER, type: 'identifier'},
                {header: MASTER_CATEGORY_HEADER, type: 'masterCategory'},
                {header: STATUS_HEADER, type: 'status'},
                {header: IS_META_HEADER, type: 'isMeta'}
            ],
            {
                action: 'insert',
                columns: [
                    {value: null},
                    {cast: masterCategory.code, value: masterCategory.code},
                    {value: 'active', cast: 'active'},
                    {value: null}
                ]
            },
            {
                action: 'insert',
                columns: [
                    {value: null},
                    {value: masterCategory.code, error: new DisallowedMasterCategoryForMetaProduct().toFlatArray()},
                    {value: 'active', cast: 'active'},
                    {value: 't', cast: true}
                ]
            },
            {
                action: 'insert',
                columns: [
                    {value: null},
                    {cast: masterCategory.code, value: masterCategory.code},
                    {value: 'active', cast: 'active'},
                    {value: 'f', cast: false}
                ]
            },
            {
                action: 'insert',
                columns: [
                    {value: null},
                    {cast: masterCategory.code, value: masterCategory.code},
                    {value: 'active', cast: 'active'},
                    {error: new InvalidImportSpreadsheetProductBooleanValue().toFlatArray(), value: 'qwerty'}
                ]
            },
            {
                action: 'update',
                columns: [
                    {cast: product1.identifier, value: String(product1.identifier)},
                    {
                        cast: masterCategory.code,
                        value: masterCategory.code,
                        oldValue: masterCategory.code
                    },
                    {value: 'disabled', cast: 'disabled', oldValue: 'active'},
                    {cast: false, value: 'f', oldValue: false}
                ]
            },
            {
                action: 'update',
                columns: [
                    {cast: product2.identifier, value: String(product2.identifier)},
                    {
                        oldValue: metaProductMasterCategory.code,
                        value: masterCategory.code,
                        error: new DisallowedMasterCategoryForMetaProduct().toFlatArray()
                    },
                    {value: 'disabled', cast: 'disabled', oldValue: 'active'},
                    {error: new ChangingIsMetaForProductIsForbidden().toFlatArray(), value: 'f', oldValue: true}
                ]
            },
            {
                action: 'update',
                columns: [
                    {cast: product3.identifier, value: String(product3.identifier)},
                    {
                        value: null,
                        oldValue: metaProductMasterCategory.code
                    },
                    {value: 'disabled', cast: 'disabled', oldValue: 'active'},
                    {value: null, oldValue: true}
                ]
            }
        ]);

        expect(resolver.getStoreList()).toEqual([
            {
                action: 'insert',
                masterCategory: masterCategory.code,
                status: 'active',
                volume: {}
            },
            {
                action: 'insert',
                isMeta: true,
                masterCategory: metaProductMasterCategory.code,
                status: 'active',
                volume: {}
            },
            {
                action: 'insert',
                isMeta: false,
                masterCategory: masterCategory.code,
                status: 'active',
                volume: {}
            },
            {
                action: 'update',
                identifier: product1.identifier,
                isMeta: false,
                masterCategory: masterCategory.code,
                status: 'disabled',
                volume: {}
            },
            {
                action: 'update',
                identifier: product3.identifier,
                masterCategory: metaProductMasterCategory.code,
                status: 'disabled',
                volume: {}
            }
        ]);
    });

    it('should throw on exceeding inserts limit', async () => {
        const originalLimit = config.import.maxInsertRows;
        config.import.maxInsertRows = 5;

        const {infoModel, masterCategory, user, region} = await createMasterCategoryWithInfoModel();

        const {attr: stringAttr} = await createAttribute({type: AttributeType.STRING, isValueRequired: true});
        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [stringAttr]
        });

        const content = [
            [MASTER_CATEGORY_HEADER, stringAttr.code],
            ...Array.from({length: 10}, (_, i) => [masterCategory.code, String(i)])
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id});

        await expect(new Resolver({importKey, authorId: user.id}).handle()).rejects.toThrow(
            ImportSpreadsheetTooManyProductInserts
        );
        config.import.maxInsertRows = originalLimit;
    });

    it('should allow to use already uploaded images', async () => {
        const {infoModel, masterCategory, user, region} = await createMasterCategoryWithInfoModel();

        const product1 = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const product2 = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const {attr: imageSingleAttr} = await createAttribute({type: AttributeType.IMAGE});
        const {attr: imageMultipleAttr} = await createAttribute({type: AttributeType.IMAGE, isArray: true});

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [imageSingleAttr, imageMultipleAttr]
        });

        const imc1 = await TestFactory.createImageCache({url: 'https://foo.bar/baz/1.png'});
        const imc2 = await TestFactory.createImageCache({url: 'https://foo.bar/baz/2.png'});
        const imc3 = await TestFactory.createImageCache({url: 'https://foo.bar/baz/3.png'});

        const content = [
            [IDENTIFIER_HEADER, imageSingleAttr.code, imageMultipleAttr.code],
            [product1.identifier, imc1.url, [imc2.url, imc3.url].join(ARRAY_VALUE_DELIMITER)],
            [product2.identifier, 'https://foo.bar/baz/100500.png', '']
        ] as never;

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id});

        await expect(new Resolver({importKey, authorId: user.id}).handle()).resolves.toEqual([
            [
                {header: IDENTIFIER_HEADER, type: 'identifier'},
                {header: imageSingleAttr.code, type: 'image'},
                {header: imageMultipleAttr.code, type: 'image'}
            ],
            {
                action: 'update',
                columns: [
                    {cast: product1.identifier, value: String(product1.identifier)},
                    {cast: imc1.url, value: imc1.url},
                    {
                        cast: [imc2.url, imc3.url],
                        value: [imc2.url, imc3.url].join(ARRAY_VALUE_DELIMITER)
                    }
                ]
            },
            {
                columns: [
                    {cast: product2.identifier, value: String(product2.identifier)},
                    {
                        error: [
                            new InvalidImportSpreadsheetProductAttributeValue({
                                key: imageSingleAttr.code
                            }).toFlatArray(),
                            new InvalidImportSpreadsheetProductImageValue().toFlatArray()
                        ].flat(),
                        value: 'https://foo.bar/baz/100500.png'
                    },
                    {value: null}
                ],
                error: new ExactImportSpreadsheetProductVolume().toFlatArray()
            }
        ]);
    });
});

async function createAttribute({
    user,
    type = AttributeType.STRING,
    code = uuid,
    isValueLocalizable,
    isArray,
    isValueRequired,
    isUnique
}: {
    user?: User;
    type?: AttributeType;
    code?: string;
    isValueLocalizable?: boolean;
    isArray?: boolean;
    isValueRequired?: boolean;
    isUnique?: boolean;
} = {}) {
    if (!user) {
        user = await TestFactory.createUser();
    }

    const attr = await TestFactory.createAttribute({
        attribute: {type, code, isValueLocalizable, isArray, isValueRequired, isUnique},
        userId: user.id
    });

    return {user, attr};
}
