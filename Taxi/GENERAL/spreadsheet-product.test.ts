import {seed, uuid} from 'casual';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {createSelectOptions} from 'tests/unit/util';

import {
    ARRAY_VALUE_DELIMITER,
    FRONT_CATEGORY_HEADER,
    IDENTIFIER_HEADER,
    IS_META_HEADER,
    MASTER_CATEGORY_HEADER,
    STATUS_HEADER
} from '@/src/constants/import';
import type {Region} from '@/src/entities/region/entity';
import type {Role} from '@/src/entities/role/entity';
import type {User} from '@/src/entities/user/entity';
import {
    AttributeIsNotConfirmable,
    ConfirmEmptyValueIsForbidden,
    EmptyImportSpreadsheetProductMasterCategoryValue,
    ForbiddenInConfirmableImport,
    ForbiddenToChangeConfirmedValueInNormalImport,
    ForbiddenToImportImageThroughConfirmedImport,
    ImportSpreadsheetAttributeMissedInProductInfoModel,
    InvalidImportSpreadsheetProductAttributeValue,
    InvalidImportSpreadsheetProductBooleanValue,
    InvalidImportSpreadsheetProductFrontCategoryValue,
    InvalidImportSpreadsheetProductIdentifierValue,
    InvalidImportSpreadsheetProductImageValue,
    InvalidImportSpreadsheetProductMasterCategoryValue,
    InvalidImportSpreadsheetProductNumberValue,
    InvalidImportSpreadsheetProductStatusValue,
    InvalidImportSpreadsheetProductValuesSize,
    InvalidImportSpreadsheetProductValueType,
    InvalidMultipleAttributeValueMaxSize,
    InvalidNumberIsIntegerAttributeValue,
    InvalidNumberIsNonNegativeAttributeValue,
    InvalidNumberMaxAttributeValue,
    InvalidNumberMinAttributeValue,
    InvalidRequiredAttributeValue,
    InvalidStringMaxAttributeValue,
    InvalidStringMinAttributeValue,
    serializeErrorToFlatArray,
    UnknownImportSpreadsheetProductAction
} from '@/src/errors';
import {OldValues} from 'service/import/old-values';
import {SpreadsheetAttributes} from 'service/import/spreadsheet-attributes';
import {FALSY_VALUE_SLUGS, RawValue, SpreadsheetProduct, TRUTHY_VALUE_SLUGS} from 'service/import/spreadsheet-product';
import {AttributeLang, AttributeType} from 'types/attribute';
import {ImportMode} from 'types/import';

seed(3);

