import {setAddressHelper} from '../set_address_helper';
import {setAddDeliveryAddressMode, setEditState, setGeoLocationUpdateState} from '../';

jest.mock('../set_address_helper', () => ({
    setAddressHelper: jest.fn(() => () => {})
}));
jest.mock('../', () => ({
    setAddDeliveryAddressMode: jest.fn(),
    setEditState: jest.fn(),
    setGeoLocationUpdateState: jest.fn()
}));

import {saveAddressesFromGeoCoder} from '../save_addresses_from_geo_coder';

const dispatch = jest.fn();

describe('Action: saveAddressesFromGeoCoder', () => {
    afterEach(() => {
        dispatch.mockClear();
        setAddressHelper.mockClear();
        setAddDeliveryAddressMode.mockClear();
        setEditState.mockClear();
        setGeoLocationUpdateState.mockClear();
    });

    it('should save home/work address', () => {
        const addressId = 'home';
        const address = {flat: 'flat', addressLine: 'address line'};

        saveAddressesFromGeoCoder(address, addressId, false)(dispatch);

        expect(dispatch.mock.calls.length).toBe(3);
        expect(setAddressHelper).toBeCalled();
        expect(setAddressHelper).toBeCalledWith({id: addressId, flat: 'flat', addressLine: 'address line'}, false);
        expect(setEditState).toBeCalled();
        expect(setEditState).toBeCalledWith(addressId);
        expect(setGeoLocationUpdateState).toBeCalled();
        expect(setGeoLocationUpdateState).toBeCalledWith(false, null);
    });

    it('should save delivery address', () => {
        const addressId = 'home';
        const address = {flat: 'flat', addressLine: 'address line'};

        saveAddressesFromGeoCoder(address, addressId, true)(dispatch);

        expect(dispatch.mock.calls.length).toBe(4);
        expect(setAddressHelper).toBeCalled();
        expect(setAddressHelper).toBeCalledWith({id: addressId, flat: 'flat', addressLine: 'address line'}, true);
        expect(setEditState).toBeCalled();
        expect(setEditState).toBeCalledWith(addressId);
        expect(setGeoLocationUpdateState).toBeCalled();
        expect(setGeoLocationUpdateState).toBeCalledWith(false, null);
        expect(setAddDeliveryAddressMode).toBeCalled();
        expect(setAddDeliveryAddressMode).toBeCalledWith(false);
    });
});
