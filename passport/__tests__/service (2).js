import metrics from '../../../../../metrics';
import {ADDRESSES_GOAL_PREFIX, EDIT_MODE_ADDRESSES, setAddressesEditMode} from '../../../actions';
import {setEditMode as setEditModeAction} from '../../../../../common/actions';

import {sendMetrics, setEditMode} from '../service';

jest.mock('../../../../../metrics', () => ({
    goal: jest.fn()
}));
jest.mock('../../../actions', () => ({
    setAddressesEditMode: jest.fn()
}));
jest.mock('../../../../../common/actions', () => ({
    setEditMode: jest.fn()
}));

const props = {
    address: {id: 'home'},
    dispatch: jest.fn()
};

describe('Address component service', () => {
    describe('sendMetrics', () => {
        afterEach(() => {
            metrics.goal.mockClear();
        });

        it('should send metrics', () => {
            sendMetrics.call({props});

            expect(metrics.goal).toBeCalled();
            expect(metrics.goal).toBeCalledWith(`${ADDRESSES_GOAL_PREFIX}_add_home`);
        });
    });

    describe('setEditMode', () => {
        afterEach(() => {
            props.dispatch.mockClear();
            setAddressesEditMode.mockClear();
            setEditModeAction.mockClear();
        });

        it('should set edit mode', () => {
            setEditMode.call({props});

            expect(props.dispatch.mock.calls.length).toBe(2);
            expect(setAddressesEditMode).toBeCalled();
            expect(setAddressesEditMode).toBeCalledWith(EDIT_MODE_ADDRESSES);
            expect(setEditModeAction).toBeCalled();
            expect(setEditModeAction).toBeCalledWith(EDIT_MODE_ADDRESSES);
        });
    });
});
