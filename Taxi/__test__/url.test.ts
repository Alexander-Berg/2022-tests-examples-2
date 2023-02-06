import {makeUrlSafe, normalizeUrl} from '../url';

test('makeUrlSafe - корректно схлопывает лишние слеши', () => {
    expect(makeUrlSafe('https://my-long-name-host.yandex-team.ru//2api/shmapi3///pam/pam/pam//')).toBe(
        'https://my-long-name-host.yandex-team.ru/2api/shmapi3/pam/pam/pam/'
    );

    expect(makeUrlSafe('//my-long-name-host.yandex-team.ru//2api/shmapi3///pam/pam/pam//')).toBe(
        '/my-long-name-host.yandex-team.ru/2api/shmapi3/pam/pam/pam/'
    );

    expect(makeUrlSafe('http://my-long-name-host.yandex-team.ru//2api/shmapi3///pam/pam/1//')).toBe(
        'http://my-long-name-host.yandex-team.ru/2api/shmapi3/pam/pam/1/'
    );

    expect(makeUrlSafe('//my-long-name-host.yandex-team.ru//2api/shmapi3///pam/pam/1//')).toBe(
        '/my-long-name-host.yandex-team.ru/2api/shmapi3/pam/pam/1/'
    );

    expect(makeUrlSafe('http://my-long-name-host.yandex-team.ru//2api/shmapi3///pam/pam/один//')).toBe(
        'http://my-long-name-host.yandex-team.ru/2api/shmapi3/pam/pam/один/'
    );

    expect(makeUrlSafe('//my-long-name-host.yandex-team.ru//2api/shmapi3///pam/pam/один//')).toBe(
        '/my-long-name-host.yandex-team.ru/2api/shmapi3/pam/pam/один/'
    );
});

test('normalizeUrl', () => {
    expect(normalizeUrl('https://my-long-name-host.yandex-team.ru//2api/shmapi3///pam/pam/pam//')).toBe(
        'https://my-long-name-host.yandex-team.ru/2api/shmapi3/pam/pam/pam/'
    );

    expect(normalizeUrl('//my-long-name-host.yandex-team.ru//2api/shmapi3///pam/pam/pam//')).toBe(
        '/my-long-name-host.yandex-team.ru/2api/shmapi3/pam/pam/pam/'
    );

    expect(normalizeUrl(['https://my-long-name-host.yandex-team.ru/', '/2api/shmapi3///pam/pam/pam//'])).toBe(
        'https://my-long-name-host.yandex-team.ru/2api/shmapi3/pam/pam/pam/'
    );

    expect(normalizeUrl(['//my-long-name-host.yandex-team.ru', '//2api/shmapi3///pam/pam/pam//'])).toBe(
        '/my-long-name-host.yandex-team.ru/2api/shmapi3/pam/pam/pam/'
    );

    expect(normalizeUrl([undefined, '//2api/shmapi3///pam/pam/pam//'])).toBe(
        '/2api/shmapi3/pam/pam/pam/'
    );
});
