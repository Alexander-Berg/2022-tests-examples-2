import moment from 'moment';
import {dateToString, flattenObject, UTC_DATE_FORMAT} from '_pkg/utils/form';

const TIMEZONE = '+0600';

describe('utils/form', () => {
    describe('dateToString', () => {
        test('Должна возвращать функцию', () => {
            expect(dateToString()).toBeInstanceOf(Function);
        });

        test('Должна возвращать сам объект, если переданного ключа не нашлось в объекте или у него falsy значение', () => {
            const testObj = {};
            const nullTestObj = {test: null};
            const converter = dateToString('test');
            expect(converter(testObj)).toBe(testObj);
            expect(converter(nullTestObj)).toBe(nullTestObj);
        });

        test('Должна возвращать сам объект, если передали не валидную дату', () => {
            const testObj = {test: 'not a date'};
            const converter = dateToString('test');
            expect(converter(testObj)).toBe(testObj);
        });

        test('Должна склеивать время с датой и вырезать из объекта _time свойство', () => {
            const timeString = `2018-07-04T00:00:00.000${TIMEZONE}`;
            const testObj = {
                test: moment.parseZone(timeString),
                test_time: '16:20'
            };

            const converter = dateToString('test');
            expect(converter(testObj)).toMatchObject({test: `2018-07-04T16:20:00.000${TIMEZONE}`});
        });

        test('Должна склеивать время с датой, переданной в виде строки формата YYYY-MM-DD', () => {
            const testObj = {
                test: '2018-07-04',
                test_time: '16:20'
            };
            const converter = dateToString('test');
            // здесь невозможно прописать конкретное значение, т.к. на разных машинах с разными часовыми поясами оно будет выдавать разные значения
            expect(converter(testObj)).toMatchObject({test: moment(`${testObj.test}T${testObj.test_time}`).format(UTC_DATE_FORMAT)});
        });

        test('flattenObject simple', () => {
            const data = {a: {b: {c: 1}}};

            expect(flattenObject(data)).toEqual({'a.b.c': 1});
        });

        test('flattenObject with func', () => {
            const f = () => true;
            const data = {a: {b: {c: f}}};

            expect(flattenObject(data)).toEqual({'a.b.c': f});
        });
    });
});
