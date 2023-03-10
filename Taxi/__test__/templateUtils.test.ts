import {Types} from '../consts';
import {buildOptions, buildSchemaPathsByType} from '../utils';

const testDataWithNestedObjectsWithoutArrays = {
    data: {
        $type: 'object',
        $properties: {
            test_string: {$type: 'string', $label: 'FIRST LEVEL STRING'},
            test_number: {$type: 'number', $label: 'FIRST LEVEL NUMBER'},
            test_obj: {
                $type: 'object',
                $properties: {
                    test_string: {$type: 'string', $label: 'SECOND LEVEL STRING'},
                    test_number: {$type: 'number', $label: 'SECOND LEVEL NUMBER'},
                    test_obj: {
                        $type: 'object',
                        $properties: {
                            test_string: {$type: 'string', $label: 'THIRD LEVEL STRING'},
                            test_number: {$type: 'number', $label: 'THIRD LEVEL NUMBER'},
                        },
                    },
                },
            },
        },
    },
};

const testDataWithNestedObjects = {
    data: {
        $type: 'object',
        $properties: {
            test_arr: {
                $type: 'array',
                $items: {
                    $type: 'object',
                    $properties: {
                        test_string: {$type: 'string', $label: 'FIRST LEVEL STRING'},
                        test_number: {$type: 'number', $label: 'FIRST LEVEL NUMBER'},
                        test_arr: {
                            $type: 'array',
                            $items: {
                                $type: 'object',
                                $properties: {
                                    test_string: {$type: 'string', $label: 'SECOND LEVEL STRING'},
                                    test_number: {$type: 'number', $label: 'SECOND LEVEL NUMBER'},
                                },
                            },
                        },
                        test_obj: {
                            $type: 'object',
                            $properties: {
                                test_string: {$type: 'string', $label: 'THIRD LEVEL STRING'},
                                test_number: {$type: 'number', $label: 'THIRD LEVEL NUMBER'},
                                test_arr: {
                                    $type: 'array',
                                    $items: {
                                        $type: 'object',
                                        $properties: {
                                            test_string: {$type: 'string', $label: 'FOURTH LEVEL STRING'},
                                            test_number: {$type: 'number', $label: 'FOURTH LEVEL NUMBER'},
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
    },
};

const testDataWithNestedArraysOnlySimpleTypesAsArrayItem = {
    test_arr: {
        $type: 'array',
        $items: {
            test_string: {$type: 'string', $label: 'FIRST LEVEL STRING'},
            test_number: {$type: 'number', $label: 'FIRST LEVEL NUMBER'},
            test_arr: {
                $type: 'array',
                $items: {
                    test_string: {$type: 'string', $label: 'SECOND LEVEL STRING'},
                    test_number: {$type: 'number', $label: 'SECOND LEVEL NUMBER'},
                },
            },
        },
    },
};

describe('templates utils', () => {
    describe('buildOptions ?????????????????? ???????????? ???????? ?????? ?????????????? ??????????', () => {
        test('?????? ???????? string ?? ?????????????????? ?????????????? ?????????????????????? ?? ????????????????', () => {
            expect(buildOptions(testDataWithNestedObjectsWithoutArrays, Types.String))
                .toEqual([
                    {
                        label: 'FIRST LEVEL STRING',
                        value: 'data.$properties.test_string',
                    },
                    {
                        label: 'SECOND LEVEL STRING',
                        value: 'data.$properties.test_obj.$properties.test_string',
                    },
                    {
                        label: 'THIRD LEVEL STRING',
                        value: 'data.$properties.test_obj.$properties.test_obj.$properties.test_string',
                    },
                ]);
        });

        test('?????? ???????? number ?? ?????????????????? ?????????????? ?????????????????????? ?? ????????????????', () => {
            expect(buildOptions(testDataWithNestedObjectsWithoutArrays, Types.Number))
                .toEqual([
                    {
                        label: 'FIRST LEVEL NUMBER',
                        value: 'data.$properties.test_number',
                    },
                    {
                        label: 'SECOND LEVEL NUMBER',
                        value: 'data.$properties.test_obj.$properties.test_number',
                    },
                    {
                        label: 'THIRD LEVEL NUMBER',
                        value: 'data.$properties.test_obj.$properties.test_obj.$properties.test_number',
                    },
                ]);
        });

        test('?????? ???????? string ???? ???????????????? ??????????, ???????? ???????????? ?????????????????? ???????????? ??????????????', () => {
            expect(buildOptions(testDataWithNestedObjects, Types.String)).toEqual([]);
            expect(buildOptions(testDataWithNestedArraysOnlySimpleTypesAsArrayItem, Types.String)).toEqual([]);
        });

        test('?????? ???????? number ???? ???????????????? ??????????, ???????? ?????????? ?????????????????? ???????????? ??????????????', () => {
            expect(buildOptions(testDataWithNestedObjects, Types.Number)).toEqual([]);
            expect(buildOptions(testDataWithNestedArraysOnlySimpleTypesAsArrayItem, Types.Number)).toEqual([]);
        });
    });

    describe('buildOptions ?????????????????? ???????????? ???????? ?????? ?????????????? ??????????', () => {
        test('?????? ???????? object ?? ?????????????????? ?????????????? ?????????????????????? ?? ????????????????', () => {
            expect(buildOptions(
                testDataWithNestedObjectsWithoutArrays,
                Types.Object,
                testDataWithNestedObjectsWithoutArrays.data.$properties.test_obj.$properties.test_obj,
                ),
            ).toEqual([
                {
                    label: 'data',
                    value: 'data',
                },
                {
                    label: 'data.$properties.test_obj',
                    value: 'data.$properties.test_obj',
                },
                {
                    label: 'data.$properties.test_obj.$properties.test_obj',
                    value: 'data.$properties.test_obj.$properties.test_obj',
                },
            ]);

            expect(buildOptions(
                testDataWithNestedObjectsWithoutArrays,
                Types.Object,
            ));
        });

        test('?????? ???????? object, ???????????????????? ?? ???????? ????????????', () => {
            expect(buildOptions(
                {
                    test_obj: testDataWithNestedObjects.data.$properties.test_arr.$items.$properties.test_obj,
                },
                Types.Object,
                testDataWithNestedObjects.data.$properties.test_arr.$items.$properties.test_obj,
            )).toEqual([
                {
                    label: 'test_obj',
                    value: 'test_obj',
                },
            ]);
        });

        test('?????? ?????????????? object, ???????????????????? ?? ???????? ????????????', () => {
            expect(buildOptions(
                {
                    test_obj: testDataWithNestedObjects.data.$properties.test_arr.$items.$properties.test_obj,
                },
                Types.Object,
            )).toEqual([
                {
                    label: 'test_obj',
                    value: 'test_obj',
                },
            ]);
        });

        test('?????? ???????? array ?? ?????????????????? ?????????????? ?????????????????????? ?? ????????????????', () => {
            expect(buildOptions(
                testDataWithNestedObjects,
                Types.Array,
                testDataWithNestedObjects
                    .data.$properties.test_arr.$items.$properties.test_obj.$properties.test_arr,
            )).toEqual([
                {
                    label: 'data.$properties.test_arr',
                    value: 'data.$properties.test_arr',
                },
            ]);
        });

        test('?????? ???????? object ???? ???????????????? ??????????, ???????? ?????????????? ?????????????????? ???????????? ??????????????', () => {
            expect(buildOptions(
                testDataWithNestedObjects,
                Types.Object,
                testDataWithNestedObjects.data.$properties.test_arr.$items.$properties.test_obj,
                ),
            ).toEqual([]);

            expect(buildOptions(
                testDataWithNestedObjects,
                Types.Object),
            ).toEqual([
                {
                    value: 'data',
                    label: 'data',
                },
            ]);
        });
    });

    describe('buildSchemaPathsByType ?????????????????? ???????????? ????????', () => {
        test('?????? ???????? ??????????', () => {
            expect(buildSchemaPathsByType(testDataWithNestedObjects))
                .toEqual({
                    array: [
                        {
                            label: 'data.test_arr',
                            value: 'data.$properties.test_arr',
                        },
                        {
                            label: 'data.test_arr.test_arr',
                            value: 'data.$properties.test_arr.$items.$properties.test_arr',
                        },
                        {
                            label: 'data.test_arr.test_obj.test_arr',
                            value: 'data.$properties.test_arr.$items.$properties.test_obj.$properties.test_arr',
                        },
                    ],
                    number: [
                        {
                            label: 'FIRST LEVEL NUMBER',
                            value: 'data.$properties.test_arr.$items.$properties.test_number',
                        },
                        {
                            label: 'SECOND LEVEL NUMBER',
                            value: 'data.$properties.test_arr.$items.$properties' +
                                '.test_arr.$items.$properties.test_number',
                        },
                        {
                            label: 'THIRD LEVEL NUMBER',
                            value: 'data.$properties.test_arr.$items.$properties.test_obj.$properties.test_number',
                        },
                        {
                            label: 'FOURTH LEVEL NUMBER',
                            value: 'data.$properties.test_arr.$items.$properties.test_obj.$properties' +
                                '.test_arr.$items.$properties.test_number',
                        },
                    ],
                    object: [
                        {
                            label: 'data',
                            value: 'data',
                        },
                        {
                            label: 'data.test_arr',
                            value: 'data.$properties.test_arr.$items',
                        },
                        {
                            label: 'data.test_arr.test_arr',
                            value: 'data.$properties.test_arr.$items.$properties.test_arr.$items',
                        },
                        {
                            label: 'data.test_arr.test_obj',
                            value: 'data.$properties.test_arr.$items.$properties.test_obj',
                        },
                        {
                            label: 'data.test_arr.test_obj.test_arr',
                            value: 'data.$properties.test_arr.$items.$properties.test_obj.$properties.test_arr.$items',
                        },
                    ],
                    string: [
                        {
                            label: 'FIRST LEVEL STRING',
                            value: 'data.$properties.test_arr.$items.$properties.test_string',
                        },
                        {
                            label: 'SECOND LEVEL STRING',
                            value: 'data.$properties.test_arr.$items.$properties' +
                                '.test_arr.$items.$properties.test_string',
                        },
                        {
                            label: 'THIRD LEVEL STRING',
                            value: 'data.$properties.test_arr.$items.$properties' +
                                '.test_obj.$properties.test_string',
                        },
                        {
                            label: 'FOURTH LEVEL STRING',
                            value: 'data.$properties.test_arr.$items.$properties.test_obj.$properties' +
                                '.test_arr.$items.$properties.test_string',
                        },
                    ],
                });
        });
    });
});
