import {setEditMode} from '../../../../common/actions';
import {getAddresses} from '../get_addresses';
import {
    clearAddressesState,
    setAddressesSavingProgressState,
    setAddressesErrors,
    clearEditState,
    setAddressesUpdateState
} from '../';
import api from '../../../../api';

import {saveAddresses} from '../save_addresses';

jest.mock('../../../../common/actions', () => ({
    setEditMode: jest.fn()
}));
jest.mock('../get_addresses', () => ({
    getAddresses: jest.fn(() => () => {})
}));
jest.mock('../', () => ({
    NOT_FOUND: -1,
    clearAddressesState: jest.fn(),
    setAddressesSavingProgressState: jest.fn(),
    setAddressesErrors: jest.fn(),
    clearEditState: jest.fn(),
    setAddressesUpdateState: jest.fn()
}));
jest.mock('../../../../api');

const dispatch = jest.fn();

describe('Action: saveAddresses', () => {
    afterEach(() => {
        dispatch.mockClear();
        setEditMode.mockClear();
        getAddresses.mockClear();
        clearAddressesState.mockClear();
        setAddressesSavingProgressState.mockClear();
        setAddressesErrors.mockClear();
        clearEditState.mockClear();
        setAddressesUpdateState.mockClear();
        api.request.mockClear();
    });

    it('should call save.addresses with empty settings', () => {
        const getState = jest.fn(() => ({}));
        const requestParams = {addresses: JSON.stringify([]), csrf: undefined};

        api.request.mockImplementation(() => {
            return {
                done: jest.fn(() => {
                    return {
                        fail: jest.fn(() => ({
                            always: jest.fn()
                        }))
                    };
                })
            };
        });

        saveAddresses()(dispatch, getState);

        expect(dispatch.mock.calls.length).toBe(1);
        expect(setAddressesSavingProgressState).toBeCalled();
        expect(setAddressesSavingProgressState).toBeCalledWith(true);
        expect(api.request).toBeCalled();
        expect(api.request).toBeCalledWith('save.addresses', requestParams, {abortPrevious: true});
    });

    it('should call save.addresses', () => {
        const homeAddress = {id: 'home', addressLine: 'home address'};
        const workAddress = {id: 'work', addressLine: 'work address'};
        const deliveryAddress = {id: 'delivery.1', addressLine: 'delivery address'};
        const requestParams = {addresses: JSON.stringify([homeAddress, workAddress, deliveryAddress]), csrf: undefined};
        const getState = jest.fn(() => ({
            addresses: {
                home: homeAddress,
                work: workAddress,
                delivery: [deliveryAddress],
                editedFields: {
                    home: {},
                    work: {},
                    'delivery.1': {}
                }
            }
        }));

        api.request.mockImplementation(() => {
            return {
                done: jest.fn(() => {
                    return {
                        fail: jest.fn(() => ({
                            always: jest.fn()
                        }))
                    };
                })
            };
        });

        saveAddresses()(dispatch, getState);

        expect(dispatch.mock.calls.length).toBe(1);
        expect(setAddressesSavingProgressState).toBeCalled();
        expect(setAddressesSavingProgressState).toBeCalledWith(true);
        expect(api.request).toBeCalled();
        expect(api.request).toBeCalledWith('save.addresses', requestParams, {abortPrevious: true});
    });

    it('should call save.addresses with empty response', () => {
        const getState = jest.fn(() => ({}));

        api.request.mockImplementation(() => {
            return {
                done: jest.fn((doneFn) => {
                    doneFn({});

                    return {
                        fail: jest.fn(() => ({
                            always: jest.fn()
                        }))
                    };
                })
            };
        });

        saveAddresses()(dispatch, getState);

        expect(dispatch.mock.calls.length).toBe(2);
        expect(setAddressesSavingProgressState.mock.calls.length).toBe(2);
        expect(setAddressesSavingProgressState.mock.calls[0][0]).toBe(true);
        expect(setAddressesSavingProgressState.mock.calls[1][0]).toBe(false);
    });

    it('should call save.addresses with success response', () => {
        const getState = jest.fn(() => ({}));

        api.request.mockImplementation(() => {
            return {
                done: jest.fn((doneFn) => {
                    doneFn({status: 'ok'});

                    return {
                        fail: jest.fn(() => ({
                            always: jest.fn()
                        }))
                    };
                })
            };
        });

        saveAddresses()(dispatch, getState);

        expect(dispatch.mock.calls.length).toBe(6);
        expect(setAddressesUpdateState).toBeCalled();
        expect(setAddressesUpdateState).toBeCalledWith(true);
        expect(clearEditState).toBeCalled();
        expect(setEditMode).toBeCalled();
        expect(setEditMode).toBeCalledWith('');
        expect(clearAddressesState).toBeCalled();
    });

    it('should call save.addresses with fail response', () => {
        const getState = jest.fn(() => ({}));

        api.request.mockImplementation(() => {
            return {
                done: jest.fn(() => {
                    return {
                        fail: jest.fn((failFn) => {
                            failFn({errors: ['error.1', 'error.2']});

                            return {always: jest.fn()};
                        })
                    };
                })
            };
        });

        saveAddresses()(dispatch, getState);

        expect(dispatch.mock.calls.length).toBe(3);
        expect(setAddressesSavingProgressState.mock.calls.length).toBe(2);
        expect(setAddressesSavingProgressState.mock.calls[0][0]).toBe(true);
        expect(setAddressesSavingProgressState.mock.calls[1][0]).toBe(false);
        expect(setAddressesErrors).toBeCalled();
        expect(setAddressesErrors).toBeCalledWith({errors: ['error.1', 'error.2']});
    });

    it('should call save.addresses and handle each response', () => {
        const getState = jest.fn(() => ({}));

        api.request.mockImplementation(() => {
            return {
                done: jest.fn(() => {
                    return {
                        fail: jest.fn(() => ({
                            always: jest.fn((alwaysFn) => {
                                alwaysFn();
                            })
                        }))
                    };
                })
            };
        });

        jest.useFakeTimers();
        saveAddresses()(dispatch, getState);

        expect(dispatch.mock.calls.length).toBe(1);

        jest.runAllTimers();

        expect(getAddresses).toBeCalled();
    });
});
