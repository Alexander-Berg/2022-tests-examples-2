var rapidoLang = require('../../run');
var vow = require('vow');

rapidoLang.run({
    views: [
        'transforms-promise-error/blocks/test.view.js'
    ],
    levels: [{
        "path": "transforms-promise-error/blocks",
        "view": "home.desktopViews",
        "target": "some.view.js"
    }],
    destDir: 'transforms-promise-error/result',
    destView: 'desktop.view.js',
    langList: ['ru', 'uk'],
    langFile: 'transforms-promise-error/lang.json',
    command: 'command',
    includePath: 'transforms-promise-error/blocks',
    transforms: [function (fileName, contents, opts) {
        var defer = vow.defer();

        setTimeout(function () {
            defer.reject('Transform with promise error');
        }, 50);

        return defer.promise();
    }]
}).then(function () {
    console.log('Done!');
}).catch(function (err) {
    console.error(err);
    process.exit(1);
});
