import {JsonSchema} from '../../types';
import {replaceReferences} from '../replaceReferences';

describe('replaceReferences', () => {
    it('Заменяет рефы в схеме', () => {
        const schema: JsonSchema = {
            type: 'object',
            properties: {
                a: {
                    $ref: '#/components/schemas/A'
                },
                b: {
                    type: 'array',
                    items: {
                        $ref: '#/components/schemas/A'
                    }
                }
            },
            components: {
                schemas: {
                    A: {
                        type: 'string'
                    }
                }
            }
        };

        const expected: JsonSchema = {
            type: 'object',
            properties: {
                a: {
                    type: 'string'
                },
                b: {
                    type: 'array',
                    items: {
                        type: 'string'
                    }
                }
            }
        };

        const result = replaceReferences(schema);

        expect(result).toStrictEqual(expected);
    });

    it('Заменяет рефы в components/schemas', () => {
        const schema: JsonSchema = {
            type: 'object',
            properties: {
                a: {
                    $ref: '#/components/schemas/A'
                }
            },
            components: {
                schemas: {
                    A: {
                        $ref: '#/components/schemas/B'
                    },
                    B: {
                        $ref: '#/components/schemas/C'
                    },
                    C: {
                        type: 'string'
                    }
                }
            }
        };

        const expected: JsonSchema = {
            type: 'object',
            properties: {
                a: {
                    type: 'string'
                }
            }
        };

        const result = replaceReferences(schema);

        expect(result).toStrictEqual(expected);
    });

    it('Корректно обрабатывает рефы на несуществующие значения', () => {
        const schema: JsonSchema = {
            type: 'object',
            properties: {
                a: {
                    $ref: '#/components/schemas/A'
                }
            },
            components: {
                schemas: {
                    B: {
                        type: 'string'
                    }
                }
            }
        };

        const expected: JsonSchema = {
            type: 'object',
            properties: schema.properties
        };

        const result = replaceReferences(schema);

        expect(result).toStrictEqual(expected);
    });

    it('Корректно обрабатывает циклические зависимости', () => {
        const schema: JsonSchema = {
            type: 'object',
            properties: {
                a: {
                    $ref: '#/components/schemas/A'
                },
                b: {
                    $ref: '#/components/schemas/B'
                },
                c: {
                    $ref: '#/components/schemas/C'
                },
                d: {
                    $ref: '#/components/schemas/D'
                }
            },
            components: {
                schemas: {
                    A: {
                        $ref: '#/components/schemas/A'
                    },
                    B: {
                        type: 'array',
                        items: {
                            $ref: '#/components/schemas/B'
                        }
                    },
                    C: {
                        type: 'object',
                        properties: {
                            a: {
                                $ref: '#/components/schemas/C'
                            }
                        }
                    },
                    D: {
                        type: 'object',
                        properties: {},
                        discriminator: {
                            propertyName: 'a',
                            mapping: {
                                a: {
                                    type: 'object',
                                    properties: {
                                        a: {
                                            $ref: '#/components/schemas/D'
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        };

        const expected: JsonSchema = {
            type: 'object',
            properties: schema.properties
        };

        const result = replaceReferences(schema);

        expect(result).toStrictEqual(expected);
    });

    it('Заменяет рефы в descriminated полях', () => {
        const schema: JsonSchema = {
            type: 'object',
            properties: {
                a: {
                    type: 'object',
                    properties: {},
                    discriminator: {
                        propertyName: 'a',
                        mapping: {
                            a: {
                                type: 'object',
                                properties: {
                                    a: {
                                        $ref: '#/components/schemas/A'
                                    },
                                    b: {
                                        $ref: '#/components/schemas/B'
                                    }
                                }
                            }
                        }
                    }
                }
            },
            components: {
                schemas: {
                    A: {
                        type: 'boolean'
                    },
                    B: {
                        type: 'string'
                    }
                }
            }
        };

        const expected: JsonSchema = {
            type: 'object',
            properties: {
                a: {
                    type: 'object',
                    properties: {},
                    discriminator: {
                        propertyName: 'a',
                        mapping: {
                            a: {
                                type: 'object',
                                properties: {
                                    a: {
                                        type: 'boolean'
                                    },
                                    b: {
                                        type: 'string'
                                    }
                                }
                            }
                        }
                    }
                }
            }
        };

        const result = replaceReferences(schema);

        expect(result).toStrictEqual(expected);
    });
});
