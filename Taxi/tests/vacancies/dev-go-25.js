const Vacancy = require('../../page/Vacancy');

describe('Вакансии: выбранная вакансия: форма: загрузка файла', () => {

    const DATA = {
        files: {
            correct: 'cv.pdf',
            big: 'random11mb.dat',
        },
        popup: {
            ok: 'Размер загружаемых файлов превышает 10 МБ',
            limit: 'Можно прикрепить не более 1 файла',
        },
    };

    it('Открыть страницу вакансии', () => {
        Vacancy.goTo(Vacancy.checkPaths.pop());
    });

    it('Отображается форма отправки резюме', () => {
        Vacancy.switchToForm();
    });

    it('Загрузить файл больше 10мб', () => {
        Vacancy.uploadCv(DATA.files.big);
    });

    it('Отобразилось сообщение загрузки большого файла', () => {
        expect(Vacancy.formBlock.popup).toHaveTextEqual(DATA.popup.ok);
    });

    it('Загрузить корректный файл', () => {
        Vacancy.uploadCv(DATA.files.correct);
    });

    it('В списке загруженных файлов отобразилось резюме', () => {
        expect(Vacancy.getSurveyGroup(5, 'fileName')).toHaveTextEqual(DATA.files.correct);
    });

    it('Загрузить файл ещё раз', () => {
        Vacancy.uploadCv(DATA.files.correct);
    });

    it('Отобразилось сообщение превышения количества файлов', () => {
        expect(Vacancy.formBlock.popup).toHaveTextEqual(DATA.popup.limit);
    });

    it('Нажать на крестик удаления файла', () => {
        Vacancy.getSurveyGroup(5, 'fileDelete').click();
    });

    it('В списке нет загруженных файлов', () => {
        expect(Vacancy.getSurveyGroup(5, 'fileName')).not.toHaveElemExist();
    });

});
