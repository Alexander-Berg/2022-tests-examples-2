import api from '@blocks/api';
import {domikIsLoading} from '@blocks/auth/actions';
import {changeStep, changePagePopupType, changePagePopupVisibility} from '@blocks/authv2/actions';
import {updateErrors, updateStates, setCaptchaRequired} from '@blocks/actions/form';
import {requestPhoneConfirmationCode} from '@blocks/actions/phoneConfirm';
import sendToChallenge from '@blocks/authv2/actions/challenge/sendToChallenge';
import metrics from '@blocks/metrics';
// eslint-disable-next-line no-duplicate-imports
import {confirmPhone, onNext, onBack} from '../logic';
import {amRequestSmsCode} from '@blocks/authv2/actions/nativeMobileApi';
import {FIELDS_NAMES} from '@components/Field/names';
import {validateSecurityAnswer} from '../actions/validateSecurityAnswer';
import {ENTRY_REGISTER_NO_PHONE_PROCESS} from '../processes';
import {STEPS} from '../steps';

jest.mock('@blocks/api', () => ({
    validatePhone: jest.fn().mockResolvedValue(),
    checkPhoneConfirmationCode: jest.fn().mockResolvedValue(),
    findAccountsByPhone: jest.fn().mockResolvedValue(),
    findAccountsByNameAndPhone: jest.fn().mockResolvedValue()
}));
jest.mock('../actions/validateSecurityAnswer', () => ({
    validateSecurityAnswer: jest.fn()
}));
jest.mock('@blocks/auth/actions', () => ({
    domikIsLoading: jest.fn()
}));
jest.mock('@blocks/authv2/actions', () => ({
    changePagePopupType: jest.fn(),
    changePagePopupVisibility: jest.fn(),
    changeStep: jest.fn()
}));
jest.mock('@blocks/actions/form', () => ({
    updateErrors: jest.fn(),
    updateStates: jest.fn(),
    setCaptchaRequired: jest.fn()
}));
jest.mock('@blocks/actions/phoneConfirm', () => ({
    requestPhoneConfirmationCode: jest.fn(() => {
        return {
            then() {
                return {
                    catch() {}
                };
            }
        };
    })
}));
jest.mock('@blocks/metrics', () => ({
    goal: jest.fn(),
    send: jest.fn()
}));
jest.mock('@blocks/authv2/actions/challenge/sendToChallenge', () => ({
    default: jest.fn()
}));
jest.mock('@blocks/authv2/actions/nativeMobileApi', () => ({
    amRequestSmsCode: jest.fn()
}));

