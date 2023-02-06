const preconfigured = require('./mocks/preconfigured');
const tuned = require('./mocks/tuned');
const ajaxResponse = require('./mocks/ajax-response');

exports.simple = execView => execView('Etrains', {
    ...preconfigured
});

exports.tuned = execView => execView('Script', {
    content: `
        MBEM.blocks.etrains.prototype._loadData = function () {
            return new Promise(function (resolve) {
                window.respond = function () {
                    resolve(${JSON.stringify(ajaxResponse)});
                };
            });
        };
    `
}) + execView('Etrains', {
    ...tuned
});
