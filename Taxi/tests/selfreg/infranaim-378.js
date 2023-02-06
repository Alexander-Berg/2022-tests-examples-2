const { assert } = require('chai');
const placementPage = require('../../pageobjects/selfreg/page.selfreg.placement');
const vehiclePage = require('../../pageobjects/selfreg/page.selfreg.vehicle-type');
const citizenshipPage = require('../../pageobjects/selfreg/page.selfreg.citizenship');
const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');
const lavkaVacancyPage = require('../../pageobjects/selfreg/page.selfreg.lavkaVacancy');
const lavkaEducation = require('../../pageobjects/selfreg/page.selfreg.lavkaEducation');

describe('Рулетка вакансий: лавка', () => {
    it('пройти до страницы /placement', () => {
        placementPage.open();
    });

    const city = 'Белгород';
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

    it('сравнить скриншотом элементы страницы вакансии лавки', () => {
        lavkaVacancyPage.checkScreenshot('selfreg-lavkaVacansy');
        lavkaVacancyPage.goNext();
    });

    it('сравнить скриншотом страницу обучения лавки', () => {
        lavkaEducation.checkScreenshot('selfreg-lavkaEducation');
    });

    it('перейти на страницу обучения', () => {
        lavkaEducation.goNext();
        /* eslint-disable */
        assert.match(browser.getUrl(), /.*education-front.eda.tst.yandex.net.*/);
        /* eslint-enable */
    });
});
