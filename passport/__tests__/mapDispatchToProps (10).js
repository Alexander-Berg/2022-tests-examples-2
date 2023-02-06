import mapDispatchToProps from '../mapDispatchToProps';

import * as redux from 'redux';
import {onAuthMount} from '@blocks/authv2/actions/nativeMobileApi';
import {setupBackPane, canRegister, setupMode} from '../../../actions';
import {setupPane} from '../../../../common/actions';

jest.mock('redux', () => ({
    bindActionCreators: jest.fn()
}));
jest.mock('../../../actions', () => ({
    setupBackPane: jest.fn(),
    canRegister: jest.fn(),
    setupMode: jest.fn()
}));
jest.mock('../../../../common/actions', () => ({
    setupPane: jest.fn()
}));

describe('Components: AddAccountPage.mapDispatchToProps', () => {
    afterEach(() => {
        redux.bindActionCreators.mockClear();
    });

    it('should return action creators', () => {
        const dispatch = jest.fn();

        mapDispatchToProps(dispatch);

        expect(redux.bindActionCreators).toBeCalled();
        expect(redux.bindActionCreators.mock.calls[0][0]).toEqual({
            setupBackPane,
            canRegister,
            setupMode,
            setupPane,
            onMount: onAuthMount
        });
        expect(redux.bindActionCreators.mock.calls[0][1]).toBe(dispatch);
    });
});
