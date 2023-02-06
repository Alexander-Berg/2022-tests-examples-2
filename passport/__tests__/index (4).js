import {
    SET_ADDRESSES,
    SET_ADDRESS,
    SET_ADDRESSES_EDIT_MODE,
    CLEAR_ADDRESSES_STATE,
    CLEAR_EDIT_STATE,
    DELETE_ADDRESS,
    DELETE_EDIT_ADDRESS_ERRORS,
    SET_ADD_DELIVERY_ADDRESS_MODE,
    SET_ADDRESSES_CONTEXT,
    SET_ADDRESSES_ERRORS,
    SET_ADDRESSES_PROGRESS_STATE,
    SET_ADDRESSES_SAVING_PROGRESS_STATE,
    SET_ADDRESSES_SUGGEST,
    SET_ADDRESSES_UPDATE_STATE,
    SET_EDIT_ADDRESS_ERRORS,
    SET_EDIT_STATE,
    SET_GEO_LOCATION,
    SET_GEO_LOCATION_STATUS,
    SET_GEO_LOCATION_UPDATE_STATE,
    EDIT_ADDRESS_FLAT,
    EDIT_ADDRESS_LINE,
    setAddresses,
    setAddress,
    setAddressesEditMode,
    setAddressesProgressState,
    setAddressesSavingProgressState,
    setAddressesSuggest,
    setAddressesContext,
    setEditState,
    clearEditState,
    setAddressesErrors,
    setAddressesUpdateState,
    setAddDeliveryAddressMode,
    deleteAddressAction,
    setGeoLocationStatus,
    setGeoLocation,
    setGeoLocationUpdateState,
    clearAddressesState,
    setEditAddressErrors,
    deleteEditAddressErrors,
    createAddressId,
    editAddressLine,
    editAddressFlat
} from '../';

describe('Addresses actions', () => {
    it('should return set addresses action', () => {
        const addresses = {home: {id: 'home'}};
        const result = setAddresses(addresses);

        expect(result).toEqual({
            type: SET_ADDRESSES,
            addresses
        });
    });

    it('should return set address action', () => {
        const address = {id: 'home'};
        const isDeliveryAddress = false;
        const result = setAddress(address, isDeliveryAddress);

        expect(result).toEqual({
            type: SET_ADDRESS,
            address,
            isDeliveryAddress
        });
    });

    it('should return set mode action', () => {
        const mode = 'mode';
        const result = setAddressesEditMode(mode);

        expect(result).toEqual({
            type: SET_ADDRESSES_EDIT_MODE,
            mode
        });
    });

    it('should return set address progress state action', () => {
        const progress = false;
        const result = setAddressesProgressState(progress);

        expect(result).toEqual({
            type: SET_ADDRESSES_PROGRESS_STATE,
            progress
        });
    });

    it('should return set addresses saving progress state action', () => {
        const progress = false;
        const result = setAddressesSavingProgressState(progress);

        expect(result).toEqual({
            type: SET_ADDRESSES_SAVING_PROGRESS_STATE,
            progress
        });
    });

    it('should return set addresses suggest action', () => {
        const suggest = ['suggest.1', 'suggest.2'];
        const result = setAddressesSuggest(suggest);

        expect(result).toEqual({
            type: SET_ADDRESSES_SUGGEST,
            suggest
        });
    });

    it('should return set addresses context action', () => {
        const context = 'context';
        const result = setAddressesContext(context);

        expect(result).toEqual({
            type: SET_ADDRESSES_CONTEXT,
            context
        });
    });

    it('should return set edit state action', () => {
        const id = 'home';
        const result = setEditState(id);

        expect(result).toEqual({
            type: SET_EDIT_STATE,
            id
        });
    });

    it('should return clear edit state action', () => {
        const id = 'home';
        const result = clearEditState(id);

        expect(result).toEqual({
            type: CLEAR_EDIT_STATE,
            id
        });
    });

    it('should return set addresses errors action', () => {
        const errors = ['error.1', 'error.2'];
        const result = setAddressesErrors(errors);

        expect(result).toEqual({
            type: SET_ADDRESSES_ERRORS,
            errors
        });
    });

    it('should return set addresses update state action', () => {
        const state = 'state';
        const result = setAddressesUpdateState(state);

        expect(result).toEqual({
            type: SET_ADDRESSES_UPDATE_STATE,
            state
        });
    });

    it('should return set add delivery address mode action', () => {
        const mode = 'mode';
        const result = setAddDeliveryAddressMode(mode);

        expect(result).toEqual({
            type: SET_ADD_DELIVERY_ADDRESS_MODE,
            mode
        });
    });

    it('should return delete address action', () => {
        const id = 'home';
        const isDeliveryAddress = true;
        const result = deleteAddressAction(id, isDeliveryAddress);

        expect(result).toEqual({
            type: DELETE_ADDRESS,
            id,
            isDeliveryAddress
        });
    });

    it('should return set geo location status action', () => {
        const isAvailable = true;
        const result = setGeoLocationStatus(isAvailable);

        expect(result).toEqual({
            type: SET_GEO_LOCATION_STATUS,
            isAvailable
        });
    });

    it('should return set geo location action', () => {
        const geolocation = 'geolocation';
        const result = setGeoLocation(geolocation);

        expect(result).toEqual({
            type: SET_GEO_LOCATION,
            geolocation
        });
    });

    it('should return set geo location update state action', () => {
        const progress = true;
        const id = 'home';
        const result = setGeoLocationUpdateState(progress, id);

        expect(result).toEqual({
            type: SET_GEO_LOCATION_UPDATE_STATE,
            progress,
            id
        });
    });

    it('should return clear addresses state action', () => {
        const result = clearAddressesState();

        expect(result).toEqual({
            type: CLEAR_ADDRESSES_STATE
        });
    });

    it('should return set edit address errors action', () => {
        const errors = ['error.1', 'error.2'];
        const id = 'home';
        const result = setEditAddressErrors(id, errors);

        expect(result).toEqual({
            type: SET_EDIT_ADDRESS_ERRORS,
            id,
            errors
        });
    });

    it('should return delete address errors action', () => {
        const id = 'home';
        const result = deleteEditAddressErrors(id);

        expect(result).toEqual({
            type: DELETE_EDIT_ADDRESS_ERRORS,
            id
        });
    });

    it('should return unique address id', () => {
        const addressId1 = createAddressId();
        const addressId2 = createAddressId();
        const addressId3 = createAddressId();
        const addressId4 = createAddressId();
        const addressId5 = createAddressId();

        expect(addressId1).not.toEqual(addressId2);
        expect(addressId2).not.toEqual(addressId3);
        expect(addressId3).not.toEqual(addressId4);
        expect(addressId4).not.toEqual(addressId5);
        expect(addressId5).not.toEqual(addressId1);
    });

    it('should return edit address line action', () => {
        const editedAddressLine = 'address';
        const address = {id: 'home'};
        const result = editAddressLine(editedAddressLine, address);

        expect(result).toEqual({
            type: EDIT_ADDRESS_LINE,
            editedAddressLine,
            address
        });
    });

    it('should return edit address flat action', () => {
        const editedAddressFlat = 'address';
        const address = {id: 'home'};
        const result = editAddressFlat(editedAddressFlat, address);

        expect(result).toEqual({
            type: EDIT_ADDRESS_FLAT,
            editedAddressFlat,
            address
        });
    });
});
