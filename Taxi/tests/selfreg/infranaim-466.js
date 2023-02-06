const { assert } = require('chai');
const dict = require('../../../pagesDict');
const placementPage = new dict.placementPage();
const vehiclePage = new dict.vehiclePage();
const citizenshipPage = new dict.citizenshipPage();
const personalPage = new dict.personalPage();
const edaEducationPage = new dict.edaEducationPage();
const shopVacancyPage = new dict.shopVacancyPage();

describe('Рулетка вакансий: сборщик заказов', () => {
    it('пройти до страницы /placement', () => {
        placementPage.open();
    });

    const city = 'Астрахань';
    it(`выбрать ${city}`, () => {
        placementPage.selectCity(city);
    });

    it('нажать кнопку далее', () => {
        placementPage.goNext();
    });

    it('нажать далее на странице /vehicle-page', () => {
        vehiclePage.goNext();
    });

    it('выбрать гражданство и нажать далее', () => {
        citizenshipPage.selectCitizenship();
        citizenshipPage.goNext();
    });

    it('заполнить /personal-data и нажать далее', () => {
        personalPage.fillForm();
        personalPage.goNext();
    });

    it('сравнить скриншот страницы вакансии сборщика заказов', () => {
        shopVacancyPage.checkScreenshot('selfreg-shopVacancy');
        shopVacancyPage.goNext();
    });

    it('сравнить скриншот страницы обучения еды', () => {
        edaEducationPage.checkScreenshot('selfreg-edaEducation');
    });

    it('перейти на страницу обучения', () => {
        edaEducationPage.goNext();
        // eslint-disable-next-line no-undef
        assert.match(browser.getUrl(), /.*education-front.eda.tst.yandex.net.*/);
    });
});
