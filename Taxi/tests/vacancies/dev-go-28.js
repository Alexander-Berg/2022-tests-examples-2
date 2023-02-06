const Vacancy = require('../../page/Vacancy');

describe('Вакансии: выбранная вакансия: форма: валидация полей: некорректные данные', () => {

    const DATA = {
        // строка, которую будем писать во все поля
        testValue: 'test',
        // поля, которые заполним
        fields: [
            {index: 6, name: 'Резюме ссылкой'},
            {index: 7, name: 'Имя'},
            {index: 8, name: 'Фамилия'},
            {index: 9, name: 'Телефон', validation: 'Введите корректный номер телефона'},
            {index: 10, name: 'Email', validation: 'Введите корректный адрес электронной почты.'},
        ],
        // поля, в которых поставим чекбокс
        extra: [
            {index: 12, name: 'Соглашение'},
        ],
    };

    it('Открыть страницу вакансии', () => {
        Vacancy.goTo(Vacancy.checkPaths.pop());
    });

    it('Отображается форма отправки резюме', () => {
        Vacancy.switchToForm();
    });

    it('Выбрать отправку резюме ссылкой', () => {
        Vacancy.switchCvToLink();
    });

    DATA.fields.forEach(({index, name}) => {
        it(`Заполнить поле "${name}"`, () => {
            Vacancy.getSurveyGroup(index, 'input').setValue(DATA.testValue);
        });
    });

    DATA.extra.forEach(({index, name}) => {
        it(`Поставить чекбокс в поле "${name}"`, () => {
            Vacancy.getSurveyGroup(index, 'checkbox').click();
            expect(Vacancy.getSurveyGroup(index, 'checkbox')).toHaveElemSelected();
        });
    });

    it('Нажать на кнопку отправки резюме', () => {
        Vacancy.formBlock.submit.click();
    });

    DATA.fields.forEach(({index, name, validation}) => {
        validation && it(`Отобразилось сообщение валидации у поля "${name}"`, () => {
            expect(Vacancy.getSurveyGroup(index, 'validation')).toHaveTextEqual(validation);
        });
    });

});
