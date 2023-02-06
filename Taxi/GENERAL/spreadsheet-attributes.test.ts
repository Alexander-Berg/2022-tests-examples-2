import {seed, uuid} from 'casual';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {createSelectOptions} from 'tests/unit/util';

import {FRONT_CATEGORY_HEADER, IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER, STATUS_HEADER} from '@/src/constants/import';
import {
    DuplicatesSpreadsheetHeader,
    InvalidImportSpreadsheetAttributeIsArray,
    InvalidImportSpreadsheetAttributeLocalization,
    InvalidImportSpreadsheetHeaders,
    InvalidImportSpreadsheetLang,
    MissedImportSpreadsheetRequiredHeaders,
    MissedImportSpreadsheetStoredAttribute
} from '@/src/errors';
import {SpreadsheetAttributes} from 'service/import/spreadsheet-attributes';
import {AttributeType} from 'types/attribute';

seed(3);

describe('spreadsheet attributes', () => {
    it('should throw error on invalid header values', async () => {
        expect(
            () => new SpreadsheetAttributes({headers: [IDENTIFIER_HEADER, ''], availableLangsForRegion: []})
        ).toThrow(InvalidImportSpreadsheetHeaders);

        expect(
            () => new SpreadsheetAttributes({headers: [IDENTIFIER_HEADER, true], availableLangsForRegion: []})
        ).toThrow(InvalidImportSpreadsheetHeaders);

        expect(() => new SpreadsheetAttributes({headers: [IDENTIFIER_HEADER, 1], availableLangsForRegion: []})).toThrow(
            InvalidImportSpreadsheetHeaders
        );

        expect(
            () => new SpreadsheetAttributes({headers: [IDENTIFIER_HEADER, undefined], availableLangsForRegion: []})
        ).toThrow(InvalidImportSpreadsheetHeaders);

        expect(
            () => new SpreadsheetAttributes({headers: [IDENTIFIER_HEADER, null], availableLangsForRegion: []})
        ).toThrow(InvalidImportSpreadsheetHeaders);
    });

    it('should throw error on not enough headers', async () => {
        const headers = [IDENTIFIER_HEADER];

        expect(() => new SpreadsheetAttributes({headers, availableLangsForRegion: []})).toThrow(
            InvalidImportSpreadsheetHeaders
        );
    });

    it('should sanitize headers', async () => {
        const headers = [IDENTIFIER_HEADER, '<script>alert("xss");</script>'];

        expect(new SpreadsheetAttributes({headers, availableLangsForRegion: []}).getAttrDict()).toEqual({
            [IDENTIFIER_HEADER]: {actions: ['default'], key: IDENTIFIER_HEADER, type: 'identifier', pos: [0]},
            'lt;script&gt;alert("xss");&lt;/script&gt;': {
                actions: ['add'],
                key: 'lt;script&gt;alert("xss");&lt;/script&gt;',
                type: 'unknown',
                pos: [1]
            }
        });
    });

    it('should handle required headers', async () => {
        let headers = ['foo', 'bar'];

        expect(() => new SpreadsheetAttributes({headers, availableLangsForRegion: []})).toThrow(
            MissedImportSpreadsheetRequiredHeaders
        );

        headers = [IDENTIFIER_HEADER, 'bar'];
        expect(new SpreadsheetAttributes({headers, availableLangsForRegion: []}).getAttrDict()).toEqual({
            [IDENTIFIER_HEADER]: {actions: ['default'], key: IDENTIFIER_HEADER, type: 'identifier', pos: [0]},
            bar: {actions: ['default'], key: 'bar', type: 'unknown', pos: [1]}
        });

        headers = [MASTER_CATEGORY_HEADER, 'bar'];
        expect(new SpreadsheetAttributes({headers, availableLangsForRegion: []}).getAttrDict()).toEqual({
            [MASTER_CATEGORY_HEADER]: {
                actions: ['default'],
                key: MASTER_CATEGORY_HEADER,
                type: 'masterCategory',
                pos: [0]
            },
            bar: {actions: ['default'], key: 'bar', type: 'unknown', pos: [1]}
        });
    });

    it('should throw error on ident header dupe', async () => {
        const headers = [IDENTIFIER_HEADER, IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER];

        expect(new SpreadsheetAttributes({headers, availableLangsForRegion: []}).getAttrIndex()).toEqual([
            {error: new DuplicatesSpreadsheetHeader({key: 'id'}).toFlatArray(), header: 'id'},
            {error: new DuplicatesSpreadsheetHeader({key: 'id'}).toFlatArray(), header: 'id'},
            {
                attr: {actions: ['default'], key: 'master_category', pos: [2], type: 'masterCategory'},
                header: 'master_category',
                lang: undefined
            }
        ]);
    });

    it('should throw error on master category header dupe', async () => {
        const headers = [MASTER_CATEGORY_HEADER, MASTER_CATEGORY_HEADER, IDENTIFIER_HEADER];

        expect(new SpreadsheetAttributes({headers, availableLangsForRegion: []}).getAttrIndex()).toEqual([
            {
                error: new DuplicatesSpreadsheetHeader({key: 'master_category'}).toFlatArray(),
                header: 'master_category'
            },
            {
                error: new DuplicatesSpreadsheetHeader({key: 'master_category'}).toFlatArray(),
                header: 'master_category'
            },
            {attr: {actions: ['default'], key: 'id', pos: [2], type: 'identifier'}, header: 'id', lang: undefined}
        ]);
    });

    it('should throw error on front category header dupe', async () => {
        const headers = [IDENTIFIER_HEADER, FRONT_CATEGORY_HEADER, FRONT_CATEGORY_HEADER];

        expect(new SpreadsheetAttributes({headers, availableLangsForRegion: []}).getAttrIndex()).toEqual([
            {attr: {actions: ['default'], key: 'id', pos: [0], type: 'identifier'}, header: 'id', lang: undefined},
            {
                error: new DuplicatesSpreadsheetHeader({key: 'front_category'}).toFlatArray(),
                header: 'front_category'
            },
            {
                error: new DuplicatesSpreadsheetHeader({key: 'front_category'}).toFlatArray(),
                header: 'front_category'
            }
        ]);
    });

    it('should throw error on status header dupe', async () => {
        const headers = [IDENTIFIER_HEADER, STATUS_HEADER, STATUS_HEADER];

        expect(new SpreadsheetAttributes({headers, availableLangsForRegion: []}).getAttrIndex()).toEqual([
            {attr: {actions: ['default'], key: 'id', pos: [0], type: 'identifier'}, header: 'id', lang: undefined},
            {
                error: new DuplicatesSpreadsheetHeader({key: 'status'}).toFlatArray(),
                header: 'status'
            },
            {
                error: new DuplicatesSpreadsheetHeader({key: 'status'}).toFlatArray(),
                header: 'status'
            }
        ]);
    });

    it('should throw error on invalid language', async () => {
        const headers = [IDENTIFIER_HEADER, 'title|FOO'];

        expect(new SpreadsheetAttributes({headers, availableLangsForRegion: []}).getAttrIndex()).toEqual([
            {attr: {actions: ['default'], key: 'id', pos: [0], type: 'identifier'}, header: 'id', lang: undefined},
            {
                error: new InvalidImportSpreadsheetLang({header: 'title|FOO', lang: 'FOO'}).toFlatArray(),
                header: 'title|FOO'
            }
        ]);
    });

    it('should detect header language', () => {
        const headers = ['title', 'title|ru', 'title', 'title|fr', 'title|en', 'title|en', MASTER_CATEGORY_HEADER];

        const spreadsheetAttributes = new SpreadsheetAttributes({
            headers,
            availableLangsForRegion: ['ru', 'fr', 'en'] as never
        });
        const dict = spreadsheetAttributes.getAttrDict();
        const index = spreadsheetAttributes.getAttrIndex();

        const titleAttr = {
            actions: Array.from({length: 6}).fill('default'),
            key: 'title',
            type: 'unknown',
            pos: [0, 1, 2, 3, 4, 5]
        };

        const masterCategoryAttr = {
            actions: ['default'],
            key: MASTER_CATEGORY_HEADER,
            type: 'masterCategory',
            pos: [6]
        };

        expect(dict).toEqual({
            title: titleAttr,
            [MASTER_CATEGORY_HEADER]: masterCategoryAttr
        });

        expect(index).toEqual([
            {attr: titleAttr, header: headers[0], lang: undefined},
            {attr: titleAttr, header: headers[1], lang: 'ru'},
            {attr: titleAttr, header: headers[2], lang: undefined},
            {attr: titleAttr, header: headers[3], lang: 'fr'},
            {attr: titleAttr, header: headers[4], lang: 'en'},
            {attr: titleAttr, header: headers[5], lang: 'en'},
            {attr: masterCategoryAttr, header: MASTER_CATEGORY_HEADER}
        ]);
    });

    it('should refine unknown attributes', async () => {
        const user = await TestFactory.createUser();

        const numberAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.NUMBER},
            userId: user.id
        });

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        const textAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.TEXT},
            userId: user.id
        });

        const booleanAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.BOOLEAN},
            userId: user.id
        });

        const imageAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.IMAGE},
            userId: user.id
        });

        const selectAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.SELECT},
            userId: user.id
        });

        const multiselectAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.MULTISELECT},
            userId: user.id
        });

        const headers = [
            IDENTIFIER_HEADER,
            numberAttr.code,
            stringAttr.code,
            textAttr.code,
            booleanAttr.code,
            imageAttr.code,
            selectAttr.code,
            multiselectAttr.code
        ];

        const spreadsheetAttributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});

        await spreadsheetAttributes.refineAttributes();

        const dict = spreadsheetAttributes.getAttrDict();

        expect(dict).toEqual({
            id: {actions: ['default'], key: IDENTIFIER_HEADER, type: 'identifier', pos: [0]},
            [numberAttr.code]: {actions: ['default'], key: numberAttr.code, type: 'number', pos: [1]},
            [stringAttr.code]: {actions: ['default'], key: stringAttr.code, type: 'string', pos: [2]},
            [textAttr.code]: {actions: ['default'], key: textAttr.code, type: 'text', pos: [3]},
            [booleanAttr.code]: {actions: ['default'], key: booleanAttr.code, type: 'boolean', pos: [4]},
            [imageAttr.code]: {actions: ['default'], key: imageAttr.code, type: 'image', pos: [5]},
            [selectAttr.code]: {
                actions: ['default'],
                key: selectAttr.code,
                type: 'select',
                pos: [6],
                selectOptions: new Set()
            },
            [multiselectAttr.code]: {
                actions: ['default'],
                key: multiselectAttr.code,
                type: 'multiselect',
                pos: [7],
                selectOptions: new Set()
            }
        });
    });

    it('should handle inconsistent "stored <> spreadsheet" attributes', async () => {
        const someHeader = uuid;
        const headers = [IDENTIFIER_HEADER, someHeader];
        const spreadsheetAttributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await spreadsheetAttributes.refineAttributes();

        expect(spreadsheetAttributes.getAttrIndex()).toEqual([
            {attr: {actions: ['default'], key: 'id', pos: [0], type: 'identifier'}, header: 'id', lang: undefined},
            {
                error: new MissedImportSpreadsheetStoredAttribute({key: someHeader}).toFlatArray(),
                header: someHeader
            }
        ]);
    });

    it('should handle inconsistent "stored <> spreadsheet" "isArray" property', async () => {
        const user = await TestFactory.createUser();

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, stringAttr.code, stringAttr.code];
        const spreadsheetAttributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});
        await spreadsheetAttributes.refineAttributes();

        expect(spreadsheetAttributes.getAttrIndex()).toEqual([
            {attr: {actions: ['default'], key: 'id', pos: [0], type: 'identifier'}, header: 'id', lang: undefined},
            {
                error: new InvalidImportSpreadsheetAttributeIsArray({key: stringAttr.code}).toFlatArray(),
                header: stringAttr.code
            },
            {
                error: new InvalidImportSpreadsheetAttributeIsArray({key: stringAttr.code}).toFlatArray(),
                header: stringAttr.code
            }
        ]);
    });

    it('should handle falsy "isArray" property and "multiselect" attribute', async () => {
        const user = await TestFactory.createUser();

        const multiselectAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.MULTISELECT},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, multiselectAttr.code];
        const spreadsheetAttributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});

        await spreadsheetAttributes.refineAttributes();

        expect(spreadsheetAttributes.getAttrDict()[multiselectAttr.code]).toEqual({
            actions: ['default'],
            key: multiselectAttr.code,
            type: 'multiselect',
            pos: [1],
            selectOptions: new Set()
        });

        expect(spreadsheetAttributes.getAttributeMapping(multiselectAttr.code)).toEqual(1);
    });

    it('should handle inconsistent "stored <> spreadsheet" "isValueLocalizable" property', async () => {
        const user = await TestFactory.createUser();

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, stringAttr.code, `${stringAttr.code}|ru`];
        const spreadsheetAttributes = new SpreadsheetAttributes({headers, availableLangsForRegion: ['ru'] as never});
        await spreadsheetAttributes.refineAttributes();

        expect(spreadsheetAttributes.getAttrIndex()).toEqual([
            {attr: {actions: ['default'], key: 'id', pos: [0], type: 'identifier'}, header: 'id', lang: undefined},
            {
                error: new InvalidImportSpreadsheetAttributeLocalization({key: stringAttr.code}).toFlatArray(),
                header: stringAttr.code
            },
            {
                error: new InvalidImportSpreadsheetAttributeLocalization({key: stringAttr.code}).toFlatArray(),
                header: `${stringAttr.code}|ru`
            }
        ]);
    });

    it('should handle missed header language', async () => {
        const user = await TestFactory.createUser();

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isValueLocalizable: true},
            userId: user.id
        });

        const headers = [IDENTIFIER_HEADER, stringAttr.code, `${stringAttr.code}|ru`];
        const spreadsheetAttributes = new SpreadsheetAttributes({headers, availableLangsForRegion: ['ru'] as never});
        await spreadsheetAttributes.refineAttributes();

        expect(spreadsheetAttributes.getAttrIndex()).toEqual([
            {attr: {actions: ['default'], key: 'id', pos: [0], type: 'identifier'}, header: 'id', lang: undefined},
            {
                error: new InvalidImportSpreadsheetAttributeLocalization({key: stringAttr.code}).toFlatArray(),
                header: stringAttr.code
            },
            {
                error: new InvalidImportSpreadsheetAttributeLocalization({key: stringAttr.code}).toFlatArray(),
                header: `${stringAttr.code}|ru`
            }
        ]);
    });

    it('should handle "SELECT" attribute type options', async () => {
        const user = await TestFactory.createUser();

        const selectAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.SELECT},
            userId: user.id
        });

        const {optionCodes} = await createSelectOptions({userId: user.id, attributeId: selectAttr.id});

        const headers = [IDENTIFIER_HEADER, selectAttr.code];
        const spreadsheetAttributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});

        await spreadsheetAttributes.refineAttributes();

        expect(spreadsheetAttributes.getAttrDict()[selectAttr.code]).toEqual({
            actions: ['default'],
            key: selectAttr.code,
            type: 'select',
            pos: [1],
            selectOptions: new Set(optionCodes)
        });
    });

    it('should handle "MULTISELECT" attribute type options', async () => {
        const user = await TestFactory.createUser();

        const multiselectAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.MULTISELECT},
            userId: user.id
        });

        const {optionCodes} = await createSelectOptions({
            userId: user.id,
            attributeId: multiselectAttr.id
        });

        const headers = [IDENTIFIER_HEADER, multiselectAttr.code];
        const spreadsheetAttributes = new SpreadsheetAttributes({headers, availableLangsForRegion: []});

        await spreadsheetAttributes.refineAttributes();

        expect(spreadsheetAttributes.getAttrDict()[multiselectAttr.code]).toEqual({
            actions: ['default'],
            key: multiselectAttr.code,
            type: 'multiselect',
            pos: [1],
            selectOptions: new Set(optionCodes)
        });
    });
});
