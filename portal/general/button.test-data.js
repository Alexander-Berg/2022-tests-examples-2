exports.simple = function (execView) {
    return execView('Button', {
        mods: {
            theme: 'action2'
        },
        content: 'Найти и открыть серп'
    });
};

exports.disabled = function (execView) {
    return execView('Button', {
        mods: {
            theme: 'action2',
            disabled: 'yes'
        },
        content: 'Найти и открыть серп'
    });
};
