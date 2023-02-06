import {expectSaga} from 'redux-saga-test-plan';

import {formValidator} from '../validate';

const MODEL = 'MODEL';

const STATE = {
    [MODEL]: {}
};

describe('formValidator', () => {
    describe('getValidationRules', () => {
        test('возвращает false если в модели есть ошибки', () => {
            const validator = formValidator({
                modelPath: MODEL,
                getValidationRules: () => ({
                    foo: () => false
                })
            });

            return expectSaga(validator)
                .withState(STATE)
                .run()
                .then(({returnValue}) => {
                    expect(returnValue).toBe(false);
                });
        });

        test('возвращает true если в модели нет ошибок', () => {
            const validator = formValidator({
                modelPath: MODEL,
                getValidationRules: () => ({
                    foo: () => true
                })
            });

            return expectSaga(validator)
                .withState(STATE)
                .run()
                .then(({returnValue}) => {
                    expect(returnValue).toBe(true);
                });
        });
    });

    describe('getErrors', () => {
        test('возвращает false если в модели есть ошибки', () => {
            const validator = formValidator({
                modelPath: MODEL,
                getValidationRules: () => ({}),
                getErrors: () => ({
                    foo: 'bar'
                })
            });

            return expectSaga(validator)
                .withState(STATE)
                .run()
                .then(({returnValue}) => {
                    expect(returnValue).toBe(false);
                });
        });

        test('возвращает true если в модели нет ошибок', () => {
            const validator = formValidator({
                modelPath: MODEL,
                getValidationRules: () => ({}),
                getErrors: () => ({})
            });

            return expectSaga(validator)
                .withState(STATE)
                .run()
                .then(({returnValue}) => {
                    expect(returnValue).toBe(true);
                });
        });
    });

    describe('detailed', () => {
        test('с параметром detailed возвращает полный объект ошибок', () => {
            const validator = formValidator({
                modelPath: MODEL,
                detailed: true,
                getValidationRules: () => ({
                    foo: () => false
                }),
                getErrors: () => ({
                    foo: 'bar'
                })
            });

            const expected = {
                isValid: false,
                validity: {
                    foo: true
                },
                errors: {
                    foo: 'bar'
                }
            };

            return expectSaga(validator)
                .withState(STATE)
                .run()
                .then(({returnValue}) => {
                    expect(returnValue).toStrictEqual(expected);
                });
        });
    });

    describe('showAssert', () => {
        test('пробрасывает showAssert в свойства валидатора', () => {
            const showAssert = () => 'foo';

            const validator = formValidator({
                modelPath: MODEL,
                showAssert,
                getValidationRules: () => ({
                    foo: () => false
                })
            });

            expect(validator.showAssert).toBe(showAssert);
        });
    });
});
