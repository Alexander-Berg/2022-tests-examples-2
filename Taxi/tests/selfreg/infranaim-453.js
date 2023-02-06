const { assert } = require('chai');
const dict = require('../../../pagesDict');
const placementPage = new dict.placementPage();

describe('Негатив кнопки "Дальше" страницы placement', () => {
    it('открыть страницу /placement', () => {
        placementPage.open();
    });

    it('нажать на кнопку "Дальше"', () => {
        placementPage.goNext();
        assert.equal(placementPage.hintCity.getText(), 'Выберите значение');
        // eslint-disable-next-line no-undef
        assert.equal(browser.getUrl(), 'https://courier-selfreg.eda.tst.yandex.net/placement');
    });

    it('выбрать гражданство Казахстан', () => {
        placementPage.drpdwnCitizenship.click();
        placementPage.selectDropdownItem('Казахстан');

        let availableCity = placementPage.itemsAvailable;
        availableCity = availableCity.map(el => el.getText());

        assert.notInclude(availableCity, 'Москва');
    });
});
