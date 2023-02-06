const SupportMessagesList = require('../../page/SupportMessagesList.js');

const theme = 'Заказать обратный звонок';
const allThemes = 'Любая тема';

const selectTheme = themeText => {
    SupportMessagesList.filters.theme.click();
    SupportMessagesList.selectDropdownItem(themeText);
    browser.pause(2000);
};

describe('Фильтрация обращений по теме', () => {
    it('открыть раздел "Мои обращения"', () => {
        SupportMessagesList.goTo();
    });

    it('Выбрать любую тему по которой есть обращения"', () => {
        selectTheme(theme);
    });

    it('отображается список обращений согласно фильтру', () => {
        expect(SupportMessagesList.getColumn(3)).toHaveTextArrayEachEqual(theme);
    });

    it('Выбрать тему "Любая тема"', () => {
        selectTheme(allThemes);
    });

    it('отображается список всех обращений', () => {
        const elems = SupportMessagesList.getColumn(3)
            .map(elem => elem.getText())
            .filter(elem => elem !== theme);

        expect(elems.length).toBeGreaterThan(0);
    });
});
