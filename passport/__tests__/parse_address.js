import {deleteEditAddressErrors, setGeoLocationUpdateState} from '../';
import {checkRequiredFields} from '../check_required_fields';
import {saveAddressesFromGeoCoder} from '../save_addresses_from_geo_coder';
import {getLocationByGeoCode} from '../get_location_by_geo_code';
import {getLocale} from '../../../../common';

jest.mock('../', () => ({
    deleteEditAddressErrors: jest.fn(),
    setGeoLocationUpdateState: jest.fn()
}));
jest.mock('../check_required_fields', () => ({
    checkRequiredFields: jest.fn(() => () => {})
}));
jest.mock('../save_addresses_from_geo_coder', () => ({
    saveAddressesFromGeoCoder: jest.fn(() => () => {})
}));
jest.mock('../get_location_by_geo_code');
jest.mock('../../../../common', () => ({
    getLocale: jest.fn(() => 'ru')
}));

import {parseAddress} from '../parse_address';

describe('Action: parseAddress', () => {
    afterEach(() => {
        deleteEditAddressErrors.mockClear();
        setGeoLocationUpdateState.mockClear();
        checkRequiredFields.mockClear();
        saveAddressesFromGeoCoder.mockClear();
        getLocationByGeoCode.mockClear();
        getLocale.mockClear();
    });

    it('should not get location by geocode', () => {
        const dispatch = jest.fn();
        const getState = jest.fn(() => ({
            common: {
                csrf: 'token'
            }
        }));

        parseAddress({})(dispatch, getState);

        expect(dispatch.mock.calls.length).toBe(0);
    });

    it('should get location by geocode', () => {
        const dispatch = jest.fn();
        const getState = jest.fn(() => ({
            common: {
                csrf: 'token'
            }
        }));
        const addressLine = 'address line';

        getLocationByGeoCode.mockImplementation(() => {
            return {
                done: jest.fn(() => {
                    return {
                        fail: jest.fn()
                    };
                })
            };
        });

        parseAddress({addressLine})(dispatch, getState);

        expect(getLocationByGeoCode).toBeCalled();
        expect(getLocationByGeoCode).toBeCalledWith(addressLine, 'ru', true, 'token');
    });

    it('should get location by geocode with empty settings', () => {
        const dispatch = jest.fn();
        const getState = jest.fn(() => ({}));
        const addressLine = 'address line';

        getLocationByGeoCode.mockImplementation(() => {
            return {
                done: jest.fn(() => {
                    return {
                        fail: jest.fn()
                    };
                })
            };
        });

        parseAddress({addressLine})(dispatch, getState);

        expect(getLocationByGeoCode).toBeCalled();
    });

    it('should get location by geocode and dispatch 2 actions', () => {
        const dispatch = jest.fn();
        const getState = jest.fn(() => ({
            common: {
                csrf: 'token'
            }
        }));
        const address = {id: 'home', addressLine: 'address line'};

        getLocationByGeoCode.mockImplementation(() => {
            return {
                done: jest.fn((successFn) => {
                    successFn({});
                    return {
                        fail: jest.fn()
                    };
                })
            };
        });

        parseAddress(address)(dispatch, getState);

        expect(dispatch.mock.calls.length).toBe(2);
        expect(deleteEditAddressErrors).toBeCalled();
        expect(deleteEditAddressErrors).toBeCalledWith(address.id);
        expect(checkRequiredFields).toBeCalled();
        expect(saveAddressesFromGeoCoder).toBeCalled();
    });

    it('should get location by geocode and handle with new address', () => {
        const dispatch = jest.fn();
        const getState = jest.fn(() => ({
            common: {
                csrf: 'token'
            }
        }));
        const address = {id: 'home', addressLine: 'address line'};

        getLocationByGeoCode.mockImplementation(() => {
            return {
                done: jest.fn((successFn) => {
                    successFn({id: 'work', addressLine: 'work address'});
                    return {
                        fail: jest.fn()
                    };
                })
            };
        });

        parseAddress(address)(dispatch, getState);

        expect(dispatch.mock.calls.length).toBe(2);
        expect(deleteEditAddressErrors).toBeCalled();
        expect(deleteEditAddressErrors).toBeCalledWith(address.id);
        expect(checkRequiredFields).toBeCalled();
        expect(saveAddressesFromGeoCoder).toBeCalled();
    });

    it('should get location by geocode and handle with new address', () => {
        const dispatch = jest.fn();
        const getState = jest.fn(() => ({
            common: {
                csrf: 'token'
            }
        }));
        const address = {id: 'home', addressLine: 'address line'};

        getLocationByGeoCode.mockImplementation(() => {
            return {
                done: jest.fn((successFn) => {
                    successFn({id: 'work', addressLine: 'work address'});
                    return {
                        fail: jest.fn((failFn) => {
                            failFn();
                        })
                    };
                })
            };
        });

        parseAddress(address)(dispatch, getState);

        expect(dispatch.mock.calls.length).toBe(3);
        expect(setGeoLocationUpdateState.mock.calls.length).toBe(2);
    });
});
