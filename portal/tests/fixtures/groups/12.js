module.exports = function() {
    return req([
        service.market({
            id: 'fakeservice',
            notifications: [
                notification({ id: 'rcnt0', text: texts.market[0], mtime: dates.recent[9] }),
                notification({ id: 'rcnt1', text: texts.market[1], mtime: dates.recent[8] }),
                notification({ id: 'rcnt2', text: texts.market[2], mtime: dates.recent[7] }),
                notification({ id: 'rcnt3', text: texts.market[3], mtime: dates.recent[6] }),
                notification({ id: 'rcnt4', text: texts.market[4], mtime: dates.recent[5] }),
                notification({ id: 'rcnt5', text: texts.market[0], mtime: dates.recent[4] }),
                notification({ id: 'rcnt6', text: texts.market[0], mtime: dates.recent[3] }),
                notification({ id: 'rcnt7', text: texts.market[1], mtime: dates.recent[2] }),
                notification({ id: 'rcnt8', text: texts.market[2], mtime: dates.recent[1] }),
                notification({ id: 'rcnt9', text: texts.market[3], mtime: dates.recent[0] }),
                notification({ id: 'rcnt10', text: texts.market[4], mtime: dates.old[2] }),
                notification({ id: 'rcnt11', text: texts.market[0], mtime: dates.veryOld[2] }),
            ],
        }),
    ]);
};
