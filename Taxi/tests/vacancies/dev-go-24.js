const Vacancy = require('../../page/Vacancy');

describe('Вакансии: выбранная вакансия: форма: валидация полей: отсутствие', () => {

    const DATA = {
        main: 'Не все обязательные поля заполнены верно.',
        field: 'Это поле обязательно',
        // поля, у которых отобразится сообщении валидации
        // если они не будут заполнены
        fields: [
            {index: 5, name: 'Резюме файлом'},
            {index: 7, name: 'Имя'},
            {index: 8, name: 'Фамилия'},
            {index: 9, name: 'Телефон'},
            {index: 10, name: 'Email'},
            {index: 12, name: 'Соглашение'},
        ],
        // дополнительное поле, у которого отобразится сообщении валидации
        // если оно выбрано в переключателе
        extra: {
            index: 6, name: 'Резюме ссылкой',
        },
    };

    it('Открыть страницу вакансии', () => {
        Vacancy.goTo(Vacancy.checkPaths.pop());
    });

    it('Отображается форма отправки резюме', () => {
        Vacancy.switchToForm();
    });

    it('Нажать на кнопку отправки резюме', () => {
        Vacancy.formBlock.submit.click();
    });

    it('Отобразилось общее сообщение валидации', () => {
        expect(Vacancy.formBlock.validation.main).toHaveTextEqual(DATA.main);
    });

    it(`Отобразилось ${DATA.fields.length} сообщений валидации под полями в форме`, () => {
        expect(Vacancy.formBlock.validation.fields).toHaveElemLengthEqual(DATA.fields.length);
    });

    DATA.fields.forEach(({index, name}) => {
        it(`Сообщение валидации отобразилось у поля "${name}"`, () => {
            expect(Vacancy.getSurveyGroup(index, 'validation')).toHaveTextEqual(DATA.field);
        });
    });

    it('Выбрать отправку резюме ссылкой', () => {
        Vacancy.switchCvToLink();
    });

    it('Нажать на кнопку отправки резюме', () => {
        Vacancy.formBlock.submit.click();
    });

    it(`Сообщение валидации отобразилось у поля "${DATA.extra.name}"`, () => {
        expect(Vacancy.getSurveyGroup(DATA.extra.index, 'validation'))
            .toHaveTextEqual(DATA.field);
    });

    it(`Заполнить поле "${DATA.extra.name}"`, () => {
        Vacancy.getSurveyGroup(DATA.extra.index, 'input').setValue(Math.random());
    });

    it('Нажать на кнопку отправки резюме', () => {
        Vacancy.formBlock.submit.click();
    });

    it(`Сообщение валидации не отобразилось у поля "${DATA.extra.name}"`, () => {
        expect(Vacancy.getSurveyGroup(DATA.extra.index, 'validation')).not.toHaveElemExist();
    });

});
