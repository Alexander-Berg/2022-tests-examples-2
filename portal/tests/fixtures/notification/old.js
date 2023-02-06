module.exports = function() {
    return req([
        service.market({
            notifications: [
                notification({
                    id: 'rcnt0',
                    text: texts.market[0],
                    mtime: dates.veryOld[4],
                }),
            ],
        }),
    ]);
};
