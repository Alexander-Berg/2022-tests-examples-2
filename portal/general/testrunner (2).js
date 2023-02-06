const fs = require('fs'),
    path = require('path'),
    childProcess = require('child_process');

module.exports = function (config) {
    config.base = path.resolve(config.base || '.');

    config.relFiles = [];
    config.absFiles = [];

    config.files.forEach(function (file) {
        var filename = file.indexOf('/') === 0 ? path.relative(config.base, file) : file,
            absFilename = path.join(config.base, filename);

        if (!fs.existsSync(absFilename)) {
            throw new Error(absFilename + ' not found');
        }
        config.relFiles.push(filename);
        config.absFiles.push(absFilename);
    });

    if (config.browser) {
        return runKarma(config);
    } else {
        return runMocha(config);
    }
};

function runMocha(config) {
    /* fork нужен, потому что последовательные запуски mocha влияют друг на друга */
    return new Promise(function (resolve, reject) {
        let startTime = Date.now();

        let mocha = childProcess.fork(path.resolve(path.dirname(module.filename), 'testrunner-module-mocha'), {
                silent: true,
                env: {
                    ENB_DIR: config.base,
                    MOCHA_COLORS: 1
                }
            }),
            output = ['target: ' + config.target + '\n'];

        mocha.stdout.on('data', function (data) {
            output.push(data.toString('utf-8'));
        });
        mocha.stderr.on('data', function (data) {
            output.push('ERR:' + data.toString('utf-8'));
        });

        mocha.on('message', function (data) {
            let completed;

            data.output = output.join('');
            data.time = ((Date.now() - startTime) / 1000).toFixed(3);
            data.tests = 0;
            completed = data.output.match(/(\d+).+passing.+\(/);
            if (completed && completed[1]) {
                data.tests = completed[1];
            } else {
                completed = data.output.match(/testFinished/g);
                if (completed) {
                    data.tests = completed.length;
                }
            }

            if (data.status === -1) {
                reject(data);
            } else {
                resolve(data);
            }
        });

        mocha.on('exit', function (code, signal) {
            if (code) {
                var data = {
                    output: output.join(''),
                    msg: `Mocha ended with "${signal}"`,
                    time: ((Date.now() - startTime) / 1000).toFixed(3),
                    tests: 0
                };
                reject(data);
            }
        });

        mocha.send(config);
    });
}

function runKarma(config) {
    return new Promise(function (resolve, reject) {
        let startTime = Date.now();

        config = getKarmaConfiguration(config);

        let karma = childProcess.fork(path.resolve(__dirname, 'testrunner-module-karma'), {
                silent: true
            }),
            output = ['target: ' + config.files + '\n'];

        karma.stdout.on('data', function (data) {
            output.push(data.toString('utf-8'));
        });
        karma.stderr.on('data', function (data) {
            output.push('ERR:' + data.toString('utf-8'));
        });

        karma.on('message', function (data) {
            let completed;

            data.output = output.join('');
            data.time = ((Date.now() - startTime) / 1000).toFixed(3);
            data.tests = 0;
            completed = data.output.match(/(\d+) tests? completed/);
            if (completed && completed[1]) {
                data.tests = completed[1];
            } else {
                completed = data.output.match(/testFinished/g);
                if (completed) {
                    data.tests = completed.length;
                }
            }

            if (data.status === -1) {
                reject(data);
            } else {
                resolve(data);
            }
        });

        karma.on('exit', function (code, signal) {
            if (code) {
                var data = {
                    output: output.join(''),
                    msg: `Karma ended with "${signal}"`,
                    time: ((Date.now() - startTime) / 1000).toFixed(3),
                    tests: 0
                };
                console.error('reject!');
                reject(data);
            }
        });

        karma.send(config);
    });
}

function getKarmaConfiguration(config) {
    return {
        files: config.files,
        basePath: config.base,
        autoWatch: false,
        singleRun: true,
        failOnEmptyTestSuite: false,
        configFile: config.karmaconf,
        browsers: ['ChromeHeadless'],
        frameworks: ['mocha', config.jQuery || 'jquery-2.1.4'],
        reporters: [config.reporter || 'mocha'],
        hostname: 'localhost',
        listenAddress: 'localhost',
        port: config.port || 9876,
        mochaReporter: {
            showDiff: true,
            output: 'full'
        },
        allureReport: {
            reportDir: '.'
        }
    };
}
