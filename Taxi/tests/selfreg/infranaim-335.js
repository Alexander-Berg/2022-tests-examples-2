const { assert } = require('chai');
const phonePage = require('../../pageobjects/selfreg/page.selfreg.phone');

describe('Действие по нажатию кнопки "Начать" /welcome', () => {
    it('Открылась правильная страница', () => {
        phonePage.open();
        // eslint-disable-next-line no-undef
        assert.equal(browser.getUrl(), 'https://courier-selfreg.eda.tst.yandex.net/phone');
    });
});
