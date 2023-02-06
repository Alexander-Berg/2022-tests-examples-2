import moment, {Moment} from 'moment';

import {
    arrayParser,
    booleanParser,
    ExtractFilter,
    getFilterFromUrl,
    momentParser,
    numberParser,
    QueryParsers,
    stringParser,
} from '_pkg/utils/getFilterFromUrl';
import {exact} from '_types/__test__/asserts';
import {DraftModes} from '_types/common/drafts';

describe('utils/getFilterFromUrl/stringParser', () => {
    test('Должна вернуть валидную строку', () => {
        expect(stringParser()('test')).toBe('test');
    });
    test('Должна вернуть undefined', () => {
        expect(stringParser()(undefined)).toBeUndefined();
        expect(stringParser()(['foo'])).toBeUndefined();
    });
    test('При наличии дефолта должна вернуть в первую очередь значение парсинга', () => {
        expect(stringParser('test')('foo')).toBe('foo');
    });
    test('Должна вернуть дефолтное значение', () => {
        expect(stringParser('test')(undefined)).toBe('test');
        expect(stringParser('test')(['foo'])).toBe('test');
    });
    test('Должна вернуть Undefinable тип без дефолта', () => {
        const result = stringParser()('test');
        exact<typeof result, Undefinable<string>>(true);
    });
    test('Должна вернуть Undefinable<Enum> тип без дефолта', () => {
        const result = stringParser<DraftModes>()('test');
        exact<typeof result, Undefinable<DraftModes>>(true);
    });
    test('Должна вернуть NonUndefinable тип при наличии дефолта', () => {
        const TEST: string = 'test';
        const result = stringParser(TEST)('test');
        exact<typeof result, string>(true);
    });
    test('Должна вернуть NonUndefinable<Enum> тип при наличии дефолта', () => {
        const result = stringParser<DraftModes>(DraftModes.Copy)('test');
        exact<typeof result, DraftModes>(true);
    });
});

describe('utils/getFilterFromUrl/numberParser', () => {
    test('Должна вернуть валидное число', () => {
        expect(numberParser()('234')).toBe(234);
    });
    test('Должна вернуть undefined', () => {
        expect(numberParser()(undefined)).toBeUndefined();
        expect(numberParser()(['234'])).toBeUndefined();
    });
    test('При наличии дефолта должна вернуть в первую очередь значение парсинга', () => {
        expect(numberParser(111)('123')).toBe(123);
    });
    test('Должна вернуть дефолтное значение', () => {
        expect(numberParser(111)(undefined)).toBe(111);
        expect(numberParser(111)(['123'])).toBe(111);
        expect(numberParser(111)(['foo'])).toBe(111);
    });
    test('Должна вернуть Undefinable тип без дефолта', () => {
        const result = numberParser()('123');
        exact<typeof result, Undefinable<number>>(true);
    });
    test('Должна вернуть NonUndefinable тип при наличии дефолта', () => {
        const result = numberParser(111)('123');
        exact<typeof result, number>(true);
    });
});

describe('utils/getFilterFromUrl/booleanParser', () => {
    test('Должна вернуть валидный boolean', () => {
        expect(booleanParser()('true')).toBeTruthy();
        expect(booleanParser()('false')).toBeFalsy();
    });
    test('Должна вернуть undefined', () => {
        expect(booleanParser()(undefined)).toBeUndefined();
        expect(booleanParser()(['true'])).toBeUndefined();
    });
    test('При наличии дефолта должна вернуть в первую очередь значение парсинга', () => {
        expect(booleanParser(false)('true')).toBeTruthy();
        expect(booleanParser(true)('false')).toBeFalsy();
    });
    test('Должна вернуть дефолтное значение', () => {
        expect(booleanParser(true)(undefined)).toBeTruthy();
        expect(booleanParser(false)(undefined)).toBeFalsy();
        expect(booleanParser(true)(['false'])).toBeTruthy();
        expect(booleanParser(false)(['true'])).toBeFalsy();
    });
    test('Должна вернуть Undefinable тип без дефолта', () => {
        const result = booleanParser()('false');
        exact<typeof result, Undefinable<boolean>>(true);
    });
    test('Должна вернуть NonUndefinable тип при наличии дефолта', () => {
        const result = booleanParser(true)('test');
        exact<typeof result, boolean>(true);
    });
});

