jest.mock('@blocks/api', () => ({
    request: jest.fn()
}));
import * as api from '@blocks/api';
import checkCaptcha from '../methods/checkCaptcha';
import updateFieldStatus from '../methods/updateFieldStatus';
import {updateFetchingStatus} from '../actions';
import reloadCaptcha from '@components/Captcha/actions/reloadCaptcha';

jest.mock('../methods/updateFieldStatus');
jest.mock('@components/Captcha/actions/reloadCaptcha');
jest.mock('../actions', () => ({
    updateFetchingStatus: jest.fn()
}));

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

describe('checkCaptcha', () => {
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

    describe('checkCaptcha, request succeed', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.done = function(fn) {
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
        });

        it('should dispatch regFunction if request succeed', () => {
            checkCaptcha(data)(props.dispatch, getState);
            expect(props.dispatch).toBeCalled();
            expect(props.dispatch).toBeCalledWith(expect.any(Function));
        });
    });
    describe('checkCaptcha, request with error', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.done = function(fn) {
                        fn({status: 'error', errors: ['not.matched']});
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

        it('should dispatch updateFieldStatus', () => {
            updateFieldStatus.mockImplementation(() => () => ({field: 'dd'}));
            checkCaptcha(data)(props.dispatch, getState);
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('captcha', 'not_valid');
        });
    });
    describe('checkCaptcha, request failed', () => {
        updateFieldStatus.mockImplementation(() => () => ({field: 'dd'}));
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.done = function() {
                        return this;
                    };
                    this.fail = function(fn) {
                        fn({status: 'error', errors: ['captcha.cannot_locate']});
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
        });

        it('should dispatch updateFieldStatus', () => {
            checkCaptcha(data)(props.dispatch, getState);
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('captcha', 'not_valid');
        });

        it('should dispatch reloadCaptcha', () => {
            checkCaptcha(data)(props.dispatch, getState);
            expect(reloadCaptcha).toBeCalled();
        });

        it('should dispatch updateFetchingStatus', () => {
            checkCaptcha(data)(props.dispatch, getState);
            expect(updateFetchingStatus).toBeCalled();
        });
    });
});
