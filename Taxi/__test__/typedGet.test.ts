import typedGet from '../typedGet';

describe('typedGet', () => {
    test('Корректно извлекается существующее значение через обычную функцию', () => {
        const targetObject = {
            subObject: {
                value: 1
            }
        };

        expect(typedGet(targetObject, function (object) {
            return object.subObject.value;
        })).toBe(1);
    });

    test('Корректно извлекается существующее значение через стрелочную функцию', () => {
        const targetObject = {
            subObject: {
                value: 1
            }
        };

        expect(typedGet(targetObject, object => {
            return object.subObject.value;
        })).toBe(1);
    });

    test('Корректно извлекается существующее значение через сокращенную стрелочную функцию', () => {
        const targetObject = {
            subObject: {
                value: 1
            }
        };

        expect(typedGet(targetObject, object => object.subObject.value)).toBe(1);
    });

    test('Корректно обрабатывает не существующие пути', () => {
        const targetObject: {subObject?: {value: number}} = {
            subObject: undefined
        };

        expect(typedGet(targetObject, object => object.subObject!.value)).toBe(undefined);
    });

    test('Корректно обрабатывает значения по-умолчанию', () => {
        const targetObject: {subObject?: {value: number}} = {
            subObject: undefined
        };

        expect(typedGet(targetObject, object => object.subObject!.value, 1)).toBe(1);
    });

    test('Корректно извлекает элементы массива', () => {
        const targetObject = {
            subObject: {
                values: [{
                    subValue: 1
                }]
            }
        };

        expect(typedGet(targetObject, object => object.subObject.values[0].subValue)).toBe(1);
    });

    test('Корректно извлекает элементы из массива', () => {
        const targetObject = [{
            subObject: {
                values: [{
                    subValue: 1
                }]
            }
        }];

        expect(typedGet(targetObject, object => object[0].subObject.values[0].subValue)).toBe(1);
    });

    test('Корректно обрабатывает пустой путь', () => {
        const targetObject = {
            subObject: 1
        };

        expect(typedGet(targetObject, object => object)).toEqual(targetObject);
    });

    test('Корректно обрабатывает вычислимые выражения', () => {
        const targetObject = {
            subObject: [{
                x: 1
            }]
        };

        const index = 0;
        const key = 'subObject';

        expect(typedGet(targetObject, object => object[key][index].x)).toEqual(1);
    });

    test('Корректно обрабатывает undefined в конце пути', () => {
        const targetObject = {
            subObject: [{
                x: undefined as any
            }]
        };

        const index = 0;
        const key = 'subObject';

        expect(typedGet(targetObject, object => object[key][index].x, 1)).toEqual(1);
        expect(typedGet(targetObject, object => object[key][2], null)).toEqual(null);
    });
});
