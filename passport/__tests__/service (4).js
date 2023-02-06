import {saveAddresses as saveAddressesAction} from '../../../actions/save_addresses';
import _isUndefined from 'lodash/isUndefined';
import metrics from '../../../../../metrics';
import {
    ADDRESSES_GOAL_PREFIX,
    EDIT_MODE_DELIVERY_ADDRESSES,
    setAddDeliveryAddressMode as setAddDeliveryAddressModeAction,
    setAddressesUpdateState,
    setAddressesEditMode,
    editAddressLine
} from '../../../actions';
import {clearState} from '../../../actions/clear_state';
import util from '../../../../../utils';
import {push} from 'connected-react-router';

jest.mock('../../../actions/save_addresses', () => ({
    saveAddresses: jest.fn()
}));
jest.mock('../../../../../metrics');
jest.mock('../../../actions/index', () => ({
    setAddDeliveryAddressMode: jest.fn(),
    setAddressesUpdateState: jest.fn(),
    setAddressesEditMode: jest.fn(),
    editAddressLine: jest.fn()
}));
jest.mock('../../../actions/clear_state', () => ({
    clearState: jest.fn()
}));
jest.mock('../../../../../utils');
jest.mock('connected-react-router', () => ({
    push: jest.fn()
}));
jest.mock('lodash/isUndefined');

import {
    closeAddressesControl,
    onSubmit,
    saveAddresses,
    setAddDeliveryAddressMode,
    handleAddressUpdate
} from '../service';

const props = {
    dispatch: jest.fn()
};

const {location} = window;

