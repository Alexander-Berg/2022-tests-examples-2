jest.mock('../../api', () => ({
    request: jest.fn()
}));
import api from '../../api';
import validatePasswordConfirm from '../methods/validatePasswordConfirm';
import updateFieldStatus from '../methods/updateFieldStatus';
import checkIfFieldEmpty from '../methods/checkIfFieldEmpty';
import findFieldsWithErrors from '../methods/findFieldsWithErrors';
import submitPhoneConfirmationCode from '../methods/submitPhoneConfirmationCode';
import validatePassword from '../methods/validatePassword';
import mockData from './__mocks__/data';

jest.mock('../methods/updateFieldStatus');
jest.mock('../methods/findFieldsWithErrors');
jest.mock('../methods/validatePasswordConfirm');
jest.mock('../methods/checkIfFieldEmpty');
jest.mock('../methods/submitPhoneConfirmationCode');

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
            password: 'passtest',
            password_confirm: 'passtestconfirm'
        },
        states: {
            name: 'valid',
            lastname: 'valid',
            email: 'valid'
        },
        errors: {
            active: 'firstname',
            phone: {
                code: ''
            }
        }
    }
});

describe('validatePassword', () => {
    updateFieldStatus.mockImplementation(() => () => ({field: 'password'}));
    findFieldsWithErrors.mockImplementation(() => () => jest.fn());
    validatePasswordConfirm.mockImplementation(() => () => jest.fn());
    submitPhoneConfirmationCode.mockImplementation(() => () => jest.fn());
    checkIfFieldEmpty.mockImplementation(() => () => false);

    describe('response is ok, no errors', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function(fn) {
                        fn({status: 'ok'});
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
            updateFieldStatus.mockClear();
        });

        it('should dispatch validatePasswordConfirm if password_confirm is defined', () => {
            validatePassword('testpass')(mockData.props.dispatch, getState);
            expect(validatePasswordConfirm).toBeCalled();
        });
        it('should call checkIfFieldEmpty', () => {
            validatePassword('testpass')(mockData.props.dispatch, getState);
            expect(checkIfFieldEmpty).toBeCalled();
        });
        it('should return if password is undefined', () => {
            const result = validatePassword()(mockData.props.dispatch, getState);

            expect(result).toBeUndefined();
        });
        it('should call updateFieldStatus if phone error', () => {
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
                        password: 'passtest',
                        password_confirm: 'passtestconfirm'
                    },
                    states: {
                        name: 'valid',
                        lastname: 'valid',
                        email: 'valid'
                    },
                    errors: {
                        active: 'firstname',
                        phone: {
                            code: 'likephonenumber'
                        }
                    }
                }
            });

            validatePassword('testpass')(mockData.props.dispatch, getState);
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('phone', 'valid');
        });
        it('should dispatch submitPhoneConfirmationCode if activeField argument equals phone', () => {
            validatePassword('testpass', 'phone')(mockData.props.dispatch, getState);
            expect(submitPhoneConfirmationCode).toBeCalled();
        });
        it('should call updateFieldStatus', () => {
            validatePassword('testpass')(mockData.props.dispatch, getState);
            expect(updateFieldStatus).toBeCalled();
        });
        it('should dispatch findFieldsWithErrors', () => {
            validatePassword('testpass')(mockData.props.dispatch, getState);
            expect(findFieldsWithErrors).toBeCalled();
        });
    });
    describe('api response error', () => {
        beforeEach(function() {
            const response = {
                validation_errors: [
                    {
                        field: 'password',
                        code: 'weak'
                    }
                ]
            };

            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function(fn) {
                        fn(response);
                        return this;
                    };
                };

                return new FakeP();
            });
        });
        afterEach(function() {
            api.request.mockClear();
            updateFieldStatus.mockClear();
        });
        it('should call updateFieldStatus', () => {
            validatePassword('testpass', 'login')(mockData.props.dispatch, getState);
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('password', 'not_valid');
        });
    });
});
