const dict = require('../../../pagesDict');
const citizenshipPage = new dict.citizenshipPage;

describe('Наличие элементов страницы /citizenship', () => {
    it('пройти до страницы /citizenship', () => {
        citizenshipPage.open();
    });

    it('элементы отображаются при открытии страницы', () => {
        citizenshipPage.BlockHeader.click();
        citizenshipPage.checkScreenshot('selfreg-sitizenship');
    });
});
