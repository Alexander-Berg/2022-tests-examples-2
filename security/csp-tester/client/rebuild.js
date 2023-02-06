var fs = require('fs'),
    path = require('path'),
    make = require('enb').make,
    watch = require('chokidar').watch,
    watchOpts = {
        persistent: true,
        ignoreInitial: true
    };

process.env.NO_AUTOMAKE || watch([
    path.join(__dirname, 'blocks', '**'),
    path.join(__dirname, 'pages', 'index', 'index.bemjson.js')
], watchOpts).on('all', function(event, file) {
    return make([], { dir: __dirname })
        .then(function() { console.log('Build finished'); })
        .fail(console.error);
});
