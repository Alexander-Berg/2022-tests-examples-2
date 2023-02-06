import moment, {Moment} from 'moment';

import {
    ExtractFilter,
    Filters,
    getFilterFromUrl,
} from '_pkg/utils/getFilterFromUrl';
import {exact} from '_types/__test__/asserts';

describe('utils/getFilterFromUrl', () => {
    test('Должна возвращать объект с валидными фильтрами', () => {
        history.pushState({}, 'test query', '/?test=string&invalid=doesntmatter');
        expect(
            getFilterFromUrl({
                test: String
            })
        ).toEqual({test: 'string'});
    });

    test('Нормально работает если в URL нет параметра', () => {
        history.pushState({}, 'test query', '/?test=string&invalid=doesntmatter');
        expect(
            getFilterFromUrl({
                test: String,
                test2: String
            })
        ).toEqual({test: 'string'});
    });

    test('Должна преобразовывать строки с числами и булевыми значениями в правильный тип', () => {
        history.pushState({}, 'test query', '/?numTest=218&trueTest=true&falseTest=false');
        expect(
            getFilterFromUrl({
                numTest: Number,
                trueTest: Boolean,
                falseTest: Boolean
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
                exclude: Array
            })
        ).toMatchObject({
            exclude: ['save_value']
        });
    });

    test('Должна преобразовывать строки с массивом', () => {
        history.pushState({}, 'test query', '/?exclude=save_value&exclude=set_classification_rule');

        const query = getFilterFromUrl({
            exclude: Array
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
                test: Number,
                date_time: String
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
                test: Number,
                date_time: String
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
        const filters: Filters<TestFilter> = {
            date: Date
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

        const filters: Filters<TestFilter> = {
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
        const filters: Filters<TestFilter> = {
            name: String,
        };

        const query = getFilterFromUrl(filters);
        exact<typeof query, TestFilter>(true);

        expect(query).toStrictEqual({});
    });

    test('String', () => {
        const x = {
            a: String
        };

        const y: Filters<{a?: string}> = {
            a: String
        };

        // @ts-expect-error
        const z: Filters<{a: string}> = {
            // @ts-expect-error
            a: String
        };

        const w: Filters<{a: string}> = {
            a: a => (a instanceof Array ? a[0] : a) || ''
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

        const y: Filters<{a?: number}> = {
            a: Number
        };

        // @ts-expect-error
        const z: Filters<{a: number}> = {
            // @ts-expect-error
            a: Number
        };

        const w: Filters<{a: number}> = {
            a: a => Number(a)
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

        const y: Filters<{a?: boolean}> = {
            a: Boolean
        };

        // @ts-expect-error
        const z: Filters<{a: boolean}> = {
            // @ts-expect-error
            a: Boolean
        };

        const w: Filters<{a: boolean}> = {
            a: a => !!a
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

        const y: Filters<{a?: Moment}> = {
            a: Date
        };

        // @ts-expect-error
        const z: Filters<{a: Moment}> = {
            // @ts-expect-error
            a: Date
        };

        const w: Filters<{a: Moment}> = {
            a: () => null as any as Moment
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

        const y: Filters<{a?: string[]}> = {
            a: Array
        };

        // @ts-expect-error
        const z: Filters<{a: string[]}> = {
            // @ts-expect-error
            a: Array
        };

        const w: Filters<{a: string[]}> = {
            a: () => null as any as string[]
        };

        type X = ExtractFilter<typeof x>;
        type Y = ExtractFilter<typeof y>;
        type W = ExtractFilter<typeof w>;

        exact<X, Y>(true);
        exact<X, {a?: string[]}>(true);
        exact<W, {a: string[]}>(true);

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

        const parser = (a: string) => (a as Sort) || Sort.Asc;

        const x = {
            a: parser
        };

        const y: Filters<{a: Sort}> = {
            a: parser
        };

        type X = ExtractFilter<typeof x>;
        type Y = ExtractFilter<typeof y>;

        exact<X, Y>(true);
        exact<X, {a: Sort}>(true);

        const qx = getFilterFromUrl(x);
        exact<typeof qx, X>(true);
        const qy = getFilterFromUrl(y);
        exact<typeof qy, X>(true);
    });

    test('Mix', () => {
        const q = getFilterFromUrl({
            a: String,
            b: (v: unknown) => !!v
        });

        exact<typeof q, {
            a?: string;
            b: boolean
        }>(true);
    });
});
