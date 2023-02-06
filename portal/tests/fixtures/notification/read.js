module.exports = function() {
    return req([
        service.market({
            notifications: [
                notification({
                    id: 'rcnt0',
                    text: texts.market[2],
                    mtime: dates.recent[4],
                    is_new: false,
                    is_read: true,
                }),
            ],
        }),
    ]);
};
