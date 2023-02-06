const getUsersFile = require('./getUsersFile');

/**
 * Авторизация в yandex-team паспорте
 */

module.exports = async () => {
    await browser.url('https://tariff-editor.taxi.tst.yandex-team.ru/');
    const currentUrl = await browser.getUrl();
    if (currentUrl.includes('passport')) {
        const users = await getUsersFile('./users.json');
        await browser.$('[name="login"]').setValue(users.robot.login);
        await browser.$('[name="passwd"]').setValue(users.robot.password);
        await browser.$('[type="submit"]').click();
    }
    await browser.$('.WelcomePage').waitForDisplayed({timeout: 20000});
};
