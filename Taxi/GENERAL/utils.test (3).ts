import {CoreConfig} from '@yandex-taxi/corp-core/config';

import {getPassportAuthUrl, getUserEmail} from './utils';

describe('corp-landing utils', () => {
    const getConfig = () =>
        ({
            passportHost: 'https://passportHost',
            host: 'https://host',
            tld: 'io',
        } as CoreConfig);

    describe('getPassportAuthUrl', () => {
        const url = getPassportAuthUrl(getConfig(), {port: '8080'});
        const urlWithoutPort = getPassportAuthUrl(getConfig());

        test('url with port is match', () => {
            expect(url).toBe(
                // eslint-disable-next-line max-len
                'https://passportHost/auth?from=taxi&retpath=https%3A%2F%2Fhttps%3A%2F%2Fhost%3A8080',
            );
        });
        test('url without port is match', () => {
            expect(urlWithoutPort).toBe(
                'https://passportHost/auth?from=taxi&retpath=https%3A%2F%2Fhttps%3A%2F%2Fhost',
            );
        });
    });

    describe('getUserEmail', () => {
        const SIMPLE_LOGIN = 'someLogin';
        const EMAIL = 'email@test.test';
        const CONFIG = getConfig();

        test('get correct simple login', () => {
            expect(getUserEmail(SIMPLE_LOGIN, CONFIG)).toBe(`${SIMPLE_LOGIN}@yandex.${CONFIG.tld}`);
        });
        test('if it is email or empty string - it just returns', () => {
            expect(getUserEmail(EMAIL, CONFIG)).toBe(EMAIL);
            expect(getUserEmail('', CONFIG)).toBe('');
        });
    });
});
