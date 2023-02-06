import model from '../model';

describe('model', () => {
    type Test = {
        subObject?: {
            value?: Array<{
                x?: number
            }>
        }
    } & {
        [x: number]: {
            subObject?: {
                value?: Array<{
                    x?: number
                }>
            }
        }
    };

    describe('Корректно извлекается путь через обычную функцию', () => {
        test('дефолтную', () => {
            expect(model<Test>(function (object) {
                return object.subObject.value[0].x;
            })).toBe('.subObject.value[0].x');
        });

        test('с индексом', () => {
            expect(model<Test>(function (object) {
                return object[0].subObject.value[0].x;
            })).toBe('[0].subObject.value[0].x');
        });

        test('без пути', () => {
            expect(model(function (object) {
                return object;
            })).toBe('');
        });
    });

    describe('Корректно извлекается путь через стрелочную функцию', () => {
        test('дефолтную', () => {
            expect(model<Test>(object => {
                return object.subObject.value;
            })).toBe('.subObject.value');
        });

        test('сокращенную', () => {
            expect(model<Test>(object => object.subObject.value)).toBe('.subObject.value');
        });

        test('с индексом', () => {
            expect(model<Test>(object => {
                return object[0].subObject.value;
            })).toBe('[0].subObject.value');
        });

        test('без пути', () => {
            expect(model<Test>(object => object)).toBe('');
        });
    });
});
