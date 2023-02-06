import mapDispatchToProps from '../mapDispatchToProps';

import * as redux from 'redux';
import {domikIsLoading, setupBackPane} from '../../../../actions';
import loginSuggestedAccount from '../../../../actions/loginSuggestedAccount';

jest.mock('redux', () => ({
    bindActionCreators: jest.fn()
}));
jest.mock('../../../../actions', () => ({
    domikIsLoading: jest.fn(),
    setupBackPane: jest.fn()
}));
jest.mock('../../../../actions/loginSuggestedAccount');

describe('Components: InvalidAccountListItem.mapDispatchToProps', () => {
    afterEach(() => {
        redux.bindActionCreators.mockClear();
        domikIsLoading.mockClear();
        setupBackPane.mockClear();
        loginSuggestedAccount.mockClear();
    });

    it('should return action creators', () => {
        const dispatch = jest.fn();

        mapDispatchToProps(dispatch);

        expect(redux.bindActionCreators).toBeCalled();
        expect(redux.bindActionCreators.mock.calls[0][0]).toEqual({
            loginSuggestedAccount,
            domikIsLoading,
            setupBackPane
        });
        expect(redux.bindActionCreators.mock.calls[0][1]).toBe(dispatch);
    });
});
