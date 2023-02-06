import {combineReducers} from 'redux';
import {expectSaga} from 'redux-saga-test-plan';
import {call} from 'typed-redux-saga';

import asyncOperationsReducer from '_pkg/reducers/asyncOperations';
import {INavMenuGroup, INavMenuItem, MenuGroups, PlatformMenuGroups} from '_types/common/infrastructure';

// по цепочке подтягиваемых зависимостей нужно переопределить эти поля в конфиге
const CONFIG_MOCK_COMMON_PARAMS = {
    lang: 'ru',
    maps: {}
};

const TARIFF_EDITOR_CONFIG_MOCK = {
    ...CONFIG_MOCK_COMMON_PARAMS,
    appType: 'taxi'
};

const TPLATFORM_TAXI_CONFIG_MOCK = {
    ...CONFIG_MOCK_COMMON_PARAMS,
    appType: 'platform',
    tplatformNamespace: 'taxi'
};

const MENU_ITEM_1: INavMenuItem = {
    url: '/some',
    title: 'some'
};

const MENU_ITEM_2: INavMenuItem = {
    url: '/some-2',
    title: 'some-2'
};

const MENU_ITEM_3: INavMenuItem = {
    url: '/some-3',
    title: 'some-3'
};

const reducer = combineReducers({
    asyncOperations: asyncOperationsReducer
});

describe('NavigationService', () => {
    function setupConfig<T>(mockOverrides: T) {
        jest.resetModules();
        jest.doMock('_pkg/config', () => mockOverrides);
    }

    it('extendNavigation должен добавить айтемы навигации верно для tariff-editor', () => {
        setupConfig(TARIFF_EDITOR_CONFIG_MOCK);

        return expectSaga(function* () {
            const {default: NavigationService} = yield* call(() => import('../NavigationService'));

            const firstState = yield* call(NavigationService.extendNavigation, []);

            expect(firstState[MenuGroups.Experiments].items.length).toBe(0);
            expect(firstState[MenuGroups.Service].items.length).toBe(0);

            return yield* call(NavigationService.extendNavigation, [
                [
                    {
                        taxi: MenuGroups.Experiments,
                        platform: PlatformMenuGroups.Tools
                    },
                    MENU_ITEM_1
                ],
                [MenuGroups.Experiments, MENU_ITEM_2],
                [MenuGroups.Service, MENU_ITEM_3]
            ]);
        })
            .withReducer(reducer)
            .run()
            .then(res => {
                const operationState: Record<string, INavMenuGroup> = res.returnValue;

                expect(operationState[PlatformMenuGroups.Tools]).toBeUndefined();
                expect(operationState[MenuGroups.Experiments].items).toStrictEqual([
                    {
                        ...MENU_ITEM_1,
                        groupId: MenuGroups.Experiments
                    },
                    {
                        ...MENU_ITEM_2,
                        groupId: MenuGroups.Experiments
                    }
                ]);
                expect(operationState[MenuGroups.Service].items).toStrictEqual([
                    {
                        ...MENU_ITEM_3,
                        groupId: MenuGroups.Service
                    }
                ]);
            });
    });

    it('extendNavigation должен добавить айтемы навигации верно для taxi.tplatform', () => {
        setupConfig(TPLATFORM_TAXI_CONFIG_MOCK);

        return expectSaga(function* () {
            const {default: NavigationService} = yield* call(() => import('../NavigationService'));

            const firstState = yield* call(NavigationService.extendNavigation, []);

            expect(firstState[MenuGroups.Experiments]).toBeUndefined();
            expect(firstState[PlatformMenuGroups.Tools].items.length).toBe(0);

            return yield* call(NavigationService.extendNavigation, [
                [
                    {
                        taxi: MenuGroups.Experiments,
                        platform: PlatformMenuGroups.Tools
                    },
                    MENU_ITEM_1
                ],
                [
                    {
                        taxi: MenuGroups.Experiments,
                        platform: {
                            market: PlatformMenuGroups.Tools
                        }
                    },
                    [MENU_ITEM_2]
                ],
                [
                    {
                        taxi: MenuGroups.Experiments,
                        platform: {
                            taxi: PlatformMenuGroups.Tools
                        }
                    },
                    [MENU_ITEM_3]
                ]
            ]);
        })
            .withReducer(reducer)
            .run()
            .then(res => {
                const operationState: Record<string, INavMenuGroup> = res.returnValue;

                expect(operationState[MenuGroups.Experiments]).toBeUndefined();
                expect(operationState[PlatformMenuGroups.Tools].items).toStrictEqual([
                    {
                        ...MENU_ITEM_1,
                        groupId: PlatformMenuGroups.Tools
                    },
                    {
                        ...MENU_ITEM_3,
                        groupId: PlatformMenuGroups.Tools
                    }
                ]);
            });
    });
});
