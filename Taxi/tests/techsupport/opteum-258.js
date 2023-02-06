const SupportMessagesList = require('../../page/SupportMessagesList.js');

const vehicleNumber = 'е001кх77';
const criterion = 'По гос. номеру';

describe('Поиск обращений: по гос. номеру', () => {
    it('открыть раздел "Мои обращения"', () => {
        SupportMessagesList.goTo();
    });

    it('В критерия поиска выбрать "По гос. номеру"', () => {
        SupportMessagesList.filters.criterion.click();
        SupportMessagesList.selectDropdownItem(criterion);
    });

    it(`В поле поиска указать номер авто ${vehicleNumber}`, () => {
        SupportMessagesList.filters.searchInput.setValue(vehicleNumber);
        browser.pause(2000);
        SupportMessagesList.getRow(1).click();
        SupportMessagesList.supportChatBlock.waitForDisplayed();
        SupportMessagesList.supportChat.infoMessage.driverLicense.scrollIntoView();
        expect(SupportMessagesList.supportChat.infoMessage.driverLicense).toHaveTextContaining(vehicleNumber);
    });
});
