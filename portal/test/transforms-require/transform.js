var path = require('path');

module.exports = function (fileName, contents) {
    "use strict";
    return '// file: ' + path.basename(fileName) + '\n' + contents;
};
