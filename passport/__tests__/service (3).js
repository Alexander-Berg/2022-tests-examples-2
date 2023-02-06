import {setAddressesEditMode} from '../../../actions/index';
import {setEditMode as setEditModeAction} from '../../../../../common/actions';

jest.mock('../../../actions', () => ({
    setAddressesEditMode: jest.fn()
}));
jest.mock('../../../../../common/actions', () => ({
    setEditMode: jest.fn()
}));

import {setEditMode} from '../service';

const props = {
    dispatch: jest.fn()
};

describe('AddressesControl component service', () => {
    describe('setEditMode', () => {
        afterEach(() => {
            props.dispatch.mockClear();
            setAddressesEditMode.mockClear();
            setEditModeAction.mockClear();
        });

        it('should set edit mode', () => {
            const mode = 'mode';

            setEditMode.call({props}, mode);

            expect(props.dispatch.mock.calls.length).toBe(2);
            expect(setAddressesEditMode).toBeCalled();
            expect(setAddressesEditMode).toBeCalledWith(mode);
            expect(setEditModeAction).toBeCalled();
            expect(setEditModeAction).toBeCalledWith(mode);
        });

        it('should set empty edit mode', () => {
            setEditMode.call({props});

            expect(props.dispatch.mock.calls.length).toBe(1);
            expect(setEditModeAction).toBeCalled();
            expect(setEditModeAction).toBeCalledWith(undefined);
        });
    });
});