describe('utils/getFilterFromUrl/momentParser', () => {
    const TEXT_DATE = '2010-12-03';
    const DEFAULT_TEXT_DATE = '2015-12-03';
    const DATE_FORMAT = 'YYYY-MM-DD';
    const DEFAULT_MOMENT_DATE = moment(DEFAULT_TEXT_DATE, DATE_FORMAT);
    test('Должна вернуть распарсенную дату раньше дефолта', () => {
        expect(momentParser(TEXT_DATE)(DEFAULT_TEXT_DATE)).toEqual(DEFAULT_MOMENT_DATE);
    });
    test('Должна вернуть дефолтную дату', () => {
        expect(momentParser(DEFAULT_TEXT_DATE)(undefined)).toEqual(DEFAULT_MOMENT_DATE);
        expect(momentParser(DEFAULT_TEXT_DATE)(['foo'])).toEqual(DEFAULT_MOMENT_DATE);
    });
    test('Должна вернуть Undefinable тип без дефолта', () => {
        const result = momentParser()(TEXT_DATE);
        exact<typeof result, Undefinable<Moment>>(true);
    });
    test('Должна вернуть NonUndefinable тип', () => {
        const result = momentParser(DEFAULT_TEXT_DATE)(TEXT_DATE);
        exact<typeof result, Moment>(true);
    });
});

describe('utils/getFilterFromUrl/arrayParser', () => {
    test('Должна вернуть валидный массив строк', () => {
        expect(arrayParser()('test')).toEqual(['test']);
        expect(arrayParser()(['test'])).toEqual(['test']);
    });
    test('Должна вернуть undefined', () => {
        expect(arrayParser()(undefined)).toBeUndefined();
    });
    test('При наличии дефолта должна вернуть в первую очередь значение парсинга', () => {
        expect(arrayParser(['test'])('foo')).toEqual(['foo']);
    });
    test('Должна вернуть дефолтное значение', () => {
        expect(arrayParser(['test'])(undefined)).toEqual(['test']);
    });
    test('Должна вернуть Undefinable тип без дефолта', () => {
        const result = arrayParser()('test');
        exact<typeof result, Undefinable<string[]>>(true);
    });
    test('Должна вернуть Undefinable<Enum[]> тип без дефолта', () => {
        const result = arrayParser<DraftModes>()('test');
        exact<typeof result, Undefinable<DraftModes[]>>(true);
    });
    test('Должна вернуть NonUndefinable тип при наличии дефолта', () => {
        const TEST: string[] = ['test'];
        const result = arrayParser(TEST)('test');
        exact<typeof result, string[]>(true);
    });
    test('Должна вернуть NonUndefinable<Enum[]> тип без дефолта', () => {
        const result = arrayParser<DraftModes>([DraftModes.Copy])('test');
        exact<typeof result, DraftModes[]>(true);
    });
});

