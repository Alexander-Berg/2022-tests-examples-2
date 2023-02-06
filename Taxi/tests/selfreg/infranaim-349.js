const { assert } = require('chai');
const citizenshipPage = require('../../pageobjects/selfreg/page.selfreg.citizenship');

describe('Выбор гражданства "Российская федерация" /citizenship', () => {
    it('пройти до страницы /citizenship', () => {
        citizenshipPage.open();
    });

    it('выбрать Россию в дропдауне стран', () => {
        citizenshipPage.selectCitizenship('rus');
        assert.equal(citizenshipPage.drpdwnCitizenship.getText(), 'Российская Федерация');
    });
});
