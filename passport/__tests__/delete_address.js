import {
    clearEditState,
    deleteAddressAction,
    setAddressesErrors,
    setAddressesSavingProgressState,
    editAddressLine
} from '../';

jest.mock('../', () => ({
    clearEditState: jest.fn(),
    deleteAddressAction: jest.fn(),
    setAddressesErrors: jest.fn(),
    setAddressesSavingProgressState: jest.fn(),
    editAddressLine: jest.fn()
}));

import {deleteAddress} from '../delete_address';

jest.mock('../../../../api', () => ({
    request: jest.fn()
}));

import * as api from '../../../../api';

describe('Action: deleteAddress', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({status: 'ok'});
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
            editAddressLine.mockClear();
            setAddressesSavingProgressState.mockClear();
        });

        it('should call delete address api', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                },
                addresses: {}
            }));
            const addressId = 'home';
            const isDelivery = false;

            deleteAddress(addressId, isDelivery)(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(4);
            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith(
                'delete.addresses',
                {id: addressId, csrf: 'token'},
                {abortPrevious: true}
            );
            expect(setAddressesSavingProgressState.mock.calls.length).toBe(2);
            expect(deleteAddressAction).toBeCalled();
            expect(deleteAddressAction).toBeCalledWith(addressId, isDelivery);
            expect(clearEditState).toBeCalled();
            expect(clearEditState).toBeCalledWith(addressId);
        });

        it('should call delete address api and clear default delivery address', () => {
            const dispatch = jest.fn();
            const defaultDelivery = {editedAddressLine: 'address'};
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                },
                addresses: {
                    delivery: [{id: 1}],
                    defaultDelivery
                }
            }));
            const addressId = 'delivery';
            const isDelivery = true;

            deleteAddress(addressId, isDelivery)(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(5);
            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith(
                'delete.addresses',
                {id: addressId, csrf: 'token'},
                {abortPrevious: true}
            );
            expect(setAddressesSavingProgressState.mock.calls.length).toBe(2);
            expect(deleteAddressAction).toBeCalled();
            expect(deleteAddressAction).toBeCalledWith(addressId, isDelivery);
            expect(editAddressLine).toBeCalled();
            expect(editAddressLine).toBeCalledWith('', defaultDelivery);
            expect(clearEditState).toBeCalled();
            expect(clearEditState).toBeCalledWith(addressId);
        });
    });

    describe('success case with fail response', () => {
        beforeEach(() => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({status: 'fail'});
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
            editAddressLine.mockClear();
            setAddressesSavingProgressState.mockClear();
        });

        it('should call delete address api with fail status', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                },
                addresses: {}
            }));
            const addressId = 'home';
            const isDelivery = false;

            deleteAddress(addressId, isDelivery)(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
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
                        fn(['error.1', 'error.2']);
                        return this;
                    };
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
            editAddressLine.mockClear();
            setAddressesSavingProgressState.mockClear();
        });

        it('should call delete address api', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                },
                addresses: {}
            }));
            const addressId = 'home';
            const isDelivery = false;

            deleteAddress(addressId, isDelivery)(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(setAddressesSavingProgressState).toBeCalled();
            expect(setAddressesSavingProgressState).toBeCalledWith(false);
            expect(setAddressesErrors).toBeCalled();
            expect(setAddressesErrors).toBeCalledWith(['error.1', 'error.2']);
        });
    });
});
