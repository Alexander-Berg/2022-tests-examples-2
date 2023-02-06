jest.mock('../../api', () => ({
    request: jest.fn()
}));
import api from '../../api';
import metrics from '../../metrics';
import {updateRegistrationErrors, updateFetchingStatus} from '../actions';
import {setCaptchaRequired} from '@blocks/actions/form';
import updateFieldStatus from '../methods/updateFieldStatus';
import sendConnectOrCompleteRegistrationData from '../methods/sendConnectOrCompleteRegistrationData';
import mockData from './__mocks__/data';

const {location} = window;

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
        captchaRequired: false,
        type: '',
        prefix: 'registration_pdd',
        values: {
            name: 'test',
            lastname: 'example',
            email: 'test@example.com',
            login: '',
            password: ''
        },
        states: {
            name: 'valid',
            lastname: 'valid',
            email: 'valid'
        }
    }
});

const formData = {
    formStatesPhone: {
        firstname: 'valid',
        lastname: 'valid',
        login: 'valid',
        password: 'valid',
        password_confirm: 'valid',
        hint_question_id: '',
        hint_question: '',
        hint_question_custom: 'valid',
        hint_answer: '',
        captcha: '',
        phone: 'valid',
        phoneCode: 'valid',
        phoneCodeStatus: 'code_sent'
    },
    validReturnedStatesPhone: {
        login: 'valid',
        firstname: 'valid',
        lastname: 'valid',
        password: 'valid',
        password_confirm: 'valid',
        phone: 'valid'
    },
    formStatesCaptcha: {
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
    validReturnedStatesCaptcha: {
        captcha: 'valid',
        login: 'valid',
        firstname: 'valid',
        hint_answer: 'valid',
        hint_question: 'valid',
        hint_question_custom: 'valid',
        lastname: 'valid',
        password: 'valid',
        password_confirm: 'valid'
    },
    formValuesPhone: {
        firstname: 'test',
        lastname: 'example',
        login: 'test.login',
        password: 'simple123',
        password_confirm: 'simple123',
        hint_question_id: '',
        hint_question: '',
        hint_question_custom: '',
        hint_answer: '',
        captcha: '',
        phone: '84951921424',
        phoneCode: '781565'
    },
    formValuesCaptcha: {
        firstname: 'test',
        lastname: 'example',
        login: 'test.login',
        password: 'simple123',
        password_confirm: 'simple123',
        hint_question_id: '99',
        hint_question: '',
        hint_question_custom: '',
        hint_answer: '',
        captcha: 'test',
        phone: '',
        phoneCode: ''
    },
    errorsObj: {
        active: '',
        firstname: {code: '', text: ''},
        lastname: {code: '', text: ''},
        login: {code: '', text: ''},
        email: {code: '', text: ''},
        emailCode: {code: '', text: ''},
        password: {code: '', text: ''},
        password_confirm: {code: '', text: ''},
        hint_question_id: {code: '', text: ''},
        hint_question: {code: '', text: ''},
        hint_question_custom: {code: '', text: ''},
        hint_answer: {code: '', text: ''},
        captcha: {code: '', text: ''},
        phone: {code: '', text: ''},
        phoneCode: {code: '', text: ''},
        phoneCodeStatus: '',
        errorDescription: '',
        hintActive: false
    }
};

jest.mock('../../metrics', () => ({
    send: jest.fn(),
    goal: jest.fn()
}));

jest.mock('../actions', () => ({
    updateRegistrationErrors: jest.fn(),
    updateFetchingStatus: jest.fn()
}));

jest.mock('@blocks/actions/form', () => ({
    setCaptchaRequired: jest.fn()
}));

jest.mock('../methods/updateFieldStatus');

describe('sendConnectOrCompleteRegistrationData', () => {
    describe('api request succeded', () => {
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
                };

                return new FakeP();
            });

            delete window.location;
            window.location = {
                href: 'some url'
            };
        });
        afterEach(function() {
            api.request.mockClear();
            window.location = location;
        });

        it('should redirect to url if response is ok', () => {
            sendConnectOrCompleteRegistrationData(formData)(mockData.props.dispatch, getState);
            expect(window.location.href).toEqual('/registration/finish?track_id=1234');
        });
        it('should distpatch metrics methods', () => {
            const prefix = getState().form.prefix;

            sendConnectOrCompleteRegistrationData(formData)(mockData.props.dispatch, getState);
            expect(metrics.send).toBeCalled();
            expect(metrics.send).toBeCalledWith(['Форма', 'Успешная регистрация']);
            expect(metrics.goal).toBeCalled();
            expect(metrics.goal).toBeCalledWith(`${prefix}_form_success`);
        });
    });
    describe('api request failed', () => {
        afterEach(function() {
            api.request.mockClear();
        });

        describe('handle captcha.required error', () => {
            beforeEach(function() {
                api.request.mockImplementation(function() {
                    const FakeP = function() {
                        this.then = function() {
                            return this;
                        };
                        this.fail = function(fn) {
                            fn({status: 'error', error: ['captcha.required']});
                            return this;
                        };
                    };

                    return new FakeP();
                });
            });
            it('should dispatch setCaptchaRequired', () => {
                sendConnectOrCompleteRegistrationData(formData)(mockData.props.dispatch, getState);
                expect(setCaptchaRequired).toBeCalled();
            });
            it('should dispatch updateFetchingStatus', () => {
                sendConnectOrCompleteRegistrationData(formData)(mockData.props.dispatch, getState);
                expect(updateFetchingStatus).toBeCalled();
            });
            it('should dispatch updateRegistrationErrors', () => {
                sendConnectOrCompleteRegistrationData(formData)(mockData.props.dispatch, getState);
                expect(updateRegistrationErrors).toBeCalled();
                expect(updateRegistrationErrors).toBeCalledWith({
                    status: '',
                    code: '',
                    text: ''
                });
            });
            it('should return $.Deferred after dispatches', () => {
                const result = sendConnectOrCompleteRegistrationData(formData)(mockData.props.dispatch, getState);

                expect(result).toEqual(
                    expect.objectContaining({
                        fail: expect.any(Function),
                        then: expect.any(Function)
                    })
                );
            });
        });

        describe('handle field error in response', () => {
            beforeEach(function() {
                api.request.mockImplementation(function() {
                    const FakeP = function() {
                        this.then = function() {
                            return this;
                        };
                        this.fail = function(fn) {
                            fn({status: 'error', error: [{field: 'domain', code: 'domain.invalid_type'}]});
                            return this;
                        };
                    };

                    return new FakeP();
                });
                updateFieldStatus.mockImplementation(() => () => ({field: 'domain'}));
            });
            it('should dispatch updateRegistrationErrors with error object', () => {
                sendConnectOrCompleteRegistrationData(formData)(mockData.props.dispatch, getState);
                expect(updateFieldStatus).toBeCalled();
            });
            it('should dispatch metrics methods', () => {
                const prefix = getState().form.prefix;

                sendConnectOrCompleteRegistrationData(formData)(mockData.props.dispatch, getState);
                expect(metrics.send).toBeCalled();
                expect(metrics.send).toBeCalledWith(['Форма', 'Показ ошибок', 'domain.invalid']);
                expect(metrics.goal).toBeCalled();
                expect(metrics.goal).toBeCalledWith(`${prefix}_form_fail`);
            });
        });

        describe('handle global error', () => {
            beforeEach(function() {
                api.request.mockImplementation(function() {
                    const FakeP = function() {
                        this.then = function() {
                            return this;
                        };
                        this.fail = function(fn) {
                            fn({status: 'error', error: ['some.error']});
                            return this;
                        };
                    };

                    return new FakeP();
                });
            });
            it('should dispatch updateRegistrationErrors with global prop', () => {
                sendConnectOrCompleteRegistrationData(formData)(mockData.props.dispatch, getState);
                expect(updateRegistrationErrors).toBeCalled();
                expect(updateRegistrationErrors).toBeCalledWith(expect.objectContaining({status: 'global'}));
            });
        });
    });
});
