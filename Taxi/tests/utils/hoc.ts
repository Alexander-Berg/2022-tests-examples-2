import React from 'react';
import {Provider} from 'react-redux';

import {withProps} from 'recompose';
import {createStore} from 'redux';

import {Config} from '../../packages/corp-client-core/config';
import {I18nProvider} from '../../packages/corp-core/i18n';
import {State} from '../../packages/corp-modules/types/state';

const t = (a: string) => a;
export const withMockI18n = () => withProps({t});
export const withMockI18nProvider = <T = any>() => (Component: React.ComponentType<T>) => (
    props: T,
) => React.createElement(I18nProvider, {t}, React.createElement(Component, props));

const getDefaultState = (): State => ({
    experiments: {},
    app: {
        destinations: [],
        requirements: {},
    },
    map: {
        center: [56, 57],
        bounds: [],
        hydrated: false,
        zoom: 11,
    },
    config: {
        logistics: {
            host: '',
            basename: '',
            oAuthPath: '',
        },
        balance: {
            url: 'https://balance.yandex.ru',
        },
        tld: 'ru',
        csrf: {
            refresh: {
                failure: 3,
                default: 15,
            },
        },
        dir: 'ltr',
        location: [0, 0],
        i18n: {
            langToLocale: {},
        },
        host: 'localhost',
        metrikaID: 'test',
        lang: 'ru',
        version: 'dev',
        mapApi: '2.1',
        branding: 'yandex',
        passportHost: 'https://passport.yandex.ru',
        passportApiHost: 'https://api.passport.yandex.ru',
        avatarsHost: 'https://avatars.mds.yandex.net',
        staticHost: 'localhost',
        oAuth: {
            url: 'test',
        },
        supchat: {
            supportHost: 'supportHost',
        },
        market: {
            marketplaceHost: 'marketplaceHost',
        },
        go: {
            landingHost: 'landingHost',
        },
        costCenters: {
            enabled: true,
            restrictions: {
                active_fields_max_count: 0,
                active_fields_min_count: 0,
                cost_centers_max_count: 0,
                field_title_max_length: 0,
                field_title_min_length: 0,
                field_values_max_count: 0,
                field_values_min_count: 0,
                total_fields_max_count: 0,
                total_fields_min_count: 0,
            },
            newClientsDate: '',
            oldClientsEnabled: [],
        },
        phones: {
            rules: [],
            localPrefixes: {
                kaz: {},
                rus: {},
                isr: {},
                arm: {},
                blr: {},
                kgz: {},
            },
        },
        corpLanding: {
            links: {
                kaz: {
                    request: '',
                    questions: '',
                },
                arm: {
                    request: '',
                    questions: '',
                },
                rus: {
                    request: '',
                    questions: '',
                },
                isr: {
                    request: '',
                    questions: '',
                },
                blr: {
                    request: '',
                    questions: '',
                },
            },
        },
        countries: {
            isr: {
                vat: 10,
                defaultPhonePrefix: '+3',
                vatIncluded: false,
                twoLetterCode: 'IL',
                currencySign: '₪',
                disableFinancialDocuments: true,
                currency: 'ILS',
                showTariffs: true,
            },
            rus: {
                defaultPhonePrefix: '+7',
                vat: 20,
                vatIncluded: true,
                twoLetterCode: 'RU',
                currencySign: '₽',
                currency: 'RUB',
                showTariffs: true,
            },
            kaz: {
                defaultPhonePrefix: '+7',
                vat: 13,
                vatIncluded: true,
                twoLetterCode: 'KZ',
                currencySign: '₸',
                currency: 'KZT',
                showTariffs: true,
            },
            arm: {
                defaultPhonePrefix: '+3',
                vat: 12,
                vatIncluded: true,
                twoLetterCode: 'AM',
                currencySign: '֏',
                currency: 'AMD',
                showTariffs: true,
            },
            blr: {
                defaultPhonePrefix: '+3',
                vat: 20,
                vatIncluded: false,
                twoLetterCode: 'BY',
                currencySign: 'Br',
                currency: 'BYN',
                showTariffs: true,
            },
            kgz: {
                defaultPhonePrefix: '+996',
                vat: 12,
                vatIncluded: false,
                twoLetterCode: 'KG',
                currencySign: 'С̲',
                currency: 'KGS',
                showTariffs: true,
            },
        },
        help: {},
        env: 'test',
        detectedCountry: 'rus',
        trial: {},
    },
    codes: {
        drive: {
            is_active: true,
            is_visible: true,
            contract_id: '111',
            balance: 0,
            deactivateThreshold: 0,
            lowBalanceNotificationEnabled: true,
            lowBalanceThreshold: 200,
            isPrepaid: true,
        },
        eats: {
            is_active: true,
            is_visible: true,
            contract_id: '111',
            balance: 0,
            deactivateThreshold: 0,
            lowBalanceNotificationEnabled: true,
            lowBalanceThreshold: 200,
            isPrepaid: true,
        },
        taxi: {
            is_active: true,
            is_visible: true,
            contract_id: '111',
            balance: 0,
            deactivateThreshold: 0,
            lowBalanceNotificationEnabled: true,
            lowBalanceThreshold: 200,
            isPrepaid: true,
        },
    },
    auth: {
        clientID: 'test',
        role: 'client',
        login: 'corp-test',
        defaultLanguage: 'ru',
        frontendVersions: {
            'corp-client': 'latest',
        },
    },
    entities: {
        departments: {},
        driveGroups: {},
        clients: {},
        managers: {},
        tariffs: {},
        users: {},
        tariffZones: {},
        decouplingTariffs: {},
        departmentManagers: {},
        roles: {},
        claims: {},
        routeInfo: {},
        driveOrders: {},
        eatsOrders: {},
        geoRestrictions: {},
        commentTemplates: {},
        nddClaimList: {},
    },
    notifications: [],
    update: {
        checkedAt: undefined,
        available: false,
        suspended: false,
    },
    client: {
        currency_sign: 'RUR',
        _id: 'client',
        country: 'rus',
        features: [],
        defaultTariff: 'business',
        cabinet_only_role_id: 'cabinet-only',
        lowBalanceNotificationEnabled: true,
        // tmp
        tmpCommonContract: false,
        collateralAccepted: false,
    },
    noMore: {
        claims: {
            active: false,
            past: false,
        },
        driveOrders: false,
        eatsOrders: false,
        nddClaims: false,
    },
    result: {
        departments: {
            available: [],
            byParent: {},
            root: [],
        },
    },
    queries: {},
});

export const withMockConfigProvider = <T = any>(config: Partial<Config>) => (
    Component: React.ComponentType<T>,
) => (props: T) =>
    React.createElement(Provider as any, {
        store: createStore((state: State | undefined) => state || getDefaultState(), {
            ...getDefaultState(),
            config,
        }),
        children: React.createElement(Component, props),
    });
