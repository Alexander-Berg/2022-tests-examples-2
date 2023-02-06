import moment from 'moment';

import {prepareQueryObject} from '../prepareQueryObject';

const testQueryObj: Indexed = {
    null: null,
    undefined: undefined,
    emptyString: '',
    string: 'TEST STRING',
    zeroNumber: 0,
    numberLessThanZero: -10,
    number: 43,
    array: [1, 'test'],
    emptyArray: [],
    booleanTrue: true,
    booleanFalse: false,
    moment: moment('2019-10-10')
};

const preparedQueryObj: Indexed = {
    string: 'TEST STRING',
    zeroNumber: 0,
    numberLessThanZero: -10,
    number: 43,
    array: [1, 'test'],
    booleanTrue: true,
    booleanFalse: false,
    moment: '2019-10-10'
};

describe('utils/prepareQueryObject', () => {
    test('Корректно вырезает значения null, undefined, пустую строку и пустой массив', () => {
        expect(prepareQueryObject(testQueryObj)).toEqual(preparedQueryObj);
    });

    describe('Корректно конвертирует значения', () => {
        test('для moment', () => {
            expect(prepareQueryObject(testQueryObj).moment).toBe(preparedQueryObj.moment);
        });

        test('для массивов', () => {
            expect(prepareQueryObject(testQueryObj).array).toEqual(preparedQueryObj.array);
        });
    });
});
