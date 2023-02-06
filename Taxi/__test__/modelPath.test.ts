import {exact} from '_types/__test__/asserts';
import {StrictModel} from '_types/common/infrastructure';

import modelPath, {modelPathStrict, pathGen, pathStrictGen} from '../modelPath';

const enum TestEnum {
    First = 'first',
    Last = 'last'
}

type TestSubType = {
    a: string;
};

type TestType = {
    x?: {
        y?: [{
            z: number
        }]
    },
    [TestEnum.First]: TestSubType;
};

type TestArrayType = TestType[];

const MODEL = 'MODEL';

describe('modelPath', () => {
    test('default', () => {
        const path = modelPath<TestType>(MODEL);
        const arrPath = modelPath<TestArrayType>(MODEL);

        expect(path(m => {
            const str = m.x.y[0].z;
            exact<typeof str, number>(true); // проверяем что вывод типов работает
            return str;
        })).toBe(`${MODEL}.x.y[0].z`);
        expect(arrPath(m => m[0].x.y[0].z)).toBe(`${MODEL}[0].x.y[0].z`);
    });

    test('root', () => {
        const path = modelPath<TestType>(MODEL, true);
        const arrPath = modelPath<TestArrayType>(MODEL, true);

        expect(path(m => {
            const str = m.x.y[0].z;
            exact<typeof str, number>(true);
            return str;
        })).toBe(`${MODEL}x.y[0].z`);
        expect(arrPath(m => m[0].x.y[0].z)).toBe(`${MODEL}[0].x.y[0].z`);
    });

    test('empty model', () => {
        const path = modelPath<TestType>('');
        const arrPath = modelPath<TestArrayType>('');

        expect(path(m => {
            const str = m.x.y[0].z;
            exact<typeof str, number>(true);
            return str;
        })).toBe(`.x.y[0].z`);
        expect(arrPath(m => m[0].x.y[0].z)).toBe(`[0].x.y[0].z`);
    });

    test('empty model root', () => {
        const path = modelPath<TestType>('', true);
        const arrPath = modelPath<TestArrayType>('', true);

        expect(path(m => {
            const str = m.x.y[0].z;
            exact<typeof str, number>(true);
            return str;
        })).toBe(`x.y[0].z`);
        expect(arrPath(m => m[0].x.y[0].z)).toBe(`[0].x.y[0].z`);
    });

    test('override root', () => {
        const path = modelPath<TestType>(MODEL, true);
        const arrPath = modelPath<TestArrayType>(MODEL, true);

        expect(path(m => {
            const str = m.x.y[0].z;
            exact<typeof str, number>(true);
            return str;
        }, false)).toBe(`${MODEL}.x.y[0].z`);
        expect(arrPath(m => m[0].x.y[0].z, false)).toBe(`${MODEL}[0].x.y[0].z`);
    });

    test('override globally', () => {
        const path = modelPath<TestType>(MODEL, true);
        const arrPath = modelPath<TestArrayType>(MODEL, true);

        const pathOverride = path.override({isRoot: false});
        const arrPathOverride = arrPath.override({isRoot: false});

        expect(path(m => {
            const str = m.x.y[0].z;
            exact<typeof str, number>(true);
            return str;
        })).toBe(`${MODEL}x.y[0].z`);
        expect(arrPath(m => m[0].x.y[0].z)).toBe(`${MODEL}[0].x.y[0].z`);

        expect(pathOverride(m => {
            const str = m.x.y[0].z;
            exact<typeof str, number>(true);
            return str;
        })).toBe(`${MODEL}.x.y[0].z`);
        expect(arrPathOverride(m => m[0].x.y[0].z)).toBe(`${MODEL}[0].x.y[0].z`);
    });

    test('composition', () => {
        const basePath = modelPath<TestType>(MODEL);
        const compositePath = modelPath<TestSubType>(basePath(m => m[TestEnum.First]));

        expect(compositePath(m => m.a)).toBe(`${MODEL}.${TestEnum.First}.a`);
    });

    test('StrictModel<M>', () => {
        const basePath = modelPath(MODEL as StrictModel<TestType>);
        const innerPath = basePath(m => m[TestEnum.First]);
        exact<typeof innerPath, StrictModel<TestSubType>>(true);

        const compositePath = modelPath(innerPath);
        const subPath = compositePath(m => m.a);
        exact<typeof subPath, StrictModel<string>>(true);
    });
});

