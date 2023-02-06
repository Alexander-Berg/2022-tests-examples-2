import qs from 'querystring';

import {AUTH_CONFIG} from '../config/auth';
import {loginPages} from '../page-objects';

export async function authToPassport() {
    await loginPages.passport.auth.open();

    await loginPages.passport.auth.selectToAuthViaMail();

    await loginPages.passport.auth.login(
        AUTH_CONFIG.CREDENTIALS.USERNAME,
        AUTH_CONFIG.CREDENTIALS.PASSWORD,
    );

    await loginPages.passport.auth.findProfileFirstName();
    await loginPages.passport.auth.findProfileLastName();
}

export async function authViaAqua() {
    const query = qs.stringify(AUTH_CONFIG.AQUA_ACCESS);

    await browser.url(`https://aqua.yandex-team.ru/auth-html?${query}`);
}
