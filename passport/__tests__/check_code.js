jest.mock('../../../api', () => ({
    request: jest.fn()
}));
import api from '../../../api';
import {setModalStatus, setFetchingStatus, checkStatus} from '../../actions';
import processError from '../../helpers/process_error';
import checkCode from '../check_code';

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
            method: 'phone',
            status: 'unconfirmed'
        },
        form: {
            code: '123',
            answer: '',
            captcha: ''
        }
    }
});
const dispatch = jest.fn();

describe('checkCode', () => {
    describe('api request succeed', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.done = (fn) => {
                        fn({status: 'ok'});
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
        });

        it('should setFetchingStatus', () => {
            checkCode('123', 'phone')(dispatch, getState);
            expect(setFetchingStatus).toBeCalled();
            expect(setFetchingStatus.mock.calls[0][0]).toEqual(true);
        });

        it('should dispatch setModalStatus if response ok', () => {
            checkCode('123', 'phone')(dispatch, getState);
            expect(setModalStatus).toBeCalled();
        });

        it('should dispatch checkStatus', () => {
            checkCode('123', 'phone')(dispatch, getState);
            expect(checkStatus).toBeCalled();
            expect(checkStatus).toBeCalledWith('code_checked');
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
                        fn({status: 'error', code: 'code.invalid'});
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
        });

        it('should dispatch processError if response error', () => {
            checkCode('123', 'phone')(dispatch, getState);
            expect(processError).toBeCalled();
            expect(processError).toBeCalledWith('code', 'code.invalid');
        });
    });

    describe('api request always', () => {
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
        });

        it('should setFetchingStatus', () => {
            checkCode('123', 'phone')(dispatch, getState);
            expect(setFetchingStatus).toBeCalled();
            expect(setFetchingStatus.mock.calls[1][0]).toEqual(false);
        });
    });
});
