const DetailsTab = require('../../page/driverCard/DetailsTab');
const RegularCharges = require('../../page/RegularCharges');

describe('Периодические списания: фильтрация по типу водителя: СМЗ', () => {
    const link = '/regular-charges?limit=40';
    const CHECKS_LIMIT = 10;

    it('Открыт раздел "Периодические списания"', () => {
        RegularCharges.open(link);
        RegularCharges.getRow().status.waitForDisplayed();
    });

    it('В фильтре выбора типа водителей указать "СМЗ"', () => {
        RegularCharges.driverTypeFilter.click();
        RegularCharges.selectList[1].click();
    });

    for (let i = 0; i < CHECKS_LIMIT; i++) {
        it(`Списание ${i + 1} создано на СМЗ водителя`, () => {
            browser.pause(1000);
            RegularCharges.getRow(i + 1).driver.click();
            RegularCharges.switchTab();

            try {
                DetailsTab.selfEmployedBlock.unlinkRequestButton.waitForDisplayed();
                expect(DetailsTab.selfEmployedBlock.unlinkRequestButton).toExist();
            } catch {
                DetailsTab.selfEmployedBlock.repeatRequestButton.waitForDisplayed();
                expect(DetailsTab.selfEmployedBlock.repeatRequestButton).toExist();
            }

            expect(DetailsTab.selfEmployedBlock.linkProfileButton).not.toExist();

            browser.closeWindow();
            RegularCharges.switchTab(0);
        });
    }

});
