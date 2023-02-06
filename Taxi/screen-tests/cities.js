const auth = require('../support/auth');
const checkAdminElement = require('../support/checkAdminElement');

describe('/cities', () => {
    before(async () => {
        await auth();
    });

    it('Просмотр города', async () => {
        await checkAdminElement(
            {cityInfo: '.LayoutContent__inner'},
            '/cities/edit/Новосибирск',
            async () => {
                await browser.$('[value="novosibirsk"]').waitForDisplayed();
            }
        );
    });
});
