module.exports = function() {
    return req([
        service.zen({
            notifications: [
                notification({ id: 'rcnt0', important: true, text: texts.zen[0], groupID: 'fakegroup', mtime: dates.recent[2] }),
                notification({ id: 'rcnt1', text: texts.zen[1], groupID: 'fakegroup', mtime: dates.recent[3] }),
                notification({ id: 'rcnt2', important: true, text: texts.zen[2], groupID: 'fakegroup', mtime: dates.recent[1], avatar: avatars.default }),
                notification({ id: 'rcnt3', important: true, is_new: false, is_read: true, text: texts.zen[3], mtime: dates.recent[0], preview: previews.zen }),
                notification({ id: 'rcnt4', text: texts.zen[4], mtime: dates.recent[4] }),
            ],
        }),
    ]);
};
