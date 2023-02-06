import prepareProps from '../prepareProps';

describe('Components: AccountListItem.prepareProps', () => {
    it('should return prepared props', () => {
        const props = {
            account: {
                avatarId: 'avatarId',
                login: 'login',
                displayName: 'displayName',
                hasSocial: true,
                mail: 'mail',
                socialProvider: 'vk'
            },
            avatarSettings: {
                host: 'avatarSettings.host',
                pathname: 'avatarSettings.pathname.%uid%.%size%.%login%'
            },
            logoutUrl: 'logoutUrl',
            isDefault: false,
            fallbackUrl: 'fallbackUrl',
            onClick: 'onClick'
        };

        const result = prepareProps(props);

        expect(result).toEqual({
            fallbackUrl: 'fallbackUrl',
            socialProvider: 'vk',
            avatarStyle: {
                backgroundImage: 'url("https://avatarSettings.hostavatarSettings.pathname.avatarId.200.login")'
            },
            displayName: 'displayName',
            displayLogin: i18n('_AUTH_.SocialBlock.BigButton.vk'),
            isDefaultAvatar: false,
            isDefault: false,
            hasSocial: true,
            onClick: 'onClick'
        });
    });

    it('should fallback props', () => {
        const props = {
            account: {
                avatarId: 'avatarId',
                login: 'login',
                displayName: 'displayName',
                hasSocial: false,
                mail: 'mail',
                socialProvider: 'vk'
            },
            avatarSettings: {
                host: 'avatarSettings.host',
                pathname: 'avatarSettings.pathname.%uid%.%size%.%login%'
            },
            logoutUrl: null,
            isDefault: true,
            fallbackUrl: 'fallbackUrl',
            onClick: 'onClick'
        };

        let result = prepareProps(props);

        expect(result).toEqual({
            fallbackUrl: 'fallbackUrl',
            socialProvider: 'vk',
            avatarStyle: {
                backgroundImage: 'url("https://avatarSettings.hostavatarSettings.pathname.avatarId.200.login")'
            },
            displayName: 'displayName',
            displayLogin: 'mail',
            isDefault: true,
            isDefaultAvatar: false,
            hasSocial: false,
            onClick: 'onClick'
        });

        props.account.mail = null;
        result = prepareProps(props);
        expect(result.displayLogin).toBe('');
    });

    it('should return default email as display login', () => {
        const defaultEmail = 'defaultEmail';

        const props = {
            account: {
                avatarId: 'avatarId',
                login: 'login',
                displayName: 'displayName',
                hasSocial: false,
                defaultEmail
            },
            avatarSettings: {
                host: 'avatarSettings.host',
                pathname: 'avatarSettings.pathname.%uid%.%size%.%login%'
            },
            logoutUrl: null,
            isDefault: true,
            fallbackUrl: 'fallbackUrl',
            onClick: 'onClick'
        };

        const result = prepareProps(props);

        expect(result.displayLogin).toEqual(defaultEmail);
    });
});
