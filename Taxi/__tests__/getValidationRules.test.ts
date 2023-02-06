import {expectSaga} from 'redux-saga-test-plan';

import {formValidator} from '_pkg/sagas/validate';

import {JsonSchema} from '../../types';
import {getValidationRules} from '../getValidationRules';

const MODEL = 'MODEL';

describe('getValidationRules', () => {
    test('Валидирует required значения в полях с типом string', () => {
        const state = {
            [MODEL]: {
                foo: undefined,
                bar: 'bar'
            }
        };

        const schema: JsonSchema = {
            type: 'object',
            required: ['foo', 'bar'],
            properties: {
                foo: {type: 'string'},
                bar: {type: 'string'}
            }
        };

        const validator = formValidator({
            modelPath: MODEL,
            detailed: true,
            getValidationRules: model => getValidationRules(model, schema)
        });

        return expectSaga(validator)
            .withState(state)
            .run()
            .then(({returnValue: {validity}}) => {
                expect(validity.foo).toBe(true);
                expect(validity.bar).toBe(false);
            });
    });

    test('Валидирует required значения в полях с типом number', () => {
        const state = {
            [MODEL]: {
                foo: undefined,
                bar: 1
            }
        };

        const schema: JsonSchema = {
            type: 'object',
            required: ['foo', 'bar'],
            properties: {
                foo: {type: 'number'},
                bar: {type: 'number'}
            }
        };

        const validator = formValidator({
            modelPath: MODEL,
            detailed: true,
            getValidationRules: model => getValidationRules(model, schema)
        });

        return expectSaga(validator)
            .withState(state)
            .run()
            .then(({returnValue: {validity}}) => {
                expect(validity.foo).toBe(true);
                expect(validity.bar).toBe(false);
            });
    });

    test('Валидирует required значения в полях с типом boolean', () => {
        const state = {
            [MODEL]: {
                foo: undefined,
                bar: false
            }
        };

        const schema: JsonSchema = {
            type: 'object',
            required: ['foo'],
            properties: {
                foo: {type: 'boolean'},
                bar: {type: 'boolean'}
            }
        };

        const validator = formValidator({
            modelPath: MODEL,
            detailed: true,
            getValidationRules: model => getValidationRules(model, schema)
        });

        return expectSaga(validator)
            .withState(state)
            .run()
            .then(({returnValue: {validity}}) => {
                expect(validity.foo).toBe(true);
                expect(validity.bar).toBe(false);
            });
    });

    test('Валидирует required значения в полях с типом array', () => {
        const state = {
            [MODEL]: {
                foo: undefined,
                bar: [1, 2, 3],
                baz: undefined
            }
        };

        const schema: JsonSchema = {
            type: 'object',
            required: ['foo', 'bar'],
            properties: {
                foo: {type: 'array', items: {}},
                bar: {type: 'array', items: {}},
                baz: {type: 'array', items: {}}
            }
        };

        const validator = formValidator({
            modelPath: MODEL,
            detailed: true,
            getValidationRules: model => getValidationRules(model, schema)
        });

        return expectSaga(validator)
            .withState(state)
            .run()
            .then(({returnValue: {validity}}) => {
                expect(validity.foo).toBe(true);
                expect(validity.bar).toBe(false);
                expect(validity.baz).toBe(false);
            });
    });

    test('Валидирует required значения в полях с типом object', () => {
        const state = {
            [MODEL]: {
                foo: undefined,
                bar: {b: 1},
                baz: undefined
            }
        };

        const schema: JsonSchema = {
            type: 'object',
            required: ['foo', 'bar'],
            properties: {
                foo: {
                    type: 'object',
                    properties: {}
                },
                bar: {
                    type: 'object',
                    properties: {}
                },
                baz: {
                    type: 'object',
                    properties: {}
                }
            }
        };

        const validator = formValidator({
            modelPath: MODEL,
            detailed: true,
            getValidationRules: model => getValidationRules(model, schema)
        });

        return expectSaga(validator)
            .withState(state)
            .run()
            .then(({returnValue: {validity}}) => {
                expect(validity.foo).toBe(true);
                expect(validity.bar).toBe(false);
                expect(validity.baz).toBe(false);
            });
    });

    test('Валидирует required в вложенных объектах', () => {
        const state = {
            [MODEL]: {}
        };

        const schema: JsonSchema = {
            type: 'object',
            required: ['foo'],
            properties: {
                foo: {
                    type: 'object',
                    required: ['bar'],
                    properties: {
                        bar: {
                            type: 'string'
                        }
                    }
                }
            }
        };

        const validator = formValidator({
            modelPath: MODEL,
            detailed: true,
            getValidationRules: model => getValidationRules(model, schema)
        });

        return expectSaga(validator)
            .withState(state)
            .run()
            .then(({returnValue: {validity}}) => {
                expect(validity['foo.bar']).toBe(true);
            });
    });

    test('Валидирует required поля в массивах объектов', () => {
        const state = {
            [MODEL]: {
                foo: [{}]
            }
        };

        const schema: JsonSchema = {
            type: 'object',
            properties: {
                foo: {
                    type: 'array',
                    items: {
                        type: 'object',
                        required: ['bar'],
                        properties: {
                            bar: {
                                type: 'string'
                            }
                        }
                    }
                }
            }
        };

        const validator = formValidator({
            modelPath: MODEL,
            detailed: true,
            getValidationRules: model => getValidationRules(model, schema)
        });

        return expectSaga(validator)
            .withState(state)
            .run()
            .then(({returnValue: {validity}}) => {
                expect(validity['foo.0.bar']).toBe(true);
            });
    });

    test('Валидирует required значения в полях из дискриминатора', () => {
        const state = {
            [MODEL]: {
                foo: 'bar'
            }
        };

        const schema: JsonSchema = {
            type: 'object',
            properties: {
                foo: {
                    type: 'string'
                }
            },
            discriminator: {
                propertyName: 'foo',
                mapping: {
                    bar: {
                        type: 'object',
                        required: ['bar'],
                        properties: {
                            bar: {
                                type: 'string'
                            }
                        }
                    }
                }
            }
        };

        const validator = formValidator({
            modelPath: MODEL,
            detailed: true,
            getValidationRules: model => getValidationRules(model, schema)
        });

        return expectSaga(validator)
            .withState(state)
            .run()
            .then(({returnValue: {validity}}) => {
                expect(validity.bar).toBe(true);
            });
    });

    test('Валидирует required значения в наследуемых полях, если они заполнены', () => {
        const state = {
            [MODEL]: {
                foo: null,
                bar: {
                    baz: '',
                    booz: 'filled'
                }
            }
        };

        const schema: JsonSchema = {
            type: 'object',
            required: ['foo'],
            properties: {
                foo: {
                    type: 'string'
                },
                bar: {
                    required: ['baz'],
                    type: 'object',
                    properties: {
                        baz: {
                            type: 'string'
                        },
                        booz: {
                            type: 'string'
                        }
                    }
                }
            }
        };

        const validator = formValidator({
            modelPath: MODEL,
            detailed: true,
            getValidationRules: model => getValidationRules(model, schema, {inheritable: true})
        });

        return expectSaga(validator)
            .withState(state)
            .run()
            .then(({returnValue: {validity}}) => {
                expect(validity.foo).toBe(true);
                expect(validity['bar.baz']).toBe(true);
            });
    });

    test('Не валидирует required значения в наследуемых полях, если они не заполнены', () => {
        const state = {
            [MODEL]: {}
        };

        const schema: JsonSchema = {
            type: 'object',
            required: ['foo'],
            properties: {
                foo: {
                    type: 'string'
                },
                bar: {
                    required: ['baz'],
                    type: 'object',
                    properties: {
                        baz: {
                            type: 'string'
                        }
                    }
                }
            }
        };

        const validator = formValidator({
            modelPath: MODEL,
            detailed: true,
            getValidationRules: model => getValidationRules(model, schema, {inheritable: true})
        });

        return expectSaga(validator)
            .withState(state)
            .run()
            .then(({returnValue: {validity}}) => {
                expect(validity.foo).toBeUndefined();
                expect(validity['bar.baz']).toBeUndefined();
            });
    });

    test('Корректно работает с рефами', () => {
        const state = {
            [MODEL]: {}
        };

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
                        required: ['bar'],
                        properties: {
                            bar: {
                                type: 'string'
                            }
                        }
                    }
                }
            }
        };

        const validator = formValidator({
            modelPath: MODEL,
            detailed: true,
            getValidationRules: model => getValidationRules(model, schema)
        });

        return expectSaga(validator)
            .withState(state)
            .run()
            .then(({returnValue: {validity}}) => {
                expect(validity['foo.bar']).toBe(true);
            });
    });

    test('Не валидирует объект если все вложенные поля null/undefined', () => {
        const state = {
            [MODEL]: {
                foo: {
                    bar: null,
                    baz: {
                        test: undefined
                    }
                }
            }
        };
        const schema: JsonSchema = {
            type: 'object',
            properties: {
                foo: {
                    type: 'object',
                    required: ['baz'],
                    properties: {
                        bar: {
                            type: 'string'
                        },
                        baz: {
                            type: 'object',
                            required: ['test'],
                            properties: {
                                test: {
                                    type: 'string'
                                },
                            }
                        }
                    }
                }
            }
        };

        const validator = formValidator({
            modelPath: MODEL,
            detailed: true,
            getValidationRules: model => getValidationRules(model, schema, {inheritable: true})
        });

        return expectSaga(validator)
            .withState(state)
            .run()
            .then(({returnValue: {validity}}) => {
                expect(validity.foo).toBe(false);
            });
    });
});
