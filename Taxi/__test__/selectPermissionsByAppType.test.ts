import {INavMenuItem} from '_types/common/infrastructure';

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

const TEST_DATA_COMMON_PARAMS: INavMenuItem = {
    title: 'some_title',
    url: 'some_url',
};

describe('selectPermissionsByAppType', () => {
    beforeEach(() => {
        jest.resetModules();
    });

    const setup = <T>(mockOverrides: T) => {
        jest.doMock('_pkg/config', () => mockOverrides);

        return import('../utils');
    };

    it('Для админки tariff-editor значение возвращается корректно', async () => {
        const {selectPermissionsByAppType} = await setup(TARIFF_EDITOR_CONFIG_MOCK);

        const result1 = selectPermissionsByAppType({
            ...TEST_DATA_COMMON_PARAMS,
            permissions: ['some_permission']
        });

        expect(result1).toStrictEqual(['some_permission']);

        const result2 = selectPermissionsByAppType({
            ...TEST_DATA_COMMON_PARAMS
        });

        expect(result2).toBeUndefined();
    });

    it('Для админки taxi.tplatform значение возвращается корректно', async () => {
        const {selectPermissionsByAppType} = await setup(TPLATFORM_TAXI_CONFIG_MOCK);

        const result1 = selectPermissionsByAppType({
            ...TEST_DATA_COMMON_PARAMS,
            permissions: {
                platform: ['some_permission'],
            }
        });

        expect(result1).toStrictEqual(['some_permission']);

        const result2 = selectPermissionsByAppType({
            ...TEST_DATA_COMMON_PARAMS,
            permissions: {
                platform: {
                    taxi: ['some_permission']
                }
            }
        });

        expect(result2).toStrictEqual(['some_permission']);

        const result3 = selectPermissionsByAppType({
            ...TEST_DATA_COMMON_PARAMS,
            permissions: {
                taxi: ['some_permission']
            }
        });

        expect(result3).toBeUndefined();

        const result4 = selectPermissionsByAppType({
            ...TEST_DATA_COMMON_PARAMS,
            permissions: {
                platform: {
                    market: ['some_permission']
                }
            }
        });

        expect(result4).toBeUndefined();
    });

    it('Для админки market.tplatform значение возвращается корректно', async () => {
        const {selectPermissionsByAppType} = await setup(TPLATFORM_MARKET_CONFIG_MOCK);

        const result1 = selectPermissionsByAppType({
            ...TEST_DATA_COMMON_PARAMS,
            permissions: {
                platform: ['some_permission'],
            }
        });

        expect(result1).toStrictEqual(['some_permission']);

        const result2 = selectPermissionsByAppType({
            ...TEST_DATA_COMMON_PARAMS,
            permissions: {
                platform: {
                    market: ['some_permission']
                }
            }
        });

        expect(result2).toStrictEqual(['some_permission']);

        const result3 = selectPermissionsByAppType({
            ...TEST_DATA_COMMON_PARAMS,
            permissions: {
                taxi: ['some_permission']
            }
        });

        expect(result3).toBeUndefined();

        const result4 = selectPermissionsByAppType({
            ...TEST_DATA_COMMON_PARAMS,
            permissions: {
                platform: {
                    taxi: ['some_permission']
                }
            }
        });

        expect(result4).toBeUndefined();
    });
});
