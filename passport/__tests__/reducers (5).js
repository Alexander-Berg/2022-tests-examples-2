import reducer from '../reducers';
import {
    CLEAR_ADDRESSES_STATE,
    CLEAR_EDIT_STATE,
    DEFAULT_DELIVERY_ADDRESS_ID,
    DELETE_ADDRESS,
    DELETE_EDIT_ADDRESS_ERRORS,
    EDIT_ADDRESS_FLAT,
    EDIT_ADDRESS_LINE,
    EDIT_MODE_ADDRESSES,
    SET_ADD_DELIVERY_ADDRESS_MODE,
    SET_ADDRESS,
    SET_ADDRESSES,
    SET_ADDRESSES_CONTEXT,
    SET_ADDRESSES_EDIT_MODE,
    SET_ADDRESSES_ERRORS,
    SET_ADDRESSES_PROGRESS_STATE,
    SET_ADDRESSES_SAVING_PROGRESS_STATE,
    SET_ADDRESSES_SUGGEST,
    SET_ADDRESSES_UPDATE_STATE,
    SET_EDIT_ADDRESS_ERRORS,
    SET_EDIT_STATE,
    SET_GEO_LOCATION,
    SET_GEO_LOCATION_STATUS,
    SET_GEO_LOCATION_UPDATE_STATE
} from '../actions';

const defaultState = {
    delivery: [],
    home: {
        id: 'home',
        editedAddressLine: ''
    },
    work: {
        id: 'work',
        editedAddressLine: ''
    },
    defaultDelivery: {
        id: 'delivery',
        editedAddressLine: '',
        editedAddressFlat: ''
    },
    progress: false,
    savingProgress: false,
    mode: EDIT_MODE_ADDRESSES,
    suggest: [],
    context: '',
    editedFields: {},
    errors: [],
    isUpdated: false,
    addDeliveryAddress: false,
    isGeoLocationAvailable: false,
    geoLocation: {},
    geoLocationUpdateState: {
        progress: false,
        id: null
    },
    editErrors: {}
};

