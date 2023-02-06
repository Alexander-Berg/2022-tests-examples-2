const ParkProfile = require('../page/ParkProfile');
const {randomNumLength} = require('../../../utils/number');

describe('Профиль партнёра: изменение телефона', () => {

    let initialPhoneNumber;

    it('Открыть страницу профиля партнёра', () => {
        ParkProfile.goTo();
    });

    it('сохранить номер телефона', () => {
        initialPhoneNumber = ParkProfile.contactPhone.getValue();
    });

    it('изменить телефон', () => {
        ParkProfile.contactPhone.click();
        ParkProfile.clearWithBackspace(ParkProfile.contactPhone);
        ParkProfile.type(ParkProfile.contactPhone, `+7${randomNumLength(10)}`);
    });

    it('сохранить страницу', () => {
        ParkProfile.saveButton.click();
    });

    it('обновить страницу', () => {
        browser.refresh();
    });

    it('сравнить номер телефона с номером из шага 2 - должны различаться', () => {
        expect(ParkProfile.contactPhone).not.toHaveAttribute('value', initialPhoneNumber);
    });

    it('вернуть исходные данные', () => {
        ParkProfile.contactPhone.click();
        ParkProfile.clearWithBackspace(ParkProfile.contactPhone);
        ParkProfile.type(ParkProfile.contactPhone, initialPhoneNumber);
        ParkProfile.saveButton.click();
    });
});
