const DetailsTab = require('../../page/driverCard/DetailsTab');
const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');

const driverLicense = '77783232';
const driverName = 'MAN Z.';
const startDate = '03.02.2022';
const tooltipText = `${driverName} привлечен ${startDate} в рамках оказания услуги по поиску и привлечению водителей с собственным транспортным средством`;

describe('Создание платного водителя: появление тултипа при вводе ВУ', () => {
    it('Нажать "+" в заголовке списка водителей', () => {
        DriversPage.goTo();
        DriversPage.addDriverButton.waitForDisplayed();
        DriversPage.addDriverButton.click();
        DriverCard.waitingLoadThisPage(15_000);
    });

    it(`Заполнить поле "Серия и номер ВУ" одним из ВУ платного найма: ${driverLicense}`, () => {
        DetailsTab.detailsBlock.driverLicense.waitForDisplayed();
        DetailsTab.detailsBlock.driverLicense.setValue(driverLicense);
        expect(DetailsTab.detailsBlock.paidToUs.tooltip).toBeDisplayed();
    });

    it('навести курсор на тултип платного найма', () => {
        DetailsTab.detailsBlock.paidToUs.tooltip.moveTo();
        DetailsTab.detailsBlock.paidToUs.popup.waitForDisplayed();
        expect(DetailsTab.detailsBlock.paidToUs.popup).toHaveText(tooltipText);
    });
});
