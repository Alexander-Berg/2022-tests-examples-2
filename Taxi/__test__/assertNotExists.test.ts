import {assertNotExists} from '../assertNotExists';

type ModelProps = {
    a: {
        b: string[];
        с?: number;
    };
    d: boolean;
    e?: Array<{
        f: string;
        g: string;
    }>;
};

const MODEL: ModelProps = {
    a: {
        b: ['hi']
    },
    d: true
};
const ERROR = new Error('Value expected');

describe('assertNotExists', () => {
    test('выкинет ошибку при null и undefined', () => {
        expect(() => assertNotExists(null)).toThrowError(ERROR);
        expect(() => assertNotExists(undefined)).toThrowError(ERROR);
        expect(() => assertNotExists(MODEL.a.с)).toThrowError(ERROR);
        expect(() => assertNotExists(MODEL.e)).toThrowError(ERROR);
        expect(() => assertNotExists(MODEL.a.b[1])).toThrowError(ERROR);
    });

    test('выкинет пользовательскую ошибку, если она передана', () => {
        const error = 'error';
        expect(() => assertNotExists(MODEL.a.с, error)).toThrowError(new Error(error));
    });

    test('не выкинет ошибку при существующих данных', () => {
        expect(assertNotExists(MODEL)).toBeUndefined();
        expect(assertNotExists(MODEL.a)).toBeUndefined();
        expect(assertNotExists(MODEL.d)).toBeUndefined();

        expect(assertNotExists(false)).toBeUndefined();
        expect(assertNotExists('')).toBeUndefined();
        expect(assertNotExists(0)).toBeUndefined();
        expect(assertNotExists([])).toBeUndefined();
        expect(assertNotExists({})).toBeUndefined();
        expect(assertNotExists(1)).toBeUndefined();
    });
});
