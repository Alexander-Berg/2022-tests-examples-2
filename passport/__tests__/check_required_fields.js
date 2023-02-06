import {checkRequiredFields} from '../check_required_fields';

import {deleteEditAddressErrors, setEditAddressErrors} from '../';
jest.mock('../', () => ({
    deleteEditAddressErrors: jest.fn(),
    setEditAddressErrors: jest.fn()
}));

describe('Action: checkRequiredFields', () => {
    it('should delete field errors and create new with default address', () => {
        const dispatch = jest.fn();
        const addressId = 'home';

        checkRequiredFields(undefined, addressId)(dispatch);

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(2);
        expect(deleteEditAddressErrors).toBeCalled();
        expect(deleteEditAddressErrors).toBeCalledWith(addressId);
    });

    it('should delete field errors and does not create new', () => {
        const dispatch = jest.fn();
        const addressId = 'home';
        const address = {id: addressId, country: 'country', city: 'city', building: 'building'};

        checkRequiredFields(address, addressId)(dispatch);

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(1);
    });

    it('should delete field errors and create new error for country', () => {
        const dispatch = jest.fn();
        const addressId = 'home';
        const address = {id: addressId, city: 'city', building: 'building'};

        checkRequiredFields(address, addressId)(dispatch);

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(2);
        expect(setEditAddressErrors).toBeCalled();
        expect(setEditAddressErrors).toBeCalledWith(addressId, ['empty.country']);
    });

    it('should delete field errors and create new error for building', () => {
        const dispatch = jest.fn();
        const addressId = 'home';
        const address = {id: addressId, city: 'city', country: 'country'};

        checkRequiredFields(address, addressId)(dispatch);

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(2);
        expect(setEditAddressErrors).toBeCalled();
        expect(setEditAddressErrors).toBeCalledWith(addressId, ['incorrect-address']);
    });
});
