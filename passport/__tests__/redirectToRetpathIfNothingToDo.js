import _ from 'lodash';
import {redirectToRetpathIfNothingToDo} from '../redirectToRetpathIfNothingToDo';

describe('routes/authRegComplete/redirectToRetpathIfNothingToDo', () => {
    const createReqMock = (req) =>
        _.merge(
            {
                headers: ['x-real-scheme'],
                hostname: 'yandex.test/'
            },
            req
        );
    const createResMock = (res) =>
        _.merge(
            {
                locals: {
                    result: {
                        completeSubmit: {}
                    },
                    store: {
                        common: {}
                    }
                },
                redirect: jest.fn()
            },
            res
        );

    afterEach(() => {
        jest.clearAllMocks();
    });
    it('should call redirect to retpath if it is valid', () => {
        const reqMock = createReqMock();
        const resMock = createResMock({
            locals: {
                store: {
                    common: {
                        retpath: 'test/auth'
                    }
                }
            }
        });

        redirectToRetpathIfNothingToDo(reqMock, resMock);

        expect(resMock.redirect).toBeCalledWith('test/auth');
    });
    it('should call redirect to default url if retpath is not valid', () => {
        const reqMock = createReqMock();
        const resMock = createResMock();

        redirectToRetpathIfNothingToDo(reqMock, resMock);

        expect(resMock.redirect).toBeCalledWith('yandex.test/passport?mode=passport');
    });
});
