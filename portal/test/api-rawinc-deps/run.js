var rapidoLang = require('../../run');

rapidoLang.run({
    views: [
        'api-rawinc-deps/blocks/test.view.js'
    ],
    levels: [{
        "path": "api-rawinc-deps/blocks",
        "view": "home.desktopViews",
        "target": "some.view.js"
    }],
    destDir: 'api-rawinc-deps/result',
    destView: 'desktop.view.js',
    langList: ['ru', 'uk'],
    langFile: 'api-rawinc-deps/lang.json',
    command: 'command',
    includePath: 'api-rawinc-deps/blocks',
    output: {
        watch: true
    }
}).then(function () {
    console.log('Done!');
}).catch(function (err) {
    console.error(err);
    process.exit(1);
});
