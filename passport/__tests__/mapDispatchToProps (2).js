import mapDispatchToProps from '../mapDispatchToProps';

import * as redux from 'redux';

import redirectToRetpath from '../../../../actions/redirectToRetpath';

jest.mock('redux', () => ({
    bindActionCreators: jest.fn()
}));
jest.mock('../../../../actions', () => ({
    changeMobileMenuVisibility: jest.fn(),
    changeMobileMenuType: jest.fn(),
    setProccessedAccountUid: jest.fn()
}));
jest.mock('../../../../actions/redirectToRetpath');
jest.mock('../../../../actions/logoutAccount');

describe('Components: DefaultAccountListItem.mapDispatchToProps', () => {
    afterEach(() => {
        redux.bindActionCreators.mockClear();
        redirectToRetpath.mockClear();
    });

    it('should return action creators', () => {
        const dispatch = jest.fn();

        mapDispatchToProps(dispatch);

        expect(redux.bindActionCreators).toBeCalled();
        expect(redux.bindActionCreators.mock.calls[0][0]).toEqual({
            redirectToRetpath
        });
        expect(redux.bindActionCreators.mock.calls[0][1]).toBe(dispatch);
    });
});
