import {omitEmptyValues} from '../utils';

describe('omitEmptyValues', () => {
    test('default', () => {
        const data: Record<string, any> = {
            emptyArray: [],
            arrayWithNull: [null],
            arrayWithEmptyObjects: [{test: null}, {some: {test: null}}],
            arrayWithFilledObjects: [{data: 'data'}],
            emptyObject: {},
            filledArray: [123, 'test'],
            mixedArray: ['some', 0, false, true, null] as any[],
            simpleField: 'qwer',
            objectWithEmptyFields: {
                emptyField: null
            },
            mixedObject: {
                empty: undefined,
                zeroIsNotEmpty: 0,
                number: 123,
                string: 'false',
                deepObject: {
                    empty: undefined,
                    data: 'data',
                    emptyArray: []
                }
            },
            nullField: null,
            undefinedField: undefined,
            falseField: false,
            trueField: true
        };
        const expected = {
            arrayWithFilledObjects: [{data: 'data'}],
            filledArray: [123, 'test'],
            mixedArray: ['some', 0, false, true],
            simpleField: 'qwer',
            mixedObject: {
                zeroIsNotEmpty: 0,
                number: 123,
                string: 'false',
                deepObject: {
                    data: 'data',
                }
            },
            falseField: false,
            trueField: true
        };

        expect(omitEmptyValues(data)).toEqual(expected);
    });
});
