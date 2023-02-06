const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');

describe('Наличие элементов страницы /personal-data', () => {
    it('пройти до страницы /placement', () => {
        personalPage.open();
    });

    it('элементы отображаются при открытии страницы', () => {
        personalPage.blockHeader.click();
        personalPage.checkScreenshot('selfreg-personalData');
    });
});
