import mapDispatchToProps from '../mapDispatchToProps';

import * as redux from 'redux';
import {updatePasswordValue, setPasswordError} from '../../../actions';

jest.mock('redux', () => ({
    bindActionCreators: jest.fn()
}));
jest.mock('../../../actions', () => ({
    updatePasswordValue: jest.fn(),
    setPasswordError: jest.fn()
}));
jest.mock('../../../actions/switchToModeMagic');

describe('Components: PasswordForm.mapDispatchToProps', () => {
    afterEach(() => {
        redux.bindActionCreators.mockClear();
        updatePasswordValue.mockClear();
        setPasswordError.mockClear();
    });

    it('should return action creators', () => {
        const dispatch = jest.fn();

        mapDispatchToProps(dispatch);

        expect(redux.bindActionCreators).toBeCalled();
        expect(redux.bindActionCreators.mock.calls[0][0]).toEqual({
            updatePasswordValue,
            setPasswordError
        });
        expect(redux.bindActionCreators.mock.calls[0][1]).toBe(dispatch);
    });
});
