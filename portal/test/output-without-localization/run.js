var rapidoLang = require('../../run');

rapidoLang.run({
    views: [
        'blocks/test.view.js',
        'blocks2/test.view.js'
    ],
    levels: [{
        "path": "blocks",
        "view": "home.desktopViews",
        "target": "some.view.js"
    }, {
        "path": "blocks2",
        "view": "home.desktopViews2",
        "target": "some2.view.js"
    }],
    destDir: 'result',
    destView: 'desktop.view.js',
    langList: ['ru', 'uk'],
    langFile: 'lang.json',
    command: 'command',
    includePath: 'blocks',
    rootDir: 'output-without-localization',
    output: {
        localize: false
    }
}).then(function () {
    console.log('Done!');
}).catch(function (err) {
    console.error(err);
    process.exit(1);
});
