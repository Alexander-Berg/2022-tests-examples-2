jest.mock('../../api', () => ({
    request: jest.fn()
}));
import api from '../../api';
import mockData from './__mocks__/data';
import {setSuggestionFetching} from '../actions';
import updateFieldStatus from '../methods/updateFieldStatus';
import findFieldsWithErrors from '../methods/findFieldsWithErrors';
import getSuggestedLogins from '../methods/getSuggestedLogins';
import validateLogin from '../methods/validateLogin';
import validatePassword from '../methods/validatePassword';
import metrics from '../../metrics';

jest.mock('../actions', () => ({
    setSuggestionFetching: jest.fn()
}));

jest.mock('../methods/updateFieldStatus');
jest.mock('../methods/findFieldsWithErrors');
jest.mock('../methods/validatePassword');
jest.mock('../methods/getSuggestedLogins');

jest.mock('../../metrics', () => ({
    send: jest.fn(),
    goal: jest.fn()
}));

const getState = () => ({
    settings: {
        language: 'ru',
        uatraits: {
            isMobile: false,
            isTouch: false
        }
    },
    common: {
        csrf: '12345',
        track_id: '1234',
        from: 'mail'
    },
    form: {
        values: {
            name: 'test',
            lastname: 'example',
            email: 'test@example.com',
            login: 'testLogin',
            password: 'testPassword'
        },
        states: {
            name: 'valid',
            lastname: 'valid',
            email: 'valid'
        },
        errors: {
            active: 'firstname'
        }
    },
    logins: {
        loginsList: ['test', 'test2']
    }
});

describe('validateLogin', () => {
    const login = 'test.login';

    updateFieldStatus.mockImplementation(() => () => ({field: 'answer'}));
    findFieldsWithErrors.mockImplementation(() => () => jest.fn());
    validatePassword.mockImplementation(() => () => jest.fn());
    getSuggestedLogins.mockImplementation(() => () => []);

    describe('response is ok', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function(fn) {
                        fn({status: 'ok'});
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
        });

        it('should dispatch setSuggestionFetching', () => {
            validateLogin(login)(mockData.props.dispatch, getState);
            expect(setSuggestionFetching).toBeCalled();
        });

        it('should dispatch validatePassword', () => {
            validateLogin(login)(mockData.props.dispatch, getState);
            expect(validatePassword).toBeCalled();
        });

        it('should call updateFieldStatus', () => {
            validateLogin(login)(mockData.props.dispatch, getState);
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('login', 'valid');
        });

        it('should dispatch findFieldsWithErrors', () => {
            validateLogin(login)(mockData.props.dispatch, getState);
            expect(findFieldsWithErrors).toBeCalled();
        });

        it('should call metrics.send', () => {
            validateLogin(login)(mockData.props.dispatch, getState);
            expect(metrics.send).toBeCalled();
            expect(metrics.send).toBeCalledWith(['Форма', 'Успешное заполнение поля "логин"']);
        });
    });

    describe('response is error', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function(fn) {
                        fn(['login.endswithhyphen']);
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
            getSuggestedLogins.mockClear();
        });

        it('should call updateFieldStatus', () => {
            validateLogin(login)(mockData.props.dispatch, getState);
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('login', 'not_valid');
        });

        it('should dispatch getSuggestedLogins', () => {
            validateLogin(login)(mockData.props.dispatch, getState);
            expect(getSuggestedLogins).toBeCalled();
        });

        it('should not dispatch getSuggestedLogins if login is empty', () => {
            validateLogin('')(mockData.props.dispatch, getState);
            expect(getSuggestedLogins).not.toBeCalled();
        });
    });
});
