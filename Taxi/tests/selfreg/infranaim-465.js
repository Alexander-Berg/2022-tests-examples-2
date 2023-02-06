const { assert } = require('chai');
const dict = require('../../../pagesDict');
const placementPage = new dict.placementPage();
const vehiclePage = new dict.vehiclePage();
const citizenshipPage = new dict.citizenshipPage();
const personalPage = new dict.personalPage();
const lavkaVacancyPage = new dict.lavkaVacancyPage();
const lavkaEducation = new dict.lavkaEducationPage();

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
        lavkaVacancyPage.checkScreenshot('selfreg-lavkaVacancy');
        lavkaVacancyPage.goNext();
    });

    it('сравнить скриншотом страницу обучения лавки', () => {
        lavkaEducation.checkScreenshot('selfreg-lavkaEducation');
    });

    it('перейти на страницу обучения', () => {
        lavkaEducation.goNext();
        // eslint-disable-next-line no-undef
        assert.match(browser.getUrl(), /.*education-front.eda.tst.yandex.net.*/);
    });
});
