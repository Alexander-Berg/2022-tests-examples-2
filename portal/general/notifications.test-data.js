/* eslint-env es6 */

const notifAll = require('./mocks/notifications-all');

function notificationsAlert(data) {
    return function (execView) {
        const req = Object.assign({}, data);
        return execView.withReq('Notifications', {
            items: data.Alert.list
        }, req) +
            '<div class="dialog__overlay"><div class="dialog__wrapper"><div class="dialog__list">' +
            execView.withReq('Dialog_type_notifications', {}, req) +
            '</div></div></div>';
    };
}


exports.notifAll = notificationsAlert(notifAll);
