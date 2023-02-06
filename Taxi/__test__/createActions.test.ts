import {getClassMethods} from '_pkg/utils/createActions';

// tslint:disable:max-classes-per-file

describe('utils/createActions', () => {
    describe('getClassMethods', () => {
        test('работает с пропертями', () => {
            class API {
                public static toString = () => 'API';
                public find = () => 1;
            }

            const methods = getClassMethods(new API());

            expect(methods).toHaveLength(1);
            expect(methods).toContain('find');
        });

        test('работает с методами', () => {
            class API {
                public static toString = () => 'API';
                public find () {
                    return 1;
                }
            }

            const methods = getClassMethods(new API());

            expect(methods).toHaveLength(1);
            expect(methods).toContain('find');
        });

        test('работает с наследованием', () => {
            class API1 {
                public find() {
                    return 1;
                }
            }

            class API2 extends API1 {
                public request() {
                    return 2;
                }
            }

            const methods = getClassMethods(new API2());

            expect(methods).toHaveLength(2);
            expect(methods).toContain('request');
            expect(methods).toContain('find');
        });

        test('работает с переопределением', () => {
            class API1 {
                public find() {
                    return 1;
                }
            }

            class API2 extends API1 {
                public find() {
                    return 2;
                }
            }

            const methods = getClassMethods(new API2());

            expect(methods).toHaveLength(1);
            expect(methods).toContain('find');
        });

        test('работает со статическими пропсами', () => {
            class API {
                public static find = () => 1;
            }

            const methods = getClassMethods(API);

            expect(methods).toHaveLength(1);
            expect(methods).toContain('find');
        });

        test('работает с наследованием статических пропсов', () => {
            class API1 {
                public static find1 = () => 1;
            }

            class API2 extends API1 {
                public static find2 = () => 1;
            }

            const methods = getClassMethods(API2);

            expect(methods).toHaveLength(2);
            expect(methods).toContain('find1');
            expect(methods).toContain('find2');
        });

        test('работает со статическими методами', () => {
            class API {
                public static find() {
                    return 1;
                }
            }

            const methods = getClassMethods(API);

            expect(methods).toHaveLength(1);
            expect(methods).toContain('find');
        });

        test('работает с наследованием статических методов', () => {
            class API1 {
                public static find1 () {
                    return 1;
                }
            }

            class API2 extends API1 {
                public static find2 () {
                    return 1;
                }
            }

            const methods = getClassMethods(API2);

            expect(methods).toHaveLength(2);
            expect(methods).toContain('find1');
            expect(methods).toContain('find2');
        });
    });
});
