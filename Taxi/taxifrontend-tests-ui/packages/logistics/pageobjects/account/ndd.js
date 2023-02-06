const {authorize} = require('../../support/auth');

module.exports = {
    async authorizeAndOpenNDD() {
        const loginUser = 'corp-logisticauto41902';
        await browser.url(
            `https://passport-test.yandex.ru/auth?new=0&origin=b2b_dostavka&retpath=${browser.config.baseUrl}/account`
        );
        await authorize(loginUser);
        //Проверяем, что страница загрузилась и обновляем ее, чтобы выставился параметр timezone в localStorage
        await browser.$('//*[text()="Меню"]').waitForDisplayed();
        // Устанавливаем русский язык
        await browser.setCookies({
            name: 'lang',
            value: 'ru'
        });
        await browser.refresh();
        await browser.pause(1000);

        await browser.$('[href="/account/ndd"]').click();
    }
};
