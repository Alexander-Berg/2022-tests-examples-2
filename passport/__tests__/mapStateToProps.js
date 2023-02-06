import mapStateToProps from '../mapStateToProps';

describe('Components: AccountList.mapStateToProps', () => {
    it('should return accounts list', () => {
        const state = {
            auth: {
                authorizedAccountsDefaultUid: 1,
                unitedAccounts: {
                    1: {
                        uid: 1,
                        status: 'VALID'
                    },
                    2: {
                        uid: 2,
                        status: 'INVALID'
                    },
                    3: {
                        uid: 3,
                        status: 'INVALID',
                        allowed_auth_methods: ['password']
                    },
                    4: {
                        uid: 4,
                        status: 'VALID'
                    }
                }
            },
            customs: {}
        };

        const result = mapStateToProps(state);

        expect(result.authorizedAccounts).toEqual([
            {
                uid: 1,
                status: 'VALID'
            },
            {
                uid: 4,
                status: 'VALID'
            }
        ]);
        expect(result.defaultAccount).toEqual({
            uid: 1,
            status: 'VALID'
        });
        expect(result.suggestedAccounts).toEqual([
            {
                uid: 3,
                status: 'INVALID',
                allowed_auth_methods: ['password']
            }
        ]);
        expect(result.invalidAccounts).toEqual([
            {
                uid: 2,
                status: 'INVALID'
            }
        ]);
        expect(result.hasUnauthorizedAccounts).toBe(true);
        expect(result.isSessionOverflow).toBe(false);
    });

    it('should return accounts list without unathorized accounts', () => {
        const state = {
            auth: {
                authorizedAccountsDefaultUid: 1,
                unitedAccounts: {
                    1: {
                        uid: 1,
                        status: 'VALID'
                    },
                    4: {
                        uid: 4,
                        status: 'VALID'
                    }
                }
            },
            customs: {}
        };

        const result = mapStateToProps(state);

        expect(result.authorizedAccounts).toEqual([
            {
                uid: 1,
                status: 'VALID'
            },
            {
                uid: 4,
                status: 'VALID'
            }
        ]);
        expect(result.defaultAccount).toEqual({
            uid: 1,
            status: 'VALID'
        });
        expect(result.suggestedAccounts).toEqual([]);
        expect(result.invalidAccounts).toEqual([]);
        expect(result.hasUnauthorizedAccounts).toBe(false);
        expect(result.isSessionOverflow).toBe(false);
    });
    it('should skip scholar on non scholar origin', () => {
        const state = {
            auth: {
                authorizedAccountsDefaultUid: 1,
                unitedAccounts: {
                    1: {
                        uid: 1,
                        status: 'VALID',
                        isScholar: true
                    },
                    4: {
                        uid: 4,
                        status: 'VALID'
                    }
                }
            },
            customs: {}
        };

        const result = mapStateToProps(state);

        expect(result.authorizedAccounts).toEqual([
            {
                uid: 4,
                status: 'VALID'
            }
        ]);
        expect(result.defaultAccount).toEqual(undefined);
        expect(result.suggestedAccounts).toEqual([]);
        expect(result.invalidAccounts).toEqual([]);
        expect(result.hasUnauthorizedAccounts).toBe(false);
        expect(result.isSessionOverflow).toBe(false);
    });
    it('should return accounts list with scholar accounts', () => {
        const state = {
            auth: {
                authorizedAccountsDefaultUid: 1,
                unitedAccounts: {
                    1: {
                        uid: 1,
                        isScholar: true,
                        status: 'VALID'
                    },
                    4: {
                        uid: 4,
                        status: 'VALID'
                    }
                }
            },
            customs: {allowScholar: true}
        };

        const result = mapStateToProps(state);

        expect(result.authorizedAccounts).toEqual([
            {
                uid: 1,
                isScholar: true,
                status: 'VALID'
            },
            {
                uid: 4,
                status: 'VALID'
            }
        ]);
        expect(result.defaultAccount).toEqual({
            uid: 1,
            isScholar: true,
            status: 'VALID'
        });
        expect(result.suggestedAccounts).toEqual([]);
        expect(result.invalidAccounts).toEqual([]);
        expect(result.hasUnauthorizedAccounts).toBe(false);
        expect(result.isSessionOverflow).toBe(false);
    });
});
