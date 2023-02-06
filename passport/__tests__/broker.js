import broker from '../broker';

import * as passport from '@plibs/pclientjs/js/passport';
import socialBroker from '../../../social/broker';
import redirectToBackpath from '../actions/redirectToBackpath';
import redirectToRetpath from '../actions/redirectToRetpath';

jest.mock('@plibs/pclientjs/js/passport', () => ({
    isTouch: true
}));
jest.mock('../../../social/broker', () => ({
    init: jest.fn(),
    start: jest.fn()
}));
jest.mock('../actions/redirectToBackpath');
jest.mock('../actions/redirectToRetpath');

// 54.55 |       32 |        0 |    54.55
// 66.67 |       36 |        0 |    66.67
// 72.22 |       44 |        0 |    72.22
// 77.78 |       56 |        0 |    77.78
// 86.11 |       68 |        0 |    86.11
// 91.89 |       72 |        0 |    91.89
// 86.11 |       72 |        0 |    86.11
// 91.67 |       80 |        0 |    91.67
// 94.44 |       88 |        0 |    94.44
// 97.22 |       92 |        0 |    97.22

const {location, protocol, host} = window;

Object.defineProperty(global.window, 'addEventListener', {
    configurable: true,
    writable: true
});

Object.defineProperty(global.window, 'attachEvent', {
    configurable: true,
    writable: true
});

