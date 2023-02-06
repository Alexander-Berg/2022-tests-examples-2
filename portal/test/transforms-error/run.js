var rapidoLang = require('../../run');

rapidoLang.run({
    views: [
        'transforms-error/blocks/test.view.js'
    ],
    levels: [{
        "path": "transforms-error/blocks",
        "view": "home.desktopViews",
        "target": "some.view.js"
    }],
    destDir: 'transforms-error/result',
    destView: 'desktop.view.js',
    langList: ['ru', 'uk'],
    langFile: 'transforms-error/lang.json',
    command: 'command',
    includePath: 'transforms-error/blocks',
    transforms: [function (fileName, contents, opts) {
        throw 'TransformError';
    }]
}).then(function () {
    console.log('Done!');
}).catch(function (err) {
    console.error(err);
    process.exit(1);
});
