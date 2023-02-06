module.exports = function() {
    return req([
        service.q({
            notifications: [
                notification({
                    id: 'rcnt0',
                    text: texts.q[1],
                    mtime: dates.recent[4],
                    is_new: false,
                    is_read: true,
                    avatar: avatars.default,
                }),
            ],
        }),
    ]);
};
