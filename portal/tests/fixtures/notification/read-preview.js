module.exports = function() {
    return req([
        service.yandex({
            notifications: [
                notification({
                    id: 'rcnt0',
                    text: texts.yandex[0],
                    mtime: dates.recent[4],
                    is_new: false,
                    is_read: true,
                    preview: previews.plus,
                }),
            ],
        }),
    ]);
};
