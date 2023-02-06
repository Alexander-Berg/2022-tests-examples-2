import moment from 'moment';

import {DATE_FORMAT} from '../../../consts';
import {FieldValueModel, Value} from '../../../types';
import {formatValue} from '../formatValue';

describe('formatValue', () => {
    test('Корректно форматирует поле с типом string', () => {
        const val: FieldValueModel = {
            type: 'string',
            stringValue: 'foo',
            booleanValue: false
        };

        const expected: Value = {
            type: 'string',
            stringValue: 'foo'
        };

        const actual = formatValue(val);

        expect(expected).toStrictEqual(actual);
    });

    test('Корректно форматирует поле с типом number', () => {
        const val: FieldValueModel = {
            type: 'number',
            numberValue: '1',
            booleanValue: false
        };

        const expected: Value = {
            type: 'number',
            numberValue: 1
        };

        const actual = formatValue(val);

        expect(expected).toStrictEqual(actual);
    });

    test('Корректно форматирует поле с типом integer', () => {
        const val: FieldValueModel = {
            type: 'integer',
            integerValue: '1',
            booleanValue: false
        };

        const expected: Value = {
            type: 'integer',
            integerValue: 1
        };

        const actual = formatValue(val);

        expect(expected).toStrictEqual(actual);
    });

    test('Корректно форматирует поле с типом boolean', () => {
        const val: FieldValueModel = {
            type: 'boolean',
            integerValue: '1',
            booleanValue: false
        };

        const expected: Value = {
            type: 'boolean',
            booleanValue: false
        };

        const actual = formatValue(val);

        expect(expected).toStrictEqual(actual);
    });

    test('Корректно форматирует поле с типом datetime', () => {
        const date = moment('2020-01-01');

        const val: FieldValueModel = {
            type: 'datetime',
            datetimeValue: date,
            booleanValue: false,
            $view: {
                time: '01:00'
            }
        };

        const expected: Value = {
            type: 'datetime',
            datetimeValue: date.hours(1).format(DATE_FORMAT)
        };

        const actual = formatValue(val);

        expect(expected).toStrictEqual(actual);
    });

    test('Корректно форматирует поле с типом array', () => {
        const val: FieldValueModel = {
            type: 'array',
            arrayValue: [
                {
                    type: 'string',
                    stringValue: 'string',
                    numberValue: '0'
                }
            ],
            booleanValue: false
        };

        const expected: Value = {
            type: 'array',
            arrayValue: [
                {
                    type: 'string',
                    stringValue: 'string'
                }
            ]
        };

        const actual = formatValue(val);

        expect(expected).toStrictEqual(actual);
    });

    test('Корректно форматирует поле с типом file', () => {
        const val: FieldValueModel = {
            type: 'file',
            fileValue: 'file',
            booleanValue: false
        };

        const expected: Value = {
            type: 'file',
            fileValue: 'file'
        };

        const actual = formatValue(val);

        expect(expected).toStrictEqual(actual);
    });
});
