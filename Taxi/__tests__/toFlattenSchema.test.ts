import {get} from 'lodash';

import {JsonSchema} from '../../types';
import {toFlattenSchema} from '../toFlattenSchema';

describe('toFlattenSchema', () => {
    test('Работает итератор', () => {
        const mockIterate = jest.fn<unknown, [JsonSchema, any, boolean | undefined]>();
        const model = {
            foo: 'foo',
            bar: 2,
            baz: undefined
        };
        const schema: JsonSchema = {
            type: 'object',
            required: ['foo', 'bar'],
            properties: {
                foo: {type: 'string'},
                bar: {type: 'number'},
                baz: {type: 'boolean'}
            }
        };

        toFlattenSchema(schema, model, mockIterate);
        expect(mockIterate).toHaveBeenCalledTimes(3);
        const types = mockIterate.mock.calls.map(arg => arg[0].type);
        expect(types).toEqual(expect.arrayContaining(['string', 'number', 'boolean']));

        const values = mockIterate.mock.calls.map(arg => arg[1]);
        expect(values).toEqual(expect.arrayContaining(Object.values(model)));

        const required = mockIterate.mock.calls.map(arg => arg[2]);
        expect(required).toEqual(expect.arrayContaining([true, true, false]));
    });

    test('Применяет модификации ко всем узлам типа number', () => {
        const model = {
            foo: 'foo',
            bar: 2,
            baz: undefined,
            oof: [3, 7],
            hello: {
                world: 'and bye'
            },
            very: {
                very: {
                    deep: [
                        {
                            value: 4
                        },
                        {
                            value: 5
                        },
                        {
                            value: 6
                        }
                    ]
                }
            }
        };
        const schema: JsonSchema = {
            type: 'object',
            properties: {
                foo: {type: 'string'},
                bar: {type: 'number'},
                baz: {type: 'boolean'},
                oof: {
                    type: 'array',
                    items: {
                        type: 'number'
                    }
                },
                hello: {
                    type: 'object',
                    properties: {
                        world: {
                            type: 'string'
                        }
                    }
                },
                very: {
                    type: 'object',
                    properties: {
                        very: {
                            type: 'object',
                            properties: {
                                deep: {
                                    type: 'array',
                                    items: {
                                        properties: {
                                            value: {
                                                type: 'number'
                                            }
                                        },
                                        type: 'object'
                                    }
                                }
                            }
                        }
                    }
                }
            }
        };

        const expected = {
            'bar': 4,
            'oof.0': 9,
            'oof.1': 49,
            'very.very.deep.0.value': 16,
            'very.very.deep.1.value': 25,
            'very.very.deep.2.value': 36
        };

        const actual = toFlattenSchema(schema, model, ({type}, value) => {
            if (type === 'number') {
                return Math.pow(value, 2);
            }
        });

        expect(actual).toEqual(expected);
    });

    test('Применяет модификации ко всем узлам типа string/boolean', () => {
        const model = {
            foo: 'test',
            bar: 2,
            baz: undefined,
            oof: ['one', 'two'],
            hello: {
                world: 'hello'
            },
            very: {
                very: {
                    deep: [
                        {
                            value: 'very very deep value'
                        }
                    ]
                }
            }
        };
        const schema: JsonSchema = {
            type: 'object',
            properties: {
                foo: {type: 'string'},
                bar: {type: 'number'},
                baz: {type: 'boolean'},
                oof: {
                    type: 'array',
                    items: {
                        type: 'string'
                    }
                },
                hello: {
                    type: 'object',
                    properties: {
                        world: {
                            type: 'string'
                        }
                    }
                },
                very: {
                    type: 'object',
                    properties: {
                        very: {
                            type: 'object',
                            properties: {
                                deep: {
                                    type: 'array',
                                    items: {
                                        properties: {
                                            value: {
                                                type: 'string'
                                            }
                                        },
                                        type: 'object'
                                    }
                                }
                            }
                        }
                    }
                }
            }
        };

        const expected = {
            'foo': 'TEST',
            'oof.0': 'ONE',
            'oof.1': 'TWO',
            'hello.world': 'HELLO',
            'very.very.deep.0.value': 'VERY VERY DEEP VALUE'
        };

        const actual = toFlattenSchema(schema, model, ({type}, value) => {
            if (type === 'string') {
                return value.toUpperCase();
            }
        });

        expect(actual).toEqual(expected);
    });

    test('Применяет модификации ко всем узлам типа object/array', () => {
        const model = {
            foo: [1, 2, 3, 4, 5, 6],
            very: {
                very: {
                    deep: [
                        {
                            one: 'very very deep value',
                            two: 'very very deep value',
                            three: 'very very deep value'
                        },
                        {
                            one: 'very very deep value',
                            two: 'very very deep value',
                            three: 'very very deep value'
                        }
                    ]
                }
            }
        };
        const schema: JsonSchema = {
            type: 'object',
            properties: {
                foo: {
                    type: 'array',
                    items: {
                        type: 'number'
                    }
                },
                very: {
                    type: 'object',
                    properties: {
                        very: {
                            type: 'object',
                            properties: {
                                deep: {
                                    type: 'array',
                                    items: {
                                        properties: {
                                            one: {
                                                type: 'string'
                                            },
                                            two: {
                                                type: 'string'
                                            },
                                            three: {
                                                type: 'string'
                                            }
                                        },
                                        type: 'object'
                                    }
                                }
                            }
                        }
                    }
                }
            }
        };

        const expected = {
            'foo': 6,
            'very': 'very',
            'very.very': 'deep',
            'very.very.deep': 2,
            'very.very.deep.0': 'one,two,three',
            'very.very.deep.1': 'one,two,three'
        };

        const actual = toFlattenSchema(schema, model, ({type}, value) => {
            if (type === 'array') {
                return value.length;
            }
            if (type === 'object') {
                return Object.keys(value).join();
            }
        });

        expect(actual).toEqual(expected);
    });

    test('Корректно работает с пустой моделькой', () => {
        const model = {};
        const schema: JsonSchema = {
            type: 'object',
            properties: {
                foo: {
                    type: 'array',
                    items: {
                        type: 'number'
                    }
                },
                bar: {
                    type: 'string'
                }
            }
        };

        const actual = toFlattenSchema(schema, model, (_, value) => value);
        expect(actual).toEqual({});
    });

    test('Корректно работает с пустой схемой', () => {
        const model = {
            foo: '1243',
            baz: [
                {
                    bar: true
                }
            ]
        };
        const schema: JsonSchema = {};

        const actual = toFlattenSchema(schema, model, (_, value) => value);
        expect(actual).toEqual({});
    });

    test('Корректно работает с required полями', () => {
        const model = {
            foo: '1243',
            baz: [
                {
                    bar: true,
                    oof: 'test'
                }
            ]
        };
        const schema: JsonSchema = {
            type: 'object',
            properties: {
                foo: {
                    type: 'string'
                },
                baz: {
                    type: 'array',
                    items: {
                        required: ['oof'],
                        properties: {
                            oof: {
                                type: 'string'
                            },
                            bar: {
                                type: 'boolean'
                            }
                        },
                        type: 'object'
                    }
                }
            }
        };

        const mockFn = jest.fn();
        const actual = toFlattenSchema(schema, model, (_, _value, isRequired) => {
            return isRequired ? mockFn : undefined;
        });

        expect(get(actual, 'baz.0.oof')).toBe(mockFn);
    });

    test('Корректно работает с опцией inheritable', () => {
        const model = {
            foo: '1243',
            baz: undefined
        };
        const schema: JsonSchema = {
            required: ['baz'],
            type: 'object',
            properties: {
                foo: {
                    type: 'string'
                },
                baz: {
                    required: ['oof'],
                    properties: {
                        oof: {
                            type: 'string'
                        },
                        bar: {
                            type: 'boolean'
                        }
                    },
                    type: 'object'
                }
            }
        };

        const mockFn = jest.fn();
        toFlattenSchema(schema, model, (_, _value, isRequired) => {
            return isRequired ? mockFn() : undefined;
        }, {inheritable: true});

        expect(mockFn).not.toBeCalled();
    });

    test('Корректно работает с рефами', () => {
        const model = {
            foo: {
                bar: 'string'
            }
        };

        const schema: JsonSchema = {
            type: 'object',
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

        const expected = {
            'foo.bar': 'STRING'
        };

        const actual = toFlattenSchema(schema, model, ({type}, value) => {
            if (type === 'string') {
                return value.toUpperCase();
            }
        });

        expect(actual).toEqual(expected);
    });
});
