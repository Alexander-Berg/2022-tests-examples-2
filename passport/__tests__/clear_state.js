import {setEditMode} from '../../../../common/actions';
import {clearAddressesState} from '../';
import {getAddresses} from '../get_addresses';

import {clearState} from '../clear_state';

jest.mock('../../../../common/actions', () => ({
    setEditMode: jest.fn()
}));
jest.mock('../', () => ({
    clearAddressesState: jest.fn()
}));
jest.mock('../get_addresses', () => ({
    getAddresses: jest.fn()
}));

describe('Action: clearState', () => {
    it('should dispatch 3 actions', () => {
        const dispatch = jest.fn();

        clearState()(dispatch);

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(3);
        expect(setEditMode).toBeCalled();
        expect(setEditMode).toBeCalledWith('');
        expect(getAddresses).toBeCalled();
        expect(clearAddressesState).toBeCalled();
    });
});
