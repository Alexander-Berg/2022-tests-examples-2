const SupportMessagesList = require('../../page/SupportMessagesList.js');

const driverLicense = '5555566610';
const criterion = 'По ВУ';

describe('Поиск обращений: по ВУ', () => {
    it('открыть раздел "Мои обращения"', () => {
        SupportMessagesList.goTo();
    });

    it('В критерия поиска выбрать "По ВУ"', () => {
        SupportMessagesList.filters.criterion.click();
        SupportMessagesList.selectDropdownItem(criterion);
    });

    it(`В поле поиска указать номер ВУ ${driverLicense}`, () => {
        SupportMessagesList.filters.searchInput.setValue(driverLicense);
        browser.pause(2000);
        SupportMessagesList.getRow(1).click();
        SupportMessagesList.supportChatBlock.waitForDisplayed();
        SupportMessagesList.supportChat.infoMessage.driverLicense.scrollIntoView();
        expect(SupportMessagesList.supportChat.infoMessage.driverLicense).toHaveTextContaining(driverLicense);
    });
});
