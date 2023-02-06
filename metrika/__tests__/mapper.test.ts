import { MapRule } from '../decorators';
import { mapEntity } from '../mapper';
import { ScalarFieldType, ListFieldType } from '../meta';

describe('mapper', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('should do nothing if metadata is missing', () => {
        const instance = {};
        const emptyEntity = jest.fn().mockImplementation(function () {
            return instance;
        });

        expect(mapEntity(emptyEntity, {})).toEqual(instance);
    });

    it('should throw error if data is missing', () => {
        class TestEntity {
            @MapRule({ type: ScalarFieldType.String })
            name!: string;
        }

        expect(() => {
            mapEntity(TestEntity, undefined);
        }).toThrow(new Error('entity data is empty'));
    });

    describe('initialization', () => {
        class TestEntity {
            @MapRule(ScalarFieldType.String)
            name!: string;

            @MapRule(ScalarFieldType.Int)
            age!: number;
        }

        let res: TestEntity;

        beforeEach(() => {
            res = mapEntity(TestEntity, { name: 'John', age: 22 });
        });

        it('should create instance of entity class', () => {
            expect(res).toBeInstanceOf(TestEntity);
        });

        it('should fill up instance of entity class with data', () => {
            expect(res).toEqual({ name: 'John', age: 22 });
        });
    });

    it('should allow to use shorthand type annotation', () => {
        class TestEntity {
            @MapRule(ScalarFieldType.Int)
            field!: number;
        }

        const res = mapEntity(TestEntity, { field: 1 });

        expect(res).toEqual({ field: 1 });
    });

    describe('boolean', () => {
        class TestEntity {
            @MapRule(ScalarFieldType.Boolean)
            booleanField!: boolean;
        }

        it('should map "0" to true', () => {
            const res = mapEntity(TestEntity, { boolean_field: '0' });
            expect(res.booleanField).toBe(true);
        });

        it('should map stringified boolean to true', () => {
            const res = mapEntity(TestEntity, { boolean_field: 'false' });
            expect(res.booleanField).toBe(true);
        });

        it('should map non-zero number to true', () => {
            const res = mapEntity(TestEntity, { boolean_field: 123 });
            expect(res.booleanField).toBe(true);
        });

        it('should map zero to false', () => {
            const res = mapEntity(TestEntity, { boolean_field: 0 });
            expect(res.booleanField).toBe(false);
        });

        it('should map empty string to false', () => {
            const res = mapEntity(TestEntity, { boolean_field: '' });
            expect(res.booleanField).toBe(false);
        });

        it('should map true to true', () => {
            const res = mapEntity(TestEntity, { boolean_field: true });
            expect(res.booleanField).toBe(true);
        });

        it('should map false to false', () => {
            const res = mapEntity(TestEntity, { boolean_field: false });
            expect(res.booleanField).toBe(false);
        });
    });

    describe('integer', () => {
        class TestEntity {
            @MapRule(ScalarFieldType.Int)
            intField!: number;
        }

        it('should map integer to integer', () => {
            const res = mapEntity(TestEntity, { int_field: 3 });
            expect(res.intField).toBe(3);
        });

        it('should map string integer to integer', () => {
            const res = mapEntity(TestEntity, { int_field: '1' });
            expect(res.intField).toBe(1);
        });

        it('should round float to integer', () => {
            const res = mapEntity(TestEntity, { int_field: 3.123 });
            expect(res.intField).toBe(3);
        });

        it('should round string float to integer', () => {
            const res = mapEntity(TestEntity, { int_field: '2.0' });
            expect(res.intField).toBe(2);
        });

        it('should map string to integer', () => {
            const res = mapEntity(TestEntity, { int_field: '3 4' });
            expect(res.intField).toBe(3);
        });

        it('should throw error for NaN', () => {
            expect(() => {
                mapEntity(TestEntity, { int_field: NaN });
            }).toThrow(new Error('map field=int_field error: Error: Cast field to int error, value=NaN'));
        });

        it('should throw error for non-numeric string', () => {
            expect(() => {
                mapEntity(TestEntity, { int_field: 'abc 3' });
            }).toThrow(new Error('map field=int_field error: Error: Cast field to int error, value=abc 3'));
        });

        it('should throw error for stringified boolean', () => {
            expect(() => {
                mapEntity(TestEntity, { int_field: 'false' });
            }).toThrow(new Error('map field=int_field error: Error: Cast field to int error, value=false'));
        });

        it('should throw error for boolean', () => {
            expect(() => {
                mapEntity(TestEntity, { int_field: true });
            }).toThrow(new Error('map field=int_field error: Error: Cast field to int error, value=true'));
        });
    });

    describe('float', () => {
        class TestEntity {
            @MapRule(ScalarFieldType.Float)
            floatField!: number;
        }

        it('should map float to float', () => {
            const res = mapEntity(TestEntity, { float_field: 1.123 });
            expect(res.floatField).toBe(1.123);
        });

        it('should map string float to float', () => {
            const res = mapEntity(TestEntity, { float_field: '3.456' });
            expect(res.floatField).toBe(3.456);
        });

        it('should map integer to float', () => {
            const res = mapEntity(TestEntity, { float_field: 123 });
            expect(res.floatField).toBe(123);
        });

        it('should map string integer to float', () => {
            const res = mapEntity(TestEntity, { float_field: '3' });
            expect(res.floatField).toBe(3);
        });

        it('should map string to float', () => {
            const res = mapEntity(TestEntity, { float_field: '123.4 xyz' });
            expect(res.floatField).toBe(123.4);
        });

        it('should throw error for NaN', () => {
            expect(() => {
                mapEntity(TestEntity, { float_field: NaN });
            }).toThrow(new Error('map field=float_field error: Error: Cast field to float error, value=NaN'));
        });

        it('should throw error for non-numeric string', () => {
            expect(() => {
                mapEntity(TestEntity, { float_field: 'abc 5.678' });
            }).toThrow(new Error('map field=float_field error: Error: Cast field to float error, value=abc 5.678'));
        });

        it('should throw error for stringified boolean', () => {
            expect(() => {
                mapEntity(TestEntity, { float_field: 'true' });
            }).toThrow(new Error('map field=float_field error: Error: Cast field to float error, value=true'));
        });

        it('should throw error for boolean', () => {
            expect(() => {
                mapEntity(TestEntity, { float_field: false });
            }).toThrow(new Error('map field=float_field error: Error: Cast field to float error, value=false'));
        });
    });

    it('should map string type', () => {
        class TestEntity {
            @MapRule(ScalarFieldType.String)
            stringField!: string;
        }
        const TEST_STRING = 'sdfsdfsdfgfsd';
        const toString = jest.fn().mockReturnValueOnce(TEST_STRING);
        const res = mapEntity(TestEntity, {
            string_field: {
                toString,
            },
        });
        expect(res.stringField).toBe(TEST_STRING);
        expect(toString).toBeCalled();
    });

    describe('list', () => {
        class TestEntity {
            @MapRule(ListFieldType.of(ScalarFieldType.Int))
            listField!: number[];
        }

        it('should map list type', () => {
            const res = mapEntity(TestEntity, {
                list_field: ['1', '2', '3'],
            });

            expect(res).toEqual({
                listField: [1, 2, 3],
            });
        });

        it('should throw error if list type is not an array', () => {
            expect(() => {
                mapEntity(TestEntity, {
                    list_field: 3,
                });
            }).toThrow(new Error('map field=list_field error: Error: invalid list type'));
        });
    });

    it('should error if required data is missing', () => {
        class TestEntity {
            @MapRule(ScalarFieldType.Int)
            requiredDataField!: number;
        }

        expect(() => {
            mapEntity(TestEntity, {});
        }).toThrow(new Error('map field=required_data_field error: Error: required field is empty'));
    });

    it('should not error if optional data is missing', () => {
        class TestEntity {
            @MapRule({ type: ScalarFieldType.Int, isOptional: true })
            optionalDataField?: number;
        }

        const res = mapEntity(TestEntity, {});
        expect(res.optionalDataField).toBeUndefined();
    });

    it('should map from custom name', () => {
        class TestEntity {
            @MapRule({ type: ScalarFieldType.Int, fromName: 'customNameField' })
            nameField!: number;
        }

        const e = mapEntity(TestEntity, { customNameField: 1 });
        expect(e).toEqual({ nameField: 1 });
    });

    it('should map from camel case', () => {
        class TestEntity {
            @MapRule(ScalarFieldType.Int)
            camelCaseField!: number;
        }

        const e = mapEntity(TestEntity, { camelCaseField: 1 }, false);
        expect(e).toEqual({ camelCaseField: 1 });
    });

    describe('custom mapper', () => {
        const customMapper = jest.fn();

        class TestEntity {
            @MapRule({ mapper: customMapper })
            customMapperField!: number;
        }

        it('should call custom mapper and return its result', () => {
            const RESULT = 324234;
            const VALUE = 1232244324;

            customMapper.mockReturnValueOnce(RESULT);

            const data = { custom_mapper_field: VALUE };
            const res = mapEntity(TestEntity, data);

            expect(res.customMapperField).toBe(RESULT);
            expect(customMapper).toBeCalledTimes(1);
            expect(customMapper.mock.calls.length).toBe(1);
            expect((<typeof VALUE>customMapper.mock.calls[0])[0]).toBe(VALUE);
            expect((<typeof data>customMapper.mock.calls[0])[1]).toBe(data);
        });

        it('should apply mapper from lower camel case', () => {
            const RESULT = 'sdgfgdshfg';
            const VALUE = 'nvjboigfub';

            customMapper.mockReturnValueOnce(RESULT);

            const data = { customMapperField: VALUE };
            const res = mapEntity(TestEntity, data, false);

            expect(res.customMapperField).toBe(RESULT);
            expect((<typeof VALUE>customMapper.mock.calls[0])[0]).toBe(VALUE);
            expect((<typeof data>customMapper.mock.calls[0])[1]).toBe(data);
        });

        it('should ignore unsuppoerted mapper params', () => {
            const VALUE = '43';
            const RESULT = '21';
            const data = { custom_mapper_field1: VALUE };

            customMapper.mockReturnValueOnce(RESULT);

            class CustomMapperTestEntity {
                @MapRule({
                    mapper: customMapper,
                    isOptional: false,
                    type: ScalarFieldType.Int,
                    fromName: 'customName',
                })
                customMapperField1!: number;

                @MapRule({ mapper: customMapper })
                customMapperField2!: string;
            }

            const res = mapEntity(CustomMapperTestEntity, data);

            expect(customMapper).toBeCalledTimes(2);

            const [firstCall, secondCall] = <Array<[string, typeof data | undefined]>>customMapper.mock.calls;

            expect(firstCall[0]).toBe(VALUE);
            expect(secondCall[1]).toBe(data);
            expect(secondCall[1]).toEqual(data);

            expect(secondCall[0]).toBeUndefined();
            expect(secondCall[1]).toBe(data);
            expect(secondCall[1]).toEqual(data);

            expect(res.customMapperField1).toBe(RESULT);
            expect(res.customMapperField2).toBeUndefined();
        });
    });

    it('should support nested entities', () => {
        class NestedTestEntity {
            @MapRule(ScalarFieldType.Int)
            age!: number;
        }

        class TestEntity {
            @MapRule(NestedTestEntity)
            nestedTestEntity!: NestedTestEntity;
        }

        const res = mapEntity(TestEntity, {
            nested_test_entity: {
                age: '59',
            },
        });

        expect(res).toEqual({
            nestedTestEntity: {
                age: 59,
            },
        });
    });
});
