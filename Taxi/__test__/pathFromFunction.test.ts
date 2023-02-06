import pathFromFunction from '../pathFromFunction';

/* tslint:disable */
describe('pathFromFunction', () => {
    describe('Корректно извлекается путь', () => {
        test('В функции простой return пути', () => {
            expect(pathFromFunction((object: any) => object.subObject.value)).toBe('subObject.value');
        });

        test('С индексом', () => {
            expect(pathFromFunction((object: any) => object[0].subObject.value)).toBe('[0].subObject.value');
        });

        test('Корректно обрабатывает вычислимые выражения', () => {
            const index = 0;
            const key = 'subObject';

            expect(pathFromFunction((object: any) => object[index][key])).toBe('[0].subObject');
        });

        test('без пути', () => {
            expect(pathFromFunction(object => object)).toBe('');
        });
    });

    describe('Корректно выкидываются исключения', () => {
        test('В функции есть лишние обращения к аргументу через свойство', () => {
            expect(() => pathFromFunction((object: any) => {
                object.test;
                return object.subObject.value
            })).toThrow();
        });

        test('В функции сам аргумент используется в вычислениях свойства аргумента', () => {
            expect(() => pathFromFunction((object: any) => object[object.value])).toThrow();
        })

        test('В функции есть обращения к аргументу или свойству аргумента через оператор in', () => {
            expect(() => pathFromFunction((object: any) => {
                if ('test' in object) {
                    return object.test;
                }
                return object.subObject.value
            })).toThrow();

            expect(() => pathFromFunction((object: any) => {
                if ('test' in object.parent) {
                    return object.test;
                }
                return object.subObject.value
            })).toThrow();
        });

        test('В функции пути нет return', () => {
            expect(() => pathFromFunction(object => {})).toThrow();
        })
    })
});
