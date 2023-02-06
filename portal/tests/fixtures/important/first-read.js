module.exports = function() {
    return req([
        service.q({
            notifications: [
                notification({ id: 'rcnt0', is_read: true, important: true, text: texts.q[0], mtime: dates.recent[4] }),
                notification({ id: 'rcnt1', important: true, text: texts.q[1], mtime: dates.recent[1] }),
                notification({ id: 'rcnt2', important: true, text: texts.q[2], mtime: dates.old[2] }),
                notification({ id: 'rcnt3', important: true, text: texts.q[3], mtime: dates.recent[1] }),
                notification({ id: 'rcnt4', important: true, text: texts.q[4], mtime: dates.recent[2] }),
            ],
        }),
    ]);
};
