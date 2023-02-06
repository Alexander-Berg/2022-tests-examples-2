const { assert } = require('chai');
const placementPage = require('../../pageobjects/selfreg/page.selfreg.placement');
const vehiclePage = require('../../pageobjects/selfreg/page.selfreg.vehicle-type');
const citizenshipPage = require('../../pageobjects/selfreg/page.selfreg.citizenship');
const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');
const edaEducationPage = require('../../pageobjects/selfreg/page.selfreg.education-nse');
const shopVacancyPage = require('../../pageobjects/selfreg/page.selfreg.shopVacancy');

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
        /* eslint-disable */
        assert.match(browser.getUrl(), /.*education-front.eda.tst.yandex.net.*/);
        /* eslint-enable */
    });
});
