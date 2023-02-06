module.exports = function() {
    return req([
        service({
            name: 'Я.Антивирус',
            id: 'fakeservice1',
            notifications: [
                notification({ id: 'rcnt0', text: 'Доступно 123 новых обновления', mtime: new Date(new Date().setHours(12, 0, 0, 0) - 30 * 1000 - 5 * 60 * 1000).toISOString() }),
                notification({ id: 'rcnt1', text: 'Найдено 123 вируса', preview: previews.yandex2, important: true, mtime: new Date(new Date().setHours(12, 0, 0, 0) - 30 * 1000 - 11 * 60 * 1000).toISOString() }),
            ],
        }),
        service({
            name: 'Я.Чистка',
            id: 'fakeservice2',
            notifications: [
                notification({ id: 'rcnt4', text: 'Экран протетр', preview: previews.yandex2, important: true, mtime: new Date(new Date().setHours(12, 0, 0, 0) - 30 * 1000 - 9 * 60 * 1000).toISOString() }),
                notification({ id: 'rcnt5', text: 'Кулеры продуты', preview: previews.yandex2, important: true, mtime: new Date(new Date().setHours(12, 0, 0, 0) - 30 * 1000 - 11 * 60 * 1000).toISOString() }),
                notification({ id: 'rcnt6', text: 'Обои поменяны', preview: previews.yandex2, important: true, mtime: new Date(new Date().setHours(12, 0, 0, 0) - 30 * 1000 - 12 * 60 * 1000).toISOString() }),
                notification({ id: 'rcnt7', text: 'Биткоин замайнен', preview: previews.yandex2, important: true, mtime: new Date(new Date().setHours(12, 0, 0, 0) - 30 * 1000 - 13 * 60 * 1000).toISOString() }),
                notification({ id: 'rcnt8', text: '123 пароля было изменено', preview: previews.yandex2, important: true, mtime: new Date(new Date().setHours(12, 0, 0, 0) - 30 * 1000 - 14 * 60 * 1000).toISOString() }),
            ],
        }),
    ]);
};
