import mapStateToProps from '../mapStateToProps';

describe('Components: CurrentAccount.mapStateToProps', () => {
    it('should return valid props', () => {
        const processedAccount = {
            avatarId: 'avatarId',
            login: 'login',
            displayName: 'displayName',
            hasSocial: true,
            mail: 'mail',
            socialProvider: 'vk'
        };
        const state = {
            common: {
                editUrl: 'editUrl',
                addUserUrl: 'addUserUrl'
            },
            settings: {
                avatar: {
                    host: 'avatarSettings.host',
                    pathname: 'avatarSettings.pathname.%uid%.%size%.%login%'
                }
            },
            auth: {
                processedAccount,
                unitedAccounts: [{}]
            }
        };

        const result = mapStateToProps(state);

        expect(result).toEqual({
            hasDisplayName: true,
            displayLogin: i18n('_AUTH_.SocialBlock.BigButton.vk'),
            avatarStyle: {
                backgroundImage: `url("https://avatarSettings.hostavatarSettings.pathname.avatarId.200.login")`
            },
            displayName: 'displayName',
            login: 'login',
            addUserUrl: 'addUserUrl',
            editUrl: 'editUrl',
            hasUnitedAccounts: true,
            account: processedAccount
        });
    });

    it('should fallback props', () => {
        const processedAccount = {
            avatarId: 'avatarId',
            login: 'login',
            displayName: 'displayName',
            hasSocial: false,
            mail: 'mail',
            socialProvider: 'vk'
        };
        const state = {
            common: {
                editUrl: 'editUrl',
                addUserUrl: 'addUserUrl'
            },
            settings: {
                avatar: {
                    host: 'avatarSettings.host',
                    pathname: 'avatarSettings.pathname.%uid%.%size%.%login%'
                }
            },
            auth: {
                processedAccount,
                unitedAccounts: [{}]
            }
        };

        let result = mapStateToProps(state);

        expect(result).toEqual({
            hasDisplayName: true,
            displayLogin: 'mail',
            avatarStyle: {
                backgroundImage: `url("https://avatarSettings.hostavatarSettings.pathname.avatarId.200.login")`
            },
            displayName: 'displayName',
            login: 'login',
            addUserUrl: 'addUserUrl',
            editUrl: 'editUrl',
            hasUnitedAccounts: true,
            account: processedAccount
        });

        state.auth.processedAccount.mail = null;
        result = mapStateToProps(state);

        expect(result.displayLogin).toBe('');
    });

    it('should return default email as display login', () => {
        const defaultEmail = 'defaultEmail';

        const state = {
            common: {
                editUrl: 'editUrl',
                addUserUrl: 'addUserUrl'
            },
            settings: {
                avatar: {
                    host: 'avatarSettings.host',
                    pathname: 'avatarSettings.pathname.%uid%.%size%.%login%'
                }
            },
            auth: {
                processedAccount: {
                    avatarId: 'avatarId',
                    login: 'login',
                    displayName: 'displayName',
                    hasSocial: false,
                    defaultEmail
                },
                unitedAccounts: [{}]
            }
        };

        const result = mapStateToProps(state);

        expect(result.displayLogin).toEqual(defaultEmail);
    });
});
