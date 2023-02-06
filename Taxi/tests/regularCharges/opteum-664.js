const DetailsTab = require('../../page/driverCard/DetailsTab');
const RegularCharges = require('../../page/RegularCharges');

describe('Периодические списания: фильтрация по типу водителя: парковый', () => {
    const link = '/regular-charges?limit=40';
    const CHECKS_LIMIT = 10;

    it('Открыт раздел "Периодические списания"', () => {
        RegularCharges.open(link);
        RegularCharges.getRow().status.waitForDisplayed();
    });

    it('В фильтре выбора типа водителей указать "Парковые"', () => {
        RegularCharges.driverTypeFilter.click();
        RegularCharges.selectList[2].click();
    });

    for (let i = 0; i < CHECKS_LIMIT; i++) {
        it(`Списание ${i + 1} создано на Паркового водителя`, () => {
            browser.pause(1000);
            RegularCharges.getRow(i + 1).driver.click();
            RegularCharges.switchTab();
            DetailsTab.selfEmployedBlock.linkProfileButton.waitForDisplayed();
            expect(DetailsTab.selfEmployedBlock.linkProfileButton).toExist();
            expect(DetailsTab.selfEmployedBlock.sendRequestButton).toExist();
            browser.closeWindow();
            RegularCharges.switchTab(0);
        });
    }
});
