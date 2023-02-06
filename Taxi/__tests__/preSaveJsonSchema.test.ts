// tslint:disable:max-file-line-count
import {JsonSchema} from '../../types';
import {preSaveJsonSchema} from '../preSaveJsonSchema';

describe('preSaveJsonSchema', () => {
    describe('type: boolean', () => {
        test('Корректно преобразует значение', () => {
            const model = {
                foo: 1
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'boolean'
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo).toBe(true);
        });

        test('Корректно преобразует пустое значение', () => {
            const model = {
                foo: undefined,
                bar: null
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'boolean'
                    },
                    bar: {
                        type: 'boolean'
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo).toBeUndefined();
            expect(result.bar).toBeUndefined();
        });

        test('Корректно преобразует пустое required значение', () => {
            const model = {
                foo: undefined,
                bar: null
            };

            const schema: JsonSchema = {
                type: 'object',
                required: ['foo', 'bar'],
                properties: {
                    foo: {
                        type: 'boolean'
                    },
                    bar: {
                        type: 'boolean'
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo).toBe(false);
            expect(result.bar).toBe(false);
        });

        test('Корректно преобразует значение в массивах', () => {
            const model = {
                foo: [1]
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'array',
                        items: {
                            type: 'boolean'
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo[0]).toBe(true);
        });

        test('Корректно преобразует значение в вложенных объектах', () => {
            const model = {
                foo: {
                    bar: 1
                }
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'object',
                        properties: {
                            bar: {
                                type: 'boolean'
                            }
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo.bar).toBe(true);
        });

        test('Корректно преобразует значение в объектах из дискриминатора', () => {
            const model = {
                foo: 'bar',
                bar: 1
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
                            properties: {
                                bar: {
                                    type: 'boolean'
                                }
                            }
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.bar).toBe(true);
        });
    });

    describe('type: string', () => {
        test('Корректно преобразует значение', () => {
            const model = {
                foo: 1,
                bar: 'baz'
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'string'
                    },
                    bar: {
                        type: 'string'
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo).toBe('1');
            expect(result.bar).toBe('baz');
        });

        test('Корректно преобразует пустое значение', () => {
            const model = {
                foo: '',
                bar: undefined,
                baz: null
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'string'
                    },
                    bar: {
                        type: 'string'
                    },
                    baz: {
                        type: 'string'
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo).toBeUndefined();
            expect(result.bar).toBeUndefined();
            expect(result.baz).toBeUndefined();
        });

        test('Корректно преобразует значение в массивах', () => {
            const model = {
                foo: [1]
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'array',
                        items: {
                            type: 'string'
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo).toStrictEqual(['1']);
        });

        test('Корректно преобразует значение в вложенных объектах', () => {
            const model = {
                foo: {
                    bar: 1
                }
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'object',
                        properties: {
                            bar: {
                                type: 'string'
                            }
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo.bar).toBe('1');
        });

        test('Корректно преобразует значение в объектах из дискриминатора', () => {
            const model = {
                foo: 'bar',
                bar: 1
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
                            properties: {
                                bar: {
                                    type: 'string'
                                }
                            }
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.bar).toBe('1');
        });
    });

    describe('type: integer', () => {
        test('Корректно преобразует значение', () => {
            const model = {
                foo: '1.0'
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'integer'
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo).toBe(1);
        });

        test('Корректно преобразует значение в массивах', () => {
            const model = {
                foo: ['1.0']
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'array',
                        items: {
                            type: 'integer'
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo[0]).toBe(1);
        });

        test('Корректно преобразует значение в вложенных объектах', () => {
            const model = {
                foo: {
                    bar: '1.0'
                }
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'object',
                        properties: {
                            bar: {
                                type: 'integer'
                            }
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo.bar).toBe(1);
        });

        test('Корректно преобразует значение в объектах из дискриминатора', () => {
            const model = {
                foo: 'bar',
                bar: '1.1'
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
                            properties: {
                                bar: {
                                    type: 'integer'
                                }
                            }
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.bar).toBe(1);
        });
    });

    describe('type: number', () => {
        test('Корректно преобразует значение', () => {
            const model = {
                foo: '1.1'
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'number'
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo).toBe(1.1);
        });

        test('Корректно преобразует значение в массивах', () => {
            const model = {
                foo: ['1.1']
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'array',
                        items: {
                            type: 'number'
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo[0]).toBe(1.1);
        });

        test('Корректно преобразует значение в вложенных объектах', () => {
            const model = {
                foo: {
                    bar: '1.1'
                }
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'object',
                        properties: {
                            bar: {
                                type: 'number'
                            }
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo.bar).toBe(1.1);
        });

        test('Корректно преобразует значение в объектах из дискриминатора', () => {
            const model = {
                foo: 'bar',
                bar: '1.1'
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
                            properties: {
                                bar: {
                                    type: 'number'
                                }
                            }
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.bar).toBe(1.1);
        });
    });

    describe('type: array', () => {
        test('Корректно преобразует значение', () => {
            const model = {
                foo: ['foo']
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'array',
                        items: {
                            type: 'string'
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo).toStrictEqual(['foo']);
        });

        test('Корректно преобразует пустое значение', () => {
            const model = {
                foo: []
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'array',
                        items: {
                            type: 'string'
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo).toBeUndefined();
        });

        test('Корректно преобразует пустое required значение', () => {
            const model = {
                foo: []
            };

            const schema: JsonSchema = {
                type: 'object',
                required: ['foo'],
                properties: {
                    foo: {
                        type: 'array',
                        items: {
                            type: 'string'
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo).toStrictEqual([]);
        });

        test('Удаляет некорректные элементы из значения', () => {
            const model = {
                foo: ['1', 0, undefined, null, '']
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'array',
                        items: {
                            type: 'string'
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result.foo).toStrictEqual(['1', '0']);
        });
    });

    describe('type: object', () => {
        test('Корректно преобразует значение', () => {
            const model = {};

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'string'
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result).toStrictEqual({});
        });

        test('Корректно преобразует пустое значение', () => {
            const model = {
                foo: {
                    bar: null
                }
            };

            const schema: JsonSchema = {
                type: 'object',
                properties: {
                    foo: {
                        type: 'object',
                        properties: {
                            bar: {
                                type: 'string'
                            }
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result).toStrictEqual({});
        });

        test('Корректно преобразует пустое required значение', () => {
            const model = {
                icon: {
                    url: 'foo',
                    name: 'bar',
                    badge: {
                        text: null,
                        colors: {
                            light: {},
                            dark: {}
                        }
                    }
                }
            };

            const schema: JsonSchema = {
                type: 'object',
                required: [
                    'icon'
                ],
                properties: {
                    icon: {
                        type: 'object',
                        required: [
                            'url',
                            'name'
                        ],
                        properties: {
                            url: {
                                type: 'string',
                            },
                            name: {
                                type: 'string',
                            },
                            badge: {
                                type: 'object',
                                required: [
                                    'text',
                                    'colors'
                                ],
                                properties: {
                                    text: {
                                        type: 'string',
                                    },
                                    colors: {
                                        type: 'object',
                                        required: [
                                            'light',
                                            'dark'
                                        ],
                                        properties: {
                                            light: {
                                                type: 'object',
                                                required: [
                                                    'text_color',
                                                    'background_color'
                                                ],
                                                properties: {
                                                    text_color: {
                                                        type: 'string',
                                                    },
                                                    background_color: {
                                                        type: 'string',
                                                    }
                                                }
                                            },
                                            dark: {
                                                type: 'object',
                                                required: [
                                                    'text_color',
                                                    'background_color'
                                                ],
                                                properties: {
                                                    text_color: {
                                                        type: 'string',
                                                    },
                                                    background_color: {
                                                        type: 'string',
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result).toStrictEqual({
                icon: {
                    url: 'foo',
                    name: 'bar',
                }
            });
        });
    });

    describe('refs', () => {
        test('Корректно работает с рефами', () => {
            const model = {
                foo: {
                    bar: {
                        baz: '1'
                    }
                }
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
                            properties: {
                                bar: {
                                    $ref: '#/components/schemas/Bar'
                                }
                            }
                        },
                        Bar: {
                            type: 'object',
                            properties: {
                                baz: {
                                    type: 'boolean'
                                }
                            }
                        }
                    }
                }
            };

            const expected = {
                foo: {
                    bar: {
                        baz: true
                    }
                }
            };

            const result = preSaveJsonSchema(model, schema);
            expect(result).toStrictEqual(expected);
        });
    });
});
