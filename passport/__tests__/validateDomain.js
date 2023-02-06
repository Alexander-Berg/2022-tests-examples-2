jest.mock('../../api', () => ({
    request: jest.fn()
}));
import api from '../../api';
import {updateErrorsValid} from '@blocks/actions/form';
import updateFieldStatus from '../methods/updateFieldStatus';
import checkIfFieldEmpty from '../methods/checkIfFieldEmpty';
import mockData from './__mocks__/data';
import validateConnectDomain from '../methods/validateDomain';
import validateConnectLogin from '../methods/validateConnectLogin';
import findFieldsWithErrors from '../methods/findFieldsWithErrors';

jest.mock('@blocks/actions/form', () => ({
    updateErrorsValid: jest.fn()
}));

jest.mock('../methods/updateFieldStatus');
jest.mock('../methods/checkIfFieldEmpty');
jest.mock('../methods/validateConnectLogin');
jest.mock('../methods/findFieldsWithErrors');

describe('validateConnectDomain', () => {
    const domain = 'example.domain';

    it('should dispatch updateFieldStatus if domain contains dot', () => {
        updateFieldStatus.mockImplementation(() => () => ({field: 'domain'}));

        validateConnectDomain(domain)(mockData.props.dispatch, mockData.getState);
        expect(updateFieldStatus).toBeCalled();
        expect(updateFieldStatus).toBeCalledWith('domain', 'not_valid');
    });

    it('should return and show missingValue error if domain not set', () => {
        checkIfFieldEmpty.mockImplementation(() => () => true);
        const result = validateConnectDomain('')(mockData.props.dispatch, mockData.getState);

        expect(result).toBeUndefined();
    });

    describe('api request succeded', () => {
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
                };

                return new FakeP();
            });
            updateFieldStatus.mockImplementation(() => () => ({field: 'domain'}));
            checkIfFieldEmpty.mockImplementation(() => () => false);
        });
        afterEach(function() {
            api.request.mockClear();
        });

        it('should dispatch validateConnectLogin', () => {
            validateConnectLogin.mockImplementation(() => () => {
                'ok';
            });
            validateConnectDomain('example')(mockData.props.dispatch, mockData.getState);
            expect(validateConnectLogin).toBeCalled();
        });

        it('should call updateFieldStatus', () => {
            validateConnectDomain('example')(mockData.props.dispatch, mockData.getState);
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('domain', 'valid');
        });

        it('should dispatch findFieldsWithErrors', () => {
            findFieldsWithErrors.mockImplementation(() => () => jest.fn());
            validateConnectDomain('example')(mockData.props.dispatch, mockData.getState);
            expect(findFieldsWithErrors).toBeCalled();
        });

        it('should dispatch updateErrorsValid if active error = domain', () => {
            const getState = () => ({
                common: {
                    csrf: '12345',
                    track_id: '1234'
                },
                form: {
                    values: {
                        name: 'test',
                        lastname: 'example',
                        login: '',
                        password: ''
                    },
                    errors: {
                        active: 'domain'
                    }
                }
            });

            validateConnectDomain('example')(mockData.props.dispatch, getState);
            expect(updateErrorsValid).toBeCalled();
        });
    });
    describe('api request failed', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function() {
                        return this;
                    };
                    this.fail = function(fn) {
                        fn({errors: ['domain.invalid']});
                        return this;
                    };
                };

                return new FakeP();
            });
            updateFieldStatus.mockImplementation(() => () => ({field: 'domain'}));
            checkIfFieldEmpty.mockImplementation(() => () => false);
        });
        afterEach(function() {
            api.request.mockClear();
        });
        it('should call updateFieldStatus ', () => {
            validateConnectDomain('example')(mockData.props.dispatch, mockData.getState);
            expect(updateFieldStatus).toBeCalled();
        });
    });
});
