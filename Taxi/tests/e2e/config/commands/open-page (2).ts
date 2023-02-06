import qs from 'qs';
import {PatchStyles, patchStyles} from 'tests/e2e/config/util';

import {
    DATA_LANG_COOKIE,
    REGION_COOKIE,
    REGION_ISO_CODES,
    SIDEBAR_COOKIE,
    UI_LANG_COOKIE,
    USER_PRODUCT_FILTERS_COOKIE
} from '@/src/constants';
import {ROUTES} from '@/src/constants/routes';
import type {UILanguage} from '@/src/i18n';
import {makeApiUrl} from 'client/utils/make-api-url';
import {AUTH_MOCK_USER_COOKIE, AuthUsersMocks} from 'server/middlewares/mocks/auth';
import {UPLOAD_MOCKED_IMAGE_ROUTE} from 'server/middlewares/mocks/serve-mocked-media-items-middleware';
import {assertNumber} from 'service/helper/assert-number';
import {assertString} from 'service/helper/assert-string';
import {routes, TRANSACTION_UUID_COOKIE} from 'service/transaction-controller';
import type {Language} from 'types/common';
import type {RegionCode} from 'types/region';

const IMAGE_UPLOAD_ROUTE = assertString(makeApiUrl(ROUTES.API.UPLOAD_IMAGE));

interface BuildUrlOptions {
    region?: Lowercase<RegionCode> | null;
    queryParams?: Record<string, unknown>;
}

export interface OpenPageOptions extends BuildUrlOptions {
    collapseSidebar?: boolean;
    expandUserProductFilters?: boolean;
    noCookies?: boolean;
    clearLocalStorage?: boolean;
    localStorageItems?: Record<string, unknown>;
    isReadonly?: boolean;
    dataLang?: Language;
    uiLang?: UILanguage;
    patchStyles?: PatchStyles;
}

async function openPage(this: WebdriverIO.Browser, path: string, options?: OpenPageOptions) {
    await this.execute(patchAlerts);
    const initialUrl = await this.getUrl();
    const uuid = assertString(this.executionContext.uuid);
    const port = assertNumber(this.executionContext.port);

    if (new URL(initialUrl).hostname !== new URL(assertString(process.env.BROWSER_DOMAIN)).hostname) {
        await this.url(buildPageUrl(routes.setCookie(uuid), port, {region: null}));
    }

    if (options?.noCookies) {
        const promises: Promise<unknown>[] = [
            this.deleteCookies([
                DATA_LANG_COOKIE,
                REGION_COOKIE,
                UI_LANG_COOKIE,
                SIDEBAR_COOKIE,
                USER_PRODUCT_FILTERS_COOKIE
            ]),
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
            {name: SIDEBAR_COOKIE, value: options?.collapseSidebar ? 'true' : 'false'},
            {name: USER_PRODUCT_FILTERS_COOKIE, value: options?.expandUserProductFilters ? 'true' : 'false'}
        ]);
    }
    if (options?.clearLocalStorage) {
        await this.execute(clearLocalStorage);
    }
    if (options?.localStorageItems) {
        await this.execute(setLocalStorageItems, options.localStorageItems);
    }
    await this.url(buildPageUrl(path, port, options));

    const afterLoadPromises: Promise<void>[] = [
        this.execute(patchAjax, IMAGE_UPLOAD_ROUTE, UPLOAD_MOCKED_IMAGE_ROUTE),
        this.execute(patchStyles, options?.patchStyles ?? {})
    ];

    if (options?.clearLocalStorage && !options?.localStorageItems) {
        afterLoadPromises.push(this.execute(clearLocalStorage));
    }
    if (!options?.clearLocalStorage && options?.localStorageItems) {
        afterLoadPromises.push(this.execute(setLocalStorageItems, options.localStorageItems));
    }
    if (options?.clearLocalStorage && options?.localStorageItems) {
        const items = options.localStorageItems;
        afterLoadPromises.push(this.execute(clearLocalStorage).then(() => this.execute(setLocalStorageItems, items)));
    }

    await Promise.all(afterLoadPromises);
}

function getAuthMockUserCookie(options: OpenPageOptions = {}): AuthUsersMocks {
    const {isReadonly} = options;
    if (isReadonly) {
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

function buildPageUrl(path: string, port: number, options: BuildUrlOptions = {}) {
    const {region, queryParams} = options;
    const urlPath = region === null ? path : setRegionToPath(path, region ?? process.env.TEST_REGION);
    const url = new URL(urlPath, [assertString(process.env.BROWSER_DOMAIN), port].join(':'));

    if (queryParams) {
        url.search = qs.stringify(
            {...qs.parse(url.search, {ignoreQueryPrefix: true}), ...queryParams},
            {addQueryPrefix: true}
        );
    }

    return url.href;
}

function patchAlerts() {
    window.onbeforeunload = null;
}

function patchAjax(source: string, mock: string) {
    const isString = (arg: unknown): arg is string => typeof arg === 'string';

    const fetch = window.fetch;
    window.fetch = function (input: RequestInfo, init?: RequestInit) {
        const url = isString(input) ? input : input.url;
        const replacement = url.replace(source, mock);
        return fetch.call(window, isString(input) ? replacement : {...input, url: replacement}, init);
    } as typeof fetch;

    const open = window.XMLHttpRequest.prototype.open;
    window.XMLHttpRequest.prototype.open = function (
        this: XMLHttpRequest,
        method: string,
        url: string,
        async: boolean,
        username?: string | null,
        password?: string | null
    ) {
        this.addEventListener('readystatechange', () => false, false);
        open.call(this, method, url.replace(source, mock), async, username, password);
    } as typeof open;
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

export default openPage;
export type OpenPage = typeof openPage;
