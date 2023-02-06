const ReportsSegments = require('../../../page/ReportsSegments');

describe('Добавить/удалить комментарий к записи водителя: статус', () => {

    const DATA = {
        status: [
            {
                name: 'Не работает',
                index: 0,
            },
            {
                name: 'Уволен',
                index: 2,
            },
            {
                name: 'Работает',
                index: 1,
            },
        ],
    };

    it('Открыть страницу сегментов водителей', () => {
        ReportsSegments.goTo();
    });

    DATA.status.forEach(({name, index}) => {

        describe(name, () => {

            it('Открыть редактирование комментария второго водителя', () => {
                ReportsSegments.getCells({tr: 2, td: 6, skipWait: true}).$('button').click();
            });

            it(`Изменить статус водителя на "${name}"`, () => {
                ReportsSegments.sidebarComments.status.click();
                ReportsSegments.selectOption[index].click();
            });

            it('Нажать кнопку сохранить', () => {
                ReportsSegments.sidebarComments.buttons.save.click();
            });

            it(`В таблице отображается выбранный статус водителя "${name}"`, () => {
                expect(ReportsSegments.getCells({tr: 2, td: 1})).toHaveTextEqual(name);
            });

        });

    });

});
