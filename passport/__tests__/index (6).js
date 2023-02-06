jest.mock('../../api', () => ({
    /* request: function(data) {
        const p = new Promise(function(resolve, reject) {
            resolve({status: 'ok', questions: [1, 2, 3]});
        });

        return p
    }*/
    request: jest.fn()
}));
import * as api from '../../api';
import regMethods from '../../registration/methods/basicRegistrationMethods';
import checkPhoneCode from '../../registration/methods/checkPhoneCode';
import metrics from '../../metrics';
import {
    updateStates,
    updateErrors,
    getUserQuestionsList,
    updateQuestionValues,
    updateQuestionStates,
    updateConfirmationFetchingStatus,
    updateHumanConfirmationStatus
} from '@blocks/actions/form';
import {setSuggestionFetching, updateFetchingStatus} from '../actions';
import checkIfFieldEmpty from '../methods/checkIfFieldEmpty';
import updateFieldStatus from '../methods/updateFieldStatus';
import getQuestions from '../methods/getQuestions';
import validateLogin from '../methods/validateLogin';

const props = {
    dispatch: jest.fn()
};

const getState = () => ({
    settings: {
        language: 'ru'
    },
    common: {
        csrf: '12345',
        track_id: '1234'
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
        },
        isPhoneCallConfirmationAvailable: false,
        validation: {
            phoneConfirmationType: 'sms'
        }
    }
});

jest.mock('../actions', () => ({
    updateFetchingStatus: jest.fn(),
    setSuggestionFetching: jest.fn(),
    REGISTRATION_COMPLETE_GOAL_PREFIX: 'complete',
    REGISTRATION_COMPLETE_MOBILE_GOAL_PREFIX: 'mobile',
    updateRegistrationErrors: jest.fn()
}));

jest.mock('@blocks/actions/form', () => ({
    updateErrors: jest.fn(),
    updateStates: jest.fn(),
    updateErrorStates: jest.fn(),
    getUserQuestionsList: jest.fn(),
    updateQuestionValues: jest.fn(),
    updateQuestionStates: jest.fn(),
    updateConfirmationFetchingStatus: jest.fn(),
    updateHumanConfirmationStatus: jest.fn(),
    updateValidationMethod: jest.fn(),
    updateQuestionCustomState: jest.fn(),
    updateErrorsValid: jest.fn(),
    updateGroupErrors: jest.fn()
}));

jest.mock('../../metrics', () => ({
    send: jest.fn(),
    goal: jest.fn()
}));

describe('checkIfFieldEmpty', () => {
    it('should dispatch updateStates if isEmpty is true', () => {
        checkIfFieldEmpty('', 'name')(props.dispatch, 'error text');
        expect(updateStates).toBeCalled();
        expect(updateStates).toBeCalledWith({field: 'name', status: 'not_valid'});
    });
    it('should dispatch updateErrors if isEmpty is true', () => {
        checkIfFieldEmpty('', 'name')(props.dispatch, 'error text');
        expect(updateErrors).toBeCalled();
        expect(updateErrors).toBeCalledWith({field: 'name', error: 'error text', active: true});
    });
});

describe('updateFieldStatus', () => {
    it('should dispatch updateStates if field status valid', () => {
        updateFieldStatus('name', 'valid')(props.dispatch);
        expect(updateStates).toBeCalled();
        expect(updateStates).toBeCalledWith({field: 'name', status: 'valid'});
    });
    it('should dispatch updateErrors if field status valid', () => {
        updateFieldStatus('name', 'valid')(props.dispatch);
        expect(updateErrors).toBeCalled();
        expect(updateErrors).toBeCalledWith({field: 'name', error: {code: '', text: ''}, active: false});
    });
    it('should dispatch updateErrors with error if field status valid is not valid', () => {
        updateFieldStatus('name', 'not_valid')(props.dispatch, {code: 'invalid.name', text: 'error code'});
        expect(updateErrors).toBeCalled();
        expect(updateErrors).toBeCalledWith({
            field: 'name',
            errorDescription: '',
            error: {code: 'invalid.name', text: 'error code'},
            active: true
        });
    });
});

describe('getQuestions', () => {
    beforeEach(function() {
        api.request.mockImplementation(function() {
            const p = new Promise(function(resolve) {
                resolve({status: 'ok', questions: [1, 2, 3]});
            });

            return p;
        });
    });
    afterEach(function() {
        api.request.mockClear();
    });
    it('should dispatch getQuestion list with questions', () => {
        getQuestions({track_id: '123'})(props.dispatch, getState);

        setTimeout(() => {
            expect(getUserQuestionsList).toBeCalled();
            expect(updateQuestionValues).toBeCalled();
            expect(updateQuestionStates).toBeCalled();
        }, 0);
    });
});

describe('validateLogin', () => {
    beforeEach(function() {
        api.request.mockImplementation(function() {
            const p = new Promise(function(resolve) {
                resolve({status: 'ok'});
            });

            return p;
        });
    });
    afterEach(function() {
        api.request.mockClear();
    });

    it('should dispatch setSuggestionFetching', () => {
        validateLogin('test-123')(props.dispatch, getState);
        expect(setSuggestionFetching).toBeCalled();
    });
    it('should dispatch setSuggestionFetching with false arg after api respond', () => {
        expect(setSuggestionFetching).toBeCalled();
        expect(setSuggestionFetching).toBeCalledWith(false);
    });
    describe('validateLogin with status.ok from api', () => {
        it('should metrics.send', () => {
            expect(metrics.send).toBeCalled();
        });
    });
});

describe('checkPhoneCode', () => {
    beforeEach(function() {
        api.request.mockImplementation(function() {
            const FakeP = function() {
                this.then = function(fn) {
                    fn();
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
    it('should dispatch updateConfirmationFetchingStatus', () => {
        const code = '1234';

        checkPhoneCode(code)(props.dispatch, getState);
        expect(updateConfirmationFetchingStatus).toBeCalled();
        expect(updateHumanConfirmationStatus).toBeCalled();
    });
    describe('always handler after api respond', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function() {
                        return this;
                    };
                    this.fail = function() {
                        return this;
                    };
                    this.always = function(fn) {
                        fn();
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
        });
        it('should dispatch updateConfirmationFetchingStatus', () => {
            const code = '1234';

            checkPhoneCode(code)(props.dispatch, getState);
            expect(updateConfirmationFetchingStatus).toBeCalled();
        });
    });
});

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
});
