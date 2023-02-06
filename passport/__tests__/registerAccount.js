jest.mock('../../../api', () => ({
    request: jest.fn()
}));
import api from '../../../api';
import registerAccount from '../registerAccount';
import {updateRegistrationErrors, updateFetchingStatus, showEulaPopup} from '../../../registration/actions';
import {updateStates} from '@blocks/actions/form';
import metrics from '../../../metrics';
import {handleRegistrationError} from '../../methods/registrationLiteMethods';

jest.mock('../../../registration/actions', () => ({
    updateRegistrationErrors: jest.fn(),
    updateFetchingStatus: jest.fn(),
    showEulaPopup: jest.fn()
}));

jest.mock('@blocks/actions/form', () => ({
    updateStates: jest.fn()
}));

jest.mock('../../methods/registrationLiteMethods', () => ({
    handleRegistrationError: jest.fn()
}));

jest.mock('../../../metrics', () => ({
    send: jest.fn(),
    goal: jest.fn()
}));

const {location} = window;

const getState = () => ({
    settings: {
        language: 'ru'
    },
    common: {
        track_id: '12345678',
        currentPage: 'https://passport-test.yandex.ru/registration/lite?version=1',
        csrf: '4626262'
    },
    form: {
        isEulaShowedInPopup: false,
        setting: {
            language: 'ru'
        },
        values: {
            email: 'test@example.com',
            password: 'pass123',
            password_confirm: 'pass123',
            emailCode: '12345',
            captcha: ''
        }
    },
    registrationType: 'lite-experiment',
    experimentVersion: '1'
});

const dispatch = jest.fn();

describe('registerAccount', () => {
    describe('registration done, response is ok', () => {
        beforeEach(function() {
            delete window.location;
            window.location = {
                href: 'some url',
                reload: jest.fn()
            };
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function(fn) {
                        fn({status: 'ok'});
                        return this;
                    };
                    this.fail = function() {
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
            window.location = location;
        });

        it('should set Spinner when starts', () => {
            registerAccount()(dispatch, getState);
            expect(updateFetchingStatus).toBeCalledWith(true);
        });

        it('should call metrics.send', () => {
            registerAccount()(dispatch, getState);
            expect(metrics.send).toBeCalled();
        });

        it('should redirect to finish url when done', () => {
            window.location.href = jest.fn();
            registerAccount()(dispatch, getState);
            expect(window.location.href).toEqual('/registration/finish?track_id=12345678');
        });
    });

    describe('registration failed, response is 200, but not ok', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function(fn) {
                        fn({status: 'error'});
                        return this;
                    };
                    this.fail = function() {
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
        });

        it('should remove Spinner when ends', () => {
            registerAccount()(dispatch, getState);
            expect(updateFetchingStatus).toBeCalledWith(false);
        });

        it('should call updateRegistrationErrors to show registration error', () => {
            const globalRegError = {
                status: 'error',
                code: 'global',
                text: '_AUTH_.avatar.error-internal'
            };

            registerAccount()(dispatch, getState);
            expect(updateRegistrationErrors).toBeCalled();
            expect(updateRegistrationErrors).toBeCalledWith(globalRegError);
        });
    });

    describe('registration failed, handle error', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function() {
                        return this;
                    };
                    this.fail = function(fn) {
                        fn({error: [{field: 'lastname', code: 'invalid'}]});
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
        });

        it('should remove Spinner when ends', () => {
            registerAccount()(dispatch, getState);
            expect(updateFetchingStatus).toBeCalledWith(false);
        });

        it('should call updateStates to set form to first screen', () => {
            registerAccount()(dispatch, getState);
            expect(updateStates).toBeCalled();
            expect(updateStates).toBeCalledWith({field: 'emailCodeStatus', status: ''});
        });

        it('should remove EulaPopup from screen', () => {
            registerAccount()(dispatch, getState);
            expect(showEulaPopup).toBeCalledWith(false);
        });

        it('should call handleRegistrationError to handle error', () => {
            registerAccount()(dispatch, getState);
            expect(handleRegistrationError).toBeCalled();
        });
    });
});
