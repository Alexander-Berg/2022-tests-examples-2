import {noop, times} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {createUnPatchedQueryRunner} from 'tests/unit/setup';
import {TestFactory} from 'tests/unit/test-factory';

import {CODE_PATTERN} from '@/src/constants';
import type {Attribute} from '@/src/entities/attribute/entity';
import {DbTable} from '@/src/entities/const';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {Lang} from '@/src/entities/lang/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {Product} from '@/src/entities/product/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {
    BooleanAttributeCodeDeletionForbidden,
    DuplicateOrConflictImportSpreadsheetValue,
    DuplicatesSpreadsheetHeader,
    EmptyCommitChangesError,
    EmptyImportData,
    EmptyImportModification,
    ImportDataOutdatedError,
    InvalidImportSpreadsheetAttributeLocalization,
    InvalidImportSpreadsheetHeaders,
    InvalidImportSpreadsheetLang,
    InvalidImportSpreadsheetValue,
    MissedImportRequiredIdentifier,
    MissedImportSpreadsheetRequiredHeaders,
    MissedLangForLocalizableHeader,
    MissedPrimaryColumn,
    NotAllowedCharacters,
    NotDeletableInfoModelAttribute,
    OperationTimeoutError,
    RegExpValidationError,
    SystemAttributeCodeForbidden,
    UnknownAttributeCode,
    UnknownSpreadsheetHeader
} from '@/src/errors';
import {formatPattern} from 'client/utils/format-pattern';
import InfoModelImportBase, {ColumnNames, ConstructorOptions} from 'service/info-model-import/info-model-import';
import {logger} from 'service/logger';
import {AttributeType} from 'types/attribute';

class InfoModelImport extends InfoModelImportBase {
    // Отменять запрос надо с другого соединения
    protected async cancelBackendByPid(pid: number) {
        const queryRunner = await createUnPatchedQueryRunner();
        await queryRunner.query(`SELECT pg_cancel_backend(${pid});`);
        await queryRunner.release();
    }
}

class SlowInfoModelImport extends InfoModelImport {
    private changesStarted: Promise<void>;
    private changesFinished: Promise<void>;

    public async ensureChangesStarted() {
        await this.changesStarted;
    }
    public async ensureChangesFinished() {
        await this.changesFinished;
    }

    constructor(options: ConstructorOptions) {
        super(options);
        this.changesStarted = new Promise((resolve) => {
            this.upsertInfoModelAttributes = async () => {
                resolve();
                await this.entityManager.query('SELECT pg_sleep(0.25)');
                await super.upsertInfoModelAttributes();
            };
        });

        this.changesFinished = new Promise((resolve) => {
            this.commit = () => super.commit().finally(resolve);
        });
    }
}

