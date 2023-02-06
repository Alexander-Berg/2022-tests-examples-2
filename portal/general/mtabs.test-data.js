const mtabs = require('./mocks/mtabs.json');

exports.simple = function (execView) {
    return execView('Mtabs', {}, mtabs);
};
