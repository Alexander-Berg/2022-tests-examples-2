import _ from 'lodash';
import {renderPage} from '../renderPage';

describe('routes/authRegComplete/renderPage', () => {
    const createReqMock = (req) =>
        _.merge(
            {
                headers: ['x-real-scheme'],
                hostname: 'yandex.test/',
                api: {
                    statboxLogger: jest.fn()
                }
            },
            req
        );
    const createResMock = (res) =>
        _.merge(
            {
                locals: {
                    store: {
                        common: {},
                        metrics: {}
                    },
                    result: {}
                },
                redirect: jest.fn(),
                render: jest.fn()
            },
            res
        );

    afterEach(() => {
        jest.clearAllMocks();
    });
    it('should call next if state is empty', () => {
        const reqMock = createReqMock();
        const resMock = createResMock();
        const nextMock = jest.fn();

        renderPage(reqMock, resMock, nextMock);

        expect(nextMock).toBeCalled();
    });
    it('should call redirect to default url if state is upgrade_cookies', () => {
        const reqMock = createReqMock();
        const resMock = createResMock({
            locals: {
                store: {
                    common: {
                        retpath: 'test/retpath'
                    }
                },
                result: {
                    completeSubmit: {
                        state: 'upgrade_cookies'
                    }
                }
            }
        });
        const nextMock = jest.fn();

        renderPage(reqMock, resMock, nextMock);

        expect(resMock.redirect).toBeCalledWith('yandex.test/passport?mode=lightauth2full&retpath=test%2Fretpath');
    });
    it('should call render for success request', () => {
        const reqMock = createReqMock();
        const resMock = createResMock({
            locals: {
                store: {
                    common: {
                        retpath: 'test/retpath'
                    }
                },
                result: {
                    completeSubmit: {
                        state: 'complete_autoregistered',
                        account: {}
                    }
                },
                experiments: {}
            },
            _yandexuid: '123432'
        });
        const nextMock = jest.fn();

        renderPage(reqMock, resMock, nextMock);

        expect(resMock.render).toBeCalled();
    });
});
