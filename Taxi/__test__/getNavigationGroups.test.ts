import {MenuGroups, PlatformMenuGroups} from '_types/common/infrastructure';

// по цепочке подтягиваемых зависимостей нужно переопределить эти поля в конфиге
const CONFIG_MOCK_COMMON_PARAMS = {
    lang: 'ru',
    maps: {}
};

const TARIFF_EDITOR_CONFIG_MOCK = {
    ...CONFIG_MOCK_COMMON_PARAMS,
    appType: 'taxi',
};

const TPLATFORM_TAXI_CONFIG_MOCK = {
    ...CONFIG_MOCK_COMMON_PARAMS,
    appType: 'platform',
    tplatformNamespace: 'taxi'
};

const TPLATFORM_MARKET_CONFIG_MOCK = {
    ...CONFIG_MOCK_COMMON_PARAMS,
    appType: 'platform',
    tplatformNamespace: 'market'
};

describe('getNavigationGroups', () => {
    beforeEach(() => {
        jest.resetModules();
    });

    const setup = <T>(mockOverrides: T) => {
        jest.doMock('_pkg/config', () => mockOverrides);

        return import('../utils');
    };

    it('Для админки tariff-editor значение возвращается корректно', async () => {
        const {getNavigationGroups} = await setup(TARIFF_EDITOR_CONFIG_MOCK);

        const result = getNavigationGroups();

        expect(result).toStrictEqual(Object.values(MenuGroups));
    });

    it('Для админки taxi.tplatform значение возвращается корректно', async () => {
        const {getNavigationGroups} = await setup(TPLATFORM_TAXI_CONFIG_MOCK);

        const result = getNavigationGroups();

        expect(result).toStrictEqual(Object.values(PlatformMenuGroups));
    });

    it('Для админки market.tplatform значение возвращается корректно', async () => {
        const {getNavigationGroups} = await setup(TPLATFORM_MARKET_CONFIG_MOCK);

        const result = getNavigationGroups();

        expect(result).toStrictEqual(Object.values(PlatformMenuGroups));
    });
});
