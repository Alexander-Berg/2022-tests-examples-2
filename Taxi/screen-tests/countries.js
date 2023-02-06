const auth = require('../support/auth');
const checkAdminElement = require('../support/checkAdminElement');

describe('/countries', () => {
    before(async () => {
        await auth();
    });

    it('Раздел "Страны"', async () => {
        await checkAdminElement({countries: '.Layout3__body'}, '/countries', async () => {
            await browser.$('.LayoutListItem__text').waitForDisplayed();
        });
    });

    it('Просмотр общих настроек страны', async () => {
        await checkAdminElement({countrySettings: '.LayoutContent__inner'}, '/countries/edit/rus');
    });

    it('Просмотр настроек страны для таксометра', async () => {
        await checkAdminElement(
            {countryTaximetrSettings: '.LayoutContent__inner'},
            '/countries/edit/rus',
            async () => {
                await browser.$('//*[text()="Настройки для Таксометра"]').click();
                await browser.$('//*[text()="Валюта"]').waitForDisplayed();
            }
        );
    });
});
