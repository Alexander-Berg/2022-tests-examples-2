import mapDispatchToProps from '../mapDispatchToProps';

import * as redux from 'redux';
import {updateLoginValue, setupBackPane, canRegister, setLoginError} from '../../../actions';
import switchToModeRegisterLite from '../../../actions/switchToModeRegisterLite';
import switchToModeRegister from '../../../actions/switchToModeRegister';
import {amOnLoginFormMount} from '../../../actions/multiStepAuthStart';

jest.mock('redux', () => ({
    bindActionCreators: jest.fn()
}));
jest.mock('../../../actions', () => ({
    updateLoginValue: jest.fn(),
    setupBackPane: jest.fn(),
    canRegister: jest.fn(),
    setLoginError: jest.fn()
}));
jest.mock('../../../actions/switchToModeRegisterLite');
jest.mock('../../../actions/switchToModeRegister');
jest.mock('../../../actions/multiStepAuthStart', () => ({
    amOnLoginFormMount: jest.fn()
}));

describe('Components: LoginForm.mapDispatchToProps', () => {
    afterEach(() => {
        redux.bindActionCreators.mockClear();
        updateLoginValue.mockClear();
        setupBackPane.mockClear();
        canRegister.mockClear();
        setLoginError.mockClear();
        switchToModeRegisterLite.mockClear();
        switchToModeRegister.mockClear();
        amOnLoginFormMount.mockClear();
    });

    it('should return action creators', () => {
        const dispatch = jest.fn();

        mapDispatchToProps(dispatch);

        expect(redux.bindActionCreators).toBeCalled();
        expect(redux.bindActionCreators.mock.calls[0][0]).toEqual({
            updateLoginValue,
            setupBackPane,
            canRegister,
            setLoginError,
            switchToModeRegisterLite,
            switchToModeRegister,
            onMount: amOnLoginFormMount
        });
        expect(redux.bindActionCreators.mock.calls[0][1]).toBe(dispatch);
    });
});
