import {AUTH_CONFIG} from '../../../config/auth';
import profile from '../../../fixtures/auth/profile.json';
import {
    loginPages,
    wfmPages,
} from '../../../page-objects';

describe('auth.smoke', () => {
    it('should login with valid credentials', async () => {
        await loginPages.passport.auth.open();

        await loginPages.passport.auth.login(
            AUTH_CONFIG.CREDENTIALS.USERNAME,
            AUTH_CONFIG.CREDENTIALS.PASSWORD,
        );

        const firstName = await loginPages.passport.auth.findProfileFirstName();
        const lastName = await loginPages.passport.auth.findProfileLastName();

        expect([firstName, lastName])
            .toEqual([profile.first_name, profile.last_name]);

        await wfmPages.menu.open('/skills');
        const domain = await wfmPages.menu.findDomain('Taxi');

        expect(domain)
            .toEqual('Taxi');
    });
});
