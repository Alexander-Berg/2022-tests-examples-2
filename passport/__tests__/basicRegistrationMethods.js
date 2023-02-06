jest.mock('../../api', () => ({
    request: jest.fn()
}));
import * as api from '../../api';
import regMethods from '../methods/basicRegistrationMethods';
import {updateRegistrationErrors, updateFetchingStatus} from '../actions';
import checkCaptcha from '../methods/checkCaptcha';
import metrics from '../../metrics';
import {sendRegistrationData} from '../methods/defineRegistrationFunction';

jest.mock('../../metrics', () => ({
    send: jest.fn(),
    goal: jest.fn()
}));

jest.mock('../actions', () => ({
    updateFetchingStatus: jest.fn(),
    updateRegistrationErrors: jest.fn()
}));

jest.mock('@blocks/actions/form', () => ({
    updateStates: jest.fn(),
    updateErrors: jest.fn()
}));

jest.mock('../methods/checkCaptcha');

const {location} = window;

const props = {
    dispatch: jest.fn()
};

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

const mockData = {
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

describe('sendRegistrationData', () => {
    const data = {
        captcha: 'тесткапча',
        firstname: 'test',
        hint_answer: 'joker',
        hint_question: 'Фамилия вашего любимого музыканта',
        hint_question_custom: '',
        hint_question_id: '12',
        'human-confirmation': 'captcha',
        lastname: 'testov',
        login: 'testtestov',
        password: 'simple123',
        password_confirm: 'simple123',
        phone: '',
        phoneCode: ''
    };

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
        delete window.location;
        window.location = {
            href: 'some url'
        };
    });
    afterEach(function() {
        api.request.mockClear();
        window.location = location;
    });

    it('it should call window.location href if response is ok', () => {
        sendRegistrationData(data)(props.dispatch, getState);
        expect(window.location.href).toEqual('/registration/finish?track_id=1234');
    });

    it('it should dispatch metrics methods', () => {
        sendRegistrationData(data)(props.dispatch, getState);
        expect(metrics.send).toBeCalled();
        expect(metrics.goal).toBeCalled();
    });

    describe('sendRegistrationData, request fails with global registration error', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function() {
                        return this;
                    };
                    this.fail = function(fn) {
                        fn({error: [{field: 'global', code: 'registrationsmssendperiplimitexceeded'}]});
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

        it('should dispatch updateRegistrationErrors', () => {
            sendRegistrationData(data)(props.dispatch, getState);
            expect(updateRegistrationErrors).toBeCalled();
        });
    });

    describe('sendRegistrationData, request fails with field error', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function() {
                        return this;
                    };
                    this.fail = function(fn) {
                        fn({error: [{field: 'login', code: 'login.notavailable'}]});
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

        it('should call metrics methods', () => {
            sendRegistrationData(data)(props.dispatch, getState);
            expect(metrics.send).toBeCalled();
            expect(metrics.goal).toBeCalled();
        });
    });

    describe('sendRegistrationData, request fails with unknown error', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function() {
                        return this;
                    };
                    this.fail = function(fn) {
                        fn({});
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

        it('should dispatch updateRegistrationErrors with "something wrong" error', () => {
            sendRegistrationData(data)(props.dispatch, getState);
            expect(updateRegistrationErrors).toBeCalled();
            expect(updateRegistrationErrors).toBeCalledWith({
                status: 'error',
                code: 'global',
                text: '_AUTH_.avatar.error-internal',
                descriptionText: ''
            });
        });
    });
});

describe('submitRegistration', () => {
    describe('submitRegistration', () => {
        const data = {
            captcha: 'тесткапча',
            firstname: 'test',
            hint_answer: 'joker',
            hint_question: 'Фамилия вашего любимого музыканта',
            hint_question_custom: '',
            hint_question_id: '12',
            'human-confirmation': 'captcha',
            lastname: 'testov',
            login: 'testtestov',
            password: 'simple123',
            password_confirm: 'simple123',
            phone: '',
            phoneCode: ''
        };

        it('should call updateFetchingStatus', () => {
            regMethods.submitRegistration(data)(props.dispatch, getState);
            expect(updateFetchingStatus).toBeCalled();
        });

        it('should dispatch checkCaptcha if confirmation method is captcha', () => {
            regMethods.submitRegistration(data)(props.dispatch, getState);
            expect(checkCaptcha).toBeCalled();
        });

        it('should add FROM key to data if there`s one in state', () => {
            regMethods.submitRegistration(data)(props.dispatch, getState);
            expect(checkCaptcha).toBeCalledWith(expect.objectContaining({from: 'mail'}));
        });
    });
});

describe('prepareLiteFormData', () => {
    it('should return preparedFieldsStates with phone validation', () => {
        const formStates = mockData.formStatesPhone;
        const isMobile = false;
        const method = 'phone';
        const validReturnedStates = mockData.validReturnedStatesPhone;
        const returnedStates = regMethods.prepareFormData(formStates, method, isMobile);

        expect(returnedStates).toEqual(validReturnedStates);
    });

    it('should return preparedFieldsStates with captcha validation', () => {
        const formStates = mockData.formStatesCaptcha;
        const isMobile = false;
        const method = 'captcha';
        const validReturnedStates = mockData.validReturnedStatesCaptcha;
        const returnedStates = regMethods.prepareFormData(formStates, method, isMobile);

        expect(returnedStates).toEqual(validReturnedStates);
    });

    it('should remove password_confirm from result obj if isMobile: true', () => {
        const formStates = mockData.formStatesCaptcha;
        const isMobile = true;
        const method = 'captcha';
        const returnedStates = regMethods.prepareFormData(formStates, method, isMobile);

        expect(returnedStates).not.toHaveProperty('password_confirm');
    });
});
