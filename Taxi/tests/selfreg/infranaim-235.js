const phonePage = require('../../pageobjects/selfreg/page.selfreg.phone');

describe('Наличие элементов страницы /phone', () => {
    it('Элементы отображаются при открытии страницы', () => {
        phonePage.open();
        phonePage.checkScreenshot('selfreg-phone');
    });
});
