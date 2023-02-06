import qs from 'qs';
import {patchStyles} from 'tests/e2e/config/util';

import {DATA_LANG_COOKIE, REGION_COOKIE, REGION_ISO_CODES, SIDEBAR_COOKIE, UI_LANG_COOKIE} from '@/src/constants';
import type {UILanguage} from '@/src/i18n';
import {AUTH_MOCK_USER_COOKIE, AuthUsersMocks} from 'server/middlewares/mocks/auth';
import {assertString} from 'service/helper/assert-string';
import {routes, TRANSACTION_UUID_COOKIE} from 'service/transaction-controller';
import type {Language} from 'types/common';
import type {RegionCode} from 'types/region';

interface BuildUrlOptions {
    region?: Lowercase<RegionCode> | null;
    queryParams?: Record<string, unknown>;
}
export interface OpenPageOptions extends BuildUrlOptions {
    collapseSidebar?: boolean;
    expandUserProductFilters?: boolean;
    noCookies?: boolean;
    noClearLocalStorage?: boolean;
    localStorageItems?: Record<string, unknown>;
    isReadonly?: boolean;
    isAdmin?: boolean;
    dataLang?: Language;
    uiLang?: UILanguage;
    uuid?: string;
}

export async function openPage(this: WebdriverIO.Browser, path: string, options?: OpenPageOptions) {
    await this.execute(patchAlerts);
    const initialUrl = await this.getUrl();
    const uuid = assertString(this.executionContext.uuid ?? options?.uuid);

    if (initialUrl.startsWith('data:') || initialUrl.startsWith('about:') || initialUrl.startsWith('chrome:')) {
        await this.url(buildPageUrl(routes.setCookie(uuid), {region: null}));
        const [uuidSettled] = await this.getCookies(TRANSACTION_UUID_COOKIE);
        if (uuidSettled?.value !== uuid) {
            throw new Error('Failed to set transaction uuid');
        }
    }

    if (options?.noCookies) {
        const promises: Promise<unknown>[] = [
            this.deleteCookies([DATA_LANG_COOKIE, REGION_COOKIE, UI_LANG_COOKIE, SIDEBAR_COOKIE]),
            this.setCookies({name: TRANSACTION_UUID_COOKIE, value: uuid})
        ];
        await Promise.all(promises);
    } else {
        await this.setCookies([
            {name: TRANSACTION_UUID_COOKIE, value: uuid},
            {name: DATA_LANG_COOKIE, value: options?.dataLang ?? 'ru'},
            {name: REGION_COOKIE, value: options?.region ?? ''},
            {name: UI_LANG_COOKIE, value: options?.uiLang ?? 'ru'},
            {
                name: AUTH_MOCK_USER_COOKIE,
                value: getAuthMockUserCookie(options)
            },
            {name: SIDEBAR_COOKIE, value: options?.collapseSidebar ? 'true' : 'false'}
        ]);
    }
    if (!options?.noClearLocalStorage) {
        await this.execute(clearLocalStorage);
    }
    if (options?.localStorageItems) {
        await this.execute(setLocalStorageItems, options.localStorageItems);
    }
    await this.url(buildPageUrl(path, options));
    await this.execute(patchStyles);
}

function getAuthMockUserCookie(options: OpenPageOptions = {}): AuthUsersMocks {
    const {isAdmin, isReadonly} = options;
    if (isAdmin) {
        return AuthUsersMocks.ADMIN;
    } else if (isReadonly) {
        return AuthUsersMocks.READONLY;
    } else {
        return AuthUsersMocks.DEFAULT;
    }
}

function setRegionToPath(path: string, region?: string) {
    if (!region) {
        return path;
    }
    const paths = path.split('/').filter(Boolean);
    if (REGION_ISO_CODES.includes(paths[0])) {
        paths[0] = region;
    } else {
        paths.unshift(region);
    }
    return `/${paths.join('/')}`;
}

function buildPageUrl(path: string, options: BuildUrlOptions = {}) {
    const {region, queryParams} = options;
    const urlPath = region === null ? path : setRegionToPath(path, region ?? process.env.TEST_REGION);
    const url = new URL(urlPath, `http://${process.env.BROWSER_HOST}`);

    if (queryParams) {
        url.search = qs.stringify(queryParams, {addQueryPrefix: true});
    }

    return url.href;
}

function patchAlerts() {
    window.onbeforeunload = null;
}

function clearLocalStorage() {
    if ('localStorage' in window && typeof window.localStorage.clear === 'function') {
        window.localStorage.clear();
    }
}

function setLocalStorageItems(items: Record<string, unknown>) {
    if ('localStorage' in window && typeof window.localStorage.setItem === 'function') {
        Object.entries(items).forEach(([key, value]) => window.localStorage.setItem(key, JSON.stringify(value)));
    }
}

export type OpenPage = typeof openPage;