describe('modelPathStrict', () => {
    test('default', () => {
        const path = modelPathStrict<TestType>(MODEL);
        const arrPath = modelPathStrict<TestArrayType>(MODEL);

        expect(path(m => {
            const str = m.x?.y?.[0].z;
            exact<typeof str, number | undefined>(true); // проверяем что вывод типов работает
            return str;
        })).toBe(`${MODEL}.x.y[0].z`);

        expect(arrPath(m => m[0].x?.y?.[0].z)).toBe(`${MODEL}[0].x.y[0].z`);
    });
});

describe('pathGen', () => {
    describe('with type', () => {
        test('default', () => {
            const path = pathGen<TestType>(MODEL);
            const arrPath = pathGen<TestArrayType>(MODEL);

            expect(path(m => {
                const str = m.x.y[0].z;
                exact<typeof str, number>(true); // проверяем что вывод типов работает
                return str;
            })).toBe(`${MODEL}.x.y[0].z`);
            expect(arrPath(m => m[0].x.y[0].z)).toBe(`${MODEL}[0].x.y[0].z`);
        });

        test('root', () => {
            const path = pathGen<TestType>(MODEL, true);
            const arrPath = pathGen<TestArrayType>(MODEL, true);

            expect(path(m => {
                const str = m.x.y[0].z;
                exact<typeof str, number>(true);
                return str;
            })).toBe(`${MODEL}x.y[0].z`);
            expect(arrPath(m => m[0].x.y[0].z)).toBe(`${MODEL}[0].x.y[0].z`);
        });

        test('empty model', () => {
            const path = pathGen<TestType>('');
            const arrPath = pathGen<TestArrayType>('');

            expect(path(m => {
                const str = m.x.y[0].z;
                exact<typeof str, number>(true);
                return str;
            })).toBe(`.x.y[0].z`);
            expect(arrPath(m => m[0].x.y[0].z)).toBe(`[0].x.y[0].z`);
        });

        test('empty model root', () => {
            const path = pathGen<TestType>('', true);
            const arrPath = pathGen<TestArrayType>('', true);

            expect(path(m => {
                const str = m.x.y[0].z;
                exact<typeof str, number>(true);
                return str;
            })).toBe(`x.y[0].z`);
            expect(arrPath(m => m[0].x.y[0].z)).toBe(`[0].x.y[0].z`);
        });

        test('override root', () => {
            const path = pathGen<TestType>(MODEL, true);
            const arrPath = pathGen<TestArrayType>(MODEL, true);

            expect(path(m => {
                const str = m.x.y[0].z;
                exact<typeof str, number>(true);
                return str;
            }, false)).toBe(`${MODEL}.x.y[0].z`);
            expect(arrPath(m => m[0].x.y[0].z, false)).toBe(`${MODEL}[0].x.y[0].z`);
        });

        test('override globally', () => {
            const path = pathGen<TestType>(MODEL, true);
            const arrPath = pathGen<TestArrayType>(MODEL, true);

            const pathOverride = path.override({isRoot: false});
            const arrPathOverride = arrPath.override({isRoot: false});

            expect(path(m => {
                const str = m.x.y[0].z;
                exact<typeof str, number>(true);
                return str;
            })).toBe(`${MODEL}x.y[0].z`);
            expect(arrPath(m => m[0].x.y[0].z)).toBe(`${MODEL}[0].x.y[0].z`);

            expect(pathOverride(m => {
                const str = m.x.y[0].z;
                exact<typeof str, number>(true);
                return str;
            })).toBe(`${MODEL}.x.y[0].z`);
            expect(arrPathOverride(m => m[0].x.y[0].z)).toBe(`${MODEL}[0].x.y[0].z`);
        });

        test('composition', () => {
            const basePath = pathGen<TestType>(MODEL);
            const compositePath = pathGen<TestSubType>(basePath(m => m[TestEnum.First]));

            expect(compositePath(m => m.a)).toBe(`${MODEL}.${TestEnum.First}.a`);
        });
    });

    describe('without type', () => {
        test('default', () => {
            const path = pathGen(MODEL);
            const arrPath = pathGen(MODEL);

            expect(path<TestType>(m => {
                const str = m.x.y[0].z;
                exact<typeof str, number>(true); // проверяем что вывод типов работает
                return str;
            })).toBe(`${MODEL}.x.y[0].z`);
            expect(arrPath<TestArrayType>(m => m[0].x.y[0].z)).toBe(`${MODEL}[0].x.y[0].z`);
        });

        test('root', () => {
            const path = pathGen(MODEL, true);
            const arrPath = pathGen(MODEL, true);

            expect(path<TestType>(m => {
                const str = m.x.y[0].z;
                exact<typeof str, number>(true);
                return str;
            })).toBe(`${MODEL}x.y[0].z`);
            expect(arrPath<TestArrayType>(m => m[0].x.y[0].z)).toBe(`${MODEL}[0].x.y[0].z`);
        });

        test('empty model', () => {
            const path = pathGen('');
            const arrPath = pathGen('');

            expect(path<TestType>(m => {
                const str = m.x.y[0].z;
                exact<typeof str, number>(true);
                return str;
            })).toBe(`.x.y[0].z`);
            expect(arrPath<TestArrayType>(m => m[0].x.y[0].z)).toBe(`[0].x.y[0].z`);
        });

        test('empty model root', () => {
            const path = pathGen('', true);
            const arrPath = pathGen('', true);

            expect(path<TestType>(m => {
                const str = m.x.y[0].z;
                exact<typeof str, number>(true);
                return str;
            })).toBe(`x.y[0].z`);
            expect(arrPath<TestArrayType>(m => m[0].x.y[0].z)).toBe(`[0].x.y[0].z`);
        });

        test('override root', () => {
            const path = pathGen(MODEL, true);
            const arrPath = pathGen(MODEL, true);

            expect(path<TestType>(m => {
                const str = m.x.y[0].z;
                exact<typeof str, number>(true);
                return str;
            }, false)).toBe(`${MODEL}.x.y[0].z`);
            expect(arrPath<TestArrayType>(m => m[0].x.y[0].z, false)).toBe(`${MODEL}[0].x.y[0].z`);
        });

        test('override globally', () => {
            const path = pathGen(MODEL, true);
            const arrPath = pathGen(MODEL, true);

            const pathOverride = path.override({isRoot: false});
            const arrPathOverride = arrPath.override({isRoot: false});

            expect(path<TestType>(m => {
                const str = m.x.y[0].z;
                exact<typeof str, number>(true);
                return str;
            })).toBe(`${MODEL}x.y[0].z`);
            expect(arrPath<TestArrayType>(m => m[0].x.y[0].z)).toBe(`${MODEL}[0].x.y[0].z`);

            expect(pathOverride<TestType>(m => {
                const str = m.x.y[0].z;
                exact<typeof str, number>(true);
                return str;
            })).toBe(`${MODEL}.x.y[0].z`);
            expect(arrPathOverride<TestArrayType>(m => m[0].x.y[0].z)).toBe(`${MODEL}[0].x.y[0].z`);
        });

        test('composition', () => {
            const basePath = pathGen(MODEL);
            const compositePath = pathGen(basePath<TestType>(m => m[TestEnum.First]));

            expect(compositePath<TestSubType>(m => m.a)).toBe(`${MODEL}.${TestEnum.First}.a`);
        });
    });
});

describe('pathStrictGen', () => {
    test('default', () => {
        const path = pathStrictGen<TestType>(MODEL);
        const arrPath = pathStrictGen<TestArrayType>(MODEL);

        expect(path(m => {
            const str = m.x?.y?.[0].z;
            exact<typeof str, number | undefined>(true);
            return str;
        })).toBe(`${MODEL}.x.y[0].z`);

        expect(arrPath(m => m[0].x?.y?.[0].z)).toBe(`${MODEL}[0].x.y[0].z`);
    });
});
