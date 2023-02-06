const dict = require('../../../pagesDict');
const placementPage = new dict.placementPage();

describe('Наличие элементов страницы /placement', () => {
    it('пройти до страницы /placement', () => {
        placementPage.open();
    });

    it('Элементы отображаются при открытии страницы', () => {
        placementPage.drpdwnCitizenship.waitForDisplayed();
        placementPage.checkScreenshot('selfreg-placement');
    });
});
