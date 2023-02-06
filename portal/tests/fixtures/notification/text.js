module.exports = function() {
    return req([
        service.market({
            notifications: [
                notification({
                    id: 'rcnt0',
                    text: texts.market[1],
                    mtime: dates.recent[4],
                }),
            ],
        }),
    ]);
};
