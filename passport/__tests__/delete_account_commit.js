jest.mock('../../../api', () => ({
    request: jest.fn()
}));
import api from '../../../api';
import {setFetchingStatus, setModalStatus} from '../../actions';
import {saveActionForRepeat} from '../../../common/actions';
import processError from '../../helpers/process_error';
import deleteAccountCommit from '../delete_account_commit';

jest.mock('../../actions', () => ({
    setModalStatus: jest.fn(),
    setFetchingStatus: jest.fn()
}));
jest.mock('../../../common/actions', () => ({
    saveActionForRepeat: jest.fn()
}));
jest.mock('../../helpers/process_error');

const {location} = window;

const getState = () => ({
    common: {
        csrf: '12345',
        track_id: '1234',
        retpath: ''
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

describe('deleteAccountCommit', () => {
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
            setFetchingStatus.mockClear();
            window.location = location;
        });

        it('should dispatch setFetchingStatus with true arg before request is done', () => {
            deleteAccountCommit()(dispatch, getState);
            expect(setFetchingStatus).toBeCalled();
            expect(setFetchingStatus.mock.calls[0][0]).toEqual(true);
        });

        it('should dispatch saveActionForRepeat', () => {
            deleteAccountCommit()(dispatch, getState);
            expect(saveActionForRepeat).toBeCalled();
        });

        it('should dispatch setFetchingStatus with false arg after request is done', () => {
            deleteAccountCommit()(dispatch, getState);
            expect(setFetchingStatus).toBeCalled();
            expect(setFetchingStatus.mock.calls[1][0]).toEqual(false);
        });

        it('should redirect to finish path after the commit', () => {
            deleteAccountCommit()(dispatch, getState);
            expect(window.location.href).toEqual('/auth/finish?track_id=1234&retpath=');
        });
    });

    describe('api request succeed with error', () => {
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
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
        });

        it('should dispatch processError with captcha error in args', () => {
            deleteAccountCommit()(dispatch, getState);
            expect(processError).toBeCalled();
            expect(processError).toBeCalledWith('captcha', 'captcha.not_matched');
        });

        it('should dispatch setModalStatus with false arg', () => {
            deleteAccountCommit()(dispatch, getState);
            expect(setModalStatus).toBeCalled();
            expect(setModalStatus).toBeCalledWith(false);
        });
    });

    describe('api request failed with some error', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.done = () => {
                        return this;
                    };
                    this.fail = (fn) => {
                        fn({status: 'error', errors: ['account.disabled']});
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
        });

        it('should dispatch processError with error code', () => {
            deleteAccountCommit()(dispatch, getState);
            expect(processError).toBeCalled();
            expect(processError).toBeCalledWith('phone', 'account.disabled');
        });
    });
});
