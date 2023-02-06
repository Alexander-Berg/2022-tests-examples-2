var Mocha = require('mocha');

/* Этот require нужен */
var chai = require('chai');
var chaiAsPromised = require('chai-as-promised');
require('sinon');
var sinonChai = require('sinon-chai');

chai.use(sinonChai);
chai.use(chaiAsPromised);
chai.should();

global.expect = chai.expect;
global.assert = chai.assert;

require('./viewhtml-loader');

process.on('message', function(config) {
    try {
        var mocha = new Mocha();

        mocha.globals('*');

        if (config.reporter) {
            mocha.reporter(config.reporter);
        }

        config.absFiles.forEach(mocha.addFile, mocha);

        mocha.run(function(exitCode) {
            if (exitCode) {
                process.send({
                    status: -1,
                    msg: 'Mocha has exited with code ' + exitCode
                });
            } else {
                process.send({
                    status: 0
                });
            }

            process.exit(exitCode);
        });
    } catch (e) {
        console.error(e.stack);
        process.send({
            status: -1,
            msg: e.stack
        });

        process.exit();
    }
});