describe('info-model import', () => {
    let user: User;
    let region: Region;
    let lang: Lang;
    let infoModel: InfoModel;
    let attributes: [Attribute, Attribute];
    let requiredAttributes: [Attribute, Attribute];
    let allAttributes: Attribute[];
    let masterCategory: MasterCategory;
    let product: Product;
    const mocks: jest.SpyInstance[] = [];

    beforeAll(() => {
        mocks.push(jest.spyOn(logger, 'error').mockImplementation(noop));
        mocks.push(jest.spyOn(logger, 'info').mockImplementation(noop));
    });

    afterAll(() => {
        mocks.forEach((mock) => mock.mockClear());
    });

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        lang = await TestFactory.createLang();

        const userId = user.id;
        const regionId = region.id;

        await TestFactory.createLocale({langIds: [lang.id], regionId});

        attributes = await Promise.all([
            TestFactory.createAttribute({userId, attribute: {type: AttributeType.STRING}}),
            TestFactory.createAttribute({userId, attribute: {type: AttributeType.BOOLEAN}})
        ]);

        requiredAttributes = await Promise.all([
            TestFactory.createAttribute({userId, attribute: {type: AttributeType.STRING, isValueRequired: true}}),
            TestFactory.createAttribute({userId, attribute: {type: AttributeType.STRING, isValueRequired: true}})
        ]);

        allAttributes = [...requiredAttributes, ...attributes];

        infoModel = await TestFactory.createInfoModel({
            userId,
            regionId,
            attributes: allAttributes,
            infoModel: {
                code: 'test_info_model_code',
                titleTranslationMap: {
                    [lang.isoCode]: 'info_model_title_en'
                },
                descriptionTranslationMap: {
                    [lang.isoCode]: 'info_model_description_en'
                }
            }
        });
        masterCategory = await TestFactory.createMasterCategory({userId, regionId, infoModelId: infoModel.id});

        product = await TestFactory.createProduct({userId, regionId, masterCategoryId: masterCategory.id});
        await TestFactory.createProductAttributeValue({
            userId,
            productId: product.id,
            attributeId: attributes[0].id,
            value: 'foo'
        });
    });

    it('should throw error on invalid input structure', async () => {
        for (const {content, expected} of [
            {
                content: [
                    [ColumnNames.infoModelCode, undefined],
                    ['', '']
                ],
                expected: InvalidImportSpreadsheetHeaders
            },
            {
                content: [
                    [ColumnNames.infoModelCode, ''],
                    ['', '']
                ],
                expected: InvalidImportSpreadsheetHeaders
            },
            {
                content: [
                    [ColumnNames.infoModelCode, null],
                    ['', '']
                ],
                expected: InvalidImportSpreadsheetHeaders
            },
            {
                content: [],
                expected: EmptyImportData
            },
            {
                content: [[ColumnNames.infoModelCode, 'foo']],
                expected: EmptyImportData
            },
            {
                content: [[ColumnNames.infoModelCode], ['foo']],
                expected: EmptyImportData
            },
            {
                content: [[ColumnNames.infoModelTitle], ['foo']],
                expected: MissedImportSpreadsheetRequiredHeaders
            }
        ]) {
            const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);
            await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).rejects.toThrow(expected);
        }
    });

    it('should reject row if info model code not specified', async () => {
        const content = [
            [ColumnNames.infoModelCode, `${ColumnNames.infoModelTitle}|${lang.isoCode}`],
            ['', 'foo']
        ];
        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [{value: 'code'}, {value: `title|${lang.isoCode}`}],
            {
                columns: [
                    {castedValue: null, value: ''},
                    {castedValue: 'foo', value: 'foo'}
                ],
                error: new MissedImportRequiredIdentifier().toFlatArray()
            }
        ]);
    });

    it('should reject column if duplicate header specified', async () => {
        const content = [
            [ColumnNames.infoModelCode, `${ColumnNames.infoModelTitle}|${lang.isoCode}`, ColumnNames.infoModelTitle],
            ['code', 'foo', 'bar']
        ];
        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [
                {value: 'code'},
                {
                    error: new DuplicatesSpreadsheetHeader({
                        key: `${ColumnNames.infoModelTitle}|${lang.isoCode}`
                    }).toFlatArray(),
                    value: `title|${lang.isoCode}`
                },
                {
                    error: new DuplicatesSpreadsheetHeader({
                        key: `${ColumnNames.infoModelTitle}|${lang.isoCode}`
                    }).toFlatArray(),
                    value: `title|${lang.isoCode}`
                }
            ],
            {
                action: 'insert',
                columns: [
                    {castedValue: 'code', value: 'code'},
                    {castedValue: 'foo', value: 'foo'},
                    {castedValue: 'bar', value: 'bar'}
                ],
                error: new EmptyCommitChangesError().toFlatArray()
            }
        ]);
    });

    it('should reject localizable column on invalid language specified', async () => {
        const content = [
            [ColumnNames.infoModelCode, `${ColumnNames.infoModelTitle}|ru`],
            ['code', 'foo']
        ];
        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [
                {value: 'code'},
                {
                    error: new InvalidImportSpreadsheetLang({header: 'title', lang: 'ru'}).toFlatArray(),
                    value: 'title|ru'
                }
            ],
            {
                action: 'insert',
                columns: [
                    {castedValue: 'code', value: 'code'},
                    {castedValue: 'foo', value: 'foo'}
                ],
                error: new EmptyCommitChangesError().toFlatArray()
            }
        ]);
    });

    it('should reject non-localizable column with language specified', async () => {
        const content = [
            [ColumnNames.infoModelCode, `${ColumnNames.attributeCode}|ru`],
            ['code', attributes[0].code]
        ];
        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [
                {value: ColumnNames.infoModelCode},
                {
                    error: new InvalidImportSpreadsheetAttributeLocalization({
                        key: ColumnNames.attributeCode
                    }).toFlatArray(),
                    value: `${ColumnNames.attributeCode}|ru`
                }
            ],
            {
                action: 'insert',
                columns: [
                    {castedValue: 'code', value: 'code'},
                    {castedValue: attributes[0].code, value: attributes[0].code}
                ],
                error: new EmptyCommitChangesError().toFlatArray()
            }
        ]);
    });

    it('should substitute language automatically if only on language available for region', async () => {
        const content = [
            [ColumnNames.infoModelCode, ColumnNames.infoModelTitle],
            ['code', 'foo']
        ];
        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [{value: 'code'}, {value: `title|${lang.isoCode}`}],
            {
                action: 'insert',
                columns: [
                    {castedValue: 'code', value: 'code'},
                    {castedValue: 'foo', value: 'foo'}
                ]
            }
        ]);
    });

    it('should reject column if no language specified and region has more than one language', async () => {
        const lang = await TestFactory.createLang({isoCode: 'ru'});
        await TestFactory.createLocale({langIds: [lang.id], regionId: region.id});

        const content = [
            [ColumnNames.infoModelCode, ColumnNames.infoModelTitle],
            ['code', 'foo']
        ];
        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [
                {value: ColumnNames.infoModelCode},
                {
                    error: new MissedLangForLocalizableHeader({header: 'title'}).toFlatArray(),
                    value: ColumnNames.infoModelTitle
                }
            ],
            {
                action: 'insert',
                columns: [
                    {castedValue: 'code', value: 'code'},
                    {castedValue: 'foo', value: 'foo'}
                ],
                error: new EmptyCommitChangesError().toFlatArray()
            }
        ]);
    });

    it('should reject cell if system attribute code specified', async () => {
        const content = [
            [ColumnNames.infoModelCode, ColumnNames.attributeCode],
            [infoModel.code, `_${requiredAttributes[0].code}`],
            ['code', `&${requiredAttributes[1].code}`]
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [{value: 'code'}, {value: 'attribute'}],
            {
                action: 'update',
                columns: [
                    {castedValue: infoModel.code, value: infoModel.code},
                    {
                        castedValue: `_${requiredAttributes[0].code}`,
                        error: new SystemAttributeCodeForbidden({code: requiredAttributes[0].code}).toFlatArray(),
                        value: `_${requiredAttributes[0].code}`
                    }
                ],
                error: new EmptyCommitChangesError().toFlatArray()
            },
            {
                action: 'insert',
                columns: [
                    {castedValue: 'code', value: 'code'},
                    {
                        castedValue: `&${requiredAttributes[1].code}`,
                        error: new SystemAttributeCodeForbidden({code: requiredAttributes[1].code}).toFlatArray(),
                        value: `&${requiredAttributes[1].code}`
                    }
                ],
                error: new EmptyCommitChangesError().toFlatArray()
            }
        ]);
    });

    it('should reject cell if trying to delete boolean attribute', async () => {
        const content = [
            [ColumnNames.infoModelCode, ColumnNames.attributeCode],
            [infoModel.code, `_${attributes[1].code}`]
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [{value: ColumnNames.infoModelCode}, {value: ColumnNames.attributeCode}],
            {
                action: 'update',
                columns: [
                    {castedValue: infoModel.code, value: infoModel.code},
                    {
                        castedValue: `_${attributes[1].code}`,
                        error: new BooleanAttributeCodeDeletionForbidden({code: attributes[1].code}).toFlatArray(),
                        value: `_${attributes[1].code}`
                    }
                ],
                error: new EmptyCommitChangesError().toFlatArray()
            }
        ]);
    });

    it('should reject cell if trying to delete attribute linked with product', async () => {
        const content = [
            [ColumnNames.infoModelCode, ColumnNames.attributeCode],
            [infoModel.code, `_${attributes[0].code}`]
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [{value: 'code'}, {value: 'attribute'}],
            {
                action: 'update',
                columns: [
                    {
                        castedValue: infoModel.code,
                        value: infoModel.code
                    },
                    {
                        castedValue: `_${attributes[0].code}`,
                        error: new NotDeletableInfoModelAttribute({code: attributes[0].code}).toFlatArray(),
                        value: `_${attributes[0].code}`
                    }
                ],
                error: new EmptyCommitChangesError().toFlatArray()
            }
        ]);
    });

    it('should correctly normalize, cast and reject invalid cell values', async () => {
        const content = [
            [ColumnNames.infoModelCode, ColumnNames.infoModelTitle, ColumnNames.attributeCode, ColumnNames.isImportant],
            ['code1', '', attributes[0].code, ''],
            ['code2', undefined, attributes[0].code, undefined],
            ['code3', null, attributes[0].code, null],
            ['code4', ' foo ', attributes[0].code, '  t  '],
            ['code5', 'bar', attributes[0].code, 'qwerty']
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [
                {value: ColumnNames.infoModelCode},
                {value: `${ColumnNames.infoModelTitle}|${lang.isoCode}`},
                {value: ColumnNames.attributeCode},
                {value: ColumnNames.isImportant}
            ],
            {
                action: 'insert',
                columns: [
                    {castedValue: 'code1', value: 'code1'},
                    {castedValue: null, value: ''},
                    {castedValue: attributes[0].code, value: attributes[0].code},
                    {castedValue: null, value: ''}
                ]
            },
            {
                action: 'insert',
                columns: [
                    {castedValue: 'code2', value: 'code2'},
                    {castedValue: null, value: ''},
                    {castedValue: attributes[0].code, value: attributes[0].code},
                    {castedValue: null, value: ''}
                ]
            },
            {
                action: 'insert',
                columns: [
                    {castedValue: 'code3', value: 'code3'},
                    {castedValue: null, value: ''},
                    {castedValue: attributes[0].code, value: attributes[0].code},
                    {castedValue: null, value: ''}
                ]
            },
            {
                action: 'insert',
                columns: [
                    {castedValue: 'code4', value: 'code4'},
                    {castedValue: 'foo', value: 'foo'},
                    {castedValue: attributes[0].code, value: attributes[0].code},
                    {castedValue: true, value: 't'}
                ]
            },
            {
                action: 'insert',
                columns: [
                    {castedValue: 'code5', value: 'code5'},
                    {castedValue: 'bar', value: 'bar'},
                    {castedValue: attributes[0].code, value: attributes[0].code},
                    {error: new InvalidImportSpreadsheetValue({value: 'qwerty'}).toFlatArray(), value: 'qwerty'}
                ]
            }
        ]);
    });

    it('should correctly autofill spreadsheet and count duplicates', async () => {
        const newInfoModels = await Promise.all(
            times(6, (n) =>
                TestFactory.createInfoModel({
                    userId: user.id,
                    regionId: region.id,
                    attributes: allAttributes,
                    infoModel: {
                        code: `new_info_model_code_${n}`,
                        titleTranslationMap: {},
                        descriptionTranslationMap: {}
                    }
                })
            )
        );

        const content = [
            [
                ColumnNames.infoModelCode,
                ColumnNames.infoModelTitle,
                ColumnNames.infoModelDescription,
                ColumnNames.attributeCode,
                ColumnNames.isImportant
            ],
            // Пустой код в начале файла
            ['', 'foo0', 'bar0', attributes[0].code, 't'],
            // Позитивный кейс
            [newInfoModels[0].code, 'foo1', 'bar1', attributes[0].code, 't'],
            ['', '', '', attributes[1].code, 't'],
            // Дублирование title / description
            [newInfoModels[1].code, 'foo2', '', attributes[0].code, 't'],
            ['', 'foo2', 'qwerty', attributes[1].code, 't'],
            // Дублирование code
            [newInfoModels[2].code, 'foo3', 'bar3', attributes[0].code, 't'],
            [newInfoModels[2].code, '', '', attributes[1].code, 't'],
            // Пустой атрибут с isImportant
            [newInfoModels[4].code, 'foo5', 'bar5', attributes[0].code, 't'],
            ['', '', '', '', 't'],
            [newInfoModels[5].code, 'foo6', 'bar6', attributes[0].code, 't'],
            // Дублирование атрибута
            ['', '', '', attributes[0].code, 'f']
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [
                {value: ColumnNames.infoModelCode},
                {value: `${ColumnNames.infoModelTitle}|${lang.isoCode}`},
                {value: `${ColumnNames.infoModelDescription}|${lang.isoCode}`},
                {value: ColumnNames.attributeCode},
                {value: ColumnNames.isImportant}
            ],
            {
                columns: [
                    {castedValue: null, value: ''},
                    {castedValue: 'foo0', value: 'foo0'},
                    {castedValue: 'bar0', value: 'bar0'},
                    {castedValue: attributes[0].code, value: attributes[0].code},
                    {castedValue: true, value: 't'}
                ],
                error: new MissedImportRequiredIdentifier().toFlatArray()
            },
            {
                action: 'update',
                columns: [
                    {castedValue: newInfoModels[0].code, value: newInfoModels[0].code},
                    {castedValue: 'foo1', value: 'foo1'},
                    {castedValue: 'bar1', value: 'bar1'},
                    {castedValue: attributes[0].code, value: attributes[0].code},
                    {castedValue: true, value: 't'}
                ]
            },
            {
                action: 'update',
                columns: [
                    {castedValue: newInfoModels[0].code, value: newInfoModels[0].code},
                    {castedValue: 'foo1', value: 'foo1'},
                    {castedValue: 'bar1', value: 'bar1'},
                    {castedValue: attributes[1].code, value: attributes[1].code},
                    {castedValue: true, value: 't'}
                ]
            },
            {
                action: 'update',
                columns: [
                    {castedValue: newInfoModels[1].code, value: newInfoModels[1].code},
                    {
                        castedValue: 'foo2',
                        error: new DuplicateOrConflictImportSpreadsheetValue({value: 'foo2'}).toFlatArray(),
                        value: 'foo2'
                    },
                    {
                        castedValue: null,
                        error: new DuplicateOrConflictImportSpreadsheetValue({value: 'null'}).toFlatArray(),
                        value: ''
                    },
                    {castedValue: attributes[0].code, value: attributes[0].code},
                    {castedValue: true, value: 't'}
                ]
            },
            {
                action: 'update',
                columns: [
                    {castedValue: newInfoModels[1].code, value: newInfoModels[1].code},
                    {
                        castedValue: 'foo2',
                        error: new DuplicateOrConflictImportSpreadsheetValue({value: 'foo2'}).toFlatArray(),
                        value: 'foo2'
                    },
                    {
                        castedValue: 'qwerty',
                        error: new DuplicateOrConflictImportSpreadsheetValue({value: 'qwerty'}).toFlatArray(),
                        value: 'qwerty'
                    },
                    {castedValue: attributes[1].code, value: attributes[1].code},
                    {castedValue: true, value: 't'}
                ]
            },
            {
                action: 'update',
                columns: [
                    {
                        castedValue: newInfoModels[2].code,
                        error: new DuplicateOrConflictImportSpreadsheetValue({
                            value: newInfoModels[2].code
                        }).toFlatArray(),
                        value: newInfoModels[2].code
                    },
                    {castedValue: 'foo3', value: 'foo3'},
                    {castedValue: 'bar3', value: 'bar3'},
                    {castedValue: attributes[0].code, value: attributes[0].code},
                    {castedValue: true, value: 't'}
                ]
            },
            {
                action: 'update',
                columns: [
                    {
                        castedValue: newInfoModels[2].code,
                        error: new DuplicateOrConflictImportSpreadsheetValue({
                            value: newInfoModels[2].code
                        }).toFlatArray(),
                        value: newInfoModels[2].code
                    },
                    {castedValue: 'foo3', value: 'foo3'},
                    {castedValue: 'bar3', value: 'bar3'},
                    {castedValue: attributes[1].code, value: attributes[1].code},
                    {castedValue: true, value: 't'}
                ]
            },
            {
                action: 'update',
                columns: [
                    {castedValue: newInfoModels[4].code, value: newInfoModels[4].code},
                    {castedValue: 'foo5', value: 'foo5'},
                    {castedValue: 'bar5', value: 'bar5'},
                    {castedValue: attributes[0].code, value: attributes[0].code},
                    {castedValue: true, value: 't'}
                ]
            },
            {
                action: 'update',
                columns: [
                    {castedValue: newInfoModels[4].code, value: newInfoModels[4].code},
                    {castedValue: 'foo5', value: 'foo5'},
                    {castedValue: 'bar5', value: 'bar5'},
                    {castedValue: null, value: ''},
                    {
                        castedValue: true,
                        value: 't',
                        error: new MissedPrimaryColumn({
                            primaryColumn: ColumnNames.attributeCode,
                            secondaryColumn: ColumnNames.isImportant
                        }).toFlatArray()
                    }
                ]
            },
            {
                action: 'update',
                columns: [
                    {castedValue: newInfoModels[5].code, value: newInfoModels[5].code},
                    {castedValue: 'foo6', value: 'foo6'},
                    {castedValue: 'bar6', value: 'bar6'},
                    {
                        castedValue: attributes[0].code,
                        error: new DuplicateOrConflictImportSpreadsheetValue({value: attributes[0].code}).toFlatArray(),
                        value: attributes[0].code
                    },
                    {castedValue: true, value: 't'}
                ]
            },
            {
                action: 'update',
                columns: [
                    {castedValue: newInfoModels[5].code, value: newInfoModels[5].code},
                    {castedValue: 'foo6', value: 'foo6'},
                    {castedValue: 'bar6', value: 'bar6'},
                    {
                        castedValue: attributes[0].code,
                        error: new DuplicateOrConflictImportSpreadsheetValue({value: attributes[0].code}).toFlatArray(),
                        value: attributes[0].code
                    },
                    {castedValue: false, value: 'f'}
                ]
            }
        ]);
    });

    it('should reject cell if specified code does not match regular expression', async () => {
        const content = [
            [ColumnNames.infoModelCode, ColumnNames.attributeCode],
            ['666code', attributes[0].code]
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [{value: ColumnNames.infoModelCode}, {value: ColumnNames.attributeCode}],
            {
                action: 'insert',
                columns: [
                    {
                        castedValue: '666code',
                        error: new RegExpValidationError({
                            value: '666code',
                            pattern: formatPattern(CODE_PATTERN)
                        }).toFlatArray(),
                        value: '666code'
                    },
                    {
                        castedValue: attributes[0].code,
                        value: attributes[0].code
                    }
                ],
                error: new EmptyCommitChangesError().toFlatArray()
            }
        ]);
    });

    it('should reject localizable cell if it contains forbidden character sequences', async () => {
        const content = [
            [ColumnNames.infoModelCode, ColumnNames.infoModelTitle],
            ['code1', 'foo %(bar)'],
            ['code2', 'foo (bar)%'],
            ['code3', 'foo\nbar']
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [{value: ColumnNames.infoModelCode}, {value: `${ColumnNames.infoModelTitle}|${lang.isoCode}`}],
            {
                action: 'insert',
                columns: [
                    {castedValue: 'code1', value: 'code1'},
                    {
                        castedValue: 'foo %(bar)',
                        error: new NotAllowedCharacters({value: 'foo %(bar)', characters: '%('}).toFlatArray(),
                        value: 'foo %(bar)'
                    }
                ],
                error: new EmptyCommitChangesError().toFlatArray()
            },
            {
                action: 'insert',
                columns: [
                    {castedValue: 'code2', value: 'code2'},
                    {
                        castedValue: 'foo (bar)%',
                        error: new NotAllowedCharacters({value: 'foo (bar)%', characters: ')%'}).toFlatArray(),
                        value: 'foo (bar)%'
                    }
                ],
                error: new EmptyCommitChangesError().toFlatArray()
            },
            {
                action: 'insert',
                columns: [
                    {castedValue: 'code3', value: 'code3'},
                    {
                        castedValue: 'foo\nbar',
                        error: new NotAllowedCharacters({value: 'foo\nbar', characters: '\n'}).toFlatArray(),
                        value: 'foo\nbar'
                    }
                ],
                error: new EmptyCommitChangesError().toFlatArray()
            }
        ]);
    });

    it('should invalidate column on unknown header specified', async () => {
        const content = [
            [ColumnNames.infoModelCode, 'foo_bar_baz'],
            [infoModel.code, 'qwerty']
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [
                {value: ColumnNames.infoModelCode},
                {
                    error: new UnknownSpreadsheetHeader({header: 'foo_bar_baz'}).toFlatArray(),
                    value: 'foo_bar_baz'
                }
            ],
            {
                action: 'update',
                columns: [
                    {castedValue: infoModel.code, value: infoModel.code},
                    {
                        error: new UnknownSpreadsheetHeader({header: 'foo_bar_baz'}).toFlatArray(),
                        value: 'qwerty'
                    }
                ],
                error: new EmptyCommitChangesError().toFlatArray()
            }
        ]);
    });

    it('should reject cell if unknown attribute specified', async () => {
        const content = [
            [ColumnNames.infoModelCode, ColumnNames.attributeCode],
            [infoModel.code, 'qwerty']
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [{value: ColumnNames.infoModelCode}, {value: ColumnNames.attributeCode}],
            {
                action: 'update',
                columns: [
                    {
                        castedValue: infoModel.code,
                        value: infoModel.code
                    },
                    {
                        castedValue: 'qwerty',
                        error: new UnknownAttributeCode({code: 'qwerty'}).toFlatArray(),
                        value: 'qwerty'
                    }
                ],
                error: new EmptyCommitChangesError().toFlatArray()
            }
        ]);
    });

    it('should reject column if dependent column specified without primary one', async () => {
        const content = [
            [ColumnNames.infoModelCode, ColumnNames.infoModelTitle, ColumnNames.isImportant],
            [infoModel.code, '', 't']
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [
                {value: ColumnNames.infoModelCode},
                {value: `${ColumnNames.infoModelTitle}|${lang.isoCode}`},
                {
                    error: new MissedPrimaryColumn({
                        primaryColumn: ColumnNames.attributeCode,
                        secondaryColumn: ColumnNames.isImportant
                    }).toFlatArray(),
                    value: ColumnNames.isImportant
                }
            ],
            {
                action: 'update',
                columns: [
                    {castedValue: infoModel.code, value: infoModel.code},
                    {castedValue: null, value: ''},
                    {castedValue: true, value: 't'}
                ]
            }
        ]);
    });

    it('should reject rows if they will not cause any mutation', async () => {
        const content = [
            [ColumnNames.infoModelCode, ColumnNames.infoModelTitle, ColumnNames.attributeCode, ColumnNames.isImportant],
            [infoModel.code, infoModel.titleTranslationMap[lang.isoCode], attributes[0].code, 'f'],
            ['', '', attributes[1].code, 'f']
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [
                {value: ColumnNames.infoModelCode},
                {value: `${ColumnNames.infoModelTitle}|${lang.isoCode}`},
                {value: ColumnNames.attributeCode},
                {value: ColumnNames.isImportant}
            ],
            {
                action: 'update',
                columns: [
                    {castedValue: infoModel.code, value: infoModel.code},
                    {
                        castedValue: infoModel.titleTranslationMap[lang.isoCode],
                        value: infoModel.titleTranslationMap[lang.isoCode]
                    },
                    {castedValue: attributes[0].code, value: attributes[0].code},
                    {castedValue: false, value: 'f'}
                ],
                error: new EmptyImportModification().toFlatArray()
            },
            {
                action: 'update',
                columns: [
                    {castedValue: infoModel.code, value: infoModel.code},
                    {
                        castedValue: infoModel.titleTranslationMap[lang.isoCode],
                        value: infoModel.titleTranslationMap[lang.isoCode]
                    },
                    {castedValue: attributes[1].code, value: attributes[1].code},
                    {castedValue: false, value: 'f'}
                ],
                error: new EmptyImportModification().toFlatArray()
            }
        ]);
    });

    it('should reject infomodel relative cell if it will not cause any mutation', async () => {
        const content = [
            [ColumnNames.infoModelCode, ColumnNames.infoModelTitle, ColumnNames.infoModelDescription],
            [infoModel.code, infoModel.titleTranslationMap[lang.isoCode], 'qwerty']
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [
                {value: ColumnNames.infoModelCode},
                {value: `${ColumnNames.infoModelTitle}|${lang.isoCode}`},
                {value: `${ColumnNames.infoModelDescription}|${lang.isoCode}`}
            ],
            {
                action: 'update',
                columns: [
                    {castedValue: infoModel.code, value: infoModel.code},
                    {
                        castedValue: 'info_model_title_en',
                        error: new EmptyImportModification().toFlatArray(),
                        value: infoModel.titleTranslationMap[lang.isoCode]
                    },
                    {castedValue: 'qwerty', value: 'qwerty'}
                ]
            }
        ]);
    });

    it('should reject attribute relative cells if they will not cause any mutation', async () => {
        const content = [
            [ColumnNames.infoModelCode, ColumnNames.infoModelTitle, ColumnNames.attributeCode, ColumnNames.isImportant],
            [infoModel.code, 'qwerty', attributes[0].code, 'f']
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [
                {value: ColumnNames.infoModelCode},
                {value: `${ColumnNames.infoModelTitle}|${lang.isoCode}`},
                {value: ColumnNames.attributeCode},
                {value: ColumnNames.isImportant}
            ],
            {
                action: 'update',
                columns: [
                    {castedValue: infoModel.code, value: infoModel.code},
                    {castedValue: 'qwerty', value: 'qwerty'},
                    {
                        castedValue: attributes[0].code,
                        error: new EmptyImportModification().toFlatArray(),
                        value: attributes[0].code
                    },
                    {
                        castedValue: false,
                        error: new EmptyImportModification().toFlatArray(),
                        value: 'f'
                    }
                ]
            }
        ]);
    });

    it('should throw on commit if no mutation will happen', async () => {
        const content = [
            [ColumnNames.infoModelCode, ColumnNames.infoModelTitle, ColumnNames.attributeCode, ColumnNames.isImportant],
            [infoModel.code, infoModel.titleTranslationMap[lang.isoCode], attributes[0].code, 'f'],
            ['', '', attributes[1].code, 'f']
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);
        const infoModelImport = new InfoModelImport({importKey, authorId: user.id});
        await expect(infoModelImport.resolve()).resolves.not.toThrow();
        await expect(infoModelImport.commit()).rejects.toThrow(EmptyCommitChangesError);
    });

    it('should throw on commit if resolved data changed', async () => {
        const attribute = await TestFactory.createAttribute({userId: user.id, attribute: {type: AttributeType.STRING}});
        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [attribute]
        });

        const content = [
            [ColumnNames.infoModelCode, ColumnNames.attributeCode, ColumnNames.isImportant],
            [infoModel.code, `_${attribute.code}`, ''],
            [infoModel.code, attributes[0].code, 't']
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);
        const infoModelImport = new InfoModelImport({importKey, authorId: user.id});
        await expect(infoModelImport.resolve()).resolves.not.toThrow();

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            productId: product.id,
            attributeId: attribute.id,
            value: 'baz'
        });

        await expect(infoModelImport.commit()).rejects.toThrow(ImportDataOutdatedError);
    });

    it('should create and update info-model with attributes', async () => {
        const newAttr = await TestFactory.createAttribute({userId: user.id, attribute: {type: AttributeType.NUMBER}});

        const content = [
            [ColumnNames.infoModelCode, ColumnNames.infoModelTitle, ColumnNames.attributeCode, ColumnNames.isImportant],
            [infoModel.code, 'new_im_title1', newAttr.code, 't'],
            ['new_im_code', 'new_im_title2', attributes[0].code, 't']
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);
        const infoModelImport = new InfoModelImport({authorId: user.id, importKey});

        await expect(infoModelImport.resolve()).resolves.not.toThrow();

        const importStats = await infoModelImport.commit();
        const newIm = await TestFactory.getInfoModels('new_im_code');

        expect(importStats).toEqual({
            updated: [infoModel.id],
            inserted: [newIm.id]
        });

        const infoModelAttributes = await TestFactory.getInfoModelAttributes();

        expect(
            infoModelAttributes.find(
                ({infoModelId, attributeId}) => infoModelId === infoModel.id && attributeId === newAttr.id
            )
        ).toMatchObject({isImportant: true});

        const requiredAttributesIds = requiredAttributes.map(({id}) => id).sort((a, b) => a - b);
        const regularAttributesIds = attributes.map(({id}) => id).sort((a, b) => a - b);
        const created = infoModelAttributes.filter(({infoModelId}) => infoModelId === newIm.id);

        const createdRequiredIds = created
            .filter(({attributeId}) => requiredAttributesIds.includes(attributeId))
            .map(({attributeId}) => attributeId)
            .sort((a, b) => a - b);

        expect(createdRequiredIds).toEqual(requiredAttributesIds);

        const createdRegular = created
            .filter(({attributeId}) => regularAttributesIds.includes(attributeId))
            .map(({attributeId, isImportant}) => ({id: attributeId, isImportant}))
            .sort((a, b) => a.id - b.id);

        expect(createdRegular).toEqual([{id: attributes[0].id, isImportant: true}]);
    });

    it('should delete info-model attributes', async () => {
        const initialLength = [...attributes, ...requiredAttributes].length;
        await expect(TestFactory.getInfoModelAttributes()).resolves.toHaveLength(initialLength);

        const newAttr1 = await TestFactory.createAttribute({userId: user.id, attribute: {type: AttributeType.NUMBER}});
        const newAttr2 = await TestFactory.createAttribute({userId: user.id, attribute: {type: AttributeType.NUMBER}});
        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [newAttr1, newAttr2]
        });

        await expect(TestFactory.getInfoModelAttributes()).resolves.toHaveLength(initialLength + 2);

        const content = [
            [ColumnNames.infoModelCode, ColumnNames.attributeCode, ColumnNames.isImportant],
            [infoModel.code, `_${newAttr1.code}`, 'f']
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);
        const infoModelImport = new InfoModelImport({authorId: user.id, importKey});

        await expect(infoModelImport.resolve()).resolves.not.toThrow();
        await expect(infoModelImport.commit()).resolves.not.toThrow();

        await expect(TestFactory.getInfoModelAttributes()).resolves.toHaveLength(initialLength + 1);
    });

    it('should queue product fullness and confirmation tasks', async () => {
        const content = [
            [ColumnNames.infoModelCode, ColumnNames.infoModelTitle, ColumnNames.attributeCode, ColumnNames.isImportant],
            [infoModel.code, 'new_im_title1', attributes[0].code, 't']
        ];

        await expect(TestFactory.getTaskQueue()).resolves.toHaveLength(0);
        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);
        const infoModelImport = new InfoModelImport({authorId: user.id, importKey});

        await expect(infoModelImport.resolve()).resolves.not.toThrow();
        await expect(infoModelImport.commit()).resolves.not.toThrow();

        await expect(TestFactory.getTaskQueue()).resolves.toHaveLength(2);
    });

    it('should stop applying changes after lock timeout', async () => {
        const content = [
            [ColumnNames.infoModelCode, ColumnNames.infoModelTitle, ColumnNames.attributeCode, ColumnNames.isImportant],
            [infoModel.code, '', attributes[0].code, 't'],
            ['some_im_code', 'new_im_title', attributes[0].code, 't']
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);
        const params = {authorId: user.id, importKey};

        await expect(new SlowInfoModelImport(params).resolve()).resolves.not.toThrow();

        jest.useFakeTimers();
        const slowInfoModelImport = new SlowInfoModelImport(params);
        const commitPromise = slowInfoModelImport.commit();
        await slowInfoModelImport.ensureChangesStarted();
        jest.runAllTimers();
        jest.useRealTimers();
        await expect(commitPromise).rejects.toThrow(OperationTimeoutError);
        await slowInfoModelImport.ensureChangesFinished();
        expect(await TestFactory.dispatchHistory()).toHaveLength(0);

        // Косвенная проверка
        // Так как в таблицах, которые завязаны на историю будет пусто, потому что
        // откатится user и запросы на вставку не пройдут,
        // проверим что ничего не записалось в task_queue, так как она не завязана на историю
        // и не требует наличия пользователя в user
        expect(await TestFactory.getTaskQueue()).toHaveLength(0);
    });

    it('should correctly create records in history', async () => {
        const newAttr = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.NUMBER, code: 'new_attr_code'}
        });
        const newInfoModels = await Promise.all(
            times(5, (n) =>
                TestFactory.createInfoModel({
                    userId: user.id,
                    regionId: region.id,
                    attributes: allAttributes,
                    infoModel: {
                        code: `new_info_model_code_${n}`,
                        titleTranslationMap: {},
                        descriptionTranslationMap: {}
                    }
                })
            )
        );

        await TestFactory.flushHistory();
        await expect(TestFactory.getHistory()).resolves.toHaveLength(0);

        const content = [
            [
                ColumnNames.infoModelCode,
                ColumnNames.infoModelTitle,
                ColumnNames.infoModelDescription,
                ColumnNames.attributeCode,
                ColumnNames.isImportant
            ],
            // Удаляем атрибут привязанный к продукту - ничего не должно пройти
            [
                infoModel.code,
                infoModel.titleTranslationMap[lang.isoCode],
                infoModel.descriptionTranslationMap[lang.isoCode],
                `_${attributes[0].code}`,
                'ложь'
            ],
            // Вносим значения, которые и так есть в БД - ничего не должно пройти
            ['', '', '', attributes[1].code, 'false'],
            // Удаляем атрибут которого и так нет в ИМ, но обновление title должно пройти
            [newInfoModels[0].code, 'title0', '', `_${newAttr.code}`, 'f'],
            // Удаляем boolean атрибут, ничего не должно пройти
            [newInfoModels[1].code, 'title1', 'description1', `_${attributes[1].code}`, 'f'],
            // Указываем невалидный атрибут, ничего не должно пройти
            [newInfoModels[2].code, 'title2', 'description2', 'qwerty', 'f'],
            // Позитивный кейс (добавление / обновление) - все должно пройти
            [newInfoModels[3].code, '', '', newAttr.code, 'f'],
            ['', '', '', attributes[0].code, 't'],
            // Удаление должно пройти
            [newInfoModels[4].code, '', '', `_${attributes[0].code}`, 'f'],
            // Позитивный кейс (создание) - все должно пройти
            ['foo_info_model_code', 'fooTitle', 'fooDescription', newAttr.code, 'f']
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);
        const infoModelImport = new InfoModelImport({authorId: user.id, importKey});

        await expect(infoModelImport.resolve()).resolves.not.toThrow();
        await expect(infoModelImport.commit()).resolves.not.toThrow();

        await TestFactory.dispatchDeferred();
        const historyRecords = await TestFactory.getHistory();
        expect(historyRecords).toHaveLength(8);

        const fooInfoModel = await TestFactory.getInfoModels('foo_info_model_code');
        const expectedHistoryMutation = {
            info_model: {
                I: [fooInfoModel.id],
                U: [newInfoModels[0].id],
                D: [] as number[]
            },
            info_model_attribute: {
                I: {
                    [newInfoModels[3].id]: [newAttr.id],
                    [fooInfoModel.id]: [...requiredAttributes, newAttr].map(({id}) => id)
                },
                U: {
                    [newInfoModels[3].id]: [attributes[0].id]
                },
                D: {
                    [newInfoModels[4].id]: [attributes[0].id]
                }
            }
        };

        const actualHistoryMutation: typeof expectedHistoryMutation = {
            info_model: {I: [], U: [], D: []},
            info_model_attribute: {I: {}, U: {}, D: {}}
        };

        historyRecords
            .sort((a, b) => a.id - b.id)
            .forEach(({tableName, action, oldRow, newRow}) => {
                const row = (oldRow ?? newRow ?? {}) as Record<string, string>;
                if (tableName === DbTable.INFO_MODEL) {
                    const imId = Number(row.id);
                    actualHistoryMutation.info_model[action].push(imId);
                }
                if (tableName === DbTable.INFO_MODEL_ATTRIBUTE) {
                    const imId = Number(row.info_model_id);
                    const attrId = Number(row.attribute_id);
                    actualHistoryMutation.info_model_attribute[action][imId] ||= [];
                    actualHistoryMutation.info_model_attribute[action][imId].push(attrId);
                }
            });

        expect(actualHistoryMutation).toEqual(expectedHistoryMutation);
    });

    it('should correctly handle empty rows and cell', async () => {
        const newAttr = await TestFactory.createAttribute({userId: user.id, attribute: {type: AttributeType.STRING}});

        const content = [
            [
                ColumnNames.infoModelCode,
                ColumnNames.infoModelTitle,
                ColumnNames.infoModelDescription,
                ColumnNames.isImportant,
                ColumnNames.attributeCode
            ],
            ['', '', '', '', ''],
            [infoModel.code, 'new_title', '', '', ''],
            ['', '', '', '', ''],
            ['', '', '', '', newAttr.code],
            [undefined, undefined, undefined, undefined, undefined],
            ['new_info_model_code', '', '', 't', ''],
            [null, null, null, null, null]
        ];

        const {importKey} = await TestFactory.createImportSpreadsheet({content, regionId: region.id} as never);

        await expect(new InfoModelImport({importKey, authorId: user.id}).resolve()).resolves.toEqual([
            [
                {value: ColumnNames.infoModelCode},
                {value: `${ColumnNames.infoModelTitle}|${lang.isoCode}`},
                {value: `${ColumnNames.infoModelDescription}|${lang.isoCode}`},
                {value: ColumnNames.isImportant},
                {value: ColumnNames.attributeCode}
            ],
            {
                action: 'update',
                columns: [
                    {castedValue: infoModel.code, value: infoModel.code},
                    {castedValue: 'new_title', value: 'new_title'},
                    {castedValue: null, value: ''},
                    {castedValue: null, value: '', error: new EmptyImportModification().toFlatArray()},
                    {castedValue: null, value: '', error: new EmptyImportModification().toFlatArray()}
                ]
            },
            {
                action: 'update',
                columns: [
                    {castedValue: infoModel.code, value: infoModel.code},
                    {castedValue: 'new_title', value: 'new_title'},
                    {castedValue: null, value: ''},
                    {castedValue: null, value: ''},
                    {castedValue: newAttr.code, value: newAttr.code}
                ]
            },
            {
                action: 'insert',
                columns: [
                    {castedValue: 'new_info_model_code', value: 'new_info_model_code'},
                    {castedValue: null, value: ''},
                    {castedValue: null, value: ''},
                    {
                        castedValue: true,
                        value: 't',
                        error: new MissedPrimaryColumn({
                            primaryColumn: ColumnNames.attributeCode,
                            secondaryColumn: ColumnNames.isImportant
                        }).toFlatArray()
                    },
                    {castedValue: null, value: ''}
                ]
            }
        ]);
    });
});
