import validateForm, {getFormValues} from '../methods/validateForm';
import handleValidationError from '../methods/handleValidationError.js';
import sendDataForRegistration from '../methods/sendDataForRegistration';
import {showEulaPopup} from '../actions';
import registrationLiteMethods from '../../registration-lite/methods/registrationLiteMethods';

jest.mock('../methods/handleValidationError');
jest.mock('../methods/sendDataForRegistration');
jest.mock('../methods/checkCaptcha');
jest.mock('../../registration-lite/methods/registrationLiteMethods');
jest.mock('../actions', () => ({
    showEulaPopup: jest.fn()
}));

registrationLiteMethods.sendEmail = jest.fn();

describe('getFormValues', () => {
    const state = {
        form: {
            type: 'alternative',
            values: {
                firstname: 'василий',
                lastname: 'уткин',
                surname: '',
                login: 'utkin',
                password: 'simple123',
                password_confirm: 'simple123',
                hint_answer: 'answer',
                hint_question: 'Фамилия вашего любимого музыканта',
                hint_question_custom: '',
                hint_question_id: '12',
                captcha: 'абзац',
                phone: '',
                phoneCode: ''
            }
        }
    };

    it('should return values from state data', () => {
        const returnedData = {
            firstname: 'василий',
            lastname: 'уткин',
            surname: '',
            login: 'utkin',
            password: 'simple123',
            password_confirm: 'simple123',
            hint_answer: 'answer',
            hint_question: 'Фамилия вашего любимого музыканта',
            hint_question_custom: '',
            hint_question_id: '12',
            captcha: 'абзац',
            phone: '',
            phoneCode: ''
        };

        expect(getFormValues(state)).toEqual(returnedData);
    });

    it('should remove captcha from state data if registration type is complete', () => {
        const returnedData = {
            firstname: 'василий',
            lastname: 'уткин',
            surname: '',
            login: 'utkin',
            password: 'simple123',
            password_confirm: 'simple123',
            hint_answer: 'answer',
            hint_question: 'Фамилия вашего любимого музыканта',
            hint_question_custom: '',
            hint_question_id: '12',
            phone: '',
            phoneCode: '',
            state: 'complete_social'
        };

        state.registrationName = 'complete';
        state.person = {
            hasRecoveryMethod: true
        };
        state.form.type = 'complete_social';

        expect(getFormValues(state)).toEqual(returnedData);
    });
});

describe('validateForm', () => {
    describe('form invalid', () => {
        const getState = makeGetStateFunc('withInvalidForm');

        it('should call handleValidationError', () => {
            validateForm(false)(jest.fn(), getState);

            expect(handleValidationError).toBeCalled();
        });

        it('should call handleValidationError with correct error object as arg', () => {
            const expectedErrorObj = {
                firstname: {
                    code: 'missingvalue',
                    text: '_AUTH_.firstname_errors_missingvalue',
                    descriptionText: ''
                },
                password: {
                    code: 'missingvalue',
                    text: '_AUTH_.password_errors_missingvalue',
                    descriptionText: ''
                }
            };

            validateForm(false)(jest.fn(), getState);
            expect(handleValidationError.mock.calls[0][2]).toEqual(expectedErrorObj);
        });
    });
    describe('form valid', () => {
        beforeEach(function() {
            sendDataForRegistration.mockClear();
        });
        const getState = makeGetStateFunc();

        it('should send correct data to sendDataForRegistration function', () => {
            const expectedValues = {
                captcha: 'test',
                hint_answer: 'testanswer',
                hint_question: 'Фамилия вашего любимого музыканта',
                hint_question_custom: '',
                hint_question_id: '12',
                'human-confirmation': 'captcha',
                lastname: 'example',
                login: 'testlogin',
                name: 'test',
                password: 'testpass',
                password_confirm: 'testpass',
                phone: '',
                phoneCode: ''
            };

            validateForm(false)(jest.fn(), getState);
            expect(sendDataForRegistration).toBeCalled();
            expect(sendDataForRegistration.mock.calls[0][1]).toEqual(expectedValues);
        });

        it('should show eula popup if isEulaShowedInPopup is set', () => {
            const getState = makeGetStateFunc('withEulaInPopup');

            validateForm(false)(jest.fn(), getState);
            expect(showEulaPopup).toBeCalled();
        });
    });
});

function makeGetStateFunc(...conditions) {
    const basicState = {
        settings: {
            language: 'ru',
            uatraits: {
                isMobile: false,
                isTouch: false
            }
        },
        person: {},
        common: {
            csrf: '12345',
            track_id: '1234',
            from: 'mail'
        },
        form: {
            isEulaShowedInPopup: false,
            values: {
                name: 'test',
                lastname: 'example',
                login: 'testlogin',
                password: 'testpass',
                password_confirm: 'testpass',
                hint_question_id: '12',
                hint_question: 'Фамилия вашего любимого музыканта',
                hint_question_custom: '',
                hint_answer: 'testanswer',
                captcha: 'test',
                phone: '',
                phoneCode: ''
            },
            states: {
                firstname: 'valid',
                lastname: 'valid',
                login: 'valid',
                password: 'valid',
                password_confirm: 'valid',
                hint_question_id: 'valid',
                hint_question: 'valid',
                hint_question_custom: 'valid',
                hint_answer: 'valid',
                captcha: 'valid',
                phone: '',
                phoneCode: '',
                phoneCodeStatus: ''
            },
            errors: {
                active: '',
                firstname: {
                    code: '',
                    text: ''
                },
                lastname: {
                    code: '',
                    text: ''
                },
                login: {
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
                hint_question_id: {
                    code: '',
                    text: ''
                },
                hint_question: {
                    code: '',
                    text: ''
                },
                hint_question_custom: {
                    code: '',
                    text: ''
                },
                hint_answer: {
                    code: '',
                    text: ''
                },
                captcha: {
                    code: '',
                    text: ''
                },
                phone: {
                    code: '',
                    text: ''
                },
                phoneCode: {
                    code: '',
                    text: ''
                },
                phoneCodeStatus: ''
            },
            isPhoneCallConfirmationAvailable: false,
            validation: {
                method: 'captcha'
            }
        }
    };

    if (conditions.includes('withInvalidForm')) {
        basicState.form.states.firstname = 'not_valid';
        basicState.form.states.password = 'not_valid';
    }
    if (conditions.includes('withEulaInPopup')) {
        basicState.form.isEulaShowedInPopup = true;
    }
    if (conditions.includes('isLiteReg')) {
        basicState.registrationType = 'lite';
    }
    if (conditions.includes('phoneConfirmation')) {
        basicState.form.validation.method = 'phone';
        basicState.form.values.phone = '+79001234567';
        basicState.form.states.phone = 'valid';
        basicState.form.states.phoneCode = 'valid';
        basicState.form.states.phoneCodeStatus = 'code_sent';
        basicState.form.validation.humanConfirmationDone = true;
    }
    return function() {
        return basicState;
    };
}
