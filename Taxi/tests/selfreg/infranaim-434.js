const { assert } = require('chai');
const dict = require('../../../pagesDict');
const phonePage = new dict.phonePage();

describe('Действие по нажатию кнопки "Начать" /welcome', () => {
    it('Открылась правильная страница', () => {
        phonePage.open();
        // eslint-disable-next-line no-undef
        assert.equal(browser.getUrl(), 'https://courier-selfreg.eda.tst.yandex.net/phone');
    });
});
