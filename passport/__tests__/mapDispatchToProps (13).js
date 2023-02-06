import mapDispatchToProps from '../mapDispatchToProps';

import * as redux from 'redux';
import {updateLoginValue, updatePasswordValue, setupBackPane, setupMode} from '../../../actions';
import {setupPane} from '../../../../common/actions';
import changeNativeInputValue from '../../../actions/changeNativeInputValue';

jest.mock('redux', () => ({
    bindActionCreators: jest.fn()
}));
jest.mock('../../../actions', () => ({
    updateLoginValue: jest.fn(),
    updatePasswordValue: jest.fn(),
    setupBackPane: jest.fn(),
    setupMode: jest.fn()
}));
jest.mock('../../../actions/changeNativeInputValue');
jest.mock('../../../../common/actions', () => ({
    setupPane: jest.fn()
}));

describe('Components: WelcomePage.mapDispatchToProps', () => {
    afterEach(() => {
        redux.bindActionCreators.mockClear();
    });

    it('should return action creators', () => {
        const dispatch = jest.fn();

        mapDispatchToProps(dispatch);

        expect(redux.bindActionCreators).toBeCalled();
        expect(redux.bindActionCreators.mock.calls[0][0]).toEqual({
            updatePasswordValue,
            updateLoginValue,
            setupBackPane,
            setupMode,
            setupPane,
            changeNativeInputValue
        });
        expect(redux.bindActionCreators.mock.calls[0][1]).toBe(dispatch);
    });
});
