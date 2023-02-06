import formatAccountListUrl from '../formatAccountListUrl';

describe('Helpers: formatAccountListUrl', () => {
    it('should handle logout action', () => {
        const options = {
            embeddedAuthUrl: 'option_embeddedAuthUrl',
            yu: 'option_yu',
            retpath: 'https://ya.ru?ololo=pepepe',
            uid: 'option_uid',
            action: 'logout',
            origin: 'origin',
            login: 'option_login'
        };
        const url = formatAccountListUrl(options);

        expect(url).toBe(
            `option_embeddedAuthUrl&yu=option_yu&action=logout&uid=option_uid&retpath=${encodeURIComponent(
                options.retpath
            )}&origin=origin`
        );
    });

    it('should handle change_default action', () => {
        const options = {
            embeddedAuthUrl: 'option_embeddedAuthUrl',
            yu: 'option_yu',
            retpath: 'option_retpath',
            uid: 'option_uid',
            action: 'change_default',
            origin: 'origin',
            login: 'option_login'
        };
        const url = formatAccountListUrl(options);

        expect(url).toBe(
            // eslint-disable-next-line max-len
            'option_embeddedAuthUrl&yu=option_yu&action=change_default&uid=option_uid&retpath=option_retpath&origin=origin'
        );
    });

    it('should handle switchTo action', () => {
        const options = {
            embeddedAuthUrl: 'option_embeddedAuthUrl',
            yu: 'option_yu',
            retpath: 'option_retpath',
            uid: 'option_uid',
            action: 'switchTo',
            origin: 'origin',
            login: 'option_login'
        };
        const url = formatAccountListUrl(options);

        expect(url).toBe('/auth/welcome?uid=option_uid&retpath=option_retpath&origin=origin');
    });

    it('should handle login action', () => {
        const options = {
            embeddedAuthUrl: 'option_embeddedAuthUrl',
            yu: 'option_yu',
            retpath: 'option_retpath',
            uid: 'option_uid',
            action: 'login',
            origin: 'origin',
            login: 'option_login'
        };
        const url = formatAccountListUrl(options);

        expect(url).toBe('/auth/add?login=option_login&retpath=option_retpath&origin=origin');
    });

    it('should handle retpath action', () => {
        const options = {
            embeddedAuthUrl: 'option_embeddedAuthUrl',
            yu: 'option_yu',
            retpath: 'option_retpath',
            uid: 'option_uid',
            action: 'retpath',
            origin: 'origin',
            login: 'option_login'
        };
        const url = formatAccountListUrl(options);

        expect(url).toBe('option_retpath');
    });

    it('should handle fallback to undefined action', () => {
        const options = {
            embeddedAuthUrl: 'option_embeddedAuthUrl',
            yu: 'option_yu',
            retpath: 'option_retpath',
            uid: 'option_uid',
            action: 'noname_action',
            origin: 'origin',
            login: 'option_login'
        };
        const url = formatAccountListUrl(options);

        expect(url).toBe('');
    });
});
