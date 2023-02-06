const dict = require('../../../pagesDict');
const phonePage = new dict.phonePage();

describe('Наличие элементов страницы /phone', () => {
    it('Элементы отображаются при открытии страницы', () => {
        phonePage.open();
        phonePage.checkScreenshot('selfreg-phone');
    });
});
