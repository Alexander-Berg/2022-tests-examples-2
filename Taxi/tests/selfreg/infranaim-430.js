const { assert } = require('chai');
const dict = require('../../../pagesDict');
const personalPage = new dict.personalPage;

describe('Негативные проверки поля "Дата рождения" страницы /personal-data', () => {
    it('пройти до страницы /personal-data', () => {
        personalPage.open();
    });

    const inputs = ['214', 'asfg', '2001.01.01', '21ю21.2000', '20040205'];
    inputs.forEach(text => {
        it(`ввести ${text} в Дата  рождения`, () => {
            personalPage.fillDateBirth(text);
            personalPage.calendar.waitForDisplayed();
            // eslint-disable-next-line no-undef
            browser.keys('Enter');
            assert.equal(personalPage.fldDateBirth.getText(), '');
        });
    });
});
