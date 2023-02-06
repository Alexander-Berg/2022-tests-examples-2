const { assert } = require('chai');
const placementPage = require('../../pageobjects/selfreg/page.selfreg.placement');
const vehiclePage = require('../../pageobjects/selfreg/page.selfreg.vehicle-type');
const citizenshipPage = require('../../pageobjects/selfreg/page.selfreg.citizenship');
const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');
const edaDeliveryVacancyPage = require('../../pageobjects/selfreg/page.selfreg.edaDeliveryVacancy');
const edaDeliveryEducatonPage = require('../../pageobjects/selfreg/page.selfreg.edaDeliveryEducation');

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
        /* eslint-disable */
        assert.match(browser.getUrl(), /.*education-front.eda.tst.yandex.net.*/);
        /* eslint-enable */
    });
});
