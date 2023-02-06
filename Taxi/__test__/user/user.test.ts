import {accessRestrictedSelector, userDomainsSelector, userLoadStatusSelector} from '../../user';

import {
    getAccessRestrictedMockInitial,
    getAccessRestrictedMockSuccess,
    getUserDomainsMock,
    getUserStatusMock,
} from './store';

test('accessRestrictedSelector return true on empty user data', () => {
    const {store, result} = getAccessRestrictedMockInitial();
    const selected = accessRestrictedSelector(store);

    expect(selected).toBe(result);
});
test('accessRestrictedSelector return false on filled user data', () => {
    const {store, result} = getAccessRestrictedMockSuccess();
    const selected = accessRestrictedSelector(store);

    expect(selected).toBe(result);
});

test('userDomainsSelector return [] on empty restrictions', () => {
    const {store, result} = getUserDomainsMock();
    const selected = userDomainsSelector(store);

    expect(selected).toStrictEqual(result);
});

test('userLoadStatusSelector return correct status', () => {
    const {store, result} = getUserStatusMock();
    const selected = userLoadStatusSelector(store);

    expect(selected).toBe(result);
});
