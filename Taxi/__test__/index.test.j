/*
import {printFactory} from '../index';

const LANGUAGE = 'ru';

const ERRORS = {
    errorNoTranslation: (keyset, key) => `errorNoTranslation:${keyset}.${key}`,
    errorNoCount: (keyset, key) => `errorNoCount:${keyset}.${key}`
};

const CONTEXT = 'CONTEXT';

const DEFAULT_KEYSET = 'taxi-supchat';
const NON_DEFAULT_KEYSET = 'OTHER';

const KEY_SIMPLE = 'SIMPLE';
const KEY_PLURAL = 'PLURAL';
const KEY_PARAMETRIZED = 'PARAMETRIZED';

const PARAM_PLURAL_NONE = 'none';
const PARAM_FIRST = 'first';
const PARAM_SECOND = 'second';

const VALUE_SIMPLE = 'VALUE_SIMPLE';
const VALUE_PLURAL = ['one', 'some', 'many', `{${PARAM_PLURAL_NONE}}`];
const getParameterizedValue = (first, second) => `Parametrized ${first} ${second}`;

const KEYSETS = {
    [DEFAULT_KEYSET]: {
        [`${CONTEXT}:${KEY_SIMPLE}`]: VALUE_SIMPLE,
        [`${CONTEXT}:${KEY_PLURAL}`]: VALUE_PLURAL,
        [`${CONTEXT}:${KEY_PARAMETRIZED}`]: getParameterizedValue(`{${PARAM_FIRST}}`, `{${PARAM_SECOND}}`)
    },
    [NON_DEFAULT_KEYSET]: {
        [`${CONTEXT}:${KEY_SIMPLE}`]: VALUE_SIMPLE
    }
};

const {createPrint, print} = printFactory(LANGUAGE, KEYSETS, ERRORS);

describe('lib:i18n', () => {
    testFunc('print', print, `${CONTEXT}:`);
    testFunc('createPrint', createPrint(CONTEXT));

    test('createPrint with defined keyset', () => {
        expect(createPrint(CONTEXT, NON_DEFAULT_KEYSET)(KEY_SIMPLE)).toBe(VALUE_SIMPLE);
    });

    function testFunc(name, func, key_prefix = '') {
        describe(`print test: ${name}`, () => {
            const createKey = key => `${key_prefix}${key}`;

            test('simple value', () => {
                expect(func(createKey(KEY_SIMPLE))).toBe(VALUE_SIMPLE);
            });

            test('parametrized', () => {
                const PARAM = {
                    FIRST: 'FIRST',
                    SECOND: 'SECOND'
                };

                expect(
                    func(createKey(KEY_PARAMETRIZED), {
                        params: {first: PARAM.FIRST, second: PARAM.SECOND}
                    })
                ).toBe(getParameterizedValue(PARAM.FIRST, PARAM.SECOND));
            });

            test('non-default keyset', () => {
                expect(func(createKey(KEY_SIMPLE), {keyset: NON_DEFAULT_KEYSET})).toBe(VALUE_SIMPLE);
            });

            test('no key', () => {
                const NOT_EXISTENT_KEY = 'NOT_EXISTENT_KEY';

                expect(func(createKey(NOT_EXISTENT_KEY))).toBe(
                    ERRORS.errorNoTranslation(DEFAULT_KEYSET, `${CONTEXT}:${NOT_EXISTENT_KEY}`)
                );
            });

            test('simple plural', () => {
                const key = createKey(KEY_PLURAL);

                expect(func(key, {count: 1})).toBe(VALUE_PLURAL[0]); // one
                expect(func(key, {count: 4})).toBe(VALUE_PLURAL[1]); // some
                expect(func(key, {count: 125})).toBe(VALUE_PLURAL[2]); // many
                expect(func(key, {count: 0})).toBe(VALUE_PLURAL[3]); // none

                expect(func(key)).toBe(ERRORS.errorNoCount(DEFAULT_KEYSET, `${CONTEXT}:${KEY_PLURAL}`));
            });

            test('plural parametrized', () => {
                const PARAM = 'NONE';

                expect(
                    func(createKey(KEY_PLURAL), {
                        count: 0,
                        params: {[PARAM_PLURAL_NONE]: PARAM}
                    })
                ).toBe(PARAM);
            });
        });
    }
});
*/