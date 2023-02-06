module.exports = function() {
    return req([
        service.yandex({
            id: 'fakeservice',
            notifications: [
                notification({ id: 'rcnt0', text: texts.market[0], mtime: dates.recent[4] }),
                notification({ id: 'rcnt1', text: texts.market[1], mtime: dates.recent[3] }),
                notification({ id: 'rcnt2', text: texts.market[2], mtime: dates.recent[2] }),
                notification({ id: 'rcnt3', text: texts.market[3], mtime: dates.recent[1] }),
                notification({ id: 'rcnt4', text: texts.market[4], mtime: dates.recent[0], preview: previews.plus }),
            ],
        }),
    ]);
};
