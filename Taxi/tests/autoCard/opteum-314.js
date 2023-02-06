const AutoCard = require('../../page/AutoCard');
const VehiclesPage = require('../../page/VehiclesPage');
const {assert} = require('chai');

let boostersDropdown,
    childSeat2BrandDropdown,
    childSeat2GroupDropdown,
    childSeatBrandDropdown,
    childSeatGroupDropdown,
    childSeatsDropdown;

describe('Настройка детских кресел и бустеров', () => {
    it('Открыть страницу автомобилей', () => {
        VehiclesPage.goTo();
    });

    it('Найти в поиске автомобиль М546АА99 и открыть его', () => {
        VehiclesPage.searchForAuto('М546АА99');
    });

    it('В разделе Комплектация и брендинг изменить значение в Бустеры', () => {
        AutoCard.boostersBlock.dropdown.waitForDisplayed();
        AutoCard.boostersBlock.dropdown.click();

        if (AutoCard.boostersBlock.dropdown.getText() !== '1') {
            AutoCard.boostersBlock.dropdownItems.b1.click();
            boostersDropdown = '1';
            return;
        }

        if (AutoCard.boostersBlock.dropdown.getText() === '1') {
            AutoCard.boostersBlock.dropdownItems.b2.click();
            boostersDropdown = '2';
        }
    });

    it('В разделе Комплектация и брендинг изменить значение в Детские кресла', () => {
        AutoCard.childSeatsBlock.dropdown.click();

        if (AutoCard.childSeatsBlock.dropdown.getText() !== '1') {
            AutoCard.childSeatsBlock.dropdownItems.s1.click();
            childSeatsDropdown = '1';
            return;
        }

        if (AutoCard.childSeatsBlock.dropdown.getText() === '1') {
            AutoCard.childSeatsBlock.dropdownItems.s2.click();
            childSeatsDropdown = '2';
        }
    });

    it('В разделе Комплектация и брендинг выбрать "Яндекс" в Марка кресла', () => {
        AutoCard.childSeatBrandBlock.dropdown.click();
        AutoCard.childSeatBrandBlock.dropdownItems.yandex.click();
        AutoCard.childSeatGroupDropdown.click();
        browser.keys('Enter');
        AutoCard.childSeatGroupDropdown.click();

        if (AutoCard.childSeatsBlock.dropdown.getText() === '1') {
            childSeatBrandDropdown = 'Яндекс';
            childSeatGroupDropdown = AutoCard.childSeatGroupDropdown.getText();
            return;
        }

        if (AutoCard.childSeatsBlock.dropdown.getText() === '2') {
            AutoCard.childSeat2BrandBlock.dropdown.click();
            AutoCard.childSeat2BrandBlock.dropdownItems.yandex.click();
            AutoCard.childSeat2GroupBlock.dropdown.click();
            browser.keys('Enter');
            AutoCard.childSeat2GroupBlock.dropdown.click();
            childSeatBrandDropdown = 'Яндекс';
            childSeatGroupDropdown = AutoCard.childSeatGroupDropdown.getText();
            childSeat2BrandDropdown = 'Яндекс';
            childSeat2GroupDropdown = AutoCard.childSeat2GroupBlock.dropdown.getText();
        }
    });

    it('Сохранить изменения', () => {
        AutoCard.saveButton.click();
    });

    it('Обновить страницу', () => {
        browser.refresh();
        AutoCard.boostersBlock.dropdown.waitForDisplayed();
    });

    it('Проверить значения после изменений', () => {
        assert.equal(AutoCard.boostersBlock.dropdown.getText(), boostersDropdown);
        assert.equal(AutoCard.childSeatsBlock.dropdown.getText(), childSeatsDropdown);
        assert.equal(AutoCard.childSeatBrandBlock.dropdown.getText(), childSeatBrandDropdown);
        assert.equal(AutoCard.childSeatGroupDropdown.getText(), childSeatGroupDropdown);

        if (AutoCard.childSeatsBlock.dropdown.getText() === '2') {
            assert.equal(AutoCard.childSeat2BrandBlock.dropdown.getText(), childSeat2BrandDropdown);
            assert.equal(AutoCard.childSeat2GroupBlock.dropdown.getText(), childSeat2GroupDropdown);
        }
    });
});
