
import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';

import inheritDescriptor from '_pkg/utils/inheritDescriptor';

import {catchWith} from '..';
import pipe, {Invoke} from '../pipeDecorator';

describe('pipeDecorator', () => {
    test('Корректно подсчитывается число оберток', () => {
        // tslint:disable-next-line: max-classes-per-file
        class ServiceWithPipes {
            public static toString = () => 'ServiceWithPipes';

            @pipe(function * (...args: any[]) {
                return 1;
            })
            @pipe(function * (...args: any[]) {
                return 1;
            })
            @pipe(function * (...args: any[]) {
                return 1;
            }, Invoke.After)
            @pipe(function * (...args: any[]) {
                return 1;
            }, Invoke.After)
            public static method(...args: any[]) {
                return 1;
            }
        }

        expect((ServiceWithPipes.method as any).__$pipeMeta.levels).toBe(4);
    });

    describe('Декоратор инвариантен относительно порядка обертки', () => {
        test('Пример 1 - pipeMeta очищается между вызовами', () => {
            let result = '0';

            // tslint:disable-next-line: max-classes-per-file
            class ServiceWithPipes {
                public static toString = () => 'ServiceWithPipes';

                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0']);
                    result += '1';
                    return result;
                })
                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', '01']);
                    result += '2';
                    return result;
                })
                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', '01', '012', '0123', '01234']);
                    result += '5';
                    return result;
                }, Invoke.After)

                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', '01', '012', '0123']);
                    result += '4';
                    return result;
                }, Invoke.After)
                public static method(...args: any[]) {
                    expect(args).toEqual(['0', '01', '012']);
                    result += '3';
                    return result;
                }
            }

            return expectSaga(function * () {
                yield matchers.call(ServiceWithPipes.method, '0');
                result = '0';
                return yield matchers.call(ServiceWithPipes.method, '0');
            })
                .run()
                .then(runResult => {
                    expect(result).toBe('012345');
                    expect(runResult.returnValue).toBe(result);
                });
        });

        test('Пример 2 - без ретерна в методе', () => {
            let result = '0';

            // tslint:disable-next-line: max-classes-per-file
            class ServiceWithPipes {
                public static toString = () => 'ServiceWithPipes';

                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', '01', '012', undefined, '01234']);
                    result += '5';
                    return result;
                }, Invoke.After)
                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', '01', '012', undefined]);
                    result += '4';
                    return result;
                }, Invoke.After)
                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0']);
                    result += '1';
                    return result;
                })
                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', '01']);
                    result += '2';
                    return result;
                })
                public static method(...args: any[]) {
                    expect(args).toEqual(['0', '01', '012']);
                    result += '3';
                }
            }

            return expectSaga(function * () {
                yield matchers.call(ServiceWithPipes.method, '0');
                result = '0';
                return yield matchers.call(ServiceWithPipes.method, '0');
            })
                .run()
                .then(runResult => {
                    expect(result).toBe('012345');
                    expect(runResult.returnValue).toBe(result);
                });
        });

        test('Пример 3 - без ретерна в Invoke.Before', () => {
            let result = '0';

            // tslint:disable-next-line: max-classes-per-file
            class ServiceWithPipes {
                public static toString = () => 'ServiceWithPipes';

                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', undefined, '012', '0123', '01234']);
                    result += '5';
                    return result;
                }, Invoke.After)
                @pipe(function * (...args: any[]): any {
                    expect(args).toEqual(['0']);
                    result += '1';
                })
                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', undefined, '012', '0123']);
                    result += '4';
                    return result;
                }, Invoke.After)
                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', undefined]);
                    result += '2';
                    return result;
                })
                public static method(...args: any[]) {
                    expect(args).toEqual(['0', undefined, '012']);
                    result += '3';
                    return result;
                }
            }

            return expectSaga(function * () {
                yield matchers.call(ServiceWithPipes.method, '0');
                result = '0';
                return yield matchers.call(ServiceWithPipes.method, '0');
            })
                .run()
                .then(runResult => {
                    expect(result).toBe('012345');
                    expect(runResult.returnValue).toBe(result);
                });
        });

        test('Пример 4 - без ретерна в Invoke.After', () => {
            let result = '0';

            // tslint:disable-next-line: max-classes-per-file
            class ServiceWithPipes {
                public static toString = () => 'ServiceWithPipes';

                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0']);
                    result += '1';
                    return result;
                })
                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', '01', '012', '0123', undefined]);
                    result += '5';
                    return result;
                }, Invoke.After)
                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', '01']);
                    result += '2';
                    return result;
                })
                @pipe(function * (...args: any[]): any {
                    expect(args).toEqual(['0', '01', '012', '0123']);
                    result += '4';
                }, Invoke.After)
                public static method(...args: any[]) {
                    expect(args).toEqual(['0', '01', '012']);
                    result += '3';
                    return result;
                }
            }

            return expectSaga(function * () {
                yield matchers.call(ServiceWithPipes.method, '0');
                result = '0';
                return yield matchers.call(ServiceWithPipes.method, '0');
            })
                .run()
                .then(runResult => {
                    expect(result).toBe('012345');
                    expect(runResult.returnValue).toBe(result);
                });
        });

        test('Пример 5 - без ретерна в последнем pipe', () => {
            let result = '0';

            // tslint:disable-next-line: max-classes-per-file
            class ServiceWithPipes {
                public static toString = () => 'ServiceWithPipes';

                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0']);
                    result += '1';
                    return result;
                })
                @pipe(function * (...args: any[]): any {
                    expect(args).toEqual(['0', '01', '012', '0123', '01234']);
                    result += '5';
                }, Invoke.After)
                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', '01', '012', '0123']);
                    result += '4';
                    return result;
                }, Invoke.After)
                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', '01']);
                    result += '2';
                    return result;
                })
                public static method(...args: any[]) {
                    expect(args).toEqual(['0', '01', '012']);
                    result += '3';
                    return result;
                }
            }

            return expectSaga(function * () {
                yield matchers.call(ServiceWithPipes.method, '0');
                result = '0';
                return yield matchers.call(ServiceWithPipes.method, '0');
            })
                .run()
                .then(runResult => {
                    expect(result).toBe('012345');
                    expect(runResult.returnValue).toBe(undefined);
                });
        });

        test('Пример 6 - с saveResult === false', () => {
            let result = '0';

            // tslint:disable-next-line: max-classes-per-file
            class ServiceWithPipes {
                public static toString = () => 'ServiceWithPipes';

                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', '01', '0123', '012345']);
                    result = `_${result}_`;
                    return result;
                }, Invoke.After, false)
                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', '01', '0123']);
                    result += '5';
                    return result;
                }, Invoke.After)
                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0']);
                    result += '1';
                    return result;
                })
                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', '01']);
                    result += '2';
                    return result;
                }, Invoke.Before, false)
                @pipe(function * (...args: any[]) {
                    expect(args).toEqual(['0', '01', '0123']);
                    result += '4';
                    return result;
                }, Invoke.After, false)
                public static method(...args: any[]) {
                    expect(args).toEqual(['0', '01']);
                    result += '3';
                    return result;
                }
            }

            return expectSaga(function * () {
                yield matchers.call(ServiceWithPipes.method, '0');
                result = '0';
                return yield matchers.call(ServiceWithPipes.method, '0');
            })
                .run()
                .then(runResult => {
                    expect(result).toBe('_012345_');
                    expect(runResult.returnValue).toBe('012345');
                });
        });
    });

    test('Привызове с разными аргументами, они корректно пробрасываются', () => {
        const mockFn = jest.fn();
        // tslint:disable-next-line: max-classes-per-file
        class ServiceWithPipes {
            public static toString = () => 'ServiceWithPipes';
            @pipe(function * (...args: any[]) {
                return mockFn(...args);
            })
            public static method(...args: any[]) {
                return;
            }
        }

        return expectSaga(function * () {
            yield matchers.call(ServiceWithPipes.method, '0');
            expect(mockFn).toHaveBeenLastCalledWith('0');
            yield matchers.call(ServiceWithPipes.method, '1', '2');
            expect(mockFn).toHaveBeenLastCalledWith('1', '2');
            yield matchers.call(ServiceWithPipes.method, '3');
            expect(mockFn).toHaveBeenLastCalledWith('3');
        })
            .run();
    });

    test('Привызове с разными аргументами, они корректно пробрасываются после ошибок', () => {
        const mockFn = jest.fn();
        // tslint:disable-next-line: prefer-const
        let result = 0;

        // tslint:disable-next-line: max-classes-per-file
        class ServiceWithPipes {
            public static toString = () => 'ServiceWithPipes';

            @catchWith(() => ({}))
            @pipe(function * (...args: any[]) {
                return result++;
            })
            @pipe(function * (...args: any[]): any {
                if (args[1] === 0) {
                    throw new Error();
                }

                return args[1];
            })
            @pipe(function * (...args: any[]) {
                return mockFn(...args);
            })
            public static method(...args: any[]) {
                return;
            }
        }

        return expectSaga(function * () {
            yield matchers.call(ServiceWithPipes.method, '1');
            expect(mockFn).toHaveBeenCalledTimes(0);
            yield matchers.call(ServiceWithPipes.method, '1');
            expect(mockFn).toHaveBeenLastCalledWith('1', 1, 1);
        })
            .run();
    });

    test('Результаты выпиливаются из стека при ошибках', () => {
        const mockFn = jest.fn();
        // tslint:disable-next-line: prefer-const
        let result = 0;

        const repeatTwice = (
            target: any,
            key: string,
            descriptor: PropertyDescriptor
        ) => {
            const origin = descriptor.value;

            return inheritDescriptor(
                descriptor,
                function * (...args: any[]) {
                    let count = 2;
                    while (count-- > 0) {
                        yield matchers.call(origin, ...args);
                    }
                }
            );
        };

        // tslint:disable-next-line: max-classes-per-file
        class ServiceWithPipes {
            public static toString = () => 'ServiceWithPipes';

            @pipe(function * (...args: any[]) {
                return 0;
            })
            @repeatTwice
            @catchWith(() => ({}))
            @pipe(function * (...args: any[]): any {
                return result++;
            })
            @pipe(function * (...args: any[]) {
                return mockFn(...args);
            })
            public static method(...args: any[]) {
                throw new Error();
            }
        }

        return expectSaga(function * () {
            yield matchers.call(ServiceWithPipes.method);
            expect(mockFn).toHaveBeenCalledTimes(2);
            expect(mockFn).toHaveBeenNthCalledWith(1, 0, 0);
            expect(mockFn).toHaveBeenNthCalledWith(2, 0, 1);
        })
            .run();
    });

    test('this внутри pipe это сервис', () => {
        // tslint:disable-next-line: max-classes-per-file
        class ServiceA {
            public static toString = () => 'ServiceA';

            @pipe(function* () {
                expect(this).toEqual(ServiceB);
            })
            public static *method(): Generator {
                //
            }
        }

        // tslint:disable-next-line: max-classes-per-file
        class ServiceB extends ServiceA {
            public static toString = () => 'ServiceB';

            @pipe(function* () {
                expect(this).toEqual(ServiceB);
            })
            public static *method() {
                yield matchers.call([this, super.method]);
            }
        }

        return expectSaga(function* () {
            yield matchers.call([ServiceB, ServiceB.method]);
        }).run();
    });
});
