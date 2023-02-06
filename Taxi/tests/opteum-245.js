const ParkProfile = require('../page/ParkProfile');
const {assert} = require('chai');

describe('Профиль партнёра: проверка тултипов', () => {
    let tooltipTextExpect;

    it('Открыть страницу профиля партнёра', () => {
        ParkProfile.goTo();
    });

    it('Контактый телефон для пассажиров соответствует ожиданиям', () => {
        ParkProfile.tooltipsArray[0].moveTo();

        assert.equal(ParkProfile.tooltipText.getText(),
            'Введите номер в международном формате для связи пассажиров с вашим таксопарком. Например: +79000000000');
    });

    it('Контактый телефон для водителей соответствует ожиданиям', () => {
        ParkProfile.tooltipsArray[1].moveTo();

        assert.equal(ParkProfile.tooltipText.getText(),
            'Введите номер телефона в международном формате, чтобы водители могли связаться с вами. Например: +79000000000');
    });

    it('Email соответствует ожиданиям', () => {
        ParkProfile.tooltipsArray[2].moveTo();

        assert.equal(ParkProfile.tooltipText.getText(),
            'Введите адрес электронной почты для связи с вами');
    });

    it('График работы соответствует ожиданиям', () => {
        ParkProfile.tooltipsArray[3].moveTo();
        tooltipTextExpect = 'Укажите график работы вашего таксопарка. Например:\nпн. — пт. с 9:00 до 18:00, сб. с 9:00 до 16:00, вс. — выходной';
        assert.equal(ParkProfile.tooltipText.getText().replace(/\s+/g, ''), tooltipTextExpect.replace(/\s+/g, ''));
    });

    it('Адрес таксопарка соответствует ожиданиям', () => {
        ParkProfile.tooltipsArray[4].moveTo();

        assert.equal(ParkProfile.tooltipText.getText(),
            'Введите адрес вашего таксопарка');
    });

    it('Условия вывода денежных средств соответствует ожиданиям', () => {
        ParkProfile.tooltipsArray[5].moveTo();

        assert.equal(ParkProfile.tooltipText.getText(),
            'Введите условия вывода денежных средств. Например: моментальный, еженедельный и т.д');
    });

    it('Дополнительная информация соответствует ожиданиям', () => {
        ParkProfile.tooltipsArray[6].moveTo();
        tooltipTextExpect = 'Здесь можно указать дополнительную информацию. Например: каналы в мессенджерах, акции, ссылки на ваши соцсети и т.д.\nПисать номера банковских карт категорически запрещено';
        assert.equal(ParkProfile.tooltipText.getText().replace(/\s+/g, ''), tooltipTextExpect.replace(/\s+/g, ''));
    });
});