describe('AddressesEditControl component service', () => {
    describe('closeAddressesControl', () => {
        beforeEach(() => {
            util.isThirdPartyUrl.mockImplementation(() => {});
            metrics.goal.mockImplementation(() => {});
            push.mockImplementation(() => {});
        });

        afterEach(() => {
            props.dispatch.mockClear();
            util.isThirdPartyUrl.mockClear();
            push.mockClear();
            metrics.goal.mockClear();
            saveAddressesAction.mockClear();
            setAddDeliveryAddressModeAction.mockClear();
            setAddressesUpdateState.mockClear();
            setAddressesEditMode.mockClear();
            clearState.mockClear();
            editAddressLine.mockClear();
        });

        it('should clear state and send metrics', () => {
            closeAddressesControl.call({props}, {}, false);

            expect(props.dispatch.mock.calls.length).toBe(1);
            expect(clearState).toBeCalled();
            expect(metrics.goal).toBeCalled();
            expect(metrics.goal).toBeCalledWith(`${ADDRESSES_GOAL_PREFIX}_close`);
        });

        it('should clear state', () => {
            closeAddressesControl.call({props}, {}, true);

            expect(props.dispatch.mock.calls.length).toBe(1);
            expect(clearState).toBeCalled();
            expect(metrics.goal.mock.calls.length).toBe(0);
        });
    });

    describe('onSubmit', () => {
        beforeEach(() => {
            util.isThirdPartyUrl.mockImplementation(() => {});
            metrics.goal.mockImplementation(() => {});
            push.mockImplementation(() => {});
        });

        afterEach(() => {
            props.dispatch.mockClear();
            util.isThirdPartyUrl.mockClear();
            push.mockClear();
            metrics.goal.mockClear();
            saveAddressesAction.mockClear();
            setAddDeliveryAddressModeAction.mockClear();
            setAddressesUpdateState.mockClear();
            setAddressesEditMode.mockClear();
            clearState.mockClear();
            editAddressLine.mockClear();
        });

        it('should save addresses', () => {
            const saveAddresses = jest.fn();
            const preventDefault = jest.fn();

            onSubmit.call({saveAddresses}, {preventDefault});

            expect(saveAddresses).toBeCalled();
            expect(preventDefault).toBeCalled();
        });
    });

    describe('saveAddresses', () => {
        beforeEach(() => {
            util.isThirdPartyUrl.mockImplementation(() => {});
            metrics.goal.mockImplementation(() => {});
            push.mockImplementation(() => {});
        });

        afterEach(() => {
            props.dispatch.mockClear();
            util.isThirdPartyUrl.mockClear();
            push.mockClear();
            metrics.goal.mockClear();
            saveAddressesAction.mockClear();
            setAddDeliveryAddressModeAction.mockClear();
            setAddressesUpdateState.mockClear();
            setAddressesEditMode.mockClear();
            clearState.mockClear();
        });

        it('should set address edit mode', () => {
            const context = {
                props: Object.assign({}, props, {
                    addresses: {
                        editErrors: {
                            flat: []
                        },
                        mode: 'mode'
                    }
                })
            };

            saveAddresses.call(context);

            expect(context.props.dispatch.mock.calls.length).toBe(1);
            expect(setAddressesEditMode).toBeCalled();
            expect(setAddressesEditMode).toBeCalledWith(EDIT_MODE_DELIVERY_ADDRESSES);
        });

        it('should not set address edit mode', () => {
            const context = {
                props: Object.assign({}, props, {
                    addresses: {
                        editErrors: {
                            flat: []
                        },
                        mode: EDIT_MODE_DELIVERY_ADDRESSES
                    }
                })
            };

            saveAddresses.call(context);

            expect(context.props.dispatch.mock.calls.length).toBe(0);
            expect(setAddressesEditMode.mock.calls.length).toBe(0);
        });

        it('should save addresses and send metrics', () => {
            const context = {
                props: Object.assign({}, props, {
                    addresses: {}
                })
            };

            saveAddresses.call(context);

            expect(context.props.dispatch.mock.calls.length).toBe(1);
            expect(saveAddressesAction).toBeCalled();
            expect(metrics.goal).toBeCalled();
            expect(metrics.goal).toBeCalledWith(`${ADDRESSES_GOAL_PREFIX}_save`);
        });
    });

    describe('setAddDeliveryAddressMode', () => {
        beforeEach(() => {
            util.isThirdPartyUrl.mockImplementation(() => {});
            metrics.goal.mockImplementation(() => {});
            push.mockImplementation(() => {});
        });

        afterEach(() => {
            props.dispatch.mockClear();
            util.isThirdPartyUrl.mockClear();
            push.mockClear();
            metrics.goal.mockClear();
            saveAddressesAction.mockClear();
            setAddDeliveryAddressModeAction.mockClear();
            setAddressesUpdateState.mockClear();
            setAddressesEditMode.mockClear();
            clearState.mockClear();
            editAddressLine.mockClear();
        });

        it('should not set add delivery address mode action', () => {
            const context = {
                props: Object.assign({}, props, {
                    addresses: {
                        geoLocationUpdateState: {
                            progress: true
                        }
                    }
                })
            };

            setAddDeliveryAddressMode.call(context);

            expect(context.props.dispatch.mock.calls.length).toBe(0);
            expect(setAddDeliveryAddressModeAction.mock.calls.length).toBe(0);
        });

        it('should not set add delivery address mode action without settings', () => {
            const defaultDelivery = {id: 'defaultDelivery'};
            const context = {
                props: Object.assign({}, props, {
                    addresses: {
                        defaultDelivery
                    }
                })
            };

            setAddDeliveryAddressMode.call(context);

            expect(context.props.dispatch.mock.calls.length).toBe(2);
            expect(editAddressLine).toBeCalled();
            expect(editAddressLine).toBeCalledWith('', defaultDelivery);
            expect(setAddDeliveryAddressModeAction).toBeCalled();
            expect(setAddDeliveryAddressModeAction).toBeCalledWith(true);
        });

        it('should set add delivery address mode action', () => {
            const defaultDelivery = {id: 'defaultDelivery'};
            const context = {
                props: Object.assign({}, props, {
                    addresses: {
                        geoLocationUpdateState: {},
                        defaultDelivery
                    }
                })
            };

            setAddDeliveryAddressMode.call(context);

            expect(context.props.dispatch.mock.calls.length).toBe(2);
            expect(editAddressLine).toBeCalled();
            expect(editAddressLine).toBeCalledWith('', defaultDelivery);
            expect(setAddDeliveryAddressModeAction).toBeCalled();
            expect(setAddDeliveryAddressModeAction).toBeCalledWith(true);
        });
    });

    describe('handleAddressUpdate', () => {
        beforeEach(() => {
            util.isThirdPartyUrl.mockImplementation(() => {});
            metrics.goal.mockImplementation(() => {});
            push.mockImplementation(() => {});
        });

        afterEach(() => {
            props.dispatch.mockClear();
            util.isThirdPartyUrl.mockClear();
            push.mockClear();
            metrics.goal.mockClear();
            saveAddressesAction.mockClear();
            setAddDeliveryAddressModeAction.mockClear();
            setAddressesUpdateState.mockClear();
            setAddressesEditMode.mockClear();
            clearState.mockClear();
            _isUndefined.mockClear();
            editAddressLine.mockClear();
        });

        it('should set address update state', () => {
            const context = {
                props: Object.assign({}, props, {
                    modal: true,
                    common: {}
                })
            };

            handleAddressUpdate.call(context);

            expect(context.props.dispatch.mock.calls.length).toBe(1);
            expect(setAddressesUpdateState).toBeCalled();
            expect(setAddressesUpdateState).toBeCalledWith(false);
        });

        it('should set address update state without settings', () => {
            const context = {
                props: Object.assign({}, props)
            };

            handleAddressUpdate.call(context);

            expect(context.props.dispatch.mock.calls.length).toBe(2);
            expect(setAddressesUpdateState).toBeCalled();
            expect(setAddressesUpdateState).toBeCalledWith(false);
        });

        it('should set address update state', () => {
            const context = {
                props: Object.assign({}, props, {
                    modal: true,
                    common: {}
                })
            };

            _isUndefined.mockImplementation(() => true);

            handleAddressUpdate.call(context);

            expect(context.props.dispatch.mock.calls.length).toBe(1);
            expect(setAddressesUpdateState).toBeCalled();
            expect(setAddressesUpdateState).toBeCalledWith(false);
        });

        it('should change window location', () => {
            const retpath = {href: '/profile'};
            const context = {
                props: Object.assign({}, props, {
                    modal: true,
                    common: {
                        retpath
                    }
                })
            };

            util.isThirdPartyUrl.mockImplementation(() => true);
            _isUndefined.mockImplementation(() => false);

            handleAddressUpdate.call(context);

            expect(util.isThirdPartyUrl).toBeCalled();
        });

        it('should push retpath to browser history', () => {
            const retpath = {href: '/auth'};
            const context = {
                props: Object.assign({}, props, {
                    modal: true,
                    common: {
                        retpath
                    }
                })
            };

            util.isThirdPartyUrl.mockImplementation(() => false);
            _isUndefined.mockImplementation(() => false);

            handleAddressUpdate.call(context);

            expect(util.isThirdPartyUrl).toBeCalled();
            expect(push).toBeCalled();
            expect(push).toBeCalledWith(retpath);
        });

        it('should push profile url to browser history', () => {
            const profileUrl = '/profile';
            const context = {
                props: Object.assign({}, props, {
                    modal: false,
                    common: {}
                })
            };

            util.isThirdPartyUrl.mockImplementation(() => false);
            _isUndefined.mockImplementation(() => false);

            handleAddressUpdate.call(context);

            expect(util.isThirdPartyUrl).toBeCalled();
            expect(push).toBeCalled();
            expect(push).toBeCalledWith(profileUrl);
        });

        it('should push profile url to browser history and do not check window location', () => {
            delete window.location;
            window.location = {
                href: undefined
            };
            const profileUrl = '/profile';
            const context = {
                props: Object.assign({}, props, {
                    modal: false,
                    common: {}
                })
            };

            util.isThirdPartyUrl.mockImplementation(() => false);
            _isUndefined.mockImplementation(() => false);

            handleAddressUpdate.call(context);

            expect(util.isThirdPartyUrl.mock.calls.length).toBe(0);
            expect(push).toBeCalled();
            expect(push).toBeCalledWith(profileUrl);

            window.location = location;
        });
    });
});
