import ReactDOM from 'react-dom';
import {
    DEFAULT_DELIVERY_ADDRESS_ID,
    setAddDeliveryAddressMode,
    setAddressesContext,
    setAddressesSuggest,
    createAddressId,
    deleteEditAddressErrors,
    setEditState,
    editAddressFlat,
    editAddressLine,
    clearEditState
} from '../../../actions';
import {deleteAddress as deleteAddressAction} from '../../../actions/delete_address';
import {parseAddress} from '../../../actions/parse_address';
import {setAddressHelper} from '../../../actions/set_address_helper';
import {getSuggest as getSuggestAction} from '../../../actions/get_suggest';
import {getGeoLocation as getGeoLocationAction} from '../../../actions/get_geo_location';

jest.mock('react-dom');
jest.mock('../../../actions', () => ({
    NOT_FOUND: -1,
    setAddDeliveryAddressMode: jest.fn(),
    setAddressesContext: jest.fn(),
    setAddressesSuggest: jest.fn(),
    createAddressId: jest.fn(() => 'address.id'),
    deleteEditAddressErrors: jest.fn(),
    setEditState: jest.fn(),
    editAddressFlat: jest.fn(),
    editAddressLine: jest.fn(),
    clearEditState: jest.fn()
}));
jest.mock('../../../actions/delete_address', () => ({
    deleteAddress: jest.fn()
}));
jest.mock('../../../actions/parse_address', () => ({
    parseAddress: jest.fn()
}));
jest.mock('../../../actions/set_address_helper', () => ({
    setAddressHelper: jest.fn()
}));
jest.mock('../../../actions/get_suggest', () => ({
    getSuggest: jest.fn()
}));
jest.mock('../../../actions/get_geo_location', () => ({
    getGeoLocation: jest.fn()
}));

import {
    getSuggest,
    setContext,
    clearContext,
    getOptions,
    isDeliveryAddress,
    getSuggestValue,
    deleteAddress,
    updatedDeliveryAddress,
    getGeoLocation,
    onAddressLineChange
} from '../service';

const props = {
    dispatch: jest.fn()
};

