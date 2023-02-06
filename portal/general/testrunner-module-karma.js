const KarmaServer = require('karma').Server;

process.env.CHROME_BIN = require('puppeteer').executablePath();

process.on('message', function(config) {
    try {
        // Karma вызывает done много раз
        let doneFired = false;

        let server = new KarmaServer(config, function (exitCode) {
            if (doneFired) {
                return;
            }
            doneFired = true;

            if (exitCode) {
                process.send({
                    status: -1,
                    msg: 'Karma has exited with code ' + exitCode
                });
            } else {
                process.send({
                    status: 0
                });
            }

            process.exit(exitCode);
        });

        server.on('browser_error', function (browser, errorStr) {
            process.send({
                status: -1,
                msg: errorStr
            });
        });

        server.start();
    } catch (err) {
        process.send({
            status: -1,
            msg: err.stack
        });
    }
});
