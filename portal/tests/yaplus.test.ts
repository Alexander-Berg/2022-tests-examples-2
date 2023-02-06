import { logError } from '@lib/log/logError';
import { getCheapest, getMostExpansive } from '../yaplus';

jest.mock('../../log/logError.ts', () => {
    return {
        logError: jest.fn().mockImplementation(() => {
            throw new Error('logError called!');
        })
    };
});
const mockedLogError = logError as jest.Mock;

describe('yaplus', function() {
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('getCheapest', function() {
        test('должнно вернуть YA_PLUS из основных типов подписки', function() {
            expect(getCheapest([
                'YA_PLUS',
                'KP_BASIC',
                'YA_PREMIUM'
            ])).toEqual('YA_PLUS');
        });

        test('должно вернуть KP_BASIC из основных типов подписки кроме YA_PLUS', function() {
            expect(getCheapest([
                'YA_PREMIUM',
                'KP_BASIC'
            ])).toEqual('KP_BASIC');
        });

        test('должно вернуть YA_PLUS из всех видом подписки', function() {
            expect(getCheapest([
                'YA_PLUS_3M',
                'YA_PLUS_KP',
                'YA_PLUS_KP_3M',
                'YA_PREMIUM',
                'KP_BASIC'
            ])).toEqual('YA_PLUS');
        });

        test('должно вернуть undefined и залогировать ошибку с новым типом', function() {
            mockedLogError.mockImplementation(() => {});

            expect(getCheapest([
                'YA_PLUS_3M_NEW'
            ])).toBeUndefined();

            expect(mockedLogError.mock.calls).toMatchSnapshot();
        });
    });

    describe('getMostExpansive', function() {
        test('должнно вернуть YA_PREMIUM из основных типов подписки', function() {
            expect(getMostExpansive([
                'YA_PLUS',
                'KP_BASIC',
                'YA_PREMIUM'
            ])).toEqual('YA_PREMIUM');
        });

        test('должно вернуть KP_BASIC из основных типов подписки кроме YA_PREMIUM', function() {
            expect(getMostExpansive([
                'YA_PLUS',
                'KP_BASIC'
            ])).toEqual('KP_BASIC');
        });

        test('должно вернуть YA_PREMIUM из всех видом подписки', function() {
            expect(getMostExpansive([
                'YA_PLUS_3M',
                'YA_PLUS_KP',
                'YA_PLUS_KP_3M',
                'YA_PREMIUM',
                'KP_BASIC'
            ])).toEqual('YA_PREMIUM');
        });

        test('должно вернуть undefined и залогировать ошибку с новым типом', function() {
            mockedLogError.mockImplementation(() => {});

            expect(getMostExpansive([
                'YA_PLUS_3M_NEW'
            ])).toBeUndefined();

            expect(mockedLogError.mock.calls).toMatchSnapshot();
        });
    });
});
