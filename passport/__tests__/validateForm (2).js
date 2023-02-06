import scrollToError from '../../../registration/methods/scrollToError';
import metrics from '../../../metrics';
import {setCurrentStep} from '../../../registration/actions';
import {updateErrorStates, updateGroupErrors} from '@blocks/actions/form';
import sendConfirmationCode from '../sendConfirmationCode';
import validateForm, {moveToPrevStep} from '../validateForm';

jest.mock('../../../registration/actions', () => ({
    setCurrentStep: jest.fn()
}));

jest.mock('@blocks/actions/form', () => ({
    updateErrorStates: jest.fn(),
    updateGroupErrors: jest.fn()
}));

jest.mock('../sendConfirmationCode');
jest.mock('../../../registration/methods/scrollToError');

jest.mock('../../../metrics', () => ({
    send: jest.fn(),
    goal: jest.fn()
}));

const getStateValidForm = () => ({
    settings: {
        language: 'ru'
    },
    common: {
        track_id: '12345678',
        currentPage: 'https://passport-test.yandex.ru/registration/lite?version=1',
        csrf: '4626262'
    },
    registrationType: 'lite-experiment',
    experimentVersion: '2',
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
        },
        states: {
            email: 'valid',
            firstname: 'valid',
            lastname: 'valid',
            password: 'valid',
            password_confirm: 'valid',
            emailCode: '',
            emailCodeStatus: '',
            captcha: ''
        },
        errors: {
            email: {
                code: '',
                text: ''
            },
            firstname: {
                code: '',
                text: ''
            },
            lastname: {
                code: '',
                text: ''
            },
            password: {
                code: '',
                text: ''
            },
            password_confirm: {
                code: '',
                text: ''
            },
            emailCode: {
                code: '',
                text: ''
            },
            captcha: {
                code: '',
                text: ''
            }
        }
    }
});

const getStateInvalidForm = () => ({
    settings: {
        language: 'ru'
    },
    common: {
        track_id: '12345678',
        currentPage: 'https://passport-test.yandex.ru/registration/lite?version=1',
        csrf: '4626262'
    },
    registrationType: 'lite-experiment',
    experimentVersion: '2',
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
        },
        states: {
            email: 'not_valid',
            firstname: 'valid',
            lastname: 'not_valid',
            password: 'valid',
            password_confirm: 'valid',
            emailCode: '',
            emailCodeStatus: '',
            captcha: ''
        },
        errors: {
            email: {
                code: 'login.not_available',
                text: 'аккаунт с этим адресом электронной почты уже зарегистрирован'
            },
            firstname: {
                code: '',
                text: ''
            },
            lastname: {
                code: 'missingvalue',
                text: 'Пожалуйста, укажите фамилию'
            },
            password: {
                code: '',
                text: ''
            },
            password_confirm: {
                code: '',
                text: ''
            },
            emailCode: {
                code: '',
                text: ''
            },
            captcha: {
                code: '',
                text: ''
            }
        }
    }
});

const dispatch = jest.fn();

describe('lite-experiment validateForm', () => {
    describe('fields are valid', () => {
        it('should call sendConfirmationCode if form data is valid', () => {
            validateForm()(dispatch, getStateValidForm);
            expect(sendConfirmationCode).toBeCalled();
        });
    });

    describe('fields are not valid', () => {
        it('should set form states to invalid', () => {
            const invalidStates = {email: 'not_valid', lastname: 'not_valid'};

            validateForm()(dispatch, getStateInvalidForm);
            expect(updateErrorStates).toBeCalled();
            expect(updateErrorStates).toBeCalledWith(invalidStates);
        });

        it('should set form errors', () => {
            const stateErrors = {
                active: 'email',
                email: {
                    code: 'login.not_available',
                    text: 'Frontend.login-email_errors_unavailable'
                },
                lastname: {
                    code: 'missingvalue',
                    text: '_AUTH_.lastname_errors_missingvalue'
                }
            };

            validateForm()(dispatch, getStateInvalidForm);
            expect(updateGroupErrors).toBeCalled();
            expect(updateGroupErrors).toBeCalledWith(stateErrors);
        });

        it('should scroll to the first form error', () => {
            Object.defineProperty(document, 'querySelector', {
                value: jest.fn(() => ({}))
            });
            validateForm()(dispatch, getStateInvalidForm);
            expect(scrollToError).toBeCalled();
        });

        it('should call metrics methods', () => {
            validateForm()(dispatch, getStateInvalidForm);
            expect(metrics.send).toBeCalled();
            expect(metrics.goal).toBeCalled();
        });
    });
});

describe('moveToPrevStep', () => {
    it('should move form to the first step if error is from first screen', () => {
        moveToPrevStep(['email', 'not_valid'], dispatch);
        expect(setCurrentStep).toBeCalledWith('start');
    });
});
