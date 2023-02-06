import { mockReq } from '@lib/views/mockReq';
import { logError } from '@lib/log/logError';
import { l10n } from '../server.l10n';

jest.mock('../../log/logError.ts', () => {
    return {
        logError: jest.fn().mockImplementation(() => {
            throw new Error('logError called!');
        })
    };
});
const mockedLogError = logError as jest.Mock;

describe('home.lang', function() {
    afterEach(() => {
        jest.clearAllMocks();
    });

    test('should return string', function() {
        expect(l10n('yandex')).toEqual('Яндекс');
        expect(l10n('mail.title')).toEqual('Почта');
    });

    test('should return array', function() {
        expect(l10n('mail.num.mail')).toEqual(['письмо', 'письма', 'писем']);
    });

    test('should return empty string if not found', function() {
        mockedLogError.mockImplementation(() => {});

        expect(l10n('some.inexistent.thing')).toEqual('');
        expect(l10n('mail.some.inexistent.thing')).toEqual('');
        expect(l10n('__proto__')).toEqual('');
        expect(l10n('mail.__proto__')).toEqual('');

        expect(mockedLogError.mock.calls).toMatchSnapshot();
    });

    test('should work with different locales', function() {
        expect(l10n('mail.title', 'ua')).toEqual('Пошта');
        expect(l10n.call(mockReq({}, { Locale: 'ua' }), 'mail.title')).toEqual('Пошта');
    });
});
