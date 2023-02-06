import metrics from '../../../../metrics';
import {ADDRESSES_GOAL_PREFIX, setAddress} from '../';

jest.mock('../../../../metrics', () => ({
    goal: jest.fn()
}));
jest.mock('../', () => ({
    setAddress: jest.fn()
}));

import {setAddressHelper} from '../set_address_helper';

const dispatch = jest.fn();

describe('Action: setAddressHelper', () => {
    afterEach(() => {
        dispatch.mockClear();
        metrics.goal.mockClear();
        setAddress.mockClear();
    });

    it('should set address', () => {
        const address = {id: 'home', flat: 'flat', addressLine: 'address line'};
        const isDelivery = false;

        setAddressHelper(address, isDelivery)(dispatch);

        expect(metrics.goal).toBeCalled();
        expect(metrics.goal).toBeCalledWith(`${ADDRESSES_GOAL_PREFIX}_fill_home`);
        expect(dispatch.mock.calls.length).toBe(1);
        expect(setAddress).toBeCalled();
        expect(setAddress).toBeCalledWith(address, isDelivery);
    });

    it('should set delivery address', () => {
        const address = {id: 'home', flat: 'flat', addressLine: 'address line'};
        const isDelivery = true;

        setAddressHelper(address, isDelivery)(dispatch);

        expect(metrics.goal).toBeCalled();
        expect(metrics.goal).toBeCalledWith(`${ADDRESSES_GOAL_PREFIX}_fill_delivery`);
        expect(dispatch.mock.calls.length).toBe(1);
        expect(setAddress).toBeCalled();
        expect(setAddress).toBeCalledWith(address, isDelivery);
    });
});
