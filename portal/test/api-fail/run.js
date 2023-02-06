var rapidoLang = require('../../run');

rapidoLang.run({
    views: [
        'api-fail/blocks/test.view.js',
        'api-fail/blocks/test2.view.js',
        'api-fail/blocks/test3.view.js'
    ],
    levels: [{
        "path": "api-fail/blocks",
        "view": "home.desktopViews",
        "target": "some.view.js"
    }],
    destDir: 'api-fail/result',
    destView: 'desktop.view.js',
    langList: ['ru', 'uk'],
    langFile: 'api-fail/lang.json',
    command: 'command',
    includePath: 'api-fail/blocks'
}).then(function () {
    console.log('Done!');
}).catch(function (err) {
    console.error(err.message);
    process.exit(1);
});
