import {push} from 'react-router-redux';
import {sendMetrics, setEditMode, showAddresses, showDeliveryAddresses} from '../service';
import {
    ADDRESSES_GOAL_PREFIX,
    EDIT_MODE_ADDRESSES,
    EDIT_MODE_DELIVERY_ADDRESSES,
    ADDRESSES_LINK,
    setAddressesEditMode
} from '../actions';
import {setEditMode as setEditModeAction} from '../../../common/actions';
import metrics from '../../../metrics';

jest.mock('../../../metrics');
jest.mock('react-router-redux', () => ({
    push: jest.fn()
}));
jest.mock('../../../common/actions', () => ({
    setEditMode: jest.fn()
}));
jest.mock('../actions', () => ({
    setAddressesEditMode: jest.fn()
}));

describe('Service: addresses', () => {
    describe('sendMetrics', () => {
        beforeEach(() => {
            metrics.goal.mockImplementation(() => {});
        });

        afterEach(() => {
            metrics.goal.mockClear();
        });

        it('should send metrics', () => {
            const goal = 'metric_goal';

            sendMetrics(goal);
            expect(metrics.goal).toBeCalled();
            expect(metrics.goal).toBeCalledWith(`${ADDRESSES_GOAL_PREFIX}_${goal}`);
        });
    });

    describe('setEditMode', () => {
        it('should set edit mode with default mode', () => {
            const dispatch = jest.fn();
            const props = {
                dispatch,
                settings: {
                    ua: {
                        isMobile: true,
                        isTouch: false,
                        isTablet: false
                    }
                }
            };

            setEditMode.call({props});

            expect(setAddressesEditMode).toBeCalled();
            expect(setAddressesEditMode).toBeCalledWith(EDIT_MODE_ADDRESSES);
            expect(push).toBeCalled();
            expect(push).toBeCalledWith(ADDRESSES_LINK);
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
        });

        it('should set edit mode for desktop', () => {
            const dispatch = jest.fn();
            const props = {
                dispatch,
                settings: {
                    ua: {
                        isMobile: false,
                        isTouch: false,
                        isTablet: true
                    }
                }
            };

            setEditMode.call({props});

            expect(setAddressesEditMode).toBeCalled();
            expect(setAddressesEditMode).toBeCalledWith(EDIT_MODE_ADDRESSES);
            expect(setEditModeAction).toBeCalled();
            expect(setEditModeAction).toBeCalledWith(EDIT_MODE_ADDRESSES);
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
        });

        it('should set edit mode without settings prop', () => {
            const dispatch = jest.fn();
            const props = {
                dispatch
            };

            setEditMode.call({props});

            expect(setAddressesEditMode).toBeCalled();
            expect(setAddressesEditMode).toBeCalledWith(EDIT_MODE_ADDRESSES);
            expect(setEditModeAction).toBeCalled();
            expect(setEditModeAction).toBeCalledWith(EDIT_MODE_ADDRESSES);
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
        });
    });

    describe('showAddresses', () => {
        it('should call setEditMode', () => {
            const setEditModeFn = jest.fn();

            showAddresses.call({setEditMode: setEditModeFn}, {});

            expect(setEditModeFn).toBeCalled();
            expect(setEditModeFn).toBeCalledWith(EDIT_MODE_ADDRESSES);
        });

        it('should call setEditMode and call preventDefault', () => {
            const setEditModeFn = jest.fn();
            const preventDefaultFn = jest.fn();

            showAddresses.call({setEditMode: setEditModeFn}, {preventDefault: preventDefaultFn});

            expect(setEditModeFn).toBeCalled();
            expect(setEditModeFn).toBeCalledWith(EDIT_MODE_ADDRESSES);
            expect(preventDefaultFn).toBeCalled();
        });
    });

    describe('showDeliveryAddresses', () => {
        it('should call setEditMode', () => {
            const setEditModeFn = jest.fn();

            showDeliveryAddresses.call({setEditMode: setEditModeFn}, {});

            expect(setEditModeFn).toBeCalled();
            expect(setEditModeFn).toBeCalledWith(EDIT_MODE_DELIVERY_ADDRESSES);
        });

        it('should call setEditMode and call preventDefault', () => {
            const setEditModeFn = jest.fn();
            const preventDefaultFn = jest.fn();

            showDeliveryAddresses.call({setEditMode: setEditModeFn}, {preventDefault: preventDefaultFn});

            expect(setEditModeFn).toBeCalled();
            expect(setEditModeFn).toBeCalledWith(EDIT_MODE_DELIVERY_ADDRESSES);
            expect(preventDefaultFn).toBeCalled();
        });
    });
});
