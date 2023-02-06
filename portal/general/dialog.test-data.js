const mocks = require('./mocks');

exports.notificationsSimple = function (execView) {

    var popup = execView('TrafinfoPopup', mocks.notificationsSimple);

    var dialog = execView('Dialog', {
        type: 'notifications',
        visible: true,
        attrs: {
            'data-index': 0
        },
        content: popup.content,
        cut: popup.extra,
        close: {
            type: 'button'
        }
    }, {
        JSON: {}
    });

    return '<div class="body__wrapper">' + execView('Dialogs', {
        list: ['Dialog_type_notifications']
    }, {
        JSON: {
            notificationsDialogs: [dialog]
        }
    }) + '</div>';
};

exports.notificationsExpand = function (execView) {

    var popup = execView('TrafinfoPopup', mocks.notificationsExpand);

    var dialog = execView('Dialog', {
        type: 'notifications',
        visible: true,
        counter: '',
        attrs: {
            'data-index': 0
        },
        content: popup.content,
        cut: popup.extra,
        close: {
            type: 'button'
        }
    }, {
        JSON: {}
    });

    return '<div class="body__wrapper">' + execView('Dialogs', {
        list: ['Dialog_type_notifications']
    }, {
        JSON: {
            notificationsDialogs: [dialog]
        }
    }) + '</div>';
};
