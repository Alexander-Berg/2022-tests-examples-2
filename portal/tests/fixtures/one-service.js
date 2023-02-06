module.exports = function() {
    return req([
        service({
            name: 'Я.Антивирус',
            id: 'fakeservice1',
            notifications: [
                notification({ id: 'rcnt0', text: 'Доступно 123 новых обновления', preview: null, important: true, mtime: new Date(new Date().setHours(12, 0, 0, 0) - 30 * 1000 - 10 * 60 * 1000).toISOString() }),
                notification({ id: 'rcnt1', text: 'Найдено 123 вируса', preview: previews.yandex2, important: true, mtime: new Date(new Date().setHours(12, 0, 0, 0) - 30 * 1000 - 12 * 60 * 1000).toISOString() }),
            ],
        }),
    ]);
};
