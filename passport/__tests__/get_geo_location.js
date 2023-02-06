import {getLocale} from '../../../../common';
import {checkRequiredFields} from '../check_required_fields';
import {getLocationByGeoCode} from '../get_location_by_geo_code';
import {
    DEFAULT_DELIVERY_ADDRESS_ID,
    setEditAddressErrors,
    setGeoLocationUpdateState,
    createAddressId,
    setGeoLocation
} from '../';

jest.mock('../../../../common', () => ({
    getLocale: jest.fn()
}));
jest.mock('../save_addresses_from_geo_coder', () => ({
    saveAddressesFromGeoCoder: jest.fn(() => () => {})
}));
jest.mock('../check_required_fields', () => ({
    checkRequiredFields: jest.fn(() => () => {})
}));
jest.mock('../get_location_by_geo_code');
jest.mock('../', () => ({
    NOT_FOUND: -1,
    setEditAddressErrors: jest.fn(),
    setGeoLocationUpdateState: jest.fn(),
    createAddressId: jest.fn(() => 'address.id'),
    setGeoLocation: jest.fn()
}));

import {getGeoLocation} from '../get_geo_location';

describe('Action: getGeoLocation', () => {
    describe('success cases', () => {
        beforeEach(() => {
            getLocationByGeoCode.mockImplementation(() => ({
                done: jest.fn((doneFn) => {
                    doneFn({
                        body: {
                            id: 'home',
                            flat: 'flat',
                            addressLine: 'address line'
                        }
                    });
                    return {
                        fail: jest.fn((failFn) => {
                            failFn({
                                errors: ['error.1', 'error.2', 'geocoder.empty']
                            });
                        })
                    };
                })
            }));
        });

        afterEach(() => {
            setGeoLocationUpdateState.mockClear();
            getLocationByGeoCode.mockClear();
            setEditAddressErrors.mockClear();
            checkRequiredFields.mockClear();
            getLocale.mockClear();
            setGeoLocation.mockClear();
        });

        it('should get geolocation', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                }
            }));
            const addressId = 'home';

            window.navigator.geolocation = {
                getCurrentPosition: jest.fn()
            };

            getGeoLocation(addressId)(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(1);
            expect(setGeoLocationUpdateState).toBeCalled();
            expect(setGeoLocationUpdateState).toBeCalledWith(true, addressId);
            expect(window.navigator.geolocation.getCurrentPosition).toBeCalled();
        });

        it('should get geolocation with default state', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({}));
            const addressId = 'home';

            window.navigator.geolocation = {
                getCurrentPosition: jest.fn()
            };

            getGeoLocation(addressId)(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(1);
            expect(setGeoLocationUpdateState).toBeCalled();
            expect(setGeoLocationUpdateState).toBeCalledWith(true, addressId);
            expect(window.navigator.geolocation.getCurrentPosition).toBeCalled();
        });

        it('should get geolocation for delivery address', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                }
            }));
            const addressId = DEFAULT_DELIVERY_ADDRESS_ID;

            window.navigator.geolocation.getCurrentPosition.mockClear();
            window.navigator.geolocation = {
                getCurrentPosition: jest.fn()
            };

            getGeoLocation(addressId)(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(1);
            expect(createAddressId).toBeCalled();
            expect(window.navigator.geolocation.getCurrentPosition).toBeCalled();
        });

        it('should not get geolocation', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                },
                addresses: {
                    isGeoLocationAvailable: false
                }
            }));
            const addressId = DEFAULT_DELIVERY_ADDRESS_ID;

            window.navigator.geolocation = null;

            getGeoLocation(addressId)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(0);
        });

        it('should get geolocation with success callback and same coords', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                },
                addresses: {
                    geoLocation: {
                        latitude: '123',
                        longitude: '321'
                    }
                }
            }));
            const addressId = DEFAULT_DELIVERY_ADDRESS_ID;

            window.navigator.geolocation = {
                getCurrentPosition: jest.fn((successFn) => {
                    const position = {
                        coords: {
                            latitude: '123',
                            longitude: '321'
                        }
                    };

                    successFn(position);
                })
            };

            getGeoLocation(addressId)(dispatch, getState);

            expect(getLocationByGeoCode.mock.calls[0][0]).toEqual('321,123');
        });

        it('should get geolocation with success for delivery address', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                },
                addresses: {
                    geoLocation: {
                        latitude: '123',
                        longitude: '321'
                    }
                }
            }));
            const addressId = DEFAULT_DELIVERY_ADDRESS_ID;

            window.navigator.geolocation = {
                getCurrentPosition: jest.fn((successFn) => {
                    const position = {
                        coords: {
                            latitude: '321',
                            longitude: '123'
                        }
                    };

                    successFn(position);
                })
            };

            getGeoLocation(addressId, true)(dispatch, getState);

            expect(getLocale).toBeCalled();
            expect(checkRequiredFields).toBeCalled();
        });

        it('should get geolocation with and set errors after call geo code', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                },
                addresses: {
                    geoLocation: {
                        latitude: '123',
                        longitude: '321'
                    }
                }
            }));
            const addressId = DEFAULT_DELIVERY_ADDRESS_ID;

            window.navigator.geolocation = {
                getCurrentPosition: jest.fn((successFn) => {
                    const position = {
                        coords: {
                            latitude: '321',
                            longitude: '123'
                        }
                    };

                    successFn(position);
                })
            };

            getGeoLocation(addressId, true)(dispatch, getState);

            expect(setEditAddressErrors).toBeCalled();
        });

        it('should get geolocation with fail', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                },
                addresses: {
                    geoLocation: {
                        latitude: '123',
                        longitude: '321'
                    }
                }
            }));
            const addressId = DEFAULT_DELIVERY_ADDRESS_ID;

            window.navigator.geolocation = {
                getCurrentPosition: jest.fn((successFn, failFn) => {
                    failFn();
                })
            };

            getGeoLocation(addressId)(dispatch, getState);

            expect(setGeoLocationUpdateState.mock.calls.length).toBe(2);
            expect(setGeoLocationUpdateState.mock.calls[1][0]).toBe(false);
        });

        it('should get geolocation with fail', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                },
                addresses: {
                    geoLocation: {
                        latitude: '123',
                        longitude: '321'
                    }
                }
            }));
            const addressId = DEFAULT_DELIVERY_ADDRESS_ID;

            window.navigator.geolocation = {
                getCurrentPosition: jest.fn((successFn) => {
                    const position = {
                        coords: {
                            latitude: '321',
                            longitude: '123'
                        }
                    };

                    successFn(position);
                })
            };

            getGeoLocation(addressId)(dispatch, getState);

            expect(setGeoLocation).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(4);
        });
    });

    describe('fail cases', () => {
        afterEach(() => {
            setGeoLocationUpdateState.mockClear();
            getLocationByGeoCode.mockClear();
            setEditAddressErrors.mockClear();
            checkRequiredFields.mockClear();
            getLocale.mockClear();
            setGeoLocation.mockClear();
            window.navigator.geolocation.getCurrentPosition.mockClear();
        });

        it('should get geolocation with errors', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                },
                addresses: {
                    geoLocation: {
                        latitude: '123',
                        longitude: '321'
                    }
                }
            }));
            const addressId = DEFAULT_DELIVERY_ADDRESS_ID;

            getLocationByGeoCode.mockClear();
            getLocationByGeoCode.mockImplementation(() => ({
                done: jest.fn((doneFn) => {
                    doneFn({
                        body: {
                            id: 'home',
                            flat: 'flat',
                            addressLine: 'address line'
                        }
                    });
                    return {
                        fail: jest.fn((failFn) => {
                            failFn({});
                        })
                    };
                })
            }));

            window.navigator.geolocation.getCurrentPosition.mockClear();
            window.navigator.geolocation = {
                getCurrentPosition: jest.fn((successFn) => {
                    const position = {
                        coords: {
                            latitude: '321',
                            longitude: '123'
                        }
                    };

                    successFn(position);
                })
            };

            getGeoLocation(addressId)(dispatch, getState);

            expect(setGeoLocationUpdateState.mock.calls.length).toBe(2);
            expect(setEditAddressErrors.mock.calls.length).toBe(0);
        });

        it('should get geolocation with empty response', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'token'
                },
                addresses: {
                    geoLocation: {
                        latitude: '123',
                        longitude: '321'
                    }
                }
            }));
            const addressId = DEFAULT_DELIVERY_ADDRESS_ID;

            getLocationByGeoCode.mockClear();
            getLocationByGeoCode.mockImplementation(() => ({
                done: jest.fn((doneFn) => {
                    doneFn({});
                    return {
                        fail: jest.fn((failFn) => {
                            failFn({});
                        })
                    };
                })
            }));

            window.navigator.geolocation.getCurrentPosition.mockClear();
            window.navigator.geolocation = {
                getCurrentPosition: jest.fn((successFn) => {
                    const position = {
                        coords: {
                            latitude: '321',
                            longitude: '123'
                        }
                    };

                    successFn(position);
                })
            };

            getGeoLocation(addressId, true)(dispatch, getState);

            expect(checkRequiredFields.mock.calls[0][0]).toEqual({});
        });
    });
});
