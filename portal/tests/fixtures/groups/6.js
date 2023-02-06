module.exports = function() {
    return req([
        service.zen({
            id: 'fakeservice',
            notifications: [
                notification({ id: 'rcnt0', text: texts.zen[0], mtime: dates.recent[5] }),
                notification({ id: 'rcnt1', text: texts.zen[1], mtime: dates.recent[4], preview: previews.afisha }),
                notification({ id: 'rcnt2', text: texts.zen[2], mtime: dates.recent[3] }),
                notification({ id: 'rcnt3', text: texts.zen[3], mtime: dates.recent[2], preview: previews.kinopoisk }),
                notification({ id: 'rcnt4', text: texts.zen[4], mtime: dates.recent[1] }),
                notification({ id: 'rcnt5', text: texts.zen[0], mtime: dates.recent[0] }),
            ],
        }),
    ]);
};
