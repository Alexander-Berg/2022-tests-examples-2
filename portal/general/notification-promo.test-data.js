const mocks = require('./mocks');

for (const data of ['bg', 'left', 'service', 'personal']) {
    exports[data] = function (execView) {
        return execView('NotificationPromo', {}, {
            NotificationPromo: mocks[data],
            stat: {
                getAttr() {}
            }
        });
    };
}
