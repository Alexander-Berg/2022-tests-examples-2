import metrics from '../../../../../metrics';
import {ADDRESSES_GOAL_PREFIX, EDIT_MODE_ADDRESSES, setAddressesEditMode} from '../../../actions/index';

jest.mock('../../../../../metrics', () => ({
    goal: jest.fn()
}));
jest.mock('../../../actions/index', () => ({
    setAddressesEditMode: jest.fn()
}));

const props = {
    dispatch: jest.fn()
};

import {setEditMode} from '../service';

describe('AddressesTypeToggle component service', () => {
    describe('setEditMode', () => {
        afterEach(() => {
            metrics.goal.mockClear();
            props.dispatch.mockClear();
            setAddressesEditMode.mockClear();
        });

        it('should set address edit mode and send metrics', () => {
            setEditMode.call({props}, EDIT_MODE_ADDRESSES);

            expect(props.dispatch.mock.calls.length).toBe(1);
            expect(metrics.goal).toBeCalled();
            expect(metrics.goal).toBeCalledWith(`${ADDRESSES_GOAL_PREFIX}_toggle_navi`);
            expect(setAddressesEditMode).toBeCalled();
            expect(setAddressesEditMode).toBeCalledWith(EDIT_MODE_ADDRESSES);
        });

        it('should set address edit mode and send metrics for delivery', () => {
            const mode = 'mode';

            setEditMode.call({props}, mode);

            expect(props.dispatch.mock.calls.length).toBe(1);
            expect(metrics.goal).toBeCalled();
            expect(metrics.goal).toBeCalledWith(`${ADDRESSES_GOAL_PREFIX}_toggle_delivery`);
            expect(setAddressesEditMode).toBeCalled();
            expect(setAddressesEditMode).toBeCalledWith(mode);
        });
    });
});
