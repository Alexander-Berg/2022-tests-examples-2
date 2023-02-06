var rapidoLang = require('../../run');

rapidoLang.run({
    views: [
        'api-run/blocks/test.view.js',
        'api-run/blocks/test2.view.js',
        'api-run/blocks/test3.view.js'
    ],
    levels: [{
        "path": "api-run/blocks",
        "view": "home.desktopViews",
        "target": "some.view.js"
    }],
    destDir: 'api-run/result',
    destView: 'desktop.view.js',
    langList: ['ru', 'uk'],
    langFile: 'api-run/lang.json',
    command: 'command',
    includePath: 'api-run/blocks',
    output: {
        watch: true
    }
}).then(function () {
    console.log('Done!');
}).catch(function (err) {
    console.error(err);
    process.exit(1);
});