describe('AddressesField component service', () => {
    describe('getSuggest', () => {
        beforeEach(() => {
            ReactDOM.findDOMNode.mockImplementation(() => {});
        });

        afterEach(() => {
            props.dispatch.mockClear();
            ReactDOM.findDOMNode.mockClear();
            setAddDeliveryAddressMode.mockClear();
            setAddressesContext.mockClear();
            setAddressesSuggest.mockClear();
            createAddressId.mockClear();
            deleteEditAddressErrors.mockClear();
            setEditState.mockClear();
            deleteAddressAction.mockClear();
            parseAddress.mockClear();
            setAddressHelper.mockClear();
            getSuggestAction.mockClear();
            getGeoLocationAction.mockClear();
            editAddressFlat.mockClear();
            editAddressLine.mockClear();
        });

        it('should dispatch get suggest action', () => {
            const state = {
                addressLine: 'address line'
            };

            getSuggest.call({props}, state.addressLine);

            expect(props.dispatch.mock.calls.length).toBe(1);
            expect(getSuggestAction).toBeCalled();
            expect(getSuggestAction).toBeCalledWith(state.addressLine);
        });
    });

    describe('setContext', () => {
        beforeEach(() => {
            ReactDOM.findDOMNode.mockImplementation(() => {});
        });

        afterEach(() => {
            props.dispatch.mockClear();
            ReactDOM.findDOMNode.mockClear();
            setAddDeliveryAddressMode.mockClear();
            setAddressesContext.mockClear();
            setAddressesSuggest.mockClear();
            createAddressId.mockClear();
            deleteEditAddressErrors.mockClear();
            setEditState.mockClear();
            deleteAddressAction.mockClear();
            parseAddress.mockClear();
            setAddressHelper.mockClear();
            getSuggestAction.mockClear();
            getGeoLocationAction.mockClear();
            editAddressFlat.mockClear();
            editAddressLine.mockClear();
        });

        it('should not dispatch actions', () => {
            const propsObject = Object.assign({}, props, {
                context: 'context',
                id: 'context'
            });

            setContext.call({props: propsObject});

            expect(props.dispatch.mock.calls.length).toBe(0);
        });

        it('should dispatch set context and suggest actions', () => {
            const propsObject = Object.assign({}, props, {
                context: 'context',
                id: 'id'
            });

            setContext.call({props: propsObject});

            expect(props.dispatch.mock.calls.length).toBe(2);
            expect(setAddressesSuggest).toBeCalled();
            expect(setAddressesSuggest).toBeCalledWith([]);
            expect(setAddressesContext).toBeCalled();
            expect(setAddressesContext).toBeCalledWith(propsObject.id);
        });
    });

    describe('clearContext', () => {
        beforeEach(() => {
            ReactDOM.findDOMNode.mockImplementation(() => {});
        });

        afterEach(() => {
            props.dispatch.mockClear();
            ReactDOM.findDOMNode.mockClear();
            setAddDeliveryAddressMode.mockClear();
            setAddressesContext.mockClear();
            setAddressesSuggest.mockClear();
            createAddressId.mockClear();
            deleteEditAddressErrors.mockClear();
            setEditState.mockClear();
            deleteAddressAction.mockClear();
            parseAddress.mockClear();
            setAddressHelper.mockClear();
            getSuggestAction.mockClear();
            getGeoLocationAction.mockClear();
            editAddressFlat.mockClear();
            editAddressLine.mockClear();
        });

        it('should dispatch set context and suggest actions', () => {
            jest.useFakeTimers();

            clearContext.call({props});

            jest.runAllTimers();

            expect(props.dispatch.mock.calls.length).toBe(2);
            expect(setAddressesSuggest).toBeCalled();
            expect(setAddressesSuggest).toBeCalledWith([]);
            expect(setAddressesContext).toBeCalled();
            expect(setAddressesContext).toBeCalledWith('');
        });
    });

    describe('getOptions', () => {
        beforeEach(() => {
            ReactDOM.findDOMNode.mockImplementation(() => {});
        });

        afterEach(() => {
            props.dispatch.mockClear();
            ReactDOM.findDOMNode.mockClear();
            setAddDeliveryAddressMode.mockClear();
            setAddressesContext.mockClear();
            setAddressesSuggest.mockClear();
            createAddressId.mockClear();
            deleteEditAddressErrors.mockClear();
            setEditState.mockClear();
            deleteAddressAction.mockClear();
            parseAddress.mockClear();
            setAddressHelper.mockClear();
            getSuggestAction.mockClear();
            getGeoLocationAction.mockClear();
            editAddressFlat.mockClear();
            editAddressLine.mockClear();
        });

        it('should return empty suggest options', () => {
            const options = getOptions.call({props});

            expect(options).toEqual([]);
        });

        it('should return suggest options', () => {
            const propsObject = Object.assign({}, props, {
                suggest: [
                    {
                        name: 'name',
                        desc: 'desc.1, desc.2',
                        lat: 'lat',
                        lon: 'lon'
                    }
                ]
            });
            const fullAddress = `desc.2, desc.1, ${propsObject.suggest[0].name}`;
            // eslint-disable-next-line max-len
            const optionValue = `${fullAddress}|${propsObject.suggest[0].name}|${propsObject.suggest[0].lat}|${propsObject.suggest[0].lon}`;

            const options = getOptions.call({props: propsObject});

            expect(options).toEqual([{content: fullAddress, value: optionValue}]);
        });

        it('should return suggest options without description', () => {
            const propsObject = Object.assign({}, props, {
                suggest: [
                    {
                        name: 'name',
                        lat: 'lat',
                        lon: 'lon'
                    }
                ]
            });
            const fullAddress = propsObject.suggest[0].name;
            // eslint-disable-next-line max-len
            const optionValue = `${fullAddress}|${propsObject.suggest[0].name}|${propsObject.suggest[0].lat}|${propsObject.suggest[0].lon}`;

            const options = getOptions.call({props: propsObject});

            expect(options).toEqual([{content: fullAddress, value: optionValue}]);
        });
    });

    describe('isDeliveryAddress', () => {
        beforeEach(() => {
            ReactDOM.findDOMNode.mockImplementation(() => {});
        });

        afterEach(() => {
            props.dispatch.mockClear();
            ReactDOM.findDOMNode.mockClear();
            setAddDeliveryAddressMode.mockClear();
            setAddressesContext.mockClear();
            setAddressesSuggest.mockClear();
            createAddressId.mockClear();
            deleteEditAddressErrors.mockClear();
            setEditState.mockClear();
            deleteAddressAction.mockClear();
            parseAddress.mockClear();
            setAddressHelper.mockClear();
            getSuggestAction.mockClear();
            getGeoLocationAction.mockClear();
            editAddressFlat.mockClear();
            editAddressLine.mockClear();
        });

        it('should return falsy for home address', () => {
            const propsObject = Object.assign({}, props, {
                id: 'home'
            });

            const result = isDeliveryAddress.call({props: propsObject});

            expect(result).toBe(false);
        });

        it('should return falsy for work address', () => {
            const propsObject = Object.assign({}, props, {
                id: 'work'
            });

            const result = isDeliveryAddress.call({props: propsObject});

            expect(result).toBe(false);
        });

        it('should return true for delivery address', () => {
            const propsObject = Object.assign({}, props, {
                id: 'delivery'
            });

            const result = isDeliveryAddress.call({props: propsObject});

            expect(result).toBe(true);
        });
    });

    describe('getSuggestValue', () => {
        const elementFocus = jest.fn();
        const elementClick = jest.fn();

        beforeEach(() => {
            ReactDOM.findDOMNode.mockImplementation(() => ({
                querySelector: jest.fn(() => {
                    return {
                        focus: elementFocus,
                        click: elementClick
                    };
                })
            }));
        });

        afterEach(() => {
            elementFocus.mockClear();
            elementClick.mockClear();
            props.dispatch.mockClear();
            ReactDOM.findDOMNode.mockClear();
            setAddDeliveryAddressMode.mockClear();
            setAddressesContext.mockClear();
            setAddressesSuggest.mockClear();
            createAddressId.mockClear();
            deleteEditAddressErrors.mockClear();
            setEditState.mockClear();
            deleteAddressAction.mockClear();
            parseAddress.mockClear();
            setAddressHelper.mockClear();
            getSuggestAction.mockClear();
            getGeoLocationAction.mockClear();
            editAddressFlat.mockClear();
            editAddressLine.mockClear();
        });

        it('should return value from suggest line', () => {
            const isDeliveryAddress = jest.fn(() => false);
            const propsObject = Object.assign({}, props, {
                id: 'home'
            });
            const payload = 'addressLine|addressLineShort|123|321';

            getSuggestValue.call({props: propsObject, isDeliveryAddress}, {target: {value: payload}});

            expect(setEditState).toBeCalled();
            expect(setEditState).toBeCalledWith(propsObject.id);
            expect(setAddressHelper).toBeCalled();
            expect(setAddressHelper).toBeCalledWith(
                {
                    id: 'home',
                    addressLine: 'addressLine',
                    addressLineShort: 'addressLineShort',
                    latitude: 123,
                    longitude: 321
                },
                false
            );
        });

        it('should return value from suggest line for delivery address', () => {
            const state = {flat: 'flat'};
            const isDeliveryAddress = jest.fn(() => true);
            const propsObject = Object.assign({}, props, {
                id: DEFAULT_DELIVERY_ADDRESS_ID,
                address: {
                    id: DEFAULT_DELIVERY_ADDRESS_ID
                }
            });
            const payload = 'addressLine|flat';

            getSuggestValue.call({props: propsObject, isDeliveryAddress, state}, {}, payload);

            expect(createAddressId).toBeCalled();
            expect(setAddDeliveryAddressMode).toBeCalled();
            expect(setAddDeliveryAddressMode).toBeCalledWith(false);
        });

        it('should return value from suggest line for delivery address and empty payload', () => {
            const state = {flat: 'flat'};
            const isDeliveryAddress = jest.fn(() => true);
            const propsObject = Object.assign({}, props, {
                id: DEFAULT_DELIVERY_ADDRESS_ID,
                address: {
                    id: DEFAULT_DELIVERY_ADDRESS_ID
                }
            });
            const payload = '';

            getSuggestValue.call({props: propsObject, isDeliveryAddress, state}, {}, payload);

            expect(createAddressId).toBeCalled();
            expect(setAddDeliveryAddressMode).toBeCalled();
            expect(setAddDeliveryAddressMode).toBeCalledWith(false);
        });
    });

    describe('deleteAddress', () => {
        beforeEach(() => {
            ReactDOM.findDOMNode.mockImplementation(() => {});
        });

        afterEach(() => {
            props.dispatch.mockClear();
            ReactDOM.findDOMNode.mockClear();
            setAddDeliveryAddressMode.mockClear();
            setAddressesContext.mockClear();
            setAddressesSuggest.mockClear();
            createAddressId.mockClear();
            deleteEditAddressErrors.mockClear();
            setEditState.mockClear();
            deleteAddressAction.mockClear();
            parseAddress.mockClear();
            setAddressHelper.mockClear();
            getSuggestAction.mockClear();
            getGeoLocationAction.mockClear();
            editAddressFlat.mockClear();
            editAddressLine.mockClear();
        });

        it('should change state and dispatch deleteAddress action', () => {
            const context = {
                props: Object.assign({}, props, {
                    id: 'home'
                }),
                isDeliveryAddress: jest.fn(() => true)
            };

            deleteAddress.call(context);

            expect(context.props.dispatch.mock.calls.length).toBe(1);
            expect(context.isDeliveryAddress).toBeCalled();
            expect(deleteAddressAction).toBeCalled();
            expect(deleteAddressAction).toBeCalledWith(context.props.id, true);
        });
    });

    describe('updatedDeliveryAddress', () => {
        beforeEach(() => {
            ReactDOM.findDOMNode.mockImplementation(() => {});
        });

        afterEach(() => {
            props.dispatch.mockClear();
            ReactDOM.findDOMNode.mockClear();
            setAddDeliveryAddressMode.mockClear();
            setAddressesContext.mockClear();
            setAddressesSuggest.mockClear();
            createAddressId.mockClear();
            deleteEditAddressErrors.mockClear();
            setEditState.mockClear();
            deleteAddressAction.mockClear();
            parseAddress.mockClear();
            setAddressHelper.mockClear();
            getSuggestAction.mockClear();
            getGeoLocationAction.mockClear();
            editAddressFlat.mockClear();
            editAddressLine.mockClear();
        });

        it('should change delivery address flat', () => {
            const context = {
                props: Object.assign({}, props, {
                    id: DEFAULT_DELIVERY_ADDRESS_ID,
                    address: {id: DEFAULT_DELIVERY_ADDRESS_ID, flat: 'flat', addressLine: 'address line'}
                })
            };
            const newFlat = 'new.flat';

            updatedDeliveryAddress.call(context, {target: {value: newFlat}});

            expect(editAddressFlat).toBeCalled();
            expect(editAddressFlat).toBeCalledWith(newFlat, context.props.address);
            expect(context.props.dispatch.mock.calls.length).toBe(1);
        });

        it('should change state for same flat', () => {
            const context = {
                props: Object.assign({}, props, {
                    id: 'delivery.1',
                    address: {id: 'delivery.1', flat: 'flat', addressLine: 'address line'}
                })
            };
            const newFlat = 'flat';

            updatedDeliveryAddress.call(context, {target: {value: newFlat}});

            expect(editAddressFlat).toBeCalled();
            expect(editAddressFlat).toBeCalledWith(newFlat, context.props.address);
            expect(context.props.dispatch.mock.calls.length).toBe(1);
        });

        it('should dispatch 2 actions', () => {
            const context = {
                props: Object.assign({}, props, {
                    id: 'delivery.1',
                    address: {id: 'delivery.1', flat: 'flat', addressLine: 'address line'}
                })
            };
            const newFlat = 'new.flat';
            const newAddress = Object.assign({}, context.props.address, {flat: newFlat, editedAddressFlat: newFlat});

            updatedDeliveryAddress.call(context, {target: {value: newFlat}});

            expect(editAddressFlat).toBeCalled();
            expect(editAddressFlat).toBeCalledWith(newFlat, context.props.address);
            expect(context.props.dispatch.mock.calls.length).toBe(3);
            expect(setAddressHelper).toBeCalled();
            expect(setAddressHelper).toBeCalledWith(newAddress, true);
            expect(setEditState).toBeCalled();
            expect(setEditState).toBeCalledWith(context.props.address.id);
        });

        it('should dispatch 2 actions for empty address', () => {
            const context = {
                props: Object.assign({}, props, {
                    id: 'delivery.1'
                })
            };
            const newFlat = 'new.flat';
            const newAddress = {flat: newFlat, editedAddressFlat: newFlat};

            updatedDeliveryAddress.call(context, {target: {value: newFlat}});

            expect(context.props.dispatch.mock.calls.length).toBe(3);
            expect(setAddressHelper).toBeCalled();
            expect(setAddressHelper).toBeCalledWith(newAddress, true);
            expect(setEditState).toBeCalled();
            expect(setEditState).toBeCalledWith(undefined);
        });
    });

    describe('getGeoLocation', () => {
        beforeEach(() => {
            ReactDOM.findDOMNode.mockImplementation(() => {});
        });

        afterEach(() => {
            props.dispatch.mockClear();
            ReactDOM.findDOMNode.mockClear();
            setAddDeliveryAddressMode.mockClear();
            setAddressesContext.mockClear();
            setAddressesSuggest.mockClear();
            createAddressId.mockClear();
            deleteEditAddressErrors.mockClear();
            setEditState.mockClear();
            deleteAddressAction.mockClear();
            parseAddress.mockClear();
            setAddressHelper.mockClear();
            getSuggestAction.mockClear();
            getGeoLocationAction.mockClear();
            editAddressFlat.mockClear();
            editAddressLine.mockClear();
        });

        it('should skip action dispatching', () => {
            const context = {
                props: Object.assign({}, props, {
                    id: 'home',
                    geoLocationUpdateState: {progress: true}
                }),
                isDeliveryAddress: jest.fn(() => true)
            };

            getGeoLocation.call(context);

            expect(context.props.dispatch.mock.calls.length).toBe(0);
        });

        it('should skip action dispatching', () => {
            const context = {
                props: Object.assign({}, props, {
                    id: 'home',
                    geoLocationUpdateState: {progress: false}
                }),
                isDeliveryAddress: jest.fn(() => true)
            };

            getGeoLocation.call(context);

            expect(context.props.dispatch.mock.calls.length).toBe(1);
            expect(getGeoLocationAction).toBeCalled();
            expect(getGeoLocationAction).toBeCalledWith(context.props.id, true);
            expect(context.isDeliveryAddress).toBeCalled();
        });
    });

    describe('onAddressLineChange', () => {
        beforeEach(() => {
            ReactDOM.findDOMNode.mockImplementation(() => {});
        });

        afterEach(() => {
            props.dispatch.mockClear();
            ReactDOM.findDOMNode.mockClear();
            setAddDeliveryAddressMode.mockClear();
            setAddressesContext.mockClear();
            setAddressesSuggest.mockClear();
            createAddressId.mockClear();
            deleteEditAddressErrors.mockClear();
            setEditState.mockClear();
            deleteAddressAction.mockClear();
            parseAddress.mockClear();
            setAddressHelper.mockClear();
            getSuggestAction.mockClear();
            getGeoLocationAction.mockClear();
            editAddressFlat.mockClear();
            editAddressLine.mockClear();
            clearEditState.mockClear();
        });

        it('should change state with callback', () => {
            const context = {
                setContext: jest.fn(),
                getSuggest: jest.fn(),
                props: Object.assign({}, props, {
                    id: 'home',
                    errors: ['geocoder.empty'],
                    address: {id: 'home'}
                })
            };
            const address = 'address';

            onAddressLineChange.call(context, {target: {value: address}});

            expect(context.props.dispatch.mock.calls.length).toBe(3);
            expect(editAddressLine).toBeCalled();
            expect(editAddressLine).toBeCalledWith(address, context.props.address);
            expect(clearEditState).toBeCalled();
            expect(clearEditState).toBeCalledWith(context.props.id);
            expect(deleteEditAddressErrors).toBeCalled();
            expect(deleteEditAddressErrors).toBeCalledWith(context.props.id);
            expect(context.setContext).toBeCalled();
            expect(context.getSuggest).toBeCalled();
        });

        it('should delete errors and change state with callback', () => {
            const context = {
                setContext: jest.fn(),
                getSuggest: jest.fn(),
                props: Object.assign({}, props, {
                    id: 'home',
                    errors: ['error.1'],
                    address: {id: 'home'}
                })
            };
            const address = 'address';

            onAddressLineChange.call(context, {target: {value: address}});

            expect(context.props.dispatch.mock.calls.length).toBe(2);
            expect(editAddressLine).toBeCalled();
            expect(editAddressLine).toBeCalledWith(address, context.props.address);
            expect(clearEditState).toBeCalled();
            expect(clearEditState).toBeCalledWith(context.props.id);
            expect(deleteEditAddressErrors.mock.calls.length).toBe(0);
            expect(context.setContext).toBeCalled();
            expect(context.getSuggest).toBeCalled();
        });

        it('should delete current address for empty address line with whitespaces', () => {
            const context = {
                setContext: jest.fn(),
                getSuggest: jest.fn(),
                props: Object.assign({}, props, {
                    id: 'home',
                    errors: ['error.1'],
                    address: {id: 'home', addressLine: 'address'}
                }),
                isDeliveryAddress: () => true
            };
            const address = '  ';

            onAddressLineChange.call(context, {target: {value: address}});

            expect(context.props.dispatch.mock.calls.length).toBe(3);
            expect(deleteAddressAction).toBeCalled();
            expect(deleteAddressAction).toBeCalledWith(context.props.id, true);
            expect(editAddressLine).toBeCalled();
            expect(editAddressLine).toBeCalledWith(address, context.props.address);
            expect(clearEditState).toBeCalled();
            expect(clearEditState).toBeCalledWith(context.props.id);
            expect(deleteEditAddressErrors.mock.calls.length).toBe(0);
            expect(context.setContext).toBeCalled();
            expect(context.getSuggest).toBeCalled();
        });

        it('should delete current address for empty address line', () => {
            const context = {
                setContext: jest.fn(),
                getSuggest: jest.fn(),
                props: Object.assign({}, props, {
                    id: 'home',
                    errors: ['error.1'],
                    address: {id: 'home', addressLine: 'address'}
                }),
                isDeliveryAddress: () => true
            };
            const address = '';

            onAddressLineChange.call(context, {target: {value: address}});

            expect(context.props.dispatch.mock.calls.length).toBe(3);
            expect(deleteAddressAction).toBeCalled();
            expect(deleteAddressAction).toBeCalledWith(context.props.id, true);
            expect(editAddressLine).toBeCalled();
            expect(editAddressLine).toBeCalledWith(address, context.props.address);
            expect(clearEditState).toBeCalled();
            expect(clearEditState).toBeCalledWith(context.props.id);
            expect(deleteEditAddressErrors.mock.calls.length).toBe(0);
            expect(context.setContext).toBeCalled();
            expect(context.getSuggest).toBeCalled();
        });
    });
});
