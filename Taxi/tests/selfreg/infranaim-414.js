const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');
const dict = require('../../../pagesDict');
const startPage = new dict.startPage;
const PhonePage = new dict.phonePage;
const PlacementPage = new dict.placementPage;
const VehiclePage = new dict.vehiclePage;
const CitizenshipPage = new dict.citizenshipPage;
const personalPage = new dict.personalPage;
const page = new PageSelfreg();

const path = '/?vacancy=eda_pedestrian';
describe(`Верстка "Стать курьером" с принудительным выбором вакансии ${path}`, () => {
    it('открыть главную страницу с гет-параметрами', () => {
        page.open(path);
    });

    it('проходим с валидными данными до страницы phone', () => {
        startPage.goNext();
    });

    it('проходим с валидными данными до страницы placement', () => {
        PhonePage.fillPhoneNumber();
        PhonePage.btnGetCode.click();
        PhonePage.confirmCode();
        PhonePage.btnNext.click();
    });

    it('проходим с валидными данными до страницы vehicle-type', () => {
        PlacementPage.fill();
        PlacementPage.goNext();
    });

    it('проходим с валидными данными до страницы citizenship', () => {
        VehiclePage.goNext();
    });

    it('проходим с валидными данными до страницы personal-data', () => {
        CitizenshipPage.fill();
        CitizenshipPage.goNext();
    });
    it('проходим с валидными данными до страницы service-shop', () => {
        personalPage.fillSecondName('Тестович');
        personalPage.fillFirstName('Тест');
        personalPage.fillContactEmail('haha@go.brrrr');
        personalPage.fillDateBirth('11.09.2001');
        personalPage.goNext();
    });

    it('сравниваем скриншот selfreg-edaDeliveryVacancy', () => {
        page.checkScreenshot('selfreg-edaDeliveryVacancy');
    });
});
