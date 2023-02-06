import { Browser } from 'hermione';

// стандартный clearValue в chrome очищает поле не тригеря стандартные события onChange.
// Соответственно реакт не узнает об изменениях и восстанавливает предыдущее значение.
const customClearValue: Browser['customClearValue'] = function(
    this: Browser,
    selector?: string,
) {
    return (
        this.customClick(selector)
            // Первый раз keys вызывается для нажатия этих кнопок
            .then(() => this.keys(['Control', 'Shift']))
            .then(() => this.keys(['a']).keys(['a']))
            .then(() => this.keys(['Control', 'Shift']))
            .then(() => this.keys(['Backspace']).keys(['Backspace']))
    );
};

export { customClearValue };