describe('Auth Social Broker', () => {
    describe('Broker.init', () => {
        beforeEach(() => {
            passport.isTouch = true;
            delete window.location;
            window.location = {
                origin: 'valid_origin',
                protocol: 'https:',
                host: 'yandex.ru'
            };
        });

        afterEach(() => {
            socialBroker.start.mockClear();
            redirectToBackpath.mockClear();
            redirectToRetpath.mockClear();
            window.location = location;
            window.protocol = protocol;
            window.host = host;
        });

        it('should init social broker with valid params', () => {
            const getState = jest.fn(() => ({
                social: {
                    brokerParams: {
                        startUrl: 'startUrl'
                    }
                },
                common: {
                    retpath: 'retpath',
                    backpath: 'backpath',
                    origin: 'origin'
                },
                auth: {
                    process_uuid: 'process_uuid'
                },
                customs: {
                    display: 'display'
                }
            }));

            const store = {getState};

            broker.init(store);

            expect(socialBroker.init).toBeCalled();
            expect(socialBroker.init).toBeCalledWith({
                resize: 1,
                startUrl: 'startUrl',
                display: 'touch',
                process_uuid: 'process_uuid',
                retnopopup: 'retpath'
            });
        });

        it('should init social broker with display popup param', () => {
            const getState = jest.fn(() => ({
                social: {
                    brokerParams: {
                        startUrl: 'startUrl'
                    }
                },
                common: {
                    retpath: 'retpath',
                    backpath: 'backpath',
                    origin: 'origin'
                },
                auth: {
                    process_uuid: 'process_uuid'
                },
                customs: {
                    display: 'popup'
                }
            }));

            const store = {getState};

            broker.init(store);

            expect(socialBroker.init).toBeCalled();
            expect(socialBroker.init).toBeCalledWith({
                resize: 1,
                startUrl: 'startUrl',
                display: 'touch',
                process_uuid: 'process_uuid',
                retnopopup: 'retpath'
            });
        });

        it('should init social broker with not touch', () => {
            const brokerIsTouchFn = broker.isTouch;

            broker.isTouch = jest.fn(() => false);

            const getState = jest.fn(() => ({
                social: {
                    brokerParams: {
                        startUrl: 'startUrl'
                    }
                },
                common: {
                    retpath: 'retpath',
                    backpath: 'backpath',
                    origin: 'origin'
                },
                auth: {
                    process_uuid: 'process_uuid'
                },
                customs: {
                    display: 'display'
                }
            }));

            const store = {getState};

            broker.init(store);

            expect(socialBroker.init).toBeCalled();
            expect(socialBroker.init).toBeCalledWith({
                resize: 1,
                process_uuid: 'process_uuid',
                startUrl: 'startUrl'
            });

            broker.isTouch = brokerIsTouchFn;
        });

        it('should fallback retpath param to profile url', () => {
            const getState = jest.fn(() => ({
                social: {
                    brokerParams: {
                        startUrl: 'startUrl'
                    }
                },
                common: {
                    backpath: 'backpath',
                    origin: 'origin'
                },
                auth: {
                    process_uuid: 'process_uuid'
                },
                customs: {
                    display: 'touch'
                }
            }));

            const store = {getState};

            broker.init(store);

            expect(socialBroker.init).toBeCalled();
            expect(socialBroker.init).toBeCalledWith({
                resize: 1,
                startUrl: 'startUrl',
                display: 'touch',
                process_uuid: 'process_uuid',
                retnopopup: 'https://yandex.ru/profile'
            });
        });

        it('should fallback retpath param to backpath for yandex origin', () => {
            const getState = jest.fn(() => ({
                social: {
                    brokerParams: {
                        startUrl: 'startUrl'
                    }
                },
                common: {
                    backpath: 'backpath',
                    origin: 'yandex'
                },
                auth: {
                    process_uuid: 'process_uuid'
                },
                customs: {
                    display: 'touch'
                }
            }));

            const store = {getState};

            broker.init(store);

            expect(socialBroker.init).toBeCalled();
            expect(socialBroker.init).toBeCalledWith({
                resize: 1,
                startUrl: 'startUrl',
                display: 'touch',
                process_uuid: 'process_uuid',
                retnopopup: 'backpath'
            });
        });

        it('should fallback retpath param to profile url for yandex origin', () => {
            const getState = jest.fn(() => ({
                social: {
                    brokerParams: {
                        startUrl: 'startUrl'
                    }
                },
                common: {
                    origin: 'yandex'
                },
                auth: {
                    process_uuid: 'process_uuid'
                },
                customs: {
                    display: 'touch'
                }
            }));

            const store = {getState};

            broker.init(store);

            expect(socialBroker.init).toBeCalled();
            expect(socialBroker.init).toBeCalledWith({
                resize: 1,
                startUrl: 'startUrl',
                display: 'touch',
                process_uuid: 'process_uuid',
                retnopopup: 'https://yandex.ru/profile'
            });
        });

        it('should handle ie browsers handler', () => {
            const getState = jest.fn(() => ({
                social: {
                    brokerParams: {
                        startUrl: 'startUrl'
                    }
                },
                common: {
                    backpath: 'backpath',
                    origin: 'yandex'
                },
                auth: {
                    process_uuid: 'process_uuid'
                },
                customs: {
                    display: 'touch'
                }
            }));

            const store = {getState};

            global.window.addEventListener = null;
            global.window.attachEvent = jest.fn();

            broker.init(store);

            expect(socialBroker.init).toBeCalled();
            expect(socialBroker.init).toBeCalledWith({
                resize: 1,
                startUrl: 'startUrl',
                display: 'touch',
                process_uuid: 'process_uuid',
                retnopopup: 'backpath'
            });
            expect(global.window.attachEvent).toBeCalled();

            global.window.addEventListener = jest.fn();
            global.window.attachEvent = jest.fn();
        });

        it('should handle global not iframe handler', () => {
            const getState = jest.fn(() => ({
                social: {
                    brokerParams: {
                        startUrl: 'startUrl'
                    }
                },
                common: {
                    backpath: 'backpath',
                    origin: 'yandex'
                },
                auth: {
                    process_uuid: 'process_uuid'
                },
                customs: {
                    display: 'touch'
                }
            }));

            const store = {getState};

            global.window.addEventListener = null;
            global.window.attachEvent = jest.fn();
            global.window.socialResponse = null;

            broker.init(store);

            expect(socialBroker.init).toBeCalled();
            expect(socialBroker.init).toBeCalledWith({
                resize: 1,
                startUrl: 'startUrl',
                display: 'touch',
                process_uuid: 'process_uuid',
                retnopopup: 'backpath'
            });
            expect(global.window.attachEvent).toBeCalled();
            expect(typeof global.window.socialResponse).toBe('function');

            const brokerOnSuccessFn = broker.onSuccess;

            broker.onSuccess = jest.fn();

            global.window.socialResponse();

            expect(broker.onSuccess).toBeCalled();

            broker.onSuccess = brokerOnSuccessFn;
            global.window.addEventListener = jest.fn();
            global.window.attachEvent = jest.fn();
        });
    });

    describe('Broker.onSuccess', () => {
        afterEach(() => {
            socialBroker.start.mockClear();
            redirectToBackpath.mockClear();
            redirectToRetpath.mockClear();
        });

        it('should handle response from social broker with invalid origin', () => {
            const message = {
                origin: 'invalid_origin'
            };

            const getStore = broker.getStore;

            broker.getStore = () => ({
                dispatch: jest.fn(),
                getState: jest.fn(() => ({
                    common: {
                        origin: 'origin',
                        pane: 'pane'
                    }
                }))
            });

            broker.onSuccess(message);

            expect(redirectToBackpath).not.toBeCalled();
            expect(redirectToRetpath).not.toBeCalled();

            broker.getStore = getStore;
        });

        it('should handle response from social broker with not social data', () => {
            const message = {
                origin: 'valid_origin',
                data: {}
            };

            const getStore = broker.getStore;

            broker.getStore = () => ({
                dispatch: jest.fn(),
                getState: jest.fn(() => ({
                    common: {
                        origin: 'origin',
                        pane: 'pane'
                    }
                }))
            });

            broker.onSuccess(message);

            expect(redirectToBackpath).not.toBeCalled();
            expect(redirectToRetpath).not.toBeCalled();

            broker.getStore = getStore;
        });

        it('should handle response from social broker with social auth pane', () => {
            const message = {
                origin: 'valid_origin',
                data: {
                    socialAuth: {}
                }
            };

            const getStore = broker.getStore;

            broker.getStore = () => ({
                dispatch: jest.fn(),
                getState: jest.fn(() => ({
                    common: {
                        origin: 'origin',
                        pane: '/auth/social?some=params'
                    }
                }))
            });

            broker.onSuccess(message);

            expect(redirectToBackpath).not.toBeCalled();
            expect(redirectToRetpath).not.toBeCalled();

            broker.getStore = getStore;
        });

        it('should handle response from social broker with fail status', () => {
            const message = {
                origin: 'valid_origin',
                data: {
                    socialAuth: {},
                    status: 'fail'
                }
            };

            const getStore = broker.getStore;

            broker.getStore = () => ({
                dispatch: jest.fn(),
                getState: jest.fn(() => ({
                    common: {
                        origin: 'origin',
                        pane: '/auth?some=params'
                    }
                }))
            });

            broker.onSuccess(message);

            expect(redirectToBackpath).not.toBeCalled();
            expect(redirectToRetpath).not.toBeCalled();

            broker.getStore = getStore;
        });

        it('should redirect to backpath with yandex origin', () => {
            window.location = {
                origin: 'yandex'
            };
            const message = {
                origin: 'yandex',
                data: {
                    socialAuth: {},
                    status: 'ok'
                }
            };

            const getStore = broker.getStore;

            broker.getStore = () => ({
                dispatch: jest.fn(),
                getState: jest.fn(() => ({
                    common: {
                        origin: 'yandex',
                        pane: '/auth?some=params'
                    }
                }))
            });

            broker.onSuccess(message);

            expect(redirectToBackpath).toBeCalled();
            expect(redirectToRetpath).not.toBeCalled();

            broker.getStore = getStore;
        });

        it('should redirect to retpath with not yandex origin', () => {
            window.location = {
                origin: 'valid_origin'
            };
            const message = {
                origin: 'valid_origin',
                data: {
                    socialAuth: {},
                    status: 'ok'
                }
            };

            const getStore = broker.getStore;

            broker.getStore = () => ({
                dispatch: jest.fn(),
                getState: jest.fn(() => ({
                    common: {
                        origin: 'valid_origin',
                        pane: '/auth?some=params'
                    }
                }))
            });

            broker.onSuccess(message);

            expect(redirectToBackpath).not.toBeCalled();
            expect(redirectToRetpath).toBeCalled();

            broker.getStore = getStore;
        });
    });

    describe('Broker.start', () => {
        afterEach(() => {
            socialBroker.start.mockClear();
            redirectToBackpath.mockClear();
            redirectToRetpath.mockClear();
        });

        it('should start social broker with valid params', () => {
            const params = ['param.1', 'param.2'];

            broker.start(params);

            expect(socialBroker.start).toBeCalled();
            expect(socialBroker.start).toBeCalledWith(params);
        });
    });
});
