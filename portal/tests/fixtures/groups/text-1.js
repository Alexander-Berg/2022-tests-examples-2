module.exports = function() {
    return req([
        service.yandex({
            id: 'fakeservice',
            notifications: [
                notification({ id: 'rcnt0', text: texts.yandex[0], groupID: 'fakegroup', mtime: dates.veryOld[3] }),
                notification({ id: 'rcnt1', text: texts.yandex[1], groupID: 'fakegroup', mtime: dates.old[1] }),
                notification({ id: 'rcnt2', text: texts.yandex[2], groupID: 'fakegroup', mtime: dates.recent[2] }),
                notification({ id: 'rcnt3', text: texts.yandex[3], mtime: dates.recent[3] }),
                notification({ id: 'rcnt4', text: texts.yandex[4], mtime: dates.recent[4] }),
            ],
        }),
    ]);
};
