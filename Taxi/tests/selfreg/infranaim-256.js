const citizenshipPage = require('../../pageobjects/selfreg/page.selfreg.citizenship');
const vehiclePage = require('../../pageobjects/selfreg/page.selfreg.vehicle-type');

describe('Наличие элементов страницы /citizenship', () => {
    it('пройти до страницы /citizenship', () => {
        vehiclePage.open();
        vehiclePage.fill();
        vehiclePage.goNext();
    });

    it('элементы отображаются при открытии страницы', () => {
        citizenshipPage.BlockHeader.click();
        citizenshipPage.checkScreenshot('selfreg-sitizenship');
    });
});
