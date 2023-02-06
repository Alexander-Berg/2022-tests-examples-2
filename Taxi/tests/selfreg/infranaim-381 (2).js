const { assert } = require('chai');
const dict = require('../../../pagesDict');
const placementPage = new dict.placementPage();
const vehiclePage = new dict.vehiclePage();
const citizenshipPage = new dict.citizenshipPage();
const personalPage = new dict.personalPage();
const edaDeliveryVacancyPage = new dict.edaDeliveryVacancyPage();
const edaDeliveryEducatonPage = new dict.edaDeliveryEducatonPage();

describe('Рулетка вакансий: еда курьер', () => {
    it('пройти до страницы /placement', () => {
        placementPage.open();
    });

    const city = 'Москва';
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

    it('сравнить скриншот страницы вакансии такси доставка', () => {
        edaDeliveryVacancyPage.checkScreenshot('selfreg-edaDeliveryVacancy');
    });

    it('нажать кнопку далее второй раз', () => {
        edaDeliveryVacancyPage.goNext();
        edaDeliveryEducatonPage.BlockHeader.click();
        edaDeliveryEducatonPage.checkScreenshot('selfreg-edaDeliveryEducation');
    });

    it('перейти на страницу обучения', () => {
        edaDeliveryEducatonPage.goNext();
        // eslint-disable-next-line no-undef
        assert.match(browser.getUrl(), /.*education-front.eda.tst.yandex.net.*/);
    });
});
