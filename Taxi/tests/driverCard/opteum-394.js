const DetailsTab = require('../../page/driverCard/DetailsTab');
const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');

const driverName = 'opteum-110';
const linkToDriver = 'https://fleet.tst.yandex.ru/drivers/cf2bd1ed7f3e7ce45fdba6a7eb656472/details?park_id=7ad36bc7560449998acbe2c57a75c293&lang=ru&theme=day';

describe('Редактирование данных профиля водителя: заблокированные поля в табе "Детали"', () => {
    it(`Открыть карточку водителя у которого есть заблокированные для редактирования поля (водитель, созданный N дней назад): ${driverName}`, () => {
        DriversPage.goTo();
        browser.url(linkToDriver);
    });

    it('Проверить заблокированные поля в блоке "Детали"', () => {
        DetailsTab.checkBlockedFields();
        expect(DriverCard.blockedFieldsMessage.text).toBeDisplayed();
        expect(DriverCard.blockedFieldsMessage.link).toBeDisplayed();
    });

    it('Cсылка в сообщении "Некоторые поля недоступны для редактирования, для внесения изменений обратитесь в поддержку" ведёт в раздел "Мои обращения"', () => {
        const linkToSupportList = `https://fleet.tst.yandex.ru${DriverCard.blockedFieldsMessage.link.getAttribute('href')}`;
        browser.url(linkToSupportList);

        expect(browser).toHaveUrlContaining('support');
    });
});
