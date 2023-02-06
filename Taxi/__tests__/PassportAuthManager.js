import config, {applyConfig, extendConfig} from '_common/static/config';
import PassportAuthManager, {TARGET_PARAM, MESSAGE_TYPES} from '_yandex/utils/PassportAuthManager';
import queryString from 'query-string';

const RETPATH = 'RETPATH?someParam=someValue';
const PASSPORT_HOST = 'PASSPORT_HOST';
const AVATAR_ID = 'AVATAR_ID';
const LOGIN = 'LOGIN';

describe('utils:PassportAuthManager', () => {
    // в jsdom нет window.open
    window.open = jest.fn();

    beforeAll(() => {
        applyConfig({
            retpath: RETPATH,
            passportHost: PASSPORT_HOST,
            auth: {
                users: [{login: LOGIN, avatarId: AVATAR_ID}]
            }
        });
    });

    test('Проверяем, что options клонирует настройки', () => {
        const pam = new PassportAuthManager();
        pam.init(config);
        expect(pam.options).not.toBe(pam.options);
        expect(pam.options).toEqual(pam._options);
    });

    test('Проверяем, что настройки конфига применились', () => {
        const pam = new PassportAuthManager();
        pam.init(config);

        expect(pam.options).toEqual(
            Object.assign(pam.options, {
                retpath: `${RETPATH}&${TARGET_PARAM}=${pam.id}`,
                passportHost: PASSPORT_HOST,
                auth: {
                    users: [{login: LOGIN, avatarId: AVATAR_ID}]
                }
            })
        );
    });

    test('Проверяем, что для IE определяется необходимость полифила', () => {
        extendConfig({browser: 'MSIE v11'});
        const pam = new PassportAuthManager();
        pam.init(config);

        expect(pam.options.polyfill).toBe(true);
        expect(window.__paw_message).toBeTruthy();
    });

    test('Проверяем, что для остальных браузеров используется window.postMessage', () => {
        extendConfig({browser: 'Chrome'});
        const pam = new PassportAuthManager();
        pam.init(config);

        expect(pam.options.polyfill).toBe(false);
        expect(window.__paw_message).toBeFalsy();
    });

    test('Проверяем настройки неавторизованного юзера', () => {
        extendConfig({auth: {}});
        const pam = new PassportAuthManager();
        pam.init(config);

        expect(pam.isAuthorized()).toBe(false);
    });

    test('Проверяем настройки авторизованного юзера', () => {
        extendConfig({auth: {users: [{login: 'YOU'}]}});
        const pam = new PassportAuthManager();
        pam.init(config);

        expect(pam.isAuthorized()).toBe(true);
    });

    test('Проверяем, что для url с нужным queryString прогоняется весь флоу', () => {
        extendConfig({auth: {users: [{login: 'YOU'}]}, browser: 'MSIE v11'});
        const pam = new PassportAuthManager();
        const originPost = pam._postMessage;
        pam._postMessage = jest.fn().mockImplementation(originPost);

        window.opener = window;
        const originParse = queryString.parse;
        queryString.parse = () => originParse(`?${TARGET_PARAM}=${pam.id}`);
        pam.init(config);

        // вызовы PING, PONG, UPDATE_PASSPRT_AUTH
        expect(pam._postMessage).toHaveBeenCalledTimes(3);
        expect(pam._postMessage).toHaveBeenLastCalledWith(
            {__paw_message: window.__paw_message},
            JSON.stringify({
                type: MESSAGE_TYPES.UPDATE_PASSPRT_AUTH,
                payload: {auth: pam._options.auth},
                id: pam.id,
                sourceId: pam.id
            }),
            location.origin
        );

        queryString.parse = originParse;
    });
});