describe('@blocks/UserEntryFlow/logic.js', () => {
    beforeEach(() => {
        api.validatePhone.mockImplementation(() => {
            return {
                then(callback = () => {}) {
                    callback({isPhoneValidForFlashCall: true});

                    return {
                        catch() {}
                    };
                }
            };
        });
    });
    afterEach(() => {
        api.validatePhone.mockClear();
        domikIsLoading.mockClear();
        changePagePopupType.mockClear();
        changePagePopupVisibility.mockClear();
        updateErrors.mockClear();
        requestPhoneConfirmationCode.mockClear();
        metrics.goal.mockClear();
        metrics.send.mockClear();
        sendToChallenge.default.mockClear();
        amRequestSmsCode.mockClear();
        changeStep.mockClear();
        validateSecurityAnswer.mockClear();
    });
    describe('onNext', () => {
        it('should validate security question ar/and security answer', () => {
            const action = onNext(STEPS.SQ_SA);
            const mockGetState = jest.fn().mockReturnValue({
                form: {
                    values: {
                        [FIELDS_NAMES.HINT_QUESTION_ID]: '12',
                        [FIELDS_NAMES.HINT_QUESTION]: 'Фамилия вашего любимого музыканта',
                        [FIELDS_NAMES.HINT_ANSWER]: 'Цой'
                    },
                    states: {
                        [FIELDS_NAMES.HINT_ANSWER]: ''
                    }
                }
            });
            const mockDispatch = jest.fn().mockImplementation((func) => {
                return Promise.resolve(typeof func === 'function' ? func(mockDispatch, mockGetState) : undefined);
            });

            action(mockDispatch, mockGetState);

            expect(validateSecurityAnswer).toBeCalledWith({[FIELDS_NAMES.HINT_ANSWER]: 'Цой'});
        });
        it('should change step to personal data', () => {
            const action = onNext(STEPS.SQ_SA);
            const mockGetState = jest.fn().mockReturnValue({
                form: {
                    values: {
                        [FIELDS_NAMES.HINT_QUESTION_ID]: '12',
                        [FIELDS_NAMES.HINT_QUESTION]: 'Фамилия вашего любимого музыканта',
                        [FIELDS_NAMES.HINT_ANSWER]: 'Цой'
                    },
                    states: {
                        [FIELDS_NAMES.HINT_ANSWER]: 'valid'
                    }
                }
            });
            const mockDispatch = jest.fn().mockImplementation((func) => {
                return Promise.resolve(typeof func === 'function' ? func(mockDispatch, mockGetState) : undefined);
            });

            action(mockDispatch, mockGetState);

            expect(domikIsLoading).toBeCalledWith(false);
        });
    });
    describe('Actions: authBySMS', () => {
        it('should request confirmation code with flashCall when am exp on', () => {
            const getState = jest.fn(() => ({
                common: {
                    askEmailUrl: 'askEmailUrl',
                    askPhoneUrl: 'askPhoneUrl'
                },
                am: {
                    isAm: true,
                    experiments: {
                        reg_call_confirm_on: true
                    }
                }
            }));
            const dispatch = jest.fn((action) => {
                if (typeof action === 'function') {
                    return action(dispatch, getState);
                }
            });

            confirmPhone()(dispatch, getState);

            expect(requestPhoneConfirmationCode).toBeCalledWith(
                expect.objectContaining({
                    phoneValidateParams: {
                        isPhoneValidForFlashCall: true
                    }
                })
            );
        });

        it.each([
            [
                STEPS.PERSONAL_DATA,
                {auth: {form: {}}, form: {values: {[FIELDS_NAMES.FIRSTNAME]: 'qwe', [FIELDS_NAMES.LASTNAME]: 'qwe'}}}
            ],
            [STEPS.PHONE_CONFIRM, {auth: {form: {}}, form: {values: {}}}]
        ])(
            // eslint-disable-next-line max-len
            'should call findAccountsByNameAndPhone before ACCOUNTS_STEP when useNewSuggestByPhone = false step = %s state = %o',
            async (step, state) => {
                expect.assertions(1);
                const action = onNext(step);
                const dispatch = jest.fn();
                const getState = jest.fn().mockReturnValue(state);

                await action(dispatch, getState);

                expect(api.findAccountsByNameAndPhone).toBeCalled();
            }
        );
        it.each([
            [
                STEPS.PERSONAL_DATA,
                {
                    auth: {form: {}},
                    common: {experiments: {flags: ['use-new-suggest-by-phone']}},
                    form: {values: {[FIELDS_NAMES.FIRSTNAME]: 'qwe', [FIELDS_NAMES.LASTNAME]: 'qwe'}}
                }
            ],
            [
                STEPS.PHONE_CONFIRM,
                {auth: {form: {}}, common: {experiments: {flags: ['use-new-suggest-by-phone']}}, form: {values: {}}}
            ]
        ])(
            // eslint-disable-next-line max-len
            'should call findAccountsByPhone before ACCOUNTS_STEP when useNewSuggestByPhone = true step = %s state = %o',
            async (step, state) => {
                expect.assertions(1);
                const action = onNext(step);
                const dispatch = jest.fn();
                const getState = jest.fn().mockReturnValue(state);

                await action(dispatch, getState);

                expect(api.findAccountsByPhone).toBeCalled();
            }
        );
        it('should not request confirmation code with flashCall with base logic', () => {
            const getState = jest.fn(() => ({
                common: {
                    askEmailUrl: 'askEmailUrl',
                    askPhoneUrl: 'askPhoneUrl'
                }
            }));
            const dispatch = jest.fn((action) => {
                if (typeof action === 'function') {
                    return action(dispatch, getState);
                }
            });

            confirmPhone()(dispatch, getState);

            expect(requestPhoneConfirmationCode).not.toBeCalledWith(
                expect.objectContaining({
                    phoneValidateParams: {
                        isPhoneValidForFlashCall: true
                    }
                })
            );
        });

        it('should request confirmation code with flashCall with base logic', () => {
            const getState = jest.fn(() => ({
                common: {
                    askEmailUrl: 'askEmailUrl',
                    askPhoneUrl: 'askPhoneUrl',
                    experiments: {
                        flags: ['restorelogin_call_flashcall']
                    }
                },
                router: {
                    location: {
                        pathname: '/auth/restore/login'
                    }
                }
            }));
            const dispatch = jest.fn((action) => {
                if (typeof action === 'function') {
                    return action(dispatch, getState);
                }
            });

            confirmPhone()(dispatch, getState);

            expect(requestPhoneConfirmationCode).toBeCalledWith(
                expect.objectContaining({
                    phoneValidateParams: {
                        isPhoneValidForFlashCall: true
                    }
                })
            );
        });

        it('should not request confirmation code with flashCall if am exp is off', () => {
            const getState = jest.fn(() => ({
                common: {
                    askEmailUrl: 'askEmailUrl',
                    askPhoneUrl: 'askPhoneUrl'
                },
                am: {
                    isAm: true,
                    experiments: {
                        reg_call_confirm_on: false
                    }
                }
            }));

            const dispatch = jest.fn((action) => {
                if (typeof action === 'function') {
                    return action(dispatch, getState);
                }
            });

            confirmPhone()(dispatch, getState);

            expect(requestPhoneConfirmationCode).not.toBeCalledWith(
                expect.objectContaining({
                    phoneValidateParams: {
                        isPhoneValidForFlashCall: true
                    }
                })
            );
        });
    });
    describe('onBack', () => {
        it('should show captcha if back to sq sa step', () => {
            const action = onBack();
            const mockGetState = jest.fn().mockReturnValue({
                router: {
                    location: {
                        pathname: '/auth/reg'
                    }
                },
                userEntryFlow: {
                    process: ENTRY_REGISTER_NO_PHONE_PROCESS,
                    step: STEPS.PERSONAL_DATA
                }
            });
            const mockDispatch = jest.fn().mockImplementation((func) => {
                return Promise.resolve(typeof func === 'function' ? func(mockDispatch, mockGetState) : undefined);
            });

            action(mockDispatch, mockGetState);

            expect(setCaptchaRequired).toBeCalledWith(true);
        });
        it('should show SQ_SA if back to SQ_SA step from captcha', () => {
            const action = onBack();
            const mockGetState = jest.fn().mockReturnValue({
                router: {
                    location: {
                        pathname: '/auth/reg'
                    }
                },
                form: {
                    captchaRequired: true
                },
                userEntryFlow: {
                    process: ENTRY_REGISTER_NO_PHONE_PROCESS,
                    step: STEPS.SQ_SA
                }
            });
            const mockDispatch = jest.fn().mockImplementation((func) => {
                return Promise.resolve(typeof func === 'function' ? func(mockDispatch, mockGetState) : undefined);
            });

            action(mockDispatch, mockGetState);

            expect(setCaptchaRequired).toBeCalledWith(false);
            expect(updateStates).toBeCalledWith({field: FIELDS_NAMES.HINT_ANSWER, status: ''});
        });
    });
});