describe('Reducer: addresses', () => {
    it('should return default state', () => {
        expect(reducer()).toEqual(defaultState);
    });

    it('should return previous state', () => {
        const state = {test: '123'};

        expect(reducer(state)).toEqual(state);
    });

    it('should handle SET_ADDRESSES action', () => {
        const addresses = {home: {id: 'home'}};

        expect(reducer({}, {type: SET_ADDRESSES, addresses})).toEqual(addresses);
    });

    it('should handle SET_ADDRESSES_PROGRESS_STATE action', () => {
        const state = {progress: false};
        const progress = true;

        const updatedState = reducer(state, {type: SET_ADDRESSES_PROGRESS_STATE, progress});

        expect(updatedState.progress).toBe(progress);
    });

    it('should handle SET_ADDRESSES_EDIT_MODE action', () => {
        const state = {mode: ''};

        const updatedState = reducer(state, {type: SET_ADDRESSES_EDIT_MODE, mode: EDIT_MODE_ADDRESSES});

        expect(updatedState.mode).toBe(EDIT_MODE_ADDRESSES);
    });

    it('should handle SET_ADDRESSES_SUGGEST action', () => {
        const state = {mode: ''};
        const suggest = ['address.1', 'address.2'];

        const updatedState = reducer(state, {type: SET_ADDRESSES_SUGGEST, suggest});

        expect(updatedState.suggest).toBe(suggest);
    });

    it('should handle SET_ADDRESSES_CONTEXT action', () => {
        const state = {context: ''};
        const context = 'addressId';

        const updatedState = reducer(state, {type: SET_ADDRESSES_CONTEXT, context});

        expect(updatedState.context).toBe(context);
    });

    it('should handle SET_EDIT_STATE action', () => {
        const state = {editedFields: {flat: false}};

        const updatedState = reducer(state, {type: SET_EDIT_STATE, id: 'flat'});

        expect(updatedState.editedFields.flat).toBe(true);
    });

    it('should handle CLEAR_EDIT_STATE action', () => {
        const state = {editedFields: {flat: false, addressLine: true}};

        const updatedState = reducer(state, {type: CLEAR_EDIT_STATE, id: 'flat'});

        expect(updatedState.editedFields).toEqual({addressLine: true});
        expect(updatedState.editedFields.flat).toBe(undefined);
    });

    it('should handle CLEAR_EDIT_STATE action without field id', () => {
        const state = {editedFields: {flat: false, addressLine: true}};

        const updatedState = reducer(state, {type: CLEAR_EDIT_STATE});

        expect(updatedState.editedFields).toEqual({});
        expect(updatedState.editedFields.flat).toBe(undefined);
    });

    it('should handle SET_ADDRESS action', () => {
        const addressId = 'home';
        const address = {id: addressId, flat: '123', addressLine: '322'};

        const updatedState = reducer({editErrors: {}}, {type: SET_ADDRESS, address});

        expect(updatedState[addressId]).toEqual(address);
    });

    it('should handle SET_ADDRESS action with empty address', () => {
        const addressId = 'home';
        const state = {home: {id: addressId, flat: '123', addressLine: '322'}, delivery: []};

        const updatedState = reducer(state, {type: SET_ADDRESS});

        expect(updatedState).toEqual(state);
    });

    it('should handle SET_ADDRESS action for delivery address', () => {
        const address = {id: 'test', flat: '123', addressLine: '322'};

        const updatedState = reducer({editErrors: {}}, {type: SET_ADDRESS, address, isDeliveryAddress: true});

        expect(updatedState.delivery).toEqual([address]);
    });

    it('should handle SET_ADDRESS action for existed delivery address', () => {
        const state = {delivery: [{id: 'test'}], editErrors: {}};
        const address = {id: 'test', flat: '123', addressLine: '322'};

        const updatedState = reducer(state, {type: SET_ADDRESS, address, isDeliveryAddress: true});

        expect(updatedState.delivery).toEqual([address]);
    });

    it('should handle SET_ADDRESSES_ERRORS action', () => {
        const errors = ['error.1', 'error.2'];

        const updatedState = reducer({}, {type: SET_ADDRESSES_ERRORS, errors});

        expect(updatedState.errors).toBe(errors);
    });

    it('should handle SET_ADDRESSES_UPDATE_STATE action', () => {
        const state = {isUpdated: false};
        const updatedState = reducer(state, {type: SET_ADDRESSES_UPDATE_STATE, state: true});

        expect(updatedState.isUpdated).toBe(true);
    });

    it('should handle SET_ADDRESSES_SAVING_PROGRESS_STATE action', () => {
        const state = {savingProgress: false};
        const updatedState = reducer(state, {type: SET_ADDRESSES_SAVING_PROGRESS_STATE, progress: true});

        expect(updatedState.savingProgress).toBe(true);
    });

    it('should handle SET_ADD_DELIVERY_ADDRESS_MODE action', () => {
        const state = {mode: false};
        const updatedState = reducer(state, {type: SET_ADD_DELIVERY_ADDRESS_MODE, mode: true});

        expect(updatedState.addDeliveryAddress).toBe(true);
    });

    it('should handle DELETE_ADDRESS action', () => {
        const state = {home: {id: 'home', flat: 'flat number', addressLine: 'address line'}};
        const updatedState = reducer(state, {type: DELETE_ADDRESS, id: 'home'});

        expect(updatedState).toEqual({home: defaultState.home});
    });

    it('should handle DELETE_ADDRESS action with delete errors', () => {
        const state = {
            home: {id: 'home', flat: 'flat number', addressLine: 'address line'},
            editErrors: {
                home: ['error.1', 'error.2']
            }
        };
        const updatedState = reducer(state, {type: DELETE_ADDRESS, id: 'home'});

        expect(updatedState.editErrors).toEqual({});
    });

    it('should handle DELETE_ADDRESS action for delivery address', () => {
        const deliveryAddress1 = {id: 'delivery1', flat: 'flat number', addressLine: 'address line'};
        const deliveryAddress2 = {id: 'delivery2', flat: 'flat number', addressLine: 'address line'};
        const state = {
            delivery: [deliveryAddress1, deliveryAddress2]
        };
        const updatedState = reducer(state, {type: DELETE_ADDRESS, id: deliveryAddress1.id, isDeliveryAddress: true});

        expect(updatedState.delivery).toEqual([deliveryAddress2]);
    });

    it('should handle DELETE_ADDRESS action for not existed delivery address', () => {
        const deliveryAddress1 = {id: 'delivery1', flat: 'flat number', addressLine: 'address line'};
        const deliveryAddress2 = {id: 'delivery2', flat: 'flat number', addressLine: 'address line'};
        const state = {
            delivery: [deliveryAddress1, deliveryAddress2]
        };
        const updatedState = reducer(state, {type: DELETE_ADDRESS, id: 'delivery3', isDeliveryAddress: true});

        expect(updatedState.delivery).toEqual(state.delivery);
    });

    it('should handle SET_GEO_LOCATION_STATUS action', () => {
        const state = {isGeoLocationAvailable: false};
        const updatedState = reducer(state, {type: SET_GEO_LOCATION_STATUS, isAvailable: true});

        expect(updatedState.isGeoLocationAvailable).toBe(true);
    });

    it('should handle SET_GEO_LOCATION action', () => {
        const state = {geoLocation: {}};
        const geoLocation = {latitude: '123', longitude: '321'};
        const updatedState = reducer(state, {type: SET_GEO_LOCATION, geolocation: geoLocation});

        expect(updatedState.geoLocation).toEqual(geoLocation);
    });

    it('should handle SET_GEO_LOCATION_UPDATE_STATE action', () => {
        const state = {geoLocationUpdateState: {}};
        const geoLocationUpdateState = {id: 'home', progress: true};
        const action = {
            type: SET_GEO_LOCATION_UPDATE_STATE,
            id: geoLocationUpdateState.id,
            progress: geoLocationUpdateState.progress
        };
        const updatedState = reducer(state, action);

        expect(updatedState.geoLocationUpdateState).toEqual(geoLocationUpdateState);
    });

    it('should handle CLEAR_ADDRESSES_STATE action', () => {
        const state = {
            delivery: [],
            home: {
                id: 'home'
            },
            work: {
                id: 'work'
            },
            progress: true,
            savingProgress: true,
            mode: EDIT_MODE_ADDRESSES,
            suggest: [],
            context: '',
            editedFields: {},
            errors: [],
            isUpdated: true,
            addDeliveryAddress: true,
            isGeoLocationAvailable: false,
            geoLocation: {},
            geoLocationUpdateState: {
                progress: true,
                id: null
            },
            editErrors: {}
        };
        const updatedState = reducer(state, {type: CLEAR_ADDRESSES_STATE});

        expect(updatedState.progress).toBe(defaultState.progress);
        expect(updatedState.savingProgress).toBe(defaultState.savingProgress);
        expect(updatedState.isUpdated).toBe(defaultState.isUpdated);
        expect(updatedState.addDeliveryAddress).toBe(defaultState.addDeliveryAddress);
        expect(updatedState.geoLocationUpdateState.progress).toBe(defaultState.geoLocationUpdateState.progress);
    });

    it('should handle SET_EDIT_ADDRESS_ERRORS action', () => {
        const errors = ['error.1', 'error.2'];
        const addressId = 'home';

        const updatedState = reducer({}, {type: SET_EDIT_ADDRESS_ERRORS, id: addressId, errors});

        expect(updatedState.editErrors[addressId]).toBe(errors);
    });

    it('should handle SET_EDIT_ADDRESS_ERRORS action for delivery address', () => {
        const errors = ['error.1', 'error.2'];
        const addressId = 'delivery';
        const state = {delivery: [{id: addressId}]};

        const updatedState = reducer(state, {type: SET_EDIT_ADDRESS_ERRORS, id: addressId, errors});

        expect(updatedState.editErrors[addressId]).toBe(errors);
    });

    it('should handle SET_EDIT_ADDRESS_ERRORS action for undefined delivery address', () => {
        const errors = ['error.1', 'error.2'];
        const addressId = 'delivery';
        const state = {delivery: []};

        const updatedState = reducer(state, {type: SET_EDIT_ADDRESS_ERRORS, id: addressId, errors});

        expect(updatedState.editErrors[addressId]).toBe(errors);
    });

    it('should handle DELETE_EDIT_ADDRESS_ERRORS action', () => {
        const errors = ['error.1', 'error.2'];
        const addressId = 'home';
        const state = {editErrors: {home: errors}};

        const updatedState = reducer(state, {type: DELETE_EDIT_ADDRESS_ERRORS, id: addressId});

        expect(updatedState.editErrors).toEqual({});
    });

    it('should handle EDIT_ADDRESS_FLAT action', () => {
        const address = {id: 'home', editedAddressFlat: ''};
        const state = {home: address};
        const editedAddressFlat = 'flat';

        const updatedState = reducer(state, {type: EDIT_ADDRESS_FLAT, editedAddressFlat, address});

        expect(updatedState.home.editedAddressFlat).toEqual(editedAddressFlat);
    });

    it('should handle EDIT_ADDRESS_FLAT action for delivery address', () => {
        const address = {id: 'delivery', editedAddressFlat: ''};
        const state = {delivery: [address]};
        const editedAddressFlat = 'flat';

        const updatedState = reducer(state, {type: EDIT_ADDRESS_FLAT, editedAddressFlat, address});

        expect(updatedState.delivery[0].editedAddressFlat).toEqual(editedAddressFlat);
    });

    it('should handle EDIT_ADDRESS_FLAT action for new delivery address', () => {
        const address = {id: 'delivery', editedAddressFlat: ''};
        const state = {delivery: []};
        const editedAddressFlat = 'flat';

        const updatedState = reducer(state, {type: EDIT_ADDRESS_FLAT, editedAddressFlat, address});

        expect(updatedState.delivery[0].editedAddressFlat).toEqual(editedAddressFlat);
    });

    it('should handle EDIT_ADDRESS_FLAT action for new delivery address without address data', () => {
        const state = {delivery: []};
        const editedAddressFlat = 'flat';

        const updatedState = reducer(state, {type: EDIT_ADDRESS_FLAT, editedAddressFlat});

        expect(updatedState.delivery[0].editedAddressFlat).toEqual(editedAddressFlat);
    });

    it('should handle EDIT_ADDRESS_LINE action', () => {
        const address = {id: 'home', editedAddressLine: '', isValid: true};
        const state = {home: address};
        const editedAddressLine = 'address';

        const updatedState = reducer(state, {type: EDIT_ADDRESS_LINE, editedAddressLine, address});

        expect(updatedState.home.editedAddressLine).toEqual(editedAddressLine);
        expect(updatedState.home.isValid).toEqual(false);
    });

    it('should handle EDIT_ADDRESS_LINE action for delivery address', () => {
        const address = {id: 'delivery', editedAddressLine: '', isValid: true};
        const state = {delivery: [address]};
        const editedAddressLine = 'address';

        const updatedState = reducer(state, {type: EDIT_ADDRESS_LINE, editedAddressLine, address});

        expect(updatedState.delivery[0].editedAddressLine).toEqual(editedAddressLine);
        expect(updatedState.delivery[0].isValid).toEqual(false);
    });

    it('should handle EDIT_ADDRESS_LINE action for new delivery address', () => {
        const address = {id: 'delivery', editedAddressLine: '', isValid: true};
        const state = {delivery: []};
        const editedAddressLine = 'address';

        const updatedState = reducer(state, {type: EDIT_ADDRESS_LINE, editedAddressLine, address});

        expect(updatedState.delivery[0].editedAddressLine).toEqual(editedAddressLine);
        expect(updatedState.delivery[0].isValid).toEqual(false);
    });

    it('should handle EDIT_ADDRESS_LINE action for new delivery address without address data', () => {
        const state = {delivery: []};
        const editedAddressLine = 'address';

        const updatedState = reducer(state, {type: EDIT_ADDRESS_LINE, editedAddressLine});

        expect(updatedState.delivery[0].editedAddressLine).toEqual(editedAddressLine);
        expect(updatedState.delivery[0].isValid).toEqual(false);
    });

    it('should handle EDIT_ADDRESS_LINE action for default delivery address', () => {
        const address = {id: DEFAULT_DELIVERY_ADDRESS_ID, editedAddressLine: '', isValid: true};
        const state = {[DEFAULT_DELIVERY_ADDRESS_ID]: address};
        const editedAddressLine = 'address';

        const updatedState = reducer(state, {type: EDIT_ADDRESS_LINE, editedAddressLine, address});

        expect(updatedState[DEFAULT_DELIVERY_ADDRESS_ID].editedAddressLine).toEqual(editedAddressLine);
        expect(updatedState[DEFAULT_DELIVERY_ADDRESS_ID].isValid).toEqual(false);
    });
});
