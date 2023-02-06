jest.mock('../../api', () => ({
    request: jest.fn()
}));
import api from '../../api';
import {updateSuggestedLogins} from '../actions';
import getSuggestedLogins from '../methods/getSuggestedLogins';
import mockData from './__mocks__/data';

jest.mock('../actions', () => ({
    updateSuggestedLogins: jest.fn()
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
            firstname: 'test',
            lastname: 'example',
            login: 'testlogin',
            password: ''
        },
        states: {
            name: 'valid',
            lastname: 'valid',
            login: 'valid',
            email: 'valid'
        },
        errors: {
            login: {
                code: 'login.not_available',
                text: 'логин недоступен'
            }
        }
    }
});

describe('getSuggestedLogins', () => {
    beforeEach(function() {
        api.request.mockImplementation(function() {
            const FakeP = function() {
                this.then = function(fn) {
                    const logins = ['example', 'testexample', 'test.example', 'texample', 't.example', 'exampletest'];

                    fn({status: 'ok', logins});
                    return this;
                };
                this.fail = function(fn) {
                    fn();
                };
            };

            return new FakeP();
        });
    });
    afterEach(function() {
        api.request.mockClear();
    });
    it('should dispatch updateSuggestedLogins with logins list', () => {
        const loginsList = ['example', 'testexample', 'test.example', 'texample', 't.example', 'exampletest'];
        const argsToSend = {
            logins: loginsList,
            showAll: false,
            isFetching: false
        };

        getSuggestedLogins()(mockData.props.dispatch, getState);
        expect(updateSuggestedLogins).toBeCalled();
        expect(updateSuggestedLogins).toBeCalledWith(argsToSend);
    });
});