describe('utils/getFilterFromUrl', () => {
    test('Должна возвращать объект с валидными фильтрами', () => {
        history.pushState({}, 'test query', '/?test=string&invalid=doesntmatter');
        expect(
            getFilterFromUrl({
                test: stringParser()
            })
        ).toEqual({test: 'string'});
    });

    test('Нормально работает если в URL нет параметра', () => {
        history.pushState({}, 'test query', '/?test=string&invalid=doesntmatter');
        expect(
            getFilterFromUrl({
                test: stringParser(),
                test2: stringParser()
            })
        ).toEqual({test: 'string'});
    });

    test('Должна преобразовывать строки с числами и булевыми значениями в правильный тип', () => {
        history.pushState({}, 'test query', '/?numTest=218&trueTest=true&falseTest=false');
        expect(
            getFilterFromUrl({
                numTest: numberParser(),
                trueTest: booleanParser(),
                falseTest: booleanParser()
            })
        ).toMatchObject({
            numTest: 218,
            trueTest: true,
            falseTest: false
        });
    });

    test('Должна преобразовывать строки с массивов и одним элементом', () => {
        history.pushState({}, 'test query', '/?exclude=save_value');
        expect(
            getFilterFromUrl({
                exclude: arrayParser()
            })
        ).toMatchObject({
            exclude: ['save_value']
        });
    });

    test('Должна преобразовывать строки с массивом', () => {
        history.pushState({}, 'test query', '/?exclude=save_value&exclude=set_classification_rule');

        const query = getFilterFromUrl({
            exclude: arrayParser()
        });

        exact<typeof query, {exclude?: string[]}>(true);
        expect(query).toMatchObject({
            exclude: ['save_value', 'set_classification_rule']
        });
    });

    test('Должен преобразовывать фильтры соответственно переданным настройкам', () => {
        history.pushState({}, 'test query', '/?test=1&date_time=16:20');
        expect(
            getFilterFromUrl({
                test: numberParser(),
                date_time: stringParser()
            })
        ).toMatchObject({
            test: 1,
            date_time: '16:20'
        });
    });

    test('Предпочитает search из параметра', () => {
        history.pushState({}, 'test query', '/?test=1&date_time=16:20');
        expect(
            getFilterFromUrl({
                test: numberParser(),
                date_time: stringParser()
            }, '?test=2&date_time=16:30')
        ).toMatchObject({
            test: 2,
            date_time: '16:30'
        });
    });

    test('Проверка вывода типов для даты', () => {
        history.pushState({}, 'test query', '/?date=2018-07-04');

        type TestFilter = {date?: Moment};

        // проверяем что для Moment нужно указывать Date
        const filters: QueryParsers<TestFilter> = {
            date: momentParser()
        };

        // проверяем что из предиката Date обратно выводится Moment
        const query = getFilterFromUrl(filters);
        exact<typeof query, {date?: Moment}>(true);

         // проверяем что реально приходит Moment
        expect(query).toMatchObject({
            date: expect.any(moment)
        });
    });

    test('Проверка вывода типов для enum', () => {
        history.pushState({}, 'test query', '/?sort=desc');

        const enum Sort {
            Asc = 'asc',
            Desc = 'desc'
        }

        type TestFilter = {sort: Sort};

        const filters: QueryParsers<TestFilter> = {
            sort: v => v as Sort
        };

        // проверяем что из обратный вывод дает ожидаемый результат
        const query = getFilterFromUrl(filters);
        exact<typeof query, TestFilter>(true);

         // проверяем что реально приходит
        expect(query).toMatchObject({
            sort: 'desc'
        });
    });

    test('Проверка парсинга отсутствующих в query значений', () => {
        history.pushState({}, 'test query', '/?mode=draft');

        type TestFilter = {name?: string};
        const filters: QueryParsers<TestFilter> = {
            name: stringParser(),
        };

        const query = getFilterFromUrl(filters);
        exact<typeof query, TestFilter>(true);

        expect(query).toStrictEqual({});
    });

    test('String', () => {
        const x = {
            a: String
        };

        const y: QueryParsers<{a?: string}> = {
            a: stringParser()
        };

        // @ts-expect-error
        const z: QueryParsers<{a: string}> = {
            // @ts-expect-error
            a: String
        };

        const w: QueryParsers<{a: string}> = {
            a: stringParser('')
        };

        type X = ExtractFilter<typeof x>;
        type Y = ExtractFilter<typeof y>;
        type W = ExtractFilter<typeof w>;

        exact<X, Y>(true);
        exact<X, {a?: string}>(true);

        const qx = getFilterFromUrl(x);
        exact<typeof qx, X>(true);
        const qy = getFilterFromUrl(y);
        exact<typeof qy, X>(true);
        const qw = getFilterFromUrl(w);
        exact<typeof qw, W>(true);
    });

    test('Number', () => {
        const x = {
            a: Number
        };

        const y: QueryParsers<{a?: number}> = {
            a: numberParser()
        };

        // @ts-expect-error
        const z: QueryParsers<{a: number}> = {
            // @ts-expect-error
            a: Number
        };

        const w: QueryParsers<{a: number}> = {
            a: numberParser(0)
        };

        type X = ExtractFilter<typeof x>;
        type Y = ExtractFilter<typeof y>;
        type W = ExtractFilter<typeof w>;

        exact<X, Y>(true);
        exact<X, {a?: number}>(true);
        exact<W, {a: number}>(true);

        const qx = getFilterFromUrl(x);
        exact<typeof qx, X>(true);
        const qy = getFilterFromUrl(y);
        exact<typeof qy, X>(true);
    });

    test('Boolean', () => {
        const x = {
            a: Boolean
        };

        const y: QueryParsers<{a?: boolean}> = {
            a: booleanParser()
        };

        // @ts-expect-error
        const z: QueryParsers<{a: boolean}> = {
            // @ts-expect-error
            a: Boolean
        };

        const w: QueryParsers<{a: boolean}> = {
            a: booleanParser(false)
        };

        type X = ExtractFilter<typeof x>;
        type Y = ExtractFilter<typeof y>;
        type W = ExtractFilter<typeof w>;

        exact<X, Y>(true);
        exact<X, {a?: boolean}>(true);
        exact<W, {a: boolean}>(true);

        const qx = getFilterFromUrl(x);
        exact<typeof qx, X>(true);
        const qy = getFilterFromUrl(y);
        exact<typeof qy, X>(true);
        const qw = getFilterFromUrl(w);
        exact<typeof qw, W>(true);
    });

    test('Date', () => {
        const x = {
            a: Date
        };

        const y: QueryParsers<{a?: Moment}> = {
            a: momentParser()
        };

        // @ts-expect-error
        const z: QueryParsers<{a: Moment}> = {
            // @ts-expect-error
            a: Date
        };

        const w: QueryParsers<{a: Moment}> = {
            a: momentParser(moment())
        };

        type X = ExtractFilter<typeof x>;
        type Y = ExtractFilter<typeof y>;
        type W = ExtractFilter<typeof w>;

        exact<X, Y>(true);
        exact<X, {a?: Moment}>(true);
        exact<W, {a: Moment}>(true);

        const qx = getFilterFromUrl(x);
        exact<typeof qx, X>(true);
        const qy = getFilterFromUrl(y);
        exact<typeof qy, X>(true);
        const qw = getFilterFromUrl(w);
        exact<typeof qw, W>(true);
    });

    test('Array', () => {
        const x = {
            a: Array
        };

        const y: QueryParsers<{a?: string[]}> = {
            a: arrayParser()
        };

        // @ts-expect-error
        const z: QueryParsers<{a: string[]}> = {
            // @ts-expect-error
            a: Array
        };

        const w: QueryParsers<{a: number[]}> = {
            a: arrayParser([])
        };

        type X = ExtractFilter<typeof x>;
        type Y = ExtractFilter<typeof y>;
        type W = ExtractFilter<typeof w>;

        exact<X, Y>(true);
        exact<X, {a?: string[]}>(true);
        exact<W, {a: number[]}>(true);

        const qx = getFilterFromUrl(x);
        exact<typeof qx, X>(true);
        const qy = getFilterFromUrl(y);
        exact<typeof qy, X>(true);
        const qw = getFilterFromUrl(w);
        exact<typeof qw, W>(true);
    });

    test('Enum', () => {
        const enum Sort {
            Asc = 'asc',
            Desc = 'desc'
        }

        const x = {
            a: stringParser<Sort>()
        };

        const y: QueryParsers<{a?: Sort}> = {
            a: stringParser<Sort>()
        };

        type X = ExtractFilter<typeof x>;
        type Y = ExtractFilter<typeof y>;

        exact<X, Y>(true);
        exact<X, {a?: Sort}>(true);

        const qx = getFilterFromUrl(x);
        exact<typeof qx, X>(true);
        const qy = getFilterFromUrl(y);
        exact<typeof qy, X>(true);
    });
});
