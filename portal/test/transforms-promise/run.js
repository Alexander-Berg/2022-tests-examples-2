var rapidoLang = require('../../run');
var vow = require('vow');

rapidoLang.run({
    views: [
        'transforms-promise/blocks/test.view.js'
    ],
    levels: [{
        "path": "transforms-promise/blocks",
        "view": "home.desktopViews",
        "target": "some.view.js"
    }],
    destDir: 'transforms-promise/result',
    destView: 'desktop.view.js',
    langList: ['ru', 'uk'],
    langFile: 'transforms-promise/lang.json',
    command: 'command',
    includePath: 'transforms-promise/blocks',
    output: {
        watch: true
    },
    transforms: [function (fileName, contents, opts) {
        var defer = vow.defer();

        setTimeout(function () {
            defer.resolve('// wait: done\n' + contents);
        }, 50);

        return defer.promise();
    }]
}).then(function () {
    console.log('Done!');
}).catch(function (err) {
    console.error(err);
    process.exit(1);
});
