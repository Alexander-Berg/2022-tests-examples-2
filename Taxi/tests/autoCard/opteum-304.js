const AutoCard = require('../../page/AutoCard');
const VehiclesPage = require('../../page/VehiclesPage');
const {assert} = require('chai');

let digitalboxCheckbox, isCheckboxChecked, lightboxCheckbox;

describe('Включение/выключение наклейки, lightbox/digitalbox в авто', () => {
    it('Открыть страницу автомобилей', () => {
        VehiclesPage.goTo();
    });

    it('Найти в поиске автомобиль 11111111111111111 и открыть его', () => {
        VehiclesPage.searchForAuto('11111111111111111');
    });

    it('В разделе комплектация и брендинг поменять чекбокс напротив "Наклейки" и сохранить', () => {
        isCheckboxChecked = AutoCard.stickersCheckbox.getAttribute('aria-checked');
        AutoCard.stickersCheckbox.click();
    });

    it('В разделе комплектация и брендинг проставить один из чекбоксов "Lightbox"/"Digitalbox"', () => {
        if (AutoCard.lightboxCheckbox.getAttribute('aria-checked') === 'false'
            && AutoCard.digitalboxCheckbox.getAttribute('aria-checked') === 'false') {
            AutoCard.lightboxCheckbox.click();
            lightboxCheckbox = 'true';
            digitalboxCheckbox = 'false';
        } else if (AutoCard.lightboxCheckbox.getAttribute('aria-checked') === 'false') {
            AutoCard.lightboxCheckbox.click();
            lightboxCheckbox = 'true';
            digitalboxCheckbox = 'false';
        } else {
            AutoCard.digitalboxCheckbox.click();
            lightboxCheckbox = 'false';
            digitalboxCheckbox = 'true';
        }
    });

    it('Сохранить изменения', () => {
        AutoCard.saveButton.click();
    });

    it('Обновить страницу', () => {
        browser.refresh();
        browser.pause(5000);
    });

    it('Проверить значения после изменений', () => {
        assert.equal(AutoCard.lightboxCheckbox.getAttribute('aria-checked'), lightboxCheckbox);
        assert.equal(AutoCard.digitalboxCheckbox.getAttribute('aria-checked'), digitalboxCheckbox);
        assert.equal(AutoCard.stickersCheckbox.getAttribute('aria-checked'), isCheckboxChecked === 'true' ? 'false' : 'true');
    });
});
