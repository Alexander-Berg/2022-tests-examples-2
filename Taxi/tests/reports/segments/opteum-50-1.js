const ReportsSegments = require('../../../page/ReportsSegments');
const {nanoid} = require('nanoid');

const getFirstDriverComment = () => ReportsSegments.getCells({tr: 1, td: 6, skipWait: true});

describe('Добавить/удалить комментарий к записи водителя: комментарий', () => {

    const DATA = {
        header: 'Редактирование',
        comment: `${nanoid()} ${nanoid(5)}`,
        buttons: {
            cancel: 'Отмена',
            save: 'Сохранить',
        },
        toast: 'Комментарий сохранен',
    };

    it('Открыть страницу сегментов водителей', () => {
        ReportsSegments.goTo();
    });

    it('Открыть редактирование комментария первого водителя', () => {
        getFirstDriverComment().$('button').click();
    });

    it('Отобразился сайдбар редактирования комментария', () => {
        expect(ReportsSegments.sidebarComments.header).toHaveTextEqual(DATA.header);
    });

    it(`В сайдбаре отображается кнопка "${DATA.buttons.cancel}"`, () => {
        expect(ReportsSegments.sidebarComments.buttons.cancel).toHaveTextEqual(DATA.buttons.cancel);
    });

    it(`В сайдбаре отображается кнопка "${DATA.buttons.save}"`, () => {
        expect(ReportsSegments.sidebarComments.buttons.save).toHaveTextEqual(DATA.buttons.save);
    });

    it('Стереть комментарий', () => {
        ReportsSegments.clearWithBackspace(ReportsSegments.sidebarComments.input);
    });

    it('Нажать кнопку сохранить', () => {
        ReportsSegments.sidebarComments.buttons.save.click();
    });

    it('В таблице отображается пустой комментарий', () => {
        expect(getFirstDriverComment()).toHaveTextEqual('');
    });

    it('Открыть редактирование комментария первого водителя', () => {
        getFirstDriverComment().$('button').click();
    });

    it('Отобразился сайдбар редактирования комментария', () => {
        expect(ReportsSegments.sidebarComments.header).toHaveTextEqual(DATA.header);
    });

    it(`Написать комментарий "${DATA.comment}"`, () => {
        ReportsSegments.sidebarComments.input.setValue(DATA.comment);
    });

    it('Нажать кнопку сохранить', () => {
        ReportsSegments.sidebarComments.buttons.save.click();
    });

    it(`Отобразилось всплывающее сообщение "${DATA.toast}"`, () => {
        expect(ReportsSegments.toast).toHaveTextEqual(DATA.toast);
    });

    it(`В таблице отображается корректный комментарий "${DATA.comment}"`, () => {
        expect(getFirstDriverComment()).toHaveTextEqual(DATA.comment);
    });

});
