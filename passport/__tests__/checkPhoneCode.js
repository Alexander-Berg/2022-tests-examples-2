jest.mock('../../api', () => ({
    request: jest.fn()
}));
import * as api from '../../api';
import checkPhoneCode from '../methods/checkPhoneCode';
import updateFieldStatus from '../methods/updateFieldStatus';
import {updateHumanConfirmationStatus, updateConfirmationFetchingStatus} from '@blocks/actions/form';

jest.mock('@blocks/actions/form', () => ({
    updateHumanConfirmationStatus: jest.fn(),
    updateConfirmationFetchingStatus: jest.fn()
}));

jest.mock('../methods/updateFieldStatus');

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
        },
        isPhoneCallConfirmationAvailable: false,
        validation: {
            phoneConfirmationType: 'sms'
        }
    }
});

describe('checkPhoneCode', () => {
    describe('request succed', () => {
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
            updateFieldStatus.mockImplementation(() => () => ({field: 'phoneCode'}));
        });
        afterEach(function() {
            api.request.mockClear();
        });

        it('should dispatch updateFieldStatus', () => {
            checkPhoneCode('1234')(props.dispatch, getState);
            expect(updateFieldStatus).toBeCalled();
        });
        it('should dispatch updateHumanConfirmationStatus', () => {
            checkPhoneCode('1234')(props.dispatch, getState);
            expect(updateHumanConfirmationStatus).toBeCalled();
        });
    });
    describe('request failed', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function() {
                        return this;
                    };
                    this.fail = function(fn) {
                        fn({status: 'error', errors: ['code.invalid']});
                        return this;
                    };
                    this.always = function() {
                        return this;
                    };
                };

                return new FakeP();
            });
            updateFieldStatus.mockImplementation(() => () => ({field: 'phoneCode'}));
        });
        afterEach(function() {
            api.request.mockClear();
        });

        it('should dispatch updateFieldStatus', () => {
            checkPhoneCode('1234')(props.dispatch, getState);
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('phoneCode', 'not_valid');
        });
    });
    describe('request always', () => {
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
                        fn({status: 'done'});
                        return this;
                    };
                };

                return new FakeP();
            });
            updateFieldStatus.mockImplementation(() => () => ({field: 'phoneCode'}));
        });
        afterEach(function() {
            api.request.mockClear();
        });

        it('should dispatch updateConfirmationFetchingStatus', () => {
            checkPhoneCode('1234')(props.dispatch, getState);
            expect(updateConfirmationFetchingStatus).toBeCalled();
            expect(updateConfirmationFetchingStatus).toBeCalledWith({isFetching: false});
        });
    });
});