describe('spreadsheet product', () => {
    let user: User;
    let region: Region;
    let role: Role;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();

        role = await TestFactory.createRole({product: {canEdit: true}});
        await TestFactory.createUserRole({userId: user.id, roleId: role.id});
    });

    it('should sanitize values', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, stringAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        const data = ['1', '<script>alert("xss");</script>'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {value: '&lt;script&gt;alert("xss");&lt;/script&gt;'}
        ]);

        for (const {data, type} of [
            {data: ['1', undefined], type: 'undefined'},
            {data: ['1', {}], type: 'object'},
            {data: ['1', 10], type: 'number'},
            {data: ['1', false], type: 'boolean'},
            {data: ['1', []], type: 'object'}
        ]) {
            expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
                {cast: 1, value: '1'},
                {error: new InvalidImportSpreadsheetProductValueType({type}).toFlatArray(), value: null}
            ]);
        }
    });

    it('should throw error on invalid values size', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isArray: true},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, stringAttr.code, stringAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data: RawValue[];

        data = ['1', 'bar'];
        expect(() => new SpreadsheetProduct({attributes, data, rules: role.rules})).toThrow(
            InvalidImportSpreadsheetProductValuesSize
        );

        data = ['1', 'bar', null, null];
        expect(() => new SpreadsheetProduct({attributes, data, rules: role.rules})).toThrow(
            InvalidImportSpreadsheetProductValuesSize
        );
    });

    it('should handle "update"/"insert" actions', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        let headers = [IDENTIFIER_HEADER, stringAttr.code];
        let attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data: RawValue[];

        data = ['1', 'bar'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[stringAttr.code]: 'bar'},
            description: {}
        });

        headers = [MASTER_CATEGORY_HEADER, stringAttr.code];
        attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        data = ['mc1', 'bar'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getResolved()).toEqual({
            action: 'insert',
            masterCategory: 'mc1',
            volume: {[stringAttr.code]: 'bar'},
            description: {}
        });

        data = ['', 'bar'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getValueIndex()).toEqual([
            {error: new UnknownImportSpreadsheetProductAction().toFlatArray(), value: null},
            {value: 'bar'}
        ]);

        headers = [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, stringAttr.code];
        attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        data = ['1', 'mc1', 'bar'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getResolved()).toEqual({
            action: 'update',
            masterCategory: 'mc1',
            identifier: 1,
            volume: {[stringAttr.code]: 'bar'},
            description: {}
        });

        headers = [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, stringAttr.code];
        attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        data = ['1', '', 'bar'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {error: new EmptyImportSpreadsheetProductMasterCategoryValue().toFlatArray(), value: null},
            {value: 'bar'}
        ]);

        headers = [IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER];
        attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        data = ['1', 'mc1'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            masterCategory: 'mc1',
            volume: {},
            description: {}
        });
    });

    it('should handle "identifier" property', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, stringAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data: RawValue[];

        data = ['', 'foo'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getValueIndex()).toEqual([
            {error: new UnknownImportSpreadsheetProductAction().toFlatArray(), value: null},
            {value: 'foo'}
        ]);

        data = ['1', 'bar'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[stringAttr.code]: 'bar'},
            description: {}
        });

        data = ['0', 'bar'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getValueIndex()).toEqual([
            {error: new UnknownImportSpreadsheetProductAction().toFlatArray(), value: '0'},
            {value: 'bar'}
        ]);
    });

    it('should handle "masterCategory" property', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        const headers = [MASTER_CATEGORY_HEADER, stringAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data: RawValue[];

        data = ['', 'foo'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getValueIndex()).toEqual([
            {error: new UnknownImportSpreadsheetProductAction().toFlatArray(), value: null},
            {value: 'foo'}
        ]);

        data = ['mc10', 'bar'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getResolved()).toEqual({
            action: 'insert',
            masterCategory: 'mc10',
            volume: {[stringAttr.code]: 'bar'},
            description: {}
        });
    });

    it('should handle front categories', async () => {
        const headers = [IDENTIFIER_HEADER, FRONT_CATEGORY_HEADER];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data: RawValue[];

        data = ['1', ''];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {value: null}
        ]);

        data = ['1', '1;2;'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {cast: ['1', '2'], value: '1;2'}
        ]);

        data = ['1', 'fc1'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getResolved()).toEqual({
            action: 'update',
            frontCategories: ['fc1'],
            identifier: 1,
            volume: {},
            description: {}
        });

        data = ['1', ' fc1 ; fc2; fc3 '];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getResolved()).toEqual({
            action: 'update',
            frontCategories: ['fc1', 'fc2', 'fc3'],
            identifier: 1,
            volume: {},
            description: {}
        });
    });

    it('should handle status', async () => {
        const headers = [IDENTIFIER_HEADER, STATUS_HEADER];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data: RawValue[];

        data = ['1', ''];
        let spreadsheetProduct = new SpreadsheetProduct({attributes, data, rules: role.rules});
        expect(spreadsheetProduct.getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {error: new InvalidImportSpreadsheetProductStatusValue().toFlatArray(), value: null}
        ]);
        expect(spreadsheetProduct.getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {},
            description: {}
        });

        data = ['1', 'foo'];
        spreadsheetProduct = new SpreadsheetProduct({attributes, data, rules: role.rules});
        expect(spreadsheetProduct.getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {error: new InvalidImportSpreadsheetProductStatusValue().toFlatArray(), value: 'foo'}
        ]);
        expect(spreadsheetProduct.getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {},
            description: {}
        });

        data = ['1', 'active'];
        spreadsheetProduct = new SpreadsheetProduct({attributes, data, rules: role.rules});
        expect(spreadsheetProduct.getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {cast: 'active', value: 'active'}
        ]);
        expect(spreadsheetProduct.getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            status: 'active',
            volume: {},
            description: {}
        });

        data = ['1', 'disabled'];
        spreadsheetProduct = new SpreadsheetProduct({attributes, data, rules: role.rules});
        expect(spreadsheetProduct.getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {cast: 'disabled', value: 'disabled'}
        ]);
        expect(spreadsheetProduct.getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            status: 'disabled',
            volume: {},
            description: {}
        });
    });

    it('should handle missed required value', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isValueRequired: true},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, stringAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        const data = ['1', null];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: stringAttr.code}),
                    new InvalidRequiredAttributeValue()
                ),
                value: null
            }
        ]);
    });

    it('should handle empty string values', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isArray: true},
            userId: user.id
        });

        let headers = [IDENTIFIER_HEADER, stringAttr.code];
        let attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        let data = ['1', [null, '', 'baz'].join(ARRAY_VALUE_DELIMITER)];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[stringAttr.code]: ['baz']},
            description: {}
        });

        headers = [IDENTIFIER_HEADER, stringAttr.code];
        attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        data = ['1', ' ; baz ; '];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[stringAttr.code]: ['baz']},
            description: {}
        });
    });

    it('should cast boolean value', async () => {
        const booleanAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.BOOLEAN, isArray: true},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, booleanAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        let data = ['1', TRUTHY_VALUE_SLUGS.join(ARRAY_VALUE_DELIMITER)];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[booleanAttr.code]: Array(TRUTHY_VALUE_SLUGS.length).fill(true)},
            description: {}
        });

        data = ['1', FALSY_VALUE_SLUGS.join(ARRAY_VALUE_DELIMITER)];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[booleanAttr.code]: Array(FALSY_VALUE_SLUGS.length).fill(false)},
            description: {}
        });

        data = ['1', 'baz'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: booleanAttr.code}),
                    new InvalidImportSpreadsheetProductBooleanValue()
                ),
                value: 'baz'
            }
        ]);
    });

    it('should cast number value', async () => {
        const numberAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.NUMBER, isArray: true},
            userId: user.id
        });

        let data = ['1', ['1', '5', null, '1.25', '6.00', '-15', '-12.7'].join(ARRAY_VALUE_DELIMITER)];
        let headers = [IDENTIFIER_HEADER, numberAttr.code];
        let attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[numberAttr.code]: [1, 5, 1.25, 6, -15, -12.7]},
            description: {}
        });

        headers = [IDENTIFIER_HEADER, numberAttr.code];
        attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        data = ['1', '7,63'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: numberAttr.code}),
                    new InvalidImportSpreadsheetProductNumberValue()
                ),
                value: '7,63'
            }
        ]);

        data = ['1', 'baz'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: numberAttr.code}),
                    new InvalidImportSpreadsheetProductNumberValue()
                ),
                value: 'baz'
            }
        ]);
    });

    it('should handle "MULTISELECT" values', async () => {
        const multiselectAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.MULTISELECT},
            userId: user.id
        });

        const {optionCodes} = await createSelectOptions({
            userId: user.id,
            attributeId: multiselectAttr.id
        });

        const headers = [IDENTIFIER_HEADER, multiselectAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        const data = ['1', ` ; ${optionCodes[0]}; ${optionCodes[1]}`];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {
                [multiselectAttr.code]: [optionCodes[0], optionCodes[1]]
            },
            description: {}
        });
    });

    it('should handle localizable values', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isValueLocalizable: true},
            userId: user.id
        });

        const textAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isArray: true, isValueLocalizable: true},
            userId: user.id
        });

        const headers = [
            IDENTIFIER_HEADER,
            `${stringAttr.code}|ru`,
            `${stringAttr.code}|en`,
            `${textAttr.code}|en`,
            `${textAttr.code}|ru`
        ];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: ['ru', 'en'] as never});
        await attributes.refineAttributes();

        const data = ['1', 'str_ru1', 'str_en1', 'text_en1;text_en2;text_en2', 'text_ru1'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {
                [stringAttr.code]: {en: 'str_en1', ru: 'str_ru1'},
                [textAttr.code]: {
                    en: ['text_en1', 'text_en2', 'text_en2'],
                    ru: ['text_ru1']
                }
            },
            description: {}
        });
    });

    it('should handle allowed identifiers', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, stringAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        let data = ['1', 'foo'];
        let identifiersAllowed = new Map([
            [2, {regionId: 1}],
            [3, {regionId: 1}]
        ]);
        expect(
            new SpreadsheetProduct({attributes, data, rules: role.rules, identifiersAllowed}).getValueIndex()
        ).toEqual([
            {error: new InvalidImportSpreadsheetProductIdentifierValue().toFlatArray(), value: '1'},
            {value: 'foo'}
        ]);

        data = ['1', 'foo'];
        identifiersAllowed = new Map([
            [1, {regionId: 1}],
            [2, {regionId: 1}],
            [3, {regionId: 1}]
        ]);
        expect(
            new SpreadsheetProduct({attributes, data, rules: role.rules, identifiersAllowed}).getValueIndex()
        ).toEqual([{cast: 1, value: '1'}, {value: 'foo'}]);
    });

    it('should handle allowed master categories', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });
        const infoModel = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });

        const headers = [MASTER_CATEGORY_HEADER, stringAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        let data = ['mc1', 'foo'];
        let masterCategoriesAllowed = new Map([
            ['mc2', {id: 2, infoModel}],
            ['mc3', {id: 3, infoModel}]
        ]);
        expect(
            new SpreadsheetProduct({attributes, data, rules: role.rules, masterCategoriesAllowed}).getValueIndex()
        ).toEqual([
            {error: new InvalidImportSpreadsheetProductMasterCategoryValue().toFlatArray(), value: 'mc1'},
            {value: 'foo'}
        ]);

        data = ['mc1', 'foo'];
        masterCategoriesAllowed = new Map([
            ['mc1', {id: 1, infoModel}],
            ['mc2', {id: 1, infoModel}],
            ['mc3', {id: 1, infoModel}]
        ]);
        expect(
            new SpreadsheetProduct({attributes, data, rules: role.rules, masterCategoriesAllowed}).getValueIndex()
        ).toEqual([{cast: 'mc1', value: 'mc1'}, {value: 'foo'}]);
    });

    it('should handle allowed front categories', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, stringAttr.code, FRONT_CATEGORY_HEADER];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        const data = ['1', 'foo', 'fc1;fc2'];
        let frontCategoriesAllowed = new Map([
            ['fc2', {id: 1}],
            ['fc3', {id: 1}]
        ]);
        expect(
            new SpreadsheetProduct({attributes, data, rules: role.rules, frontCategoriesAllowed}).getValueIndex()
        ).toEqual([
            {cast: 1, value: '1'},
            {value: 'foo'},
            {
                error: new InvalidImportSpreadsheetProductFrontCategoryValue({codes: 'fc1'}).toFlatArray(),
                value: 'fc1;fc2'
            }
        ]);

        const identifiersAllowed = new Map([[1, {}]]);
        frontCategoriesAllowed = new Map([
            ['fc1', {id: 1}],
            ['fc2', {id: 1}],
            ['fc3', {id: 1}]
        ]);
        expect(
            new SpreadsheetProduct({
                attributes,
                data,
                rules: role.rules,
                identifiersAllowed,
                frontCategoriesAllowed
            }).getValueIndex()
        ).toEqual([{cast: 1, value: '1'}, {value: 'foo'}, {cast: ['fc1', 'fc2'], value: 'fc1;fc2'}]);
    });

    it('should handle allowed attributes: master category', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        const headers = [MASTER_CATEGORY_HEADER, stringAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        const data = ['mc1', 'bar'];
        const attributesAllowed = {
            masterCategory: new Map([['mc1', new Set(['qux'])]]),
            product: new Map()
        };
        let spreadsheetProduct = new SpreadsheetProduct({attributes, data, rules: role.rules, attributesAllowed});
        expect(spreadsheetProduct.getValueIndex()).toEqual([
            {cast: 'mc1', value: 'mc1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: stringAttr.code}),
                    new ImportSpreadsheetAttributeMissedInProductInfoModel()
                ),
                value: 'bar'
            }
        ]);
        expect(spreadsheetProduct.getResolved()).toEqual({
            action: 'insert',
            masterCategory: 'mc1',
            volume: {},
            description: {}
        });

        attributesAllowed.masterCategory = new Map([['mc1', new Set([stringAttr.code])]]);
        spreadsheetProduct = new SpreadsheetProduct({attributes, data, rules: role.rules, attributesAllowed});
        expect(spreadsheetProduct.getValueIndex()).toEqual([{cast: 'mc1', value: 'mc1'}, {value: 'bar'}]);
        expect(spreadsheetProduct.getResolved()).toEqual({
            action: 'insert',
            masterCategory: 'mc1',
            volume: {[stringAttr.code]: 'bar'},
            description: {}
        });
    });

    it('should handle allowed attributes: identifier', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, stringAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        const data = ['2', 'foo'];
        const attributesAllowed = {
            masterCategory: new Map(),
            product: new Map([[2, new Set(['baz'])]])
        };
        let spreadsheetProduct = new SpreadsheetProduct({attributes, data, rules: role.rules, attributesAllowed});
        expect(spreadsheetProduct.getValueIndex()).toEqual([
            {cast: 2, value: '2'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: stringAttr.code}),
                    new ImportSpreadsheetAttributeMissedInProductInfoModel()
                ),
                value: 'foo'
            }
        ]);
        expect(spreadsheetProduct.getResolved()).toEqual({
            action: 'update',
            identifier: 2,
            volume: {},
            description: {}
        });

        attributesAllowed.product = new Map([[2, new Set([stringAttr.code])]]);
        spreadsheetProduct = new SpreadsheetProduct({attributes, data, rules: role.rules, attributesAllowed});
        expect(spreadsheetProduct.getValueIndex()).toEqual([{cast: 2, value: '2'}, {value: 'foo'}]);
        expect(spreadsheetProduct.getResolved()).toEqual({
            action: 'update',
            identifier: 2,
            volume: {[stringAttr.code]: 'foo'},
            description: {}
        });
    });

    it('should handle image urls', async () => {
        const imageAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.IMAGE},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, imageAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        let data = ['1', '/some/url'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules}).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: imageAttr.code}),
                    new InvalidImportSpreadsheetProductImageValue()
                ),
                value: '/some/url'
            }
        ]);

        data = ['1', '/good/path'];
        let images = {
            data: new Map([
                [
                    '/good/path',
                    {
                        url: '/some/url',
                        relPath: 'some/path',
                        meta: {name: 'image.png', size: 2400, width: 900, height: 900}
                    }
                ]
            ]),
            used: new Set<string>(),
            valueToName: new Map([['/some/url', '/good/path']])
        };
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules, images}).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {cast: '/some/url', value: '/good/path'}
        ]);

        data = ['1', '/bad/path'];
        images = {data: new Map(), used: new Set<string>(), valueToName: new Map()};
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules, images}).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: imageAttr.code}),
                    new InvalidImportSpreadsheetProductImageValue()
                ),
                value: '/bad/path'
            }
        ]);
    });

    it('should handle untouched image urls', async () => {
        const imageAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.IMAGE},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, imageAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        const oldValues = new OldValues();
        oldValues.set({identifier: 1, key: imageAttr.code}, {value: '/some/url', isConfirmed: false});

        const data = ['1', '/some/url'];
        let spreadsheetProduct = new SpreadsheetProduct({attributes, data, rules: role.rules, oldValues});
        expect(spreadsheetProduct.getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {cast: '/some/url', value: '/some/url'}
        ]);
        expect(spreadsheetProduct.getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[imageAttr.code]: '/some/url'},
            description: {}
        });

        // Without old values:
        spreadsheetProduct = new SpreadsheetProduct({attributes, data, rules: role.rules});
        expect(spreadsheetProduct.getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: imageAttr.code}),
                    new InvalidImportSpreadsheetProductImageValue()
                ),
                value: '/some/url'
            }
        ]);
        expect(spreadsheetProduct.getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {},
            description: {}
        });
    });

    it('should handle untouched url template', async () => {
        const imageAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.IMAGE},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, imageAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        const oldValues = new OldValues();
        oldValues.set({identifier: 1, key: imageAttr.code}, {value: '/templated/url/%s', isConfirmed: false});

        const data = ['1', '/templated/url/orig'];
        const spreadsheetProduct = new SpreadsheetProduct({attributes, data, rules: role.rules, oldValues});
        expect(spreadsheetProduct.getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {cast: '/templated/url/%s', value: '/templated/url/orig'}
        ]);
        expect(spreadsheetProduct.getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[imageAttr.code]: '/templated/url/%s'},
            description: {}
        });
    });

    it('should handle empty multiple attribute', async () => {
        const user = await TestFactory.createUser();

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isArray: true},
            userId: user.id
        });
        const numberAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.NUMBER, isArray: true},
            userId: user.id
        });
        const booleanAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.BOOLEAN, isArray: true},
            userId: user.id
        });
        const textAttrA = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isArray: true, isValueLocalizable: true},
            userId: user.id
        });
        const textAttrB = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isArray: true, isValueLocalizable: true},
            userId: user.id
        });
        const imageAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.IMAGE, isArray: true, code: `image_${uuid}`},
            userId: user.id
        });
        const multiselectAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.MULTISELECT},
            userId: user.id
        });

        const headers = [
            IDENTIFIER_HEADER,
            stringAttr.code,
            numberAttr.code,
            booleanAttr.code,
            `${textAttrA.code}|ru`,
            `${textAttrB.code}|fr`,
            `${textAttrB.code}|en`,
            imageAttr.code,
            multiselectAttr.code
        ];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: ['ru', 'fr', 'en'] as never});
        await attributes.refineAttributes();
        expect(attributes.getAttrIndex()).toEqual([
            {attr: {actions: ['default'], key: 'id', pos: [0], type: 'identifier'}, header: 'id', lang: undefined},
            {
                attr: {actions: ['default'], isArray: true, key: stringAttr.code, pos: [1], type: 'string'},
                header: stringAttr.code,
                lang: undefined
            },
            {
                attr: {actions: ['default'], isArray: true, key: numberAttr.code, pos: [2], type: 'number'},
                header: numberAttr.code,
                lang: undefined
            },
            {
                attr: {actions: ['default'], isArray: true, key: booleanAttr.code, pos: [3], type: 'boolean'},
                header: booleanAttr.code,
                lang: undefined
            },
            {
                attr: {
                    actions: ['default'],
                    isArray: true,
                    isValueLocalizable: true,
                    key: textAttrA.code,
                    pos: [4],
                    type: 'string'
                },
                header: `${textAttrA.code}|ru`,
                lang: 'ru'
            },
            {
                attr: {
                    actions: ['default', 'default'],
                    isArray: true,
                    isValueLocalizable: true,
                    key: textAttrB.code,
                    pos: [5, 6],
                    type: 'string'
                },
                header: `${textAttrB.code}|fr`,
                lang: 'fr'
            },
            {
                attr: {
                    actions: ['default', 'default'],
                    isArray: true,
                    isValueLocalizable: true,
                    key: textAttrB.code,
                    pos: [5, 6],
                    type: 'string'
                },
                header: `${textAttrB.code}|en`,
                lang: 'en'
            },
            {
                attr: {actions: ['default'], isArray: true, key: imageAttr.code, pos: [7], type: 'image'},
                header: imageAttr.code,
                lang: undefined
            },
            {
                attr: {
                    actions: ['default'],
                    key: multiselectAttr.code,
                    pos: [8],
                    selectOptions: new Set(),
                    type: 'multiselect'
                },
                header: multiselectAttr.code,
                lang: undefined
            }
        ]);

        const data = ['1', '', '', '', '', '', 'a;b;c', '', ''];
        const spreadsheetProduct = new SpreadsheetProduct({attributes, data, rules: role.rules});
        expect(spreadsheetProduct.getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {value: null},
            {value: null},
            {value: null},
            {value: null},
            {value: null},
            {cast: ['a', 'b', 'c'], value: 'a;b;c'},
            {value: null},
            {value: null}
        ]);
        expect(spreadsheetProduct.getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {
                [textAttrA.code]: {ru: null},
                [textAttrB.code]: {en: ['a', 'b', 'c'], fr: null},
                [stringAttr.code]: null,
                [numberAttr.code]: null,
                [booleanAttr.code]: null,
                [imageAttr.code]: null,
                [multiselectAttr.code]: null
            },
            description: {}
        });
    });

    it('should handle number value "min" property', async () => {
        const numberAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.NUMBER, properties: {min: 0}},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, numberAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data = ['1', '-1'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: numberAttr.code}),
                    new InvalidNumberMinAttributeValue({value: -1, min: 0})
                ),
                value: '-1'
            }
        ]);

        data = ['1', '0'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[numberAttr.code]: 0},
            description: {}
        });
    });

    it('should handle number multiple value "min" property', async () => {
        const numberAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.NUMBER, isArray: true, properties: {min: 0}},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, numberAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data = ['1', '0;-1'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: numberAttr.code}),
                    new InvalidNumberMinAttributeValue({value: -1, min: 0})
                ),
                value: '0;-1'
            }
        ]);

        data = ['1', '0;10'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[numberAttr.code]: [0, 10]},
            description: {}
        });
    });

    it('should handle number value "max" property', async () => {
        const numberAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.NUMBER, properties: {max: 10}},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, numberAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data = ['1', '11'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: numberAttr.code}),
                    new InvalidNumberMaxAttributeValue({value: 11, max: 10})
                ),
                value: '11'
            }
        ]);

        data = ['1', '10'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[numberAttr.code]: 10},
            description: {}
        });
    });

    it('should handle number multiple value "max" property', async () => {
        const numberAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.NUMBER, isArray: true, properties: {max: 10}},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, numberAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data = ['1', '0;11'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: numberAttr.code}),
                    new InvalidNumberMaxAttributeValue({value: 11, max: 10})
                ),
                value: '0;11'
            }
        ]);

        data = ['1', '0;10'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[numberAttr.code]: [0, 10]},
            description: {}
        });
    });

    it('should handle number value "isInteger" property', async () => {
        const numberAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.NUMBER, properties: {isInteger: true}},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, numberAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data = ['1', '0.25'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: numberAttr.code}),
                    new InvalidNumberIsIntegerAttributeValue({value: 0.25})
                ),
                value: '0.25'
            }
        ]);

        data = ['1', '25'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[numberAttr.code]: 25},
            description: {}
        });
    });

    it('should handle number multiple value "isInteger" property', async () => {
        const numberAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.NUMBER, isArray: true, properties: {isInteger: true}},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, numberAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data = ['1', '0;0.25'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: numberAttr.code}),
                    new InvalidNumberIsIntegerAttributeValue({value: 0.25})
                ),
                value: '0;0.25'
            }
        ]);

        data = ['1', '0;10'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[numberAttr.code]: [0, 10]},
            description: {}
        });
    });

    it('should handle number value "isNonNegative" property', async () => {
        const numberAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.NUMBER, properties: {isNonNegative: true}},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, numberAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data = ['1', '-0.25'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: numberAttr.code}),
                    new InvalidNumberIsNonNegativeAttributeValue({value: -0.25})
                ),
                value: '-0.25'
            }
        ]);

        data = ['1', '25'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[numberAttr.code]: 25},
            description: {}
        });
    });

    it('should handle number multiple value "isNonNegative" property', async () => {
        const numberAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.NUMBER, isArray: true, properties: {isNonNegative: true}},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, numberAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data = ['1', '0;-0.25'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: numberAttr.code}),
                    new InvalidNumberIsNonNegativeAttributeValue({value: -0.25})
                ),
                value: '0;-0.25'
            }
        ]);

        data = ['1', '0;10'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[numberAttr.code]: [0, 10]},
            description: {}
        });
    });

    it('should handle string value "min" property', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, properties: {min: 3}},
            userId: user.id
        });
        const textAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.TEXT, properties: {min: 3}},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, stringAttr.code, textAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data = ['1', 'fo', 'ba'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: stringAttr.code}),
                    new InvalidStringMinAttributeValue({value: 'fo', min: 3})
                ),
                value: 'fo'
            },
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: textAttr.code}),
                    new InvalidStringMinAttributeValue({value: 'ba', min: 3})
                ),
                value: 'ba'
            }
        ]);

        data = ['1', 'foo', 'baz'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[stringAttr.code]: 'foo', [textAttr.code]: 'baz'},
            description: {}
        });
    });

    it('should handle string multiple value "min" property', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isArray: true, properties: {min: 3}},
            userId: user.id
        });
        const textAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.TEXT, isArray: true, properties: {min: 3}},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, stringAttr.code, textAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data = ['1', 'bar;fo', 'baz;qu'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: stringAttr.code}),
                    new InvalidStringMinAttributeValue({value: 'fo', min: 3})
                ),
                value: 'bar;fo'
            },
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: textAttr.code}),
                    new InvalidStringMinAttributeValue({value: 'qu', min: 3})
                ),
                value: 'baz;qu'
            }
        ]);

        data = ['1', 'bar;foo', 'baz;qux'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[stringAttr.code]: ['bar', 'foo'], [textAttr.code]: ['baz', 'qux']},
            description: {}
        });
    });

    it('should handle string localized value "min" property', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isValueLocalizable: true, properties: {min: 3}},
            userId: user.id
        });
        const textAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.TEXT, isValueLocalizable: true, properties: {min: 3}},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, `${stringAttr.code}|ru`, `${textAttr.code}|en`];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: ['ru', 'en'] as never});
        await attributes.refineAttributes();
        let data = ['1', 'fo', 'ba'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: stringAttr.code}),
                    new InvalidStringMinAttributeValue({value: 'fo', min: 3})
                ),
                value: 'fo'
            },
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: textAttr.code}),
                    new InvalidStringMinAttributeValue({value: 'ba', min: 3})
                ),
                value: 'ba'
            }
        ]);

        data = ['1', 'foo', 'baz'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[stringAttr.code]: {ru: 'foo'}, [textAttr.code]: {en: 'baz'}},
            description: {}
        });
    });

    it('should handle string value "max" property', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, properties: {max: 2}},
            userId: user.id
        });
        const textAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.TEXT, properties: {max: 2}},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, stringAttr.code, textAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data = ['1', 'foo', 'baz'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: stringAttr.code}),
                    new InvalidStringMaxAttributeValue({value: 'foo', max: 2})
                ),
                value: 'foo'
            },
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: textAttr.code}),
                    new InvalidStringMaxAttributeValue({value: 'baz', max: 2})
                ),
                value: 'baz'
            }
        ]);

        data = ['1', 'fo', 'ba'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[stringAttr.code]: 'fo', [textAttr.code]: 'ba'},
            description: {}
        });
    });

    it('should handle string multiple value "max" property', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isArray: true, properties: {max: 2}},
            userId: user.id
        });
        const textAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.TEXT, isArray: true, properties: {max: 2}},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, stringAttr.code, textAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data = ['1', 'ba;foo', 'ba;qux'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: stringAttr.code}),
                    new InvalidStringMaxAttributeValue({value: 'foo', max: 2})
                ),
                value: 'ba;foo'
            },
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: textAttr.code}),
                    new InvalidStringMaxAttributeValue({value: 'qux', max: 2})
                ),
                value: 'ba;qux'
            }
        ]);

        data = ['1', 'ba;fo', 'ba;qu'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[stringAttr.code]: ['ba', 'fo'], [textAttr.code]: ['ba', 'qu']},
            description: {}
        });
    });

    it('should handle string localized value "max" property', async () => {
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isValueLocalizable: true, properties: {max: 2}},
            userId: user.id
        });
        const textAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.TEXT, isValueLocalizable: true, properties: {max: 2}},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, `${stringAttr.code}|ru`, `${textAttr.code}|en`];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: ['ru', 'en'] as never});
        await attributes.refineAttributes();
        let data = ['1', 'foo', 'baz'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: stringAttr.code}),
                    new InvalidStringMaxAttributeValue({value: 'foo', max: 2})
                ),
                value: 'foo'
            },
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: textAttr.code}),
                    new InvalidStringMaxAttributeValue({value: 'baz', max: 2})
                ),
                value: 'baz'
            }
        ]);

        data = ['1', 'fo', 'ba'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {[stringAttr.code]: {ru: 'fo'}, [textAttr.code]: {en: 'ba'}},
            description: {}
        });
    });

    it('should handle "maxArraySize" property of the value', async () => {
        const numberAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.NUMBER, isArray: true, properties: {maxArraySize: 1}},
            userId: user.id
        });
        const booleanAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.BOOLEAN, isArray: true, properties: {maxArraySize: 1}},
            userId: user.id
        });
        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isArray: true, properties: {maxArraySize: 1}},
            userId: user.id
        });
        const textAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.TEXT, isArray: true, properties: {maxArraySize: 1}},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, numberAttr.code, booleanAttr.code, stringAttr.code, textAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();
        let data = ['1', '1;2', 'yes;no', 'ba;foo', 'ba;qux'];

        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: numberAttr.code}),
                    new InvalidMultipleAttributeValueMaxSize({list: '1; 2', max: 1})
                ),
                value: '1;2'
            },
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: booleanAttr.code}),
                    new InvalidMultipleAttributeValueMaxSize({list: 'true; false', max: 1})
                ),
                value: 'yes;no'
            },
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: stringAttr.code}),
                    new InvalidMultipleAttributeValueMaxSize({list: 'ba; foo', max: 1})
                ),
                value: 'ba;foo'
            },
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: textAttr.code}),
                    new InvalidMultipleAttributeValueMaxSize({list: 'ba; qux', max: 1})
                ),
                value: 'ba;qux'
            }
        ]);

        data = ['1', '1', 'yes', 'ba', 'ba'];
        expect(new SpreadsheetProduct({attributes, data, rules: role.rules} as never).getResolved()).toEqual({
            action: 'update',
            identifier: 1,
            volume: {
                [numberAttr.code]: [1],
                [booleanAttr.code]: [true],
                [stringAttr.code]: ['ba'],
                [textAttr.code]: ['ba']
            },
            description: {}
        });
    });

    // --- <Подтвержденность в нормальном импорте> ---

    it('ignore confirmable, not confirmed values in normal mode', async () => {
        const booleanAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.BOOLEAN, isConfirmable: true},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, booleanAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        const oldValues = new OldValues();
        oldValues.set({identifier: 1, key: booleanAttr.code}, {value: false, isConfirmed: false});

        const data = ['1', 'true'];
        expect(new SpreadsheetProduct({attributes, data, oldValues, rules: role.rules}).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {cast: true, value: 'true'}
        ]);
    });

    it('ignore confirmed values in normal mode if value does not change', async () => {
        const booleanAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.BOOLEAN, isConfirmable: true},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, booleanAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        const oldValues = new OldValues();
        oldValues.set({identifier: 1, key: booleanAttr.code}, {value: false, isConfirmed: true});

        const data = ['1', 'false'];
        expect(new SpreadsheetProduct({attributes, data, oldValues, rules: role.rules}).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {cast: false, value: 'false'}
        ]);
    });

    it('should throw error on attempt of renew confirmed attribute value without confirm/decline mode', async () => {
        const booleanAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.BOOLEAN, isArray: true},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, booleanAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        const oldValues = new OldValues();
        oldValues.set({identifier: 1, key: booleanAttr.code}, {value: true, isConfirmed: true});

        const data = ['1', 'false'];
        expect(new SpreadsheetProduct({attributes, data, oldValues, rules: role.rules}).getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(new ForbiddenToChangeConfirmedValueInNormalImport()),
                value: 'false'
            }
        ]);
    });

    it('should work separately with each lang of localizable attribute', async () => {
        const localizedAttribute = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isValueLocalizable: true},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, `${localizedAttribute.code}|ru`, `${localizedAttribute.code}|en`];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: ['ru', 'en'] as never});
        await attributes.refineAttributes();

        const oldValues = new OldValues();
        oldValues.set(
            {identifier: 1, key: localizedAttribute.code},
            {value: 'rus text', lang: AttributeLang.RU, isConfirmed: true}
        );
        oldValues.set(
            {identifier: 1, key: localizedAttribute.code},
            {value: 'en text', lang: AttributeLang.EN, isConfirmed: false}
        );

        // Можно изменить значение у неподтвержденной локали
        const firstCaseData = ['1', 'rus text', 'english text'];
        expect(
            new SpreadsheetProduct({attributes, data: firstCaseData, oldValues, rules: role.rules}).getValueIndex()
        ).toEqual([{cast: 1, value: '1'}, {value: 'rus text'}, {value: 'english text'}]);

        // Нельзя изменить значение у подтвержденной локали
        const secondCaseData = ['1', 'russian text', 'english text'];
        expect(
            new SpreadsheetProduct({attributes, data: secondCaseData, oldValues, rules: role.rules}).getValueIndex()
        ).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(new ForbiddenToChangeConfirmedValueInNormalImport()),
                value: 'russian text'
            },
            {value: 'english text'}
        ]);
    });

    // --- </Подтвержденность в нормальном импорте> ---

    // --- <Подтвержденность в импорте подтверждения / расподтверждения>

    /* eslint-disable max-len */
    it('should throw error if excel had unconfirmable attributes or meta, master/front-categories, status', async () => {
        const confirmableAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.BOOLEAN, isConfirmable: true},
            userId: user.id
        });

        const unconfirmableAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.BOOLEAN},
            userId: user.id
        });

        const headers = [
            IDENTIFIER_HEADER,
            STATUS_HEADER,
            IS_META_HEADER,
            MASTER_CATEGORY_HEADER,
            FRONT_CATEGORY_HEADER,
            confirmableAttr.code,
            unconfirmableAttr.code
        ];

        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        const data = ['1', 'active', 'f', 'mc1', 'fc1;fc2', 'true', 'false'];

        expect(
            new SpreadsheetProduct({attributes, data, mode: ImportMode.CONFIRM, rules: role.rules}).getValueIndex()
        ).toEqual([
            {cast: 1, value: '1'},
            {error: serializeErrorToFlatArray(new ForbiddenInConfirmableImport()), value: 'active'},
            {error: serializeErrorToFlatArray(new ForbiddenInConfirmableImport()), value: 'f'},
            {error: serializeErrorToFlatArray(new ForbiddenInConfirmableImport()), value: 'mc1'},
            {error: serializeErrorToFlatArray(new ForbiddenInConfirmableImport()), value: 'fc1;fc2'},
            {cast: true, value: 'true'},
            {
                error: serializeErrorToFlatArray(
                    new InvalidImportSpreadsheetProductAttributeValue({key: unconfirmableAttr.code}),
                    new AttributeIsNotConfirmable()
                ),
                value: 'false'
            }
        ]);
    });

    it('should throw error on image attr in confirmed import', async () => {
        const imageAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.IMAGE, isConfirmable: true},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, imageAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        const oldValues = new OldValues();
        oldValues.set({identifier: 1, key: imageAttr.code}, {value: '/some/url', isConfirmed: true});

        const data = ['1', '/good/path'];
        const images = {
            data: new Map([
                [
                    '/good/path',
                    {
                        url: '/some/url1',
                        relPath: 'some/path',
                        meta: {name: 'image.png', size: 2400, width: 900, height: 900}
                    }
                ]
            ]),
            used: new Set<string>(),
            valueToName: new Map([['/some/url', '/good/path']])
        };
        let spreadsheetProduct = new SpreadsheetProduct({
            attributes,
            data,
            oldValues,
            mode: ImportMode.CONFIRM,
            images,
            rules: role.rules
        });
        expect(spreadsheetProduct.getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(new ForbiddenToImportImageThroughConfirmedImport()),
                value: '/good/path'
            }
        ]);

        spreadsheetProduct = new SpreadsheetProduct({
            attributes,
            data,
            oldValues,
            images,
            mode: ImportMode.DECLINE,
            rules: role.rules
        });
        expect(spreadsheetProduct.getValueIndex()).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(new ForbiddenToImportImageThroughConfirmedImport()),
                value: '/good/path'
            }
        ]);
    });

    it('should throw error on attempt of confirm empty value', async () => {
        const confirmableAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.SELECT, isConfirmable: true},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, confirmableAttr.code];
        const attributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await attributes.refineAttributes();

        const oldValues = new OldValues();
        oldValues.set({identifier: 1, key: confirmableAttr.code}, {value: 'vunshPunsh', isConfirmed: true});

        const data = ['1', ''];
        expect(
            new SpreadsheetProduct({
                attributes,
                data,
                oldValues,
                mode: ImportMode.CONFIRM,
                rules: role.rules
            }).getValueIndex()
        ).toEqual([
            {cast: 1, value: '1'},
            {
                error: serializeErrorToFlatArray(new ConfirmEmptyValueIsForbidden()),
                value: null
            }
        ]);

        // --- </Подтвержденность в импорте подтверждения / расподтверждения>
    });
});
