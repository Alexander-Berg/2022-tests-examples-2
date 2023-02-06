const placementPage = require('../../pageobjects/selfreg/page.selfreg.placement');
const vehiclePage = require('../../pageobjects/selfreg/page.selfreg.vehicle-type');
const citizenshipPage = require('../../pageobjects/selfreg/page.selfreg.citizenship');
const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');
const taxiDeliveryVacancyPage = require('../../pageobjects/selfreg/page.selfreg.taxiDeliveryVacancy');

describe('Рулетка вакансий: такси доставка', () => {
    it('пройти до страницы /placement', () => {
        placementPage.open();
    });

    const city = 'Брянск';
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
        taxiDeliveryVacancyPage.checkScreenshot('selfreg-taxiDeliveryVacancy');
    });
});
