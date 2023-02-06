import mapDispatchToProps from '../mapDispatchToProps';

import * as redux from 'redux';
import changeActiveAccount from '../../../../actions/changeActiveAccount';

jest.mock('redux', () => ({
    bindActionCreators: jest.fn()
}));
jest.mock('../../../../actions', () => ({
    changeMobileMenuVisibility: jest.fn(),
    changeMobileMenuType: jest.fn(),
    setProccessedAccountUid: jest.fn()
}));
jest.mock('../../../../actions/logoutAccount');
jest.mock('../../../../actions/changeActiveAccount');

describe('Components: AuthorizedAccountListItem.mapDispatchToProps', () => {
    afterEach(() => {
        redux.bindActionCreators.mockClear();
        changeActiveAccount.mockClear();
    });

    it('should return action creators', () => {
        const dispatch = jest.fn();

        mapDispatchToProps(dispatch);

        expect(redux.bindActionCreators).toBeCalled();
        expect(redux.bindActionCreators.mock.calls[0][0]).toEqual({
            changeActiveAccount
        });
        expect(redux.bindActionCreators.mock.calls[0][1]).toBe(dispatch);
    });
});
