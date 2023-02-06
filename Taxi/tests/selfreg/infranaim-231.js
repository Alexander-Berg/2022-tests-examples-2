const startPage = require('../../pageobjects/selfreg/page.selfreg.start');

describe('Наличие элементов страницы "Стать курьером"', () => {
    it('Элементы отображаются при открытии страницы', () => {
        startPage.open();
        startPage.btnNext.waitForDisplayed();
        startPage.checkScreenshot('selfreg-welcome');
    });
});
