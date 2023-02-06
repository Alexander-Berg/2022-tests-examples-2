const dict = require('../../../pagesDict');
const startPage = new dict.startPage;

describe('Наличие элементов страницы "Стать курьером"', () => {
    it('Элементы отображаются при открытии страницы', () => {
        startPage.open();
        startPage.btnNext.waitForDisplayed();
        startPage.checkScreenshot('selfreg-welcome');
    });
});
