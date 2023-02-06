const dict = require('../../../pagesDict');
const placementPage = new dict.placementPage();
const vehiclePage = new dict.vehiclePage();
const citizenshipPage = new dict.citizenshipPage();
const personalPage = new dict.personalPage();
const taxiDeliveryVacancyPage = new dict.TaxiDeliveryVacancyPage();

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
