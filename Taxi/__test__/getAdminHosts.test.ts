import {TARIFF_EDITOR_HOSTS} from '_pkg/constants/application';

const TARIFF_EDITOR_CONFIG_MOCK = {
    lang: 'ru',
    appType: 'taxi'
};

const TPLATFORM_TAXI_CONFIG_MOCK = {
    lang: 'ru',
    appType: 'platform',
    tplatformNamespace: 'taxi'
};

const TPLATFORM_MARKET_CONFIG_MOCK = {
    lang: 'ru',
    appType: 'platform',
    tplatformNamespace: 'market'
};

describe('getAdminHosts', () => {
    beforeEach(() => {
        jest.resetModules();
    });

    const setup = <T>(mockOverrides: T) => {
        jest.doMock('_pkg/config', () => mockOverrides);

        return import('../getAdminHosts');
    };

    it('Для админки tariff-editor возвращаются хосты tariff-editor', async () => {
        const {getAdminHosts} = await setup(TARIFF_EDITOR_CONFIG_MOCK);
        const result = getAdminHosts();

        expect(result).toStrictEqual({
            unstable: TARIFF_EDITOR_HOSTS.UNSTABLE,
            testing: TARIFF_EDITOR_HOSTS.TESTING,
            stable: TARIFF_EDITOR_HOSTS.STABLE
        });
    });

    it('Для админки taxi.tplatform возвращаются хосты такси', async () => {
        const {getAdminHosts} = await setup(TPLATFORM_TAXI_CONFIG_MOCK);
        const result = getAdminHosts();

        expect(result).toStrictEqual({
            unstable: `https://taxi.tplatform.dev.yandex-team.ru`,
            testing: `https://taxi.tplatform.tst.yandex-team.ru`,
            stable: `https://taxi.tplatform.yandex-team.ru`
        });
    });

    it('Для админки market.tplatform возвращаются хосты маркета', async () => {
        const {getAdminHosts} = await setup(TPLATFORM_MARKET_CONFIG_MOCK);
        const result = getAdminHosts();

        expect(result).toStrictEqual({
            unstable: `https://market.tplatform.dev.yandex-team.ru`,
            testing: `https://market.tplatform.tst.yandex-team.ru`,
            stable: `https://market.tplatform.yandex-team.ru`
        });
    });
});
