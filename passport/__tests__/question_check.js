jest.mock('@blocks/api', () => ({
    request: jest.fn()
}));
import api from '@blocks/api';
import reloadCaptcha from '@components/Captcha/actions/reloadCaptcha';
import {setModalStatus, setFetchingStatus, checkStatus} from '../../actions';
import processError from '../../helpers/process_error';
import questionCheck from '../question_check';

jest.mock('@components/Captcha/actions/reloadCaptcha');
jest.mock('../../actions', () => ({
    setModalStatus: jest.fn(),
    setFetchingStatus: jest.fn(),
    checkStatus: jest.fn()
}));
jest.mock('../../helpers/process_error');

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
            method: 'skip',
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

describe('questionCheck', () => {
    describe('api request succeed', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.done = (fn) => {
                        fn({status: 'ok', correct: true});
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

        it(
            'should dispatch processError with answer.missingvalue arg if questionCheck ' +
                'called without answer arg ',
            () => {
                questionCheck()(dispatch, getState);
                expect(processError).toBeCalled();
                expect(processError.mock.calls[0][0]).toBe('question');
                expect(processError.mock.calls[0][1]).toBe('answer.missingvalue');
            }
        );

        it('should setFetchingStatus', () => {
            questionCheck('test')(dispatch, getState);
            expect(setFetchingStatus).toBeCalled();
            expect(setFetchingStatus.mock.calls[0][0]).toEqual(true);
        });

        it('should dispatch checkStatus with "confirmed" arg if response ok', () => {
            questionCheck('test')(dispatch, getState);
            expect(checkStatus).toBeCalled();
            expect(checkStatus).toBeCalledWith('confirmed');
        });

        it('should dispatch setModalStatus with true arg if response ok', () => {
            questionCheck('test')(dispatch, getState);
            expect(setModalStatus).toBeCalled();
            expect(setModalStatus.mock.calls[0][0]).toEqual(true);
        });
    });

    describe('api request succeed, captcha incorrect', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.done = (fn) => {
                        fn({status: 'ok', correct: false});
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

        it('should dispatch processError with captcha error in args', () => {
            questionCheck('test')(dispatch, getState);
            expect(processError).toBeCalled();
            expect(processError).toBeCalledWith('captcha', 'captcha.not_matched');
        });
    });

    describe('api request failed', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.done = () => {
                        return this;
                    };
                    this.fail = (fn) => {
                        fn({status: 'error', code: 'answer.not_matched'});
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

        it('should dispatch reloadCaptcha', () => {
            questionCheck('test')(dispatch, getState);
            expect(reloadCaptcha).toBeCalled();
        });

        it('should dispatch processError', () => {
            questionCheck('test')(dispatch, getState);
            expect(processError).toBeCalled();
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
            questionCheck('test')(dispatch, getState);
            expect(setFetchingStatus).toBeCalled();
            expect(setFetchingStatus.mock.calls[1][0]).toBe(false);
        });
    });
});
