jest.mock('../../../../api', () => ({
    request: jest.fn()
}));

import api from '../../../../api';
import {setAddresses, setAddressesProgressState} from '../';

jest.mock('../', () => ({
    setAddresses: jest.fn(),
    setAddressesProgressState: jest.fn()
}));

import {getAddresses} from '../get_addresses';

const address = {id: 'home', flat: 'flat', addressLine: 'address line'};

describe('Action: getAddresses', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn(address);
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
        });

        it('should call get address api', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                }
            }));

            getAddresses()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('get.addresses', {csrf: 'token'});
            expect(setAddressesProgressState.mock.calls.length).toBe(2);
            expect(setAddresses).toBeCalled();
            expect(setAddresses).toBeCalledWith(address);
        });
    });

    describe('fail cases', () => {
        beforeEach(() => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({status: 'fail'});
                        return this;
                    };
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
        });

        it('should call get address api', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                }
            }));

            getAddresses()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('get.addresses', {csrf: 'token'});
            expect(setAddressesProgressState.mock.calls.length).toBe(4);
        });
    });
});
