const Vacancy = require('../../page/Vacancy');

describe('Вакансии: выбранная вакансия: форма: отображение', () => {

    const DATA = {
        form: {
            title: 'Расскажите нам о себе',
            type: ['Файл с резюме', 'Ссылка на резюме'],
        },
        file: {
            title: 'Резюме',
            button: 'Выберите файл',
            limit: 'Один файл размером до 10 МБ.',
        },
        link: {
            title: 'Ссылка',
            placeholder: 'HeadHunter, Linkedin, Github или прочее',
        },
        fields: [
            {index: 7, name: 'Имя'},
            {index: 8, name: 'Фамилия'},
            {index: 9, name: 'Телефон'},
            {index: 10, name: 'Email'},
            {index: 11, name: 'Дополнительные сведения'},
        ],
        checkbox: 'Я соглашаюсь передать свои персональные данные, содержащиеся в анкете и всех приложенных файлах, в ООО «ЯНДЕКС» исключительно для того, чтобы группа компаний «Яндекс» могла предлагать мне вакансии.'
               + ' Я понимаю и соглашаюсь, что мои данные будут храниться и обрабатываться в ООО «ЯНДЕКС» в течение десяти лет, в соответствии с Федеральным законом «О персональных данных».',
        submit: 'Отправить',
    };

    Vacancy.checkPaths.forEach(path => {
        describe(path, () => {

            it('Открыть страницу вакансии', () => {
                Vacancy.goTo(path);
            });

            it('Отображается форма отправки резюме', () => {
                Vacancy.switchToForm();
            });

            it('Отображается заголовок формы', () => {
                expect(Vacancy.formBlock.title).toHaveTextEqual(DATA.form.title);
            });

            it('Отображается переключатель типа отправки файл-ссылка', () => {
                expect(Vacancy.formBlock.type.label).toHaveTextEqual(DATA.form.type);
            });

            it('Отображается заголовок отправки файла', () => {
                expect(Vacancy.getSurveyGroup(5, 'label')).toHaveTextEqual(DATA.file.title);
            });

            it('Отображается название кнопки отправки файла', () => {
                expect(Vacancy.getSurveyGroup(5, 'buttonText')).toHaveTextEqual(DATA.file.button);
            });

            it('Отображается текст лимита отправки', () => {
                expect(Vacancy.getSurveyGroup(5, 'limit')).toHaveTextEqual(DATA.file.limit);
            });

            DATA.fields.forEach(({index, name}) => {
                it(`Отображается поле ввода "${name}"`, () => {
                    Vacancy.getSurveyGroup(index, 'input').waitForDisplayed();
                    expect(Vacancy.getSurveyGroup(index, 'label')).toHaveTextEqual(name);
                });
            });

            it('Отображается чекбокс с корректным текстом', () => {
                expect(Vacancy.getSurveyGroup(12, 'checklabel')).toHaveTextEqual(DATA.checkbox);
            });

            it('Отображается кнопка отправки резюме', () => {
                expect(Vacancy.formBlock.submit).toHaveTextEqual(DATA.submit);
            });

            it('Выбрать отправку резюме ссылкой', () => {
                Vacancy.switchCvToLink();
            });

            it('Отображается заголовок отправки ссылки', () => {
                Vacancy.getSurveyGroup(6, 'label').waitForDisplayed();
                expect(Vacancy.getSurveyGroup(6, 'label')).toHaveTextEqual(DATA.link.title);
            });

            it('Отображается плейсхолдер отправки ссылки', () => {
                expect(Vacancy.getSurveyGroup(6, 'hint')).toHaveTextEqual(DATA.link.placeholder, {js: true});
            });

            it('Вернуть отправку резюме файлом', () => {
                Vacancy.formBlock.type.file.click();
            });

        });
    });

});
