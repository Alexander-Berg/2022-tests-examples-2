import {buildSchemaFromData, DataType} from '../buildSchemaFromData';

const simpleObj = {
    str: 'testStr',
    num: 10,
    bool: false
};

const strArray = ['str1', 'str2', 'str3'];
const boolArray = [true];
const numArray = [35, 999];

const complicatedObj = {
    department: 'produce',
    categories: [
        'fruit',
        'vegetables'
    ],
    bins: [
        {
            category: 'fruit',
            type: 'apples',
            price: 1.99,
            unit: 'pound',
            quantity: 232
        },
        {
            category: 'fruit',
            type: 'bananas',
            price: 0.19,
            unit: 'each',
            quantity: 112,
            newBoolField: true
        },
        {
            category: 'vegetables',
            type: 'carrots',
            price: 1.29,
            unit: 'bag',
            quantity: 57
        }
    ]
};

describe('buildSchemaFromData', () => {
    test('корректно строит схему для простых типов', () => {
        expect(buildSchemaFromData(simpleObj)).toEqual({
            label: '',
            type: DataType.Object,
            properties: {
                bool: {
                    label: 'bool',
                    type: 'boolean',
                },
                num: {
                    label: 'num',
                    type: 'number',
                },
                str: {
                    label: 'str',
                    type: 'string',
                },
            }
        });
    });

    test('корректно строит схему для сложных типов', () => {
        expect(buildSchemaFromData(complicatedObj)).toEqual({
            type: 'object',
            label: '',
            properties: {
                department: {
                    type: 'string',
                    label: 'department',
                },
                categories: {
                    type: 'array',
                    label: 'categories',
                    items: {
                        type: 'string',
                        label: '',
                    }
                },
                bins: {
                    type: 'array',
                    label: 'bins',
                    items: {
                        type: 'object',
                        label: '',
                        properties: {
                            category: {
                                type: 'string',
                                label: 'category',
                            },
                            type: {
                                type: 'string',
                                label: 'type',
                            },
                            price: {
                                type: 'number',
                                label: 'price',
                            },
                            unit: {
                                type: 'string',
                                label: 'unit',
                            },
                            quantity: {
                                type: 'number',
                                label: 'quantity',
                            },
                            newBoolField: {
                                type: 'boolean',
                                label: 'newBoolField',
                            },
                        }
                    }
                }
            }
        });
    });

    describe('корректно строит схему для простых массивов', () => {
        test('для массива со строками', () => {
            expect(buildSchemaFromData(strArray)).toEqual({
                label: '',
                type: DataType.Array,
                items: {
                    type: 'string',
                    label: ''
                }
            });
        });
        test('для массива с булевыми', () => {
            expect(buildSchemaFromData(boolArray)).toEqual({
                label: '',
                type: DataType.Array,
                items: {
                    type: 'boolean',
                    label: ''
                }
            });
        });
        test('для массива с числами', () => {
            expect(buildSchemaFromData(numArray)).toEqual({
                label: '',
                type: DataType.Array,
                items: {
                    type: 'number',
                    label: ''
                }
            });
        });
    });
});
