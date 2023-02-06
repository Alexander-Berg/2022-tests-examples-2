const { assert } = require('chai');
const dict = require('../../../pagesDict');
const placementPage = new dict.placementPage();

describe('Негатив полей страницы placement', () => {
    it('пройти до страницы /placement', () => {
        placementPage.open();
    });

    it('выбрать город Москва', () => {
        placementPage.placeholderCity.waitForDisplayed();
        assert.isTrue(placementPage.placeholderCity.isDisplayed());
        placementPage.selectCity('Москва');
        assert.isFalse(placementPage.placeholderCity.isDisplayed());
        assert.equal(placementPage.activeCity.getText(), 'Москва');
    });

    it('выбрать гражданство Казахстан', () => {
        placementPage.drpdwnCitizenship.click();
        placementPage.selectDropdownItem('Казахстан');
        assert.isTrue(placementPage.placeholderCity.isDisplayed());
    });
});
