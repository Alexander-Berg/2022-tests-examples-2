const dict = require('../../../pagesDict');
const personalPage = new dict.personalPage;

describe('Наличие элементов страницы /personal-data', () => {
    it('пройти до страницы /placement', () => {
        personalPage.open();
    });

    it('элементы отображаются при открытии страницы', () => {
        personalPage.blockHeader.click();
        personalPage.checkScreenshot('selfreg-personalData');
    });
});
