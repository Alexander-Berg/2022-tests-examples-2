var rapidoLang = require('../../run');
var vow = require('vow');

rapidoLang.run({
    views: [
        'transforms-multiple/blocks/test.view.html',
        'transforms-multiple/blocks/test2.view.js'
    ],
    levels: [{
        "path": "transforms-multiple/blocks",
        "view": "home.desktopViews",
        "target": "some.view.js"
    }],
    destDir: 'transforms-multiple/result',
    destView: 'desktop.view.js',
    langList: ['ru', 'uk'],
    langFile: 'transforms-multiple/lang.json',
    command: 'command',
    includePath: 'transforms-multiple/blocks',
    output: {
        watch: true
    },
    transforms: [function (fileName, contents) {
        if (fileName.indexOf('.html') > -1) {
            return 'views(\'viewName\', \'' + contents.trim() + '\');\n';
        }
        return contents;
    }, function (fileName, contents, opts) {
        var defer = vow.defer();

        setTimeout(function () {
            defer.resolve('// wait: done\n' + contents);
        }, 50);

        return defer.promise();
    }, function (fileName, contents) {
        if (contents.indexOf('wait: done') === -1) {
            throw 'No wait';
        }
        return contents.replace(/morda/, 'home');
    }]
}).then(function () {
    console.log('Done!');
}).catch(function (err) {
    console.error(err);
    process.exit(1);
});
