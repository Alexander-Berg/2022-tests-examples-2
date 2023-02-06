jest.mock('../../api', () => ({
    request: jest.fn()
}));
import api from '../../api';
import mockData from './__mocks__/data';
import validateHint from '../methods/validateHint';
import updateFieldStatus from '../methods/updateFieldStatus';
import findFieldsWithErrors from '../methods/findFieldsWithErrors';
import checkIfFieldEmpty from '../methods/checkIfFieldEmpty';

jest.mock('../methods/checkIfFieldEmpty');
jest.mock('../methods/findFieldsWithErrors');
jest.mock('../methods/updateFieldStatus');
jest.mock('../actions');

describe('validateHint', () => {
    it('should check if field empty', () => {
        checkIfFieldEmpty.mockImplementation(() => () => true);
        validateHint({hint_answer: ''}, 'answer')(mockData.props.dispatch, mockData.getState);
        expect(checkIfFieldEmpty).toBeCalled();
    });
    it('should return if field empty', () => {
        checkIfFieldEmpty.mockImplementation(() => () => true);
        const result = validateHint({hint_answer: ''}, 'answer')(mockData.props.dispatch, mockData.getState);

        expect(result).toBeUndefined();
    });

    describe('validate, api response succeed', () => {
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
                };

                return new FakeP();
            });
            updateFieldStatus.mockImplementation(() => () => ({field: 'answer'}));
            findFieldsWithErrors.mockImplementation(() => () => jest.fn());
            checkIfFieldEmpty.mockImplementation(() => () => false);
        });
        afterEach(function() {
            api.request.mockClear();
        });

        it('should call updateFieldStatus if field value is valid', () => {
            validateHint({hint_answer: 'testanswer'}, 'answer')(mockData.props.dispatch, mockData.getState);
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('hint_answer', 'valid');
        });
    });
    describe('validate, api response succeed, field value is invalid', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function(fn) {
                        const response = {
                            validation_errors: [
                                {
                                    field: 'hint_answer',
                                    code: 'toolong'
                                }
                            ]
                        };

                        fn(response);
                        return this;
                    };
                    this.fail = function() {
                        return this;
                    };
                };

                return new FakeP();
            });
            updateFieldStatus.mockImplementation(() => () => ({field: 'answer'}));
            findFieldsWithErrors.mockImplementation(() => () => jest.fn());
            checkIfFieldEmpty.mockImplementation(() => () => false);
        });
        afterEach(function() {
            api.request.mockClear();
        });

        it('should call updateFieldStatus if field value invalid', () => {
            validateHint({hint_answer: 'testanswer'}, 'answer')(mockData.props.dispatch, mockData.getState);
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('hint_answer', 'not_valid');
        });
    });
    describe('validate, api response failed', () => {
        beforeEach(function() {
            api.request.mockImplementation(function() {
                const FakeP = function() {
                    this.then = function() {
                        return this;
                    };
                    this.fail = function(fn) {
                        fn();
                        return this;
                    };
                };

                return new FakeP();
            });
            updateFieldStatus.mockImplementation(() => () => ({field: 'answer'}));
            findFieldsWithErrors.mockImplementation(() => () => jest.fn());
            checkIfFieldEmpty.mockImplementation(() => () => false);
        });
        afterEach(function() {
            api.request.mockClear();
        });

        it('should call updateFieldStatus', () => {
            validateHint({hint_answer: 'testanswer'}, 'answer')(mockData.props.dispatch, mockData.getState);
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('hint_answer', 'not_valid');
        });
    });
});
