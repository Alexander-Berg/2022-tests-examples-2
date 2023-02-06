const Interview = require('../../page/Interview');

describe('Интервью: выбор направления', () => {

    const DATA = {
        title: 'Как подготовиться к очным интервью',
        buttons: [
            'backend',
            'frontend',
            'android',
            'iOS',
            'ML',
            'analytics',
            'DevOps',
            'QA',
        ],
    };

    it('Открыть страницу интервью', () => {
        Interview.goTo();
    });

    it('Отображается заголовок блока вакансий', () => {
        Interview.chooseBlock.title.scrollIntoView();
        expect(Interview.chooseBlock.title).toHaveTextEqual(DATA.title);
    });

    it('Отображаются кнопки выбора направления', () => {
        expect(Interview.chooseBlock.buttons).toHaveTextEqual(DATA.buttons);
    });

    it('Отображается выбранной первая кнопка направления', () => {
        expect(Interview.chooseBlock.selected).toHaveTextEqual(DATA.buttons[0]);
    });

    it('Отображаются корректный текст направления по умолчанию', () => {
        expect(Interview.chooseBlock.text).toHaveTextOk();
    });

    let displayText;

    DATA.buttons.forEach((button, i) => {
        // первая кнопка нажата по умолчанию, начинаем со следующей
        if (i > 0) {

            it(`Нажать на кнопку направления "${button}"`, () => {
                Interview.chooseBlock.buttons[i].click();
            });

            it(`Отображается выбранной кнопка "${button}"`, () => {
                expect(Interview.chooseBlock.selected).toHaveTextEqual(button);
            });

            it(`Отображается корректный текст направления "${button}"`, () => {
                expect(Interview.chooseBlock.text).toHaveTextOk();
            });

            it(`Текст нового выбранного направления "${button}" отличается от предыдущего "${DATA.buttons[i - 1]}"`, () => {
                expect(Interview.chooseBlock.text).not.toHaveTextEqual(displayText);
                displayText = Interview.chooseBlock.text.getText();
            });

        }
    });

});
