import {TPlatformSettings} from '_types/common/config';

const TARIFF_EDITOR_CONFIG_MOCK = {
    appType: 'taxi'
};

const TPLATFORM_TAXI_CONFIG_MOCK = {
    appType: 'platform',
    tplatformNamespace: 'taxi'
};

const TPLATFORM_MARKET_CONFIG_MOCK = {
    appType: 'platform',
    tplatformNamespace: 'market'
};

const TEST_DATA: TPlatformSettings<number> = {
    taxi: 1,
    platform: {
        taxi: 2,
        market: 3
    }
};

describe('getAppPlatformSettings', () => {
    beforeEach(() => {
        jest.resetModules();
    });

    const setup = <T>(mockOverrides: T) => {
        jest.doMock('_pkg/config', () => mockOverrides);

        return import('../getAppPlatformSettings');
    };

    it('Для админки tariff-editor значение возвращается корректно', async () => {
        const {getAppPlatformSettings} = await setup(TARIFF_EDITOR_CONFIG_MOCK);
        const result = getAppPlatformSettings(TEST_DATA);

        expect(result).toBe(1);
    });

    it('Для админки taxi.tplatform значение возвращается корректно', async () => {
        const {getAppPlatformSettings} = await setup(TPLATFORM_TAXI_CONFIG_MOCK);
        const result = getAppPlatformSettings(TEST_DATA);

        expect(result).toBe(2);
    });

    it('Для админки market.tplatform значение возвращается корректно', async () => {
        const {getAppPlatformSettings} = await setup(TPLATFORM_MARKET_CONFIG_MOCK);
        const result = getAppPlatformSettings(TEST_DATA);

        expect(result).toBe(3);
    });
});
