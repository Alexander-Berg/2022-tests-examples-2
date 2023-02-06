jest.mock('../../../api', () => ({
    request: jest.fn()
}));
import api from '../../../api';
import processError from '../../helpers/process_error';
import updateFormFields from '../../helpers/update_form_fields';
import {updateError, checkStatus, confirmPhoneCodeSend, setFetchingStatus} from '../../actions';
import sendConfirmation from '../send_confirmation';

jest.mock('../../actions', () => ({
    updateError: jest.fn(),
    checkStatus: jest.fn(),
    confirmPhoneCodeSend: jest.fn(),
    setFetchingStatus: jest.fn()
}));
jest.mock('../../helpers/process_error');
jest.mock('../../helpers/update_form_fields');

const getState = () => ({
    common: {
        csrf: '12345',
        track_id: '1234'
    },
    deleteAccount: {
        isFetching: false,
        isModalOpened: false,
        isSocialchik: false,
        isPddAdmin: false,
        confirmation: {
            method: 'phone',
            status: 'unconfirmed'
        },
        form: {
            code: '',
            answer: '',
            captcha: ''
        }
    }
});
const dispatch = jest.fn();

describe('sendConfirmation', () => {
    describe('api request succeed', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.done = (fn) => {
                        fn({status: 'ok', timeout: 30});
                        return this;
                    };
                    this.fail = () => {
                        return this;
                    };
                    this.always = () => {
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
            setFetchingStatus.mockClear();
            processError.mockClear();
        });
        const form = {
            code: '123',
            answer: 'answer',
            captcha: 'test'
        };

        it('should setFetchingStatus', () => {
            sendConfirmation(form, 'phone')(dispatch, getState);
            expect(setFetchingStatus).toBeCalled();
            expect(setFetchingStatus.mock.calls[0][0]).toEqual(true);
        });

        it('should dispatch updateError', () => {
            sendConfirmation(form, 'phone')(dispatch, getState);
            expect(updateError).toBeCalled();
            expect(updateError).toBeCalledWith({field: '', message: ''});
        });

        it('should dispatch updateFormFields', () => {
            sendConfirmation(form, 'phone')(dispatch, getState);
            expect(updateFormFields).toBeCalled();
        });

        it('should dispatch checkStatus with code_sent arg', () => {
            sendConfirmation(form, 'phone')(dispatch, getState);
            expect(checkStatus).toBeCalled();
            expect(checkStatus).toBeCalledWith('code_sent');
        });

        it('should dispatch confirmPhoneCodeSend with timeout arg', () => {
            sendConfirmation(form, 'phone')(dispatch, getState);
            expect(confirmPhoneCodeSend).toBeCalled();
            expect(confirmPhoneCodeSend).toBeCalledWith(30);
        });
    });

    describe('api request failed with normal error', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.done = () => {
                        return this;
                    };
                    this.fail = (fn) => {
                        fn({status: 'error', error: {field: 'captcha', error: 'captcha.empty'}});
                        return this;
                    };
                    this.always = () => {
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
            setFetchingStatus.mockClear();
            processError.mockClear();
        });
        const form = {
            code: '123',
            answer: 'answer',
            captcha: 'test'
        };

        it('should dispatch processError with error field and error code args', () => {
            sendConfirmation(form, 'phone')(dispatch, getState);
            expect(processError).toBeCalled();
            expect(processError).toBeCalledWith('captcha', 'captcha.empty');
        });
    });

    describe('api request done, always block', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.done = () => {
                        return this;
                    };
                    this.fail = () => {
                        return this;
                    };
                    this.always = (fn) => {
                        fn();
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
            setFetchingStatus.mockClear();
            processError.mockClear();
        });

        it('should dispatсh setFetchingStatus with false arg', () => {
            sendConfirmation({}, 'phone')(dispatch, getState);
            expect(setFetchingStatus).toBeCalled();
            expect(setFetchingStatus.mock.calls[1][0]).toBe(false);
        });
    });
});
