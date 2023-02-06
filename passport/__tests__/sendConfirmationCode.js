jest.mock('../../../api', () => ({
    request: jest.fn()
}));
import api from '../../../api';
import sendConfirmationCode from '../sendConfirmationCode';
import {showEulaPopup, updateRegistrationErrors, setCurrentStep} from '../../../registration/actions';
import {updateStates} from '@blocks/actions/form';
import {updateEmailConfirmationStatus, updateFormHeaderInfo} from '../../../registration-lite/actions';
import updateFieldStatus from '../../../registration/methods/updateFieldStatus';

jest.mock('../../../registration/actions', () => ({
    updateRegistrationErrors: jest.fn(),
    showEulaPopup: jest.fn(),
    setCurrentStep: jest.fn()
}));

jest.mock('@blocks/actions/form', () => ({
    updateStates: jest.fn()
}));

jest.mock('../../../registration-lite/actions', () => ({
    updateEmailConfirmationStatus: jest.fn(),
    updateFormHeaderInfo: jest.fn()
}));

jest.mock('../../../registration/methods/updateFieldStatus');

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

describe('sendConfirmationCode', () => {
    describe('code successfully sent', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function(fn) {
                        fn({status: 'ok'});
                        return this;
                    };
                    this.fail = function() {
                        return this;
                    };
                    this.always = function() {
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
        });
        it('should update state with "code_sent" status', () => {
            sendConfirmationCode()(dispatch, getState);
            expect(updateStates).toBeCalled();
            expect(updateStates).toBeCalledWith({field: 'emailCodeStatus', status: 'code_sent'});
        });
    });

    describe('code was not successfully sent, response is not ok', () => {
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
                    this.always = function() {
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
        });
        it('should call updateRegistrationErrors with global registration error', () => {
            sendConfirmationCode()(dispatch, getState);
            expect(updateRegistrationErrors).toBeCalled();
        });
    });

    describe('request failed with unknown error', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function() {
                        return this;
                    };
                    this.fail = function(fn) {
                        fn({status: 'error'});
                        return this;
                    };
                    this.always = function() {
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
        });
        it('should call updateRegistrationErrors with global registration error', () => {
            sendConfirmationCode()(dispatch, getState);
            expect(updateRegistrationErrors).toBeCalled();
        });
    });

    describe('request failed with normal error', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function() {
                        return this;
                    };
                    this.fail = function(fn) {
                        fn({error: ['email.send_limit_exceeded']});
                        return this;
                    };
                    this.always = function() {
                        return this;
                    };
                };

                return new FakeP();
            });
            updateFieldStatus.mockImplementation(() => () => ({field: 'email'}));
        });
        afterEach(function() {
            api.request.mockClear();
        });
        it('should call updateFieldStatus with error object', () => {
            sendConfirmationCode()(dispatch, getState);
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('email', 'not_valid');
        });
    });

    describe('request failed with "email.already_confirmed" error', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function() {
                        return this;
                    };
                    this.fail = function(fn) {
                        fn({error: ['email.already_confirmed']});
                        return this;
                    };
                    this.always = function() {
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
        });
        it('should set email confirmed', () => {
            sendConfirmationCode()(dispatch, getState);
            expect(updateEmailConfirmationStatus).toBeCalled();
        });
        it('should show Eula popup', () => {
            sendConfirmationCode()(dispatch, getState);
            expect(showEulaPopup).toBeCalledWith(true);
            expect(setCurrentStep).toBeCalledWith('eula');
            expect(updateFormHeaderInfo).toBeCalledWith({
                title: i18n('_AUTH_.acceptance.popup.title')
            });
        });
    });
});
