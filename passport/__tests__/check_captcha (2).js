jest.mock('@blocks/api', () => ({
    request: jest.fn()
}));
import api from '@blocks/api';
import reloadCaptcha from '@components/Captcha/actions/reloadCaptcha';
import {setModalStatus, setFetchingStatus} from '../../actions';
import processError from '../../helpers/process_error';
import checkCaptcha from '../check_captcha';

jest.mock('@components/Captcha/actions/reloadCaptcha');
jest.mock('../../actions', () => ({
    setModalStatus: jest.fn(),
    setFetchingStatus: jest.fn()
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

describe('checkCaptcha', () => {
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
            checkCaptcha()(dispatch, getState);
            expect(setFetchingStatus).toBeCalled();
            expect(setFetchingStatus.mock.calls[0][0]).toEqual(true);
        });

        it('should dispatch setModalStatus if response ok', () => {
            checkCaptcha()(dispatch, getState);
            expect(setModalStatus).toBeCalled();
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
                        fn({status: 'error', errors: ['captcha.missingvalue']});
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

        it('should dispatch reloadCaptcha if response error', () => {
            checkCaptcha()(dispatch, getState);
            expect(reloadCaptcha).toBeCalled();
        });

        it('should dispatch processError if response error', () => {
            checkCaptcha()(dispatch, getState);
            expect(processError).toBeCalled();
            expect(processError).toBeCalledWith('captcha', 'captcha.missingvalue');
        });
    });

    describe('api request failed with no error code', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.done = () => {
                        return this;
                    };
                    this.fail = (fn) => {
                        fn({status: 'error'});
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

        it('should dispatch processError with "captcha.not_matched" code', () => {
            checkCaptcha()(dispatch, getState);
            expect(processError).toBeCalled();
            expect(processError).toBeCalledWith('captcha', 'captcha.not_matched');
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
            checkCaptcha()(dispatch, getState);
            expect(setFetchingStatus).toBeCalled();
            expect(setFetchingStatus.mock.calls[1][0]).toEqual(false);
        });
    });
});
