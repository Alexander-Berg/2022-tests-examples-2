import {JsonSchema} from '../../types';
import * as dep from '../customValidators';
import {getValidationErrors} from '../getValidationErrors';

jest.mock('../customValidators', () => {
    return {
        array: [jest.fn()],
        number: [jest.fn()],
        string: [jest.fn()],
        object: [jest.fn()],
        boolean: [jest.fn()]
    };
});

describe('getValidationErrors', () => {
    test('Вызывает функции валидаторы для каждого типа', () => {
        const mockedDependency = dep.default as jest.Mock<typeof dep.default>;
        const model = {
            foo: 100,
            baz: ['one', 'two'],
            bar: {
                test: true
            }
        };
        const schema: JsonSchema = {
            type: 'object',
            properties: {
                foo: {
                    type: 'number'
                },
                baz: {
                    type: 'array',
                    items: {
                        type: 'string'
                    }
                },
                bar: {
                    type: 'object',
                    properties: {
                        test: {
                            type: 'boolean'
                        }
                    }
                }
            }
        };

        getValidationErrors(model, schema);

        Object.entries(mockedDependency).forEach(([key, value]) => {
            const [mockedFn] = value;
            if (key === 'string') {
                expect(mockedFn).toBeCalledTimes(2);
            }
            if (key === 'array') {
                expect(mockedFn).toBeCalledTimes(1);
            }
            // TODO см. hasValue, но возможно функционал кастомной
            // валидации для чекбоксов избыточен сам по себе
            // if (key === 'boolean') {
            //     expect(mockedFn).toBeCalledTimes(1);
            // }
            if (key === 'object') {
                expect(mockedFn).toBeCalledTimes(1);
            }
            if (key === 'number') {
                expect(mockedFn).toBeCalledTimes(1);
            }
        });
    });

    test('Корректно работает с рефами', () => {
        const model = {};

        const schema: JsonSchema = {
            type: 'object',
            required: ['foo'],
            properties: {
                foo: {
                    $ref: '#/components/schemas/Foo'
                }
            },
            components: {
                schemas: {
                    Foo: {
                        type: 'object',
                        properties: {
                            bar: {
                                type: 'string'
                            }
                        }
                    }
                }
            }
        };

        const errors = getValidationErrors(model, schema, {
            validators: {
                'foo.bar': () => ({valid: false, msg: 'test error message'})
            }
        });

        expect(errors['foo.bar']).toBe('test error message');
    });

    test('Корректно работает опции prefix и validators', () => {
        const model = {
            foo: 100,
            baz: ['one', 'two'],
            bar: {
                test: 'test test'
            },
            prefixed: [1]
        };
        const schema: JsonSchema = {
            type: 'object',
            properties: {
                foo: {
                    type: 'number'
                },
                baz: {
                    type: 'array',
                    items: {
                        type: 'string'
                    }
                },
                bar: {
                    type: 'object',
                    properties: {
                        test: {
                            type: 'string'
                        }
                    }
                },
                prefixed: {
                    type: 'array',
                    minItems: 5,
                    items: {
                        type: 'number'
                    }
                }
            }
        };

        const mockedFn = jest.fn();

        const errors = getValidationErrors(model, schema, {
            prefix: 'some_prefix',
            validators: {
                'bar.test': mockedFn,
                'prefixed': () => ({valid: false, msg: 'test error message'})
            }
        });

        expect(mockedFn).toBeCalledWith('test test');
        expect(errors['some_prefix.prefixed']).toBe('test error message');
    });
});
